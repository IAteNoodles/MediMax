#!/usr/bin/env python3
"""
Quick debug test for the LLM-based graph
"""

import os
from medimax.graph import build_graph, GraphState

def test_graph_debug():
    print("=== Graph Debug Test ===")
    
    # Test with COMPLETE data to see full flow
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
        "glucose": 100,
        "smoking": 0,
        "alcohol": 0,
        "activity": 1
    }
    
    print(f"Input payload: {payload}")
    
    try:
        print("\nBuilding graph...")
        graph = build_graph('medimax/util/model_specs.yaml', "http://10.26.5.29:8000", "http://10.26.5.99:1234", use_groq=True)
        print("Graph built successfully")
        
        print("\nInvoking graph...")
        import time
        start_time = time.time()
        state_obj = graph.invoke(GraphState(payload=payload))
        end_time = time.time()
        print(f"Graph execution completed in {end_time - start_time:.2f} seconds")
        print(f"State object type: {type(state_obj)}")
        print(f"State object: {state_obj}")
        
        if isinstance(state_obj, dict):
            result = state_obj.get('result', {})
        else:
            result = getattr(state_obj, 'result', {})
            
        print(f"\nResult: {result}")
        print(f"Result type: {type(result)}")
        
        if result:
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print("Result is empty!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Load environment
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
    test_graph_debug()
