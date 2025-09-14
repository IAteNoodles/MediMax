import requests
import json

def test_mcp_cardiovascular_validation():
    """Test the cardiovascular prediction with missing parameters"""
    
    # Test 1: Missing all parameters
    payload = {
        "method": "tools/call",
        "params": {
            "name": "Predict_Cardiovascular_Risk_With_Explanation",
            "arguments": {
                "age": 45,
                "gender": 1
                # Missing other required parameters
            }
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8005/mcp/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print("Status Code:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    test_mcp_cardiovascular_validation()