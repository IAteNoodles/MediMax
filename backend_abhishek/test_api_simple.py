#!/usr/bin/env python3
"""
Simple Traditional API Testing Script for MediMax Backend
=========================================================

This script provides basic testing for all major endpoints in app.py.
It uses:
- Random patient data for ADD operations
- Patient ID 7 for GET operations  
- Patient ID 6 for PUT operations
- Patient ID 1 for DELETE operations

Usage:
1. Start the FastAPI server: python app.py
2. Run this test: python test_api_simple.py
"""

import requests
import json
import random
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8420"
TEST_GET_ID = 7
TEST_PUT_ID = 6
TEST_DELETE_ID = 1

def generate_random_patient():
    """Generate random patient data."""
    names = ["John Smith", "Jane Doe", "Michael Brown", "Sarah Wilson", "David Lee"]
    return {
        "name": random.choice(names),
        "dob": f"{random.randint(1950, 2000)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "sex": random.choice(["Male", "Female"])
    }

def test_api(method, endpoint, data=None, params=None):
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Testing {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
            
        print(f"   Status: {response.status_code}")
        
        if response.status_code < 400:
            print(f"   ✅ Success")
            try:
                result = response.json()
                if isinstance(result, dict) and len(str(result)) < 200:
                    print(f"   Response: {result}")
                return result
            except:
                pass
        else:
            print(f"   ❌ Error: {response.text[:100]}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - is server running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        
    return None

def main():
    """Run all API tests."""
    print("🏥 MediMax Backend API Test Suite")
    print("=" * 50)
    
    # 1. Health Check
    print("\n📊 HEALTH & STATUS TESTS")
    test_api("GET", "/health")
    test_api("GET", "/test_db")
    test_api("GET", "/api/endpoints")
    
    # 2. Patient CRUD Operations
    print("\n👤 PATIENT CRUD TESTS")
    
    # CREATE - Add random patient
    patient_data = generate_random_patient()
    print(f"   Adding patient: {patient_data['name']}")
    new_patient = test_api("POST", "/db/new_patient", data=patient_data)
    
    # READ - Get patients
    test_api("GET", "/db/get_all_patients", params={"limit": 5})
    test_api("GET", "/db/get_patient_details", params={"patient_id": TEST_GET_ID})
    test_api("GET", f"/db/get_complete_patient_profile/{TEST_GET_ID}")
    test_api("GET", "/db/search_patients", params={"name": "John", "limit": 3})
    
    # UPDATE - Update patient
    update_data = generate_random_patient()
    print(f"   Updating patient {TEST_PUT_ID} to: {update_data['name']}")
    test_api("PUT", f"/db/update_patient/{TEST_PUT_ID}", data=update_data)
    
    # DELETE - Delete patient
    print(f"   Deleting patient {TEST_DELETE_ID}")
    test_api("DELETE", f"/db/delete_patient/{TEST_DELETE_ID}")
    
    # 3. Medical History
    print("\n📋 MEDICAL HISTORY TESTS")
    history_data = {
        "history_type": "allergy",
        "history_item": "Penicillin",
        "history_details": "Severe allergic reaction",
        "severity": "severe",
        "is_active": True
    }
    test_api("POST", f"/db/add_medical_history/{TEST_GET_ID}", data=history_data)
    test_api("GET", "/db/get_medical_history", params={"patient_id": TEST_GET_ID})
    test_api("GET", f"/get_medical_history/{TEST_GET_ID}")
    
    # 4. Appointments
    print("\n📅 APPOINTMENT TESTS")
    appointment_data = {
        "appointment_date": "2024-09-25",
        "appointment_time": "14:30:00",
        "status": "Scheduled",
        "appointment_type": "consultation",  # Use database enum value
        "doctor_name": "Dr. Test"
    }
    appointment = test_api("POST", f"/db/add_appointment/{TEST_GET_ID}", data=appointment_data)
    test_api("GET", "/get_n_appointments", params={"n": 5})
    test_api("GET", "/db/get_symptoms", params={"patient_id": TEST_GET_ID})
    
    # Add symptom if appointment was created
    if appointment and "appointment_id" in appointment:
        symptom_data = {
            "appointment_id": appointment["appointment_id"],
            "symptom_name": "Fever",
            "severity": "moderate",
            "onset_type": "sudden"
        }
        test_api("POST", "/db/add_symptom", data=symptom_data)
    
    # 5. Medications
    print("\n💊 MEDICATION TESTS")
    medication_data = {
        "medicine_name": "Aspirin",
        "is_continued": True,
        "prescribed_date": "2024-09-15",
        "dosage": "100mg",
        "frequency": "Daily"
    }
    test_api("POST", f"/db/add_medication/{TEST_GET_ID}", data=medication_data)
    test_api("GET", "/db/get_medications", params={"patient_id": TEST_GET_ID})
    
    # 6. Lab Reports
    print("\n🧪 LAB REPORT TESTS")
    lab_report_data = {
        "lab_date": "2024-09-15",
        "lab_type": "Blood Test",
        "ordering_doctor": "Dr. Lab"
    }
    lab_report = test_api("POST", f"/db/add_lab_report/{TEST_GET_ID}", data=lab_report_data)
    test_api("GET", f"/get_n_lab_reports/{TEST_GET_ID}")
    test_api("GET", "/db/get_medical_reports", params={"patient_id": TEST_GET_ID})
    
    # Add lab finding if lab report was created
    if lab_report and "lab_report_id" in lab_report:
        finding_data = {
            "lab_report_id": lab_report["lab_report_id"],
            "test_name": "Hemoglobin",
            "test_value": "14.5",
            "test_unit": "g/dL",
            "is_abnormal": False
        }
        test_api("POST", "/db/add_lab_finding", data=finding_data)
    
    # 7. AI/Agentic System
    print("\n🤖 AI SYSTEM TESTS")
    test_api("GET", "/models")
    
    assessment_data = {
        "patient_id": TEST_GET_ID,
        "query": "What is the patient's overall health status?"
    }
    test_api("POST", "/assess_mock", data=assessment_data)
    test_api("GET", "/frontend/get_query", params={"patient_id": TEST_GET_ID})
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print(f"📝 Test Summary:")
    print(f"   • Used random data for ADD operations")
    print(f"   • Used Patient ID {TEST_GET_ID} for GET operations")
    print(f"   • Used Patient ID {TEST_PUT_ID} for PUT operations") 
    print(f"   • Used Patient ID {TEST_DELETE_ID} for DELETE operations")
    print("\n⚠️  Note: Some tests may fail if patients don't exist in database")

if __name__ == "__main__":
    main()