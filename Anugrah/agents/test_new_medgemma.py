#!/usr/bin/env python3
"""
Test the new MedGemma endpoint
"""

import httpx

def test_new_medgemma():
    print("=== Testing New MedGemma Endpoint ===")
    
    url = "http://10.26.5.29:11434/api/chat"
    
    payload = {
        "model": "alibayram/medgemma:4b",
        "messages": [
            {"role": "user", "content": "Tell me a simple medical fact."}
        ],
        "stream": False
    }
    
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    try:
        with httpx.Client(timeout=30.0) as client:
            print("Making request...")
            response = client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"JSON response: {data}")
                content = data.get("message", {}).get("content", "")
                print(f"Content: {content}")
            else:
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_new_medgemma()
