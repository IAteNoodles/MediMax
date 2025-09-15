"""
Test client for the Knowledge Base (/kb) endpoint
This script tests the new /kb route that converts natural language to Cypher
and forwards the query to an external service.
"""

import requests
import json
from typing import Dict, Any

def test_kb_endpoint(base_url: str = "http://localhost:8000", message: str = "Find all patients with diabetes"):
    """
    Test the /kb endpoint
    
    Args:
        base_url: Base URL of the FastAPI server
        message: Natural language message to convert to Cypher
    """
    kb_url = f"{base_url}/kb"
    
    # Prepare the request payload
    payload = {
        "message": message
    }
    
    try:
        print(f"🔍 Testing KB endpoint with message: '{message}'")
        print(f"📡 Sending POST request to: {kb_url}")
        
        # Send the request
        response = requests.post(kb_url, json=payload, timeout=30)
        
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response:")
            print(f"   Original Message: {data.get('message')}")
            print(f"   Generated Cypher: {data.get('cypher_query')}")
            print(f"   External Data: {json.dumps(data.get('data', {}), indent=2)}")
        else:
            print(f"❌ Error Response:")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print(f"   {response.text}")
        
        return response
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the FastAPI server is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: The request took too long")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return None


def test_health_check(base_url: str = "http://localhost:8000"):
    """Test if the server is running"""
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            endpoints = data.get('endpoints', {})
            if 'kb' in endpoints:
                print("✅ Server is running and /kb endpoint is available")
                return True
            else:
                print("⚠️  Server is running but /kb endpoint not found")
                return False
        else:
            print(f"⚠️  Server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Testing Knowledge Base Endpoint")
    print("=" * 50)
    
    # First check if server is running
    if not test_health_check():
        print("\n💡 Please start the FastAPI server first:")
        print("   python fastapi_server.py")
        exit(1)
    
    print("\n🧪 Running tests...")
    
    # Test cases
    test_cases = [
        "Find all patients with diabetes",
        "Show me patients with high blood pressure",
        "Get all appointments for today",
        "List medications for cardiovascular conditions",
        "Find patients who have had recent lab tests"
    ]
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n--- Test {i} ---")
        test_kb_endpoint(message=test_message)
        print("-" * 30)
    
    print("\n🎉 Testing completed!")