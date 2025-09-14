#!/usr/bin/env python3
"""
Test MCP endpoint with a simple request
"""

import httpx
import json

def test_mcp_simple():
    print("=== Testing MCP Endpoint ===")
    
    url = "http://10.26.5.29:8000/chat"
    
    # Simple test message
    payload = {"message": "Hello, please respond with 'OK' to confirm you are working."}
    
    print(f"URL: {url}")
    print(f"Payload: {payload}")
    
    try:
        with httpx.Client(timeout=10.0) as client:
            print("Making request...")
            response = client.post(url, json=payload)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")  # First 200 chars
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"Response field: {data.get('response', 'No response field')}")
                except:
                    print("Not JSON response")
            
    except httpx.TimeoutException:
        print("Request timed out")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_mcp_simple()
