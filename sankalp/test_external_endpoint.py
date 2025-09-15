"""
Test script to verify external knowledge base endpoint connectivity
and parameter format
"""

import httpx
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_external_endpoint():
    """Test the external knowledge base endpoint directly"""
    
    external_endpoint = "http://10.26.5.29:8420/run_cypher_query"
    
    # Test Cypher queries to try
    test_queries = [
        "MATCH (n) RETURN count(n) LIMIT 1",  # Simple count query
        "MATCH (p:Patient) RETURN p LIMIT 5",  # Get patients
        "MATCH (n) RETURN labels(n) LIMIT 10"  # Get node labels
    ]
    
    for i, cypher_query in enumerate(test_queries, 1):
        print(f"\n--- Test {i} ---")
        print(f"Testing Cypher: {cypher_query}")
        
        # Test different parameter formats
        test_payloads = [
            {"cypher_query": cypher_query},
            {"cypher": cypher_query},
            {"query": cypher_query}
        ]
        
        for j, payload in enumerate(test_payloads, 1):
            print(f"\nTrying payload format {j}: {payload}")
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(external_endpoint, json=payload)
                    
                    print(f"Status Code: {response.status_code}")
                    print(f"Headers: {dict(response.headers)}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"✅ Success! Response: {data}")
                            print(f"✅ Correct parameter format: {list(payload.keys())[0]}")
                            return list(payload.keys())[0]  # Return the correct parameter name
                        except Exception as e:
                            print(f"⚠️  Response parsing error: {e}")
                            print(f"Raw response: {response.text}")
                    else:
                        print(f"❌ Error response: {response.text}")
                        
            except httpx.ConnectError as e:
                print(f"❌ Connection Error: {e}")
                print("🔍 Check if the external service is running and accessible")
            except httpx.TimeoutException:
                print(f"❌ Timeout Error")
            except Exception as e:
                print(f"❌ Unexpected Error: {e}")
    
    return None

async def test_network_connectivity():
    """Test basic network connectivity to the host"""
    host = "10.26.5.29"
    port = 8420
    
    print(f"🔍 Testing network connectivity to {host}:{port}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try a simple GET request to see if the service is alive
            response = await client.get(f"http://{host}:{port}/", timeout=5.0)
            print(f"✅ Host {host}:{port} is reachable")
            print(f"Status: {response.status_code}")
            return True
    except httpx.ConnectError:
        print(f"❌ Cannot connect to {host}:{port}")
        print("🔍 Possible issues:")
        print("   - Service is not running")
        print("   - Wrong IP address or port")
        print("   - Firewall blocking connection")
        print("   - Network connectivity issues")
        return False
    except Exception as e:
        print(f"❌ Network test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing External Knowledge Base Endpoint")
    print("=" * 50)
    
    async def run_tests():
        # Test basic connectivity first
        print("📡 Testing basic network connectivity...")
        connectivity = await test_network_connectivity()
        
        if not connectivity:
            print("\n💡 Please check:")
            print("1. Is the external service running?")
            print("2. Is the IP address correct (10.26.5.29)?")
            print("3. Is the port correct (8420)?")
            print("4. Are you on the same network?")
            return
        
        print("\n🧪 Testing endpoint with different parameter formats...")
        correct_param = await test_external_endpoint()
        
        if correct_param:
            print(f"\n🎉 Found working parameter format: '{correct_param}'")
        else:
            print("\n💥 No working parameter format found")
            print("🔍 Check the external service API documentation")
    
    # Run the async tests
    asyncio.run(run_tests())