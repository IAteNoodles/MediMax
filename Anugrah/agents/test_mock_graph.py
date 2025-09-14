#!/usr/bin/env python3
"""
Test the complete graph with debug output but using mock mode to avoid network issues
"""

import os
from dotenv import load_dotenv
load_dotenv()
os.environ['MEDIMAX_DEBUG'] = '1'

from medimax.graph import GraphState

def test_with_mock():
    print("=== Test Complete Graph with Mock ===")
    
    # Complete data payload
    payload = {
        "patient_history": "55-year-old male with hypertension",
        "symptoms": "Headache, fatigue, chest tightness", 
        "query": "Assess cardiovascular risk",
        "age": 55,
        "gender": 1,
        "height": 175,
        "weight": 80,
        "ap_hi": 140,
        "ap_lo": 90,
        "cholesterol": 200,
        "gluc": 100,
        "smoke": 0,
        "alco": 0,
        "active": 1
    }
    
    print(f"Input: {payload}")
    
    # Mock the problematic classes
    from medimax.util.specs_loader import ModelSpecs
    from medimax.llm.groq_client import GroqLLM
    
    class MockMCPClient:
        def __init__(self, url):
            self.base_url = url
        
        def predict_cardio(self, **params):
            print(f"[MOCK] predict_cardio called with: {params}")
            return {"prediction": 1, "probability": 0.75, "explanation": "High cardiovascular risk"}
        
        def predict_diabetes(self, **params):
            print(f"[MOCK] predict_diabetes called with: {params}")
            return {"prediction": 0, "probability": 0.25, "explanation": "Low diabetes risk"}
        
        def close(self):
            pass
    
    class MockMedGemmaClient:
        def __init__(self, url):
            self.base_url = url
        
        def generate_report(self, context, predictions):
            print(f"[MOCK] generate_report called with context: {context[:50]}...")
            print(f"[MOCK] predictions: {predictions}")
            return {
                "content": "MOCK REPORT: Patient shows high cardiovascular risk based on age, hypertension, and cholesterol levels."
            }
    
    # Build graph with mocks
    from medimax.agents.main_agent import MainAgent
    from medimax.agents.router_agent import RouterAgent
    from langgraph.graph import StateGraph, END
    
    specs = ModelSpecs('medimax/util/model_specs.yaml')
    mock_medgemma = MockMedGemmaClient("http://mock")
    mock_mcp = MockMCPClient("http://mock")
    groq = GroqLLM()
    
    main_agent = MainAgent(groq)
    router_agent = RouterAgent(specs, mock_medgemma, mock_mcp, groq)
    
    def main_node(state):
        response = main_agent.handle(state.payload)
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
    
    def router_node(state):
        response = router_agent.route(state.payload)
        state.result.update({
            'need_more_data': response.need_more_data,
            'missing_parameters': response.missing_parameters,
            'predictions': response.predictions,
            'report': response.report,
            'follow_up_questions': response.follow_up_questions,
            'routing_explanation': response.routing_explanation
        })
        
        if response.need_more_data:
            state.result['status'] = 'need_more_data'
            state.action = 'need_more_data'
        else:
            state.result['status'] = 'complete'
            state.action = 'complete'
        
        return state
    
    def decide_from_main(state):
        if state.action == 'route_to_models' and state.next_agent == 'router':
            return 'router'
        elif state.action == 'need_more_data':
            return 'need_more_data'
        else:
            return 'complete'
    
    def decide_from_router(state):
        return 'complete' if state.action == 'complete' else 'need_more_data'
    
    # Build graph
    sg = StateGraph(GraphState)
    sg.add_node('main', main_node)
    sg.add_node('router', router_node)
    sg.set_entry_point('main')
    sg.add_conditional_edges('main', decide_from_main, {
        'router': 'router',
        'need_more_data': END,
        'complete': END
    })
    sg.add_conditional_edges('router', decide_from_router, {
        'need_more_data': END,
        'complete': END
    })
    
    graph = sg.compile()
    
    print("\nExecuting graph...")
    result = graph.invoke(GraphState(payload=payload))
    
    print(f"\nFinal result: {result}")
    print(f"Result keys: {list(result.keys())}")
    if 'result' in result:
        print(f"Result content: {result['result']}")

if __name__ == "__main__":
    test_with_mock()
