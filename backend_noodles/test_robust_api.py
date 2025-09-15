"""
Test script for the robust chat API
"""

import asyncio
import httpx
import json
from datetime import datetime

# Test configuration
API_BASE_URL = "http://127.0.0.1:8000"
TEST_PATIENT_ID = 20

async def test_health_check():
    """Test the health check endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health")
            print(f"Health Check: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

async def test_chat_query():
    """Test the chat endpoint with patient medication query"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            test_message = f"What medications is patient {TEST_PATIENT_ID} taking?"
            
            chat_request = {
                "message": test_message,
                "session_id": f"test_session_{datetime.now().isoformat()}",
                "context": {"test": True},
                "max_retries": 3
            }
            
            print(f"\nSending chat request: {test_message}")
            response = await client.post(f"{API_BASE_URL}/chat", json=chat_request)
            
            print(f"Chat Response Status: {response.status_code}")
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
            
            return response.status_code == 200
    except Exception as e:
        print(f"Chat test failed: {e}")
        return False

async def test_complex_query():
    """Test a more complex medical query"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            test_message = "Can you help me understand the cardiovascular risk factors for a 45-year-old male patient?"
            
            chat_request = {
                "message": test_message,
                "session_id": "test_complex_session",
                "max_retries": 2
            }
            
            print(f"\nSending complex query: {test_message}")
            response = await client.post(f"{API_BASE_URL}/chat", json=chat_request)
            
            print(f"Complex Query Status: {response.status_code}")
            response_data = response.json()
            print(f"Response: {response_data.get('response', 'No response')[:200]}...")
            
            return response.status_code == 200
    except Exception as e:
        print(f"Complex query test failed: {e}")
        return False

async def run_tests():
    """Run all tests"""
    print("Starting Robust Chat API Tests")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing Health Check...")
    health_ok = await test_health_check()
    
    if not health_ok:
        print("❌ Health check failed - API may not be running")
        print("Please start the API with: python robust_chat_api_v2.py")
        return
    
    print("✅ Health check passed")
    
    # Wait a moment for full initialization
    await asyncio.sleep(2)
    
    # Test 2: Patient medication query
    print("\n2. Testing Patient Medication Query...")
    medication_ok = await test_chat_query()
    
    if medication_ok:
        print("✅ Patient medication query passed")
    else:
        print("❌ Patient medication query failed")
    
    # Test 3: Complex medical query
    print("\n3. Testing Complex Medical Query...")
    complex_ok = await test_complex_query()
    
    if complex_ok:
        print("✅ Complex medical query passed")
    else:
        print("❌ Complex medical query failed")
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Medication Query: {'✅' if medication_ok else '❌'}")
    print(f"Complex Query: {'✅' if complex_ok else '❌'}")
    
    total_passed = sum([health_ok, medication_ok, complex_ok])
    print(f"\nTotal: {total_passed}/3 tests passed")

if __name__ == "__main__":
    print("Robust Chat API Test Suite")
    print("Make sure the API is running: python robust_chat_api_v2.py")
    print("Press Ctrl+C to cancel\n")
    
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
    except Exception as e:
        print(f"Test suite error: {e}")