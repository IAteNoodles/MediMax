#!/usr/bin/env python3
"""
Test script to verify Neo4j date serialization fix
"""

import sys
import os
import json
from datetime import datetime
import requests

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import kg_manager, Neo4jJSONEncoder, convert_date_to_string

def test_date_serialization():
    """Test Neo4j date serialization fix"""
    print("Testing Neo4j date serialization fix...")
    
    # Test the JSON encoder
    test_data = {
        "date": datetime.now(),
        "string": "test",
        "number": 123
    }
    
    try:
        # Test custom encoder
        json_str = json.dumps(test_data, cls=Neo4jJSONEncoder)
        print(f"✓ Custom JSON encoder works: {json_str}")
    except Exception as e:
        print(f"✗ Custom JSON encoder failed: {e}")
        return False
    
    # Test date conversion
    try:
        test_date = datetime.now()
        converted = convert_date_to_string(test_date)
        print(f"✓ Date conversion works: {test_date} -> {converted}")
    except Exception as e:
        print(f"✗ Date conversion failed: {e}")
        return False
    
    return True

def test_knowledge_graph_creation():
    """Test knowledge graph creation for a patient"""
    print("\nTesting knowledge graph creation...")
    
    # Test with patient ID 1
    patient_id = 1
    
    try:
        # Make request to MCP server
        response = requests.post(
            "http://localhost:8005/mcp/call",
            json={
                "method": "call_tool",
                "params": {
                    "name": "Create_Knowledge_Graph",
                    "arguments": {"patient_id": patient_id}
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Knowledge graph creation successful: {result}")
            return True
        else:
            print(f"✗ Knowledge graph creation failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Knowledge graph creation failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Neo4j Date Serialization Fix Test ===\n")
    
    # Test serialization functions
    serialization_ok = test_date_serialization()
    
    if serialization_ok:
        # Test actual knowledge graph creation
        kg_ok = test_knowledge_graph_creation()
        
        if kg_ok:
            print("\n🎉 All tests passed! Neo4j date serialization is fixed.")
        else:
            print("\n❌ Knowledge graph test failed.")
    else:
        print("\n❌ Date serialization test failed.")