#!/usr/bin/env python3
"""
Quick test script to demonstrate the orchestration graph in action.
Shows both missing parameters and complete flow scenarios.
"""

import os
from medimax.graph import build_graph, GraphState

# Mock mode endpoints (will fail gracefully if unreachable)
MCP_URL = "http://10.26.5.29:8000"
MEDGEMMA_URL = "http://10.26.5.99:1234"

def test_missing_params():
    """Test scenario with insufficient parameters."""
    print("=== Testing Missing Parameters Scenario ===")
    
    # Incomplete payload - only has age
    payload = {
        "patient_history": "55-year-old male with history of hypertension",
        "symptoms": "Headache, fatigue, occasional chest tightness", 
        "query": "Assess cardiovascular and diabetes risk",
        "age": 55
    }
    
    print(f"Input payload: {payload}")
    
    try:
        # Build graph without Groq first - now requires Groq for LLM agents
        print("Note: LLM-based agents require Groq API")
        if not os.getenv('GROQ_API_KEY'):
            print("Skipping test - GROQ_API_KEY required for LLM-based agents")
            return
            
        graph = build_graph('medimax/util/model_specs.yaml', MCP_URL, MEDGEMMA_URL, use_groq=True)
        state = graph.invoke(GraphState(payload=payload))
        
        print(f"Result (LLM agents): {state['result']}")
        
        # Show the LLM-based decision process
        if 'routing_explanation' in state['result'] and state['result']['routing_explanation']:
            print(f"LLM Reasoning: {state['result']['routing_explanation'][:200]}...")
        
        # Now test without Groq (will fail gracefully)
        print("\n--- Testing without Groq (should show error) ---")
        try:
            graph_no_groq = build_graph('medimax/util/model_specs.yaml', MCP_URL, MEDGEMMA_URL, use_groq=False)
        except ValueError as e:
            print(f"Expected error: {e}")
        
        # Remove the old Groq conditional test since it's now required
        # if os.getenv('GROQ_API_KEY'):
        #     print("\n--- With Groq enabled ---")
        #     graph_groq = build_graph('medimax/util/model_specs.yaml', MCP_URL, MEDGEMMA_URL, use_groq=True)
        #     state_groq = graph_groq.invoke(GraphState(payload=payload))
        #     print(f"Result (with Groq): {state_groq['result']}")
        # else:
        #     print("\nSkipping Groq test - no GROQ_API_KEY in environment")
            
    except Exception as e:
        print(f"Error: {e}")
        print("This is expected if MCP/MedGemma endpoints are unreachable")

def test_complete_params():
    """Test scenario with complete cardiovascular parameters."""
    print("\n=== Testing Complete Parameters Scenario ===")
    
    # Complete payload for cardiovascular model
    payload = {
        "patient_history": "55-year-old male with hypertension, non-smoker, active lifestyle",
        "symptoms": "Occasional chest tightness during exercise",
        "query": "Assess cardiovascular risk",
        "age": 55,
        "gender": 2,  # male
        "height": 172,
        "weight": 82,
        "ap_hi": 140,  # systolic BP
        "ap_lo": 90,   # diastolic BP
        "cholesterol": 2,  # elevated
        "gluc": 1,     # normal
        "smoke": 0,    # no
        "alco": 0,     # no
        "active": 1    # yes
    }
    
    print(f"Input payload keys: {list(payload.keys())}")
    
    try:
        if not os.getenv('GROQ_API_KEY'):
            print("Skipping complete test - GROQ_API_KEY required for LLM-based agents")
            return
            
        graph = build_graph('medimax/util/model_specs.yaml', MCP_URL, MEDGEMMA_URL, use_groq=True)
        state = graph.invoke(GraphState(payload=payload))
        
        result = state['result']
        print(f"Status: {result.get('status')}")
        print(f"Action: {result.get('action')}")
        print(f"Need more data: {result.get('need_more_data')}")
        print(f"Predictions count: {len(result.get('predictions', []))}")
        if result.get('routing_explanation'):
            print(f"LLM Routing Decision: {result['routing_explanation'][:150]}...")
        if result.get('report'):
            print(f"Report preview: {result['report'][:100]}...")
            
    except Exception as e:
        print(f"Error: {e}")
        print("This is expected if MCP/MedGemma endpoints are unreachable")

if __name__ == "__main__":
    # Load environment if .env exists
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
    test_missing_params()
    test_complete_params()
    
    print("\n=== Demo Complete ===")
    print("To test with live endpoints, ensure MCP and MedGemma services are running.")
    print("To enable Groq explanations, set GROQ_API_KEY in .env file.")
