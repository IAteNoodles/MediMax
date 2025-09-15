from __future__ import annotations
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from medimax.util.specs_loader import ModelSpecs
from medimax.llm.medgemma import MedGemmaClient
from medimax.agents.router_agent import RouterAgent
from medimax.agents.main_agent import MainAgent
from medimax.llm.groq_client import GroqLLM
from medimax.mcp.client import MCPClient

class GraphState(BaseModel):
    payload: Dict[str, Any]
    result: Dict[str, Any] = Field(default_factory=dict)
    action: str = ""
    next_agent: str = ""

# Node functions

def main_agent_node(state: GraphState, main_agent: MainAgent):
    """Main agent makes orchestration decisions using LLM."""
    response = main_agent.handle(state.payload)
    
    # Update payload with enhanced structured data if available
    if response.enhanced_payload:
        state.payload.update(response.enhanced_payload)
        print(f"[MainAgent] Updated payload with extracted data: {list(response.enhanced_payload.keys())}")
    
    state.result = {
        'status': response.status,
        'action': response.action,
        'missing_parameters': response.missing_parameters,
        'report': response.report,
        'predictions': response.predictions,
        'follow_up_questions': response.follow_up_questions,
        'routing_explanation': response.routing_explanation,
        'routing_summary': response.routing_summary
    }
    state.action = response.action
    state.next_agent = response.next_agent or ""
    return state

def router_agent_node(state: GraphState, router_agent: RouterAgent):
    """Router agent makes model selection decisions using LLM."""
    response = router_agent.route(state.payload)
    
    state.result.update({
        'need_more_data': response.need_more_data,
        'missing_parameters': response.missing_parameters,
        'predictions': response.predictions,
        'report': response.report,
        'follow_up_questions': response.follow_up_questions,
        'routing_explanation': response.routing_explanation,
        'debug_info': response.debug_info
    })
    
    # Set final status based on router result
    if response.need_more_data:
        state.result['status'] = 'need_more_data'
        state.action = 'need_more_data'
    else:
        state.result['status'] = 'complete'
        state.action = 'complete'
        
    return state

def decide_next_from_main(state: GraphState):
    """Decide next step based on main agent decision."""
    if state.action == 'route_to_models' and state.next_agent == 'router':
        return 'router'
    elif state.action == 'need_more_data':
        return 'need_more_data'
    elif state.action == 'complete':
        return 'complete'
    else:
        return 'need_more_data'  # Default fallback

def decide_next_from_router(state: GraphState):
    """Decide next step based on router agent result."""
    if state.action == 'need_more_data':
        return 'need_more_data'
    else:
        return 'complete'

def build_graph(specs_path: str, mcp_url: str, medgemma_url: str, use_groq: bool = True):
    """Build LangGraph with LLM-based agents."""
    if not use_groq:
        raise ValueError("LLM-based agents require Groq API - set use_groq=True")
        
    # Initialize components
    specs = ModelSpecs(specs_path)
    medgemma = MedGemmaClient(medgemma_url)
    mcp = MCPClient(mcp_url)
    groq = GroqLLM()  # Required for LLM-based agents
    
    # Create LLM-based agents
    router_agent = RouterAgent(specs, medgemma, mcp, groq)
    main_agent = MainAgent(groq)

    # Build graph
    sg = StateGraph(GraphState)

    def _main_action(state: GraphState):
        return main_agent_node(state, main_agent)
    
    def _router_action(state: GraphState):
        return router_agent_node(state, router_agent)

    # Add nodes
    sg.add_node('main', _main_action)
    sg.add_node('router', _router_action)
    
    # Set entry point
    sg.set_entry_point('main')
    
    # Add conditional edges from main agent
    sg.add_conditional_edges('main', decide_next_from_main, {
        'router': 'router',
        'need_more_data': END,
        'complete': END
    })
    
    # Add conditional edges from router agent  
    sg.add_conditional_edges('router', decide_next_from_router, {
        'need_more_data': END,
        'complete': END
    })
    
    return sg.compile()
