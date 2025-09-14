import requests
import json

# Define the base URL of the server
BASE_URL = "http://10.26.5.99:8000"

# Mock patient data for the assessment
mock_patient_data = {
    "patient_text": "The patient is a 45-year-old male with a history of diabetes and high blood pressure. He is currently experiencing symptoms of fever, cough, and headache.",
    "query": "Cardiovascular risk assessment",
    "additional_notes": "Patient has a family history of heart disease."
}

def check_health():
    """
    Performs a health check on the server.
    """
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()  # Raise an exception for bad status codes
        print("Health Check Successful:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Health Check Failed: {e}")

def get_models():
    """
    Retrieves information about the available models from the server.
    """
    try:
        response = requests.get(f"{BASE_URL}/models")
        response.raise_for_status()
        print("\nAvailable Models:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Failed to get models: {e}")

def assess_patient(patient_data):
    """
    Sends patient data to the server for assessment.
    """
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(f"{BASE_URL}/assess", data=json.dumps(patient_data), headers=headers)
        response.raise_for_status()
        print("\nPatient Assessment Successful:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Patient Assessment Failed: {e}")

if __name__ == "__main__":
    print("--- Starting Mock Client ---")
    
    # Perform Health Check
    check_health()
    
    # Get Model Information
    get_models()
    
    # Perform Patient Assessment
    assess_patient(mock_patient_data)
    
    print("\n--- Mock Client Finished ---")
