#!/usr/bin/env python3
"""
Test script to verify MCP server fixes for:
1. Timeout parameter issue
2. Deprecated id() function warnings and fixes
3. Malformed query validation
"""

import requests
import json

def test_cypher_with_deprecated_id():
    """Test the deprecated id() function fix"""
    
    print("=== Testing Deprecated id() Function Fix ===")
    
    # Test query with deprecated id() function
    query_with_id = """
    MATCH (p:Patient)
    RETURN id(p) AS internal_id, p.name AS name, p.patient_id AS patient_id
    ORDER BY internal_id
    """
    
    url = "http://localhost:8006/mcp"
    
    # Construct MCP request payload
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "Run_Cypher_Query",
            "arguments": {
                "cypher": query_with_id
            }
        }
    }
    
    print(f"Testing query with deprecated id() function:")
    print(f"Query: {query_with_id.strip()}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if the query was fixed
            if 'result' in data and 'content' in data['result']:
                result_content = data['result']['content']
                if isinstance(result_content, list) and len(result_content) > 0:
                    result_data = result_content[0]
                    if 'text' in result_data:
                        try:
                            parsed_result = json.loads(result_data['text'])
                            if 'original_query' in parsed_result:
                                print("✅ Query was automatically fixed!")
                                print(f"Original: {parsed_result.get('original_query', 'N/A')}")
                                print(f"Fixed: {parsed_result.get('query', 'N/A')}")
                            else:
                                print("⚠️ Query executed but no fix was applied")
                        except json.JSONDecodeError:
                            print("❌ Could not parse result as JSON")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_timeout_parameter():
    """Test that the function now accepts timeout parameter"""
    
    print("\n=== Testing Timeout Parameter Compatibility ===")
    
    query = "MATCH (p:Patient) RETURN count(p) as patient_count"
    
    url = "http://localhost:8006/mcp"
    
    # Construct MCP request payload with timeout (this was causing the error)
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "Run_Cypher_Query",
            "arguments": {
                "cypher": query,
                "timeout": 120000  # This was causing the validation error
            }
        }
    }
    
    print(f"Testing query with timeout parameter:")
    print(f"Query: {query}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Function now accepts timeout parameter without error!")
            data = response.json()
            print(f"Response preview: {str(data)[:200]}...")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_malformed_query_validation():
    """Test validation of malformed queries"""
    
    print("\n=== Testing Malformed Query Validation ===")
    
    # Test the malformed query pattern from the logs
    malformed_query = "RETURN id(p) AS internal_id, p.name AS name, p.patient_id AS patient_id, p MRN: p.mrn"
    
    url = "http://localhost:8006/mcp"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "Run_Cypher_Query",
            "arguments": {
                "cypher": malformed_query
            }
        }
    }
    
    print(f"Testing malformed query:")
    print(f"Query: {malformed_query}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            result_text = ""
            if 'result' in data and 'content' in data['result']:
                result_content = data['result']['content']
                if isinstance(result_content, list) and len(result_content) > 0:
                    result_data = result_content[0]
                    if 'text' in result_data:
                        result_text = result_data['text']
            
            if 'error' in result_text or 'Failed' in result_text:
                print("✅ Malformed query was properly rejected!")
                print(f"Error message: {result_text}")
            else:
                print("⚠️ Query was executed (might have been auto-fixed)")
                print(f"Result: {result_text}")
        else:
            print(f"❌ Unexpected status: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("Testing MCP Server Fixes")
    print("=" * 50)
    
    test_timeout_parameter()
    test_cypher_with_deprecated_id()
    test_malformed_query_validation()
    
    print("\n" + "=" * 50)
    print("Test completed!")