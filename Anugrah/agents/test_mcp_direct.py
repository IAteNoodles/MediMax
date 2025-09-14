#!/usr/bin/env python3
"""
Direct MCP endpoint test
"""

import httpx
import json

def test_mcp_direct():
    print("=== Direct MCP Test ===")
    
    # Test the exact call the MCP client makes
    url = "http://10.26.5.29:8000/chat"
    
    message = """You are a system orchestrator. Call the tool exactly with the provided parameters.
Tool: Predict_Cardiovascular_Risk_With_Explanation
Parameters:
- age=55
- gender=1
- height=175
- weight=80
- ap_hi=140
- ap_lo=90
- cholesterol=200
- gluc=100
- smoke=0
- alco=0
- active=1
Return ONLY the tool JSON output."""

    payload = {"message": message}
    
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"JSON response: {data}")
            else:
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_mcp_direct()
