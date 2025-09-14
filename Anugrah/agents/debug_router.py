#!/usr/bin/env python3
"""
Debug RouterAgent to see where it's failing
"""

import os
from dotenv import load_dotenv
load_dotenv()

def debug_router():
    # Test payload with complete data
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
    
    print("=== Router Debug ===")
    print(f"Payload: {payload}")
    
    # Test the _extract method
    from medimax.agents.router_agent import RouterAgent
    from medimax.util.specs_loader import ModelSpecs
    from medimax.llm.groq_client import GroqLLM
    from medimax.llm.medgemma import MedGemmaClient
    from medimax.mcp.client import MCPClient
    
    specs = ModelSpecs('medimax/util/model_specs.yaml')
    medgemma = MedGemmaClient("http://10.26.5.99:1234")
    mcp = MCPClient("http://10.26.5.29:8000")
    groq = GroqLLM()
    
    router = RouterAgent(specs, medgemma, mcp, groq)
    
    # Test extraction
    numeric, text = router._extract(payload)
    print(f"\nExtracted numeric: {numeric}")
    print(f"Extracted text: {text}")
    
    # Test model requirements
    model_specs = router._get_model_requirements()
    print(f"\nModel requirements: {model_specs}")
    
    # Check which parameters are available vs required for cardiovascular model
    cardio_required = model_specs.get('cardiovascular_risk', [])
    print(f"\nCardiovascular model requires: {cardio_required}")
    print(f"Available parameters: {list(numeric.keys())}")
    
    missing_params = [p for p in cardio_required if p not in numeric]
    print(f"Missing parameters: {missing_params}")
    
    # Test MCP call directly
    try:
        print(f"\nTesting MCP cardiovascular prediction...")
        # Filter params to only what's required
        cardio_params = {k: v for k, v in numeric.items() if k in cardio_required}
        print(f"Sending to MCP: {cardio_params}")
        
        result = mcp.predict_cardio(**cardio_params)
        print(f"MCP result: {result}")
    except Exception as e:
        print(f"MCP call failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_router()
