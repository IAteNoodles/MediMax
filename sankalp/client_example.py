"""
Example client for the FastAPI Cypher Query Generator API
This demonstrates how to make requests to the FastAPI server
"""

import requests
import json
import socket

# Server configuration - can be changed for network access
def get_server_url():
    """Get the server URL - supports both localhost and network access"""
    # Try to get local IP for network access
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        # You can change this to use network IP instead of localhost
        # return f"http://{local_ip}:8000"  # For network access
        return "http://127.0.0.1:8000"      # For localhost only
    except:
        return "http://127.0.0.1:8000"

BASE_URL = get_server_url()

def test_health_check():
    """Test the health check endpoint"""
    print("=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start the server with: python fastapi_server.py")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_generate_cypher():
    """Test the detailed Cypher generation endpoint"""
    print("=== Testing Generate Cypher (Detailed) ===")
    
    test_data = {
        "query": "Find all users named John",
        "db_schema": "Node Labels: User, Post, Comment\nRelationship Types: CREATED, LIKES\nProperty Keys: name, title, content, timestamp",
        "context": "This is a social media database"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate_cypher",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Success!")
            print(f"Original Query: {result['original_query']}")
            print(f"Generated Cypher: {result['cypher_query']}")
            print(f"Is Valid: {result['is_valid']}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start the server with: python fastapi_server.py")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_generate_simple():
    """Test the simple Cypher generation endpoint"""
    print("=== Testing Generate Cypher (Simple) ===")
    
    test_data = {
        "query": "Show me all movies from 2020"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate_simple",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Generated Cypher: {response.text}")
        else:
            print(f"❌ Error: {response.json()}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start the server with: python fastapi_server.py")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_set_schema():
    """Test setting schema information"""
    print("=== Testing Set Schema ===")
    
    schema_data = {
        "db_schema": """
        Node Labels: Person, Movie, Director, Actor, Genre
        Relationship Types: ACTED_IN, DIRECTED, PRODUCED, BELONGS_TO
        Property Keys: name, title, year, born, rating, budget, revenue
        """
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/set_schema",
            json=schema_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        
        if result.get('success'):
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Error: {result.get('error')}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start the server with: python fastapi_server.py")
    except Exception as e:
        print(f"Error: {e}")
    print()

def test_validate_cypher():
    """Test Cypher query validation"""
    print("=== Testing Cypher Validation ===")
    
    # Test valid query
    valid_query = {
        "cypher": "MATCH (n:Person) WHERE n.name = 'John' RETURN n LIMIT 10"
    }
    
    # Test invalid query
    invalid_query = {
        "cypher": "MATCH (n:Person WHERE n.name = 'John' RETURN n"  # Missing closing parenthesis
    }
    
    for test_name, test_data in [("Valid Query", valid_query), ("Invalid Query", invalid_query)]:
        print(f"Testing {test_name}:")
        try:
            response = requests.post(
                f"{BASE_URL}/validate_cypher",
                json=test_data,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            
            if result.get('success'):
                status_icon = "✅" if result['is_valid'] else "❌"
                print(f"{status_icon} Query: {result['cypher_query']}")
                print(f"Valid: {result['is_valid']}")
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Server not running. Start the server with: python fastapi_server.py")
        except Exception as e:
            print(f"Error: {e}")
        print()

def interactive_mode():
    """Interactive mode for testing queries"""
    print("=== Interactive Mode ===")
    print("Enter natural language queries (type 'quit' to exit)")
    print("Make sure the Flask server is running!")
    print()
    
    while True:
        try:
            user_input = input("Your query: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if not user_input:
                continue
                
            # Use the simple endpoint for interactive mode
            response = requests.post(
                f"{BASE_URL}/generate_simple",
                json={"query": user_input},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                print(f"Generated Cypher: {response.text}")
            else:
                error_data = response.json()
                print(f"Error: {error_data.get('error', 'Unknown error')}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Server not running. Start the server with: python fastapi_server.py")
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
        print()

def run_all_tests():
    """Run all the test functions"""
    print("🚀 Testing FastAPI Cypher Query Generator API")
    print("=" * 50)
    
    test_health_check()
    test_set_schema()
    test_generate_cypher()
    test_generate_simple()
    test_validate_cypher()
    
    print("=" * 50)
    print("All tests completed!")
    print("\nTo start interactive mode, call: interactive_mode()")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_mode()
    elif len(sys.argv) > 1 and sys.argv[1] == "network":
        # Show network access information
        print("🌐 Network Access Information")
        print("=" * 40)
        
        # Get local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            print(f"📍 Your local IP: {local_ip}")
            print(f"🔗 Network URL: http://{local_ip}:8000")
            print(f"📚 Network Docs: http://{local_ip}:8000/docs")
            print(f"\n📱 Access from other devices:")
            print(f"   - Make sure devices are on the same WiFi network")
            print(f"   - Open browser to: http://{local_ip}:8000/docs")
            print(f"   - Or use in your apps: http://{local_ip}:8000")
        except Exception as e:
            print(f"❌ Could not determine local IP: {e}")
    else:
        run_all_tests()
        print("\nOptions:")
        print("- Run with 'python client_example.py interactive' for interactive mode")
        print("- Run with 'python client_example.py network' for network access info")