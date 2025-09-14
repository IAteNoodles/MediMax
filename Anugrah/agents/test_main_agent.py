#!/usr/bin/env python3
"""
Test MainAgent specifically with complete data
"""

import os
from dotenv import load_dotenv
load_dotenv()

from medimax.agents.main_agent import MainAgent
from medimax.llm.groq_client import GroqLLM

def test_main_agent():
    print("=== MainAgent Test ===")
    
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
        groq = GroqLLM()
        main_agent = MainAgent(groq)
        
        print("\nCalling MainAgent...")
        response = main_agent.handle(payload)
        
        print(f"Action: {response.action}")
        print(f"Status: {response.status}")
        print(f"Next Agent: {response.next_agent}")
        print(f"Missing Parameters: {response.missing_parameters}")
        print(f"Routing Explanation: {response.routing_explanation}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_agent()
