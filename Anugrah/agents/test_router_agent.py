#!/usr/bin/env python3
"""
Test RouterAgent with mock MCP and MedGemma to avoid network issues
"""

import os
from dotenv import load_dotenv
load_dotenv()

from medimax.agents.router_agent import RouterAgent
from medimax.util.specs_loader import ModelSpecs
from medimax.llm.groq_client import GroqLLM

# Mock classes for testing
class MockMCPClient:
    def __init__(self, url):
        self.url = url
    
    def predict_cardio(self, **params):
        return {"prediction": 1, "probability": 0.7}
    
    def predict_diabetes(self, **params):
        return {"prediction": 0, "probability": 0.3}
    
    def close(self):
        pass

class MockMedGemmaClient:
    def __init__(self, url):
        self.url = url
    
    def generate_report(self, context: str, predictions):
        return {
            "content": f"Mock medical report: Based on the cardiovascular risk assessment, the patient shows elevated risk factors including hypertension and age. Context: {context[:50]}..."
        }

def test_router_agent():
    print("=== RouterAgent Test (with mocks) ===")
    
    # Complete payload 
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
        specs = ModelSpecs('medimax/util/model_specs.yaml')
        mock_medgemma = MockMedGemmaClient("http://mock:1234")
        mock_mcp = MockMCPClient("http://mock:8000")
        groq = GroqLLM()
        
        router_agent = RouterAgent(specs, mock_medgemma, mock_mcp, groq)
        
        print("\nCalling RouterAgent...")
        response = router_agent.route(payload)
        
        print(f"Need More Data: {response.need_more_data}")
        print(f"Missing Parameters: {response.missing_parameters}")
        print(f"Predictions: {response.predictions}")
        print(f"Report: {response.report}")
        print(f"Routing Explanation: {response.routing_explanation}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_router_agent()
