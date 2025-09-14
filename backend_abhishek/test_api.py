#!/usr/bin/env python3
"""
Quick test to validate the database schema and API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8081"

def test_endpoints():
    print("Testing database connection...")
    try:
        response = requests.get(f"{BASE_URL}/test_db")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Available tables:", data.get("available_tables", []))
            print("Patient table structure:", data.get("patient_table_structure", []))
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Connection error: {e}")
    
    print("\nTesting patient details...")
    try:
        response = requests.get(f"{BASE_URL}/db/get_patient_details?patient_id=1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Patient data:", json.dumps(data, indent=2))
        else:
            print("Error:", response.text)
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_endpoints()