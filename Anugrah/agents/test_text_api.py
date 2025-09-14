#!/usr/bin/env python3
"""Test script for the text-based API endpoint."""

import requests
import json

def test_text_api():
    """Test the text-based assessment API."""
    
    # Test data - free-form patient text
    patient_text = """
    Patient is a 45-year-old male who came in for a routine check-up. 
    He weighs 185 pounds and is 5'10" tall. 
    His blood pressure was measured at 140/90 mmHg. 
    He has been smoking for 20 years and drinks alcohol occasionally. 
    He doesn't exercise regularly. 
    His cholesterol level is 240 mg/dL and blood glucose is 110 mg/dL.
    He has a family history of heart disease.
    He's complaining of occasional chest pain and shortness of breath.
    """
    
    payload = {
        "patient_text": patient_text,
        "query": "Assess cardiovascular risk for this patient",
        "additional_notes": "Patient seems concerned about family history"
    }
    
    # Test the API
    try:
        print("🧪 Testing text-based assessment API...")
        print(f"📝 Patient text (first 100 chars): {patient_text[:100]}...")
        
        response = requests.post(
            "http://localhost:8000/assess",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Assessment successful!")
            print(f"📋 Status: {result.get('status')}")
            print(f"🎯 Action: {result.get('action')}")
            print(f"🧠 Routing explanation: {result.get('routing_explanation')}")
            
            if result.get('predictions'):
                print("📈 Predictions:")
                for pred in result['predictions']:
                    print(f"  - {pred.get('model_name')}: {pred.get('prediction')}")
            
            if result.get('report'):
                print(f"📄 Medical report: {result['report'][:200]}...")
                
            print(f"🔍 Debug info: {result.get('debug_info')}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_text_api()
