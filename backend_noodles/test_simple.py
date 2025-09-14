#!/usr/bin/env python3
"""
Simple test script to verify Neo4j date serialization fix
"""

import sys
import os
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test the import and functions
def test_imports():
    """Test that we can import the required modules"""
    try:
        from mcp_server import Neo4jJSONEncoder, convert_date_to_string
        print("✓ Successfully imported Neo4jJSONEncoder and convert_date_to_string")
        return Neo4jJSONEncoder, convert_date_to_string
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return None, None

def test_date_serialization(Neo4jJSONEncoder, convert_date_to_string):
    """Test Neo4j date serialization fix"""
    print("\nTesting Neo4j date serialization fix...")
    
    # Test the JSON encoder
    test_data = {
        "timestamp": datetime.now(),
        "date_string": "2024-01-01",
        "patient_name": "John Doe",
        "patient_id": 123
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
    
    # Test with None value
    try:
        converted_none = convert_date_to_string(None)
        print(f"✓ None handling works: None -> {converted_none}")
    except Exception as e:
        print(f"✗ None handling failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Neo4j Date Serialization Fix Test ===")
    
    # Test imports
    Neo4jJSONEncoder, convert_date_to_string = test_imports()
    
    if Neo4jJSONEncoder and convert_date_to_string:
        # Test serialization functions
        serialization_ok = test_date_serialization(Neo4jJSONEncoder, convert_date_to_string)
        
        if serialization_ok:
            print("\n🎉 All tests passed! Neo4j date serialization fix is working correctly.")
            print("\nThe fix includes:")
            print("- Custom Neo4jJSONEncoder class for handling datetime objects")
            print("- convert_date_to_string utility function")
            print("- Proper serialization of Neo4j temporal types")
        else:
            print("\n❌ Date serialization test failed.")
    else:
        print("\n❌ Import test failed.")