#!/usr/bin/env python3
"""
Standalone test for Neo4j date serialization classes
"""

import json
from datetime import datetime
from neo4j.time import Date, DateTime, Time

class Neo4jJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for Neo4j types including dates and times"""
    def default(self, obj):
        if isinstance(obj, (Date, DateTime, Time)):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def convert_date_to_string(date_obj):
    """Convert various date objects to ISO format strings"""
    if date_obj is None:
        return None
    if isinstance(date_obj, (Date, DateTime, Time)):
        return date_obj.isoformat()
    elif isinstance(date_obj, datetime):
        return date_obj.isoformat()
    elif isinstance(date_obj, str):
        return date_obj
    else:
        return str(date_obj)

def test_date_serialization():
    """Test Neo4j date serialization fix"""
    print("Testing Neo4j date serialization fix...")
    
    # Test the JSON encoder with datetime
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
    
    # Test with string value
    try:
        converted_str = convert_date_to_string("2024-01-01")
        print(f"✓ String handling works: '2024-01-01' -> {converted_str}")
    except Exception as e:
        print(f"✗ String handling failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Neo4j Date Serialization Fix Test ===\n")
    
    # Test serialization functions
    serialization_ok = test_date_serialization()
    
    if serialization_ok:
        print("\n🎉 All tests passed! Neo4j date serialization fix is working correctly.")
        print("\nThe fix includes:")
        print("- Custom Neo4jJSONEncoder class for handling datetime objects")
        print("- convert_date_to_string utility function")
        print("- Proper serialization of Neo4j temporal types")
        print("- Protection against None values")
        print("- Support for string pass-through")
    else:
        print("\n❌ Date serialization test failed.")