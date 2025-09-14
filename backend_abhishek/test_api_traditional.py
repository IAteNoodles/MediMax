#!/usr/bin/env python3
"""
Traditional API Testing Script for MediMax Backend
=================================================

This script tests all endpoints in app.py using requests library.
- For ADD operations: Uses random patient data
- For GET operations: Uses patient ID 7
- For PUT operations: Uses patient ID 6
- For DELETE operations: Uses patient ID 1

Run this script after starting the FastAPI server:
python app.py

Then run this test:
python test_api_traditional.py
"""

import requests
import json
import random
import time
from datetime import datetime, date
import sys

# Base URL for the API
BASE_URL = "http://127.0.0.1:8420"

# Test configuration
TEST_PATIENT_ID_GET = 7
TEST_PATIENT_ID_PUT = 6
TEST_PATIENT_ID_DELETE = 1

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_test_header(test_name):
    """Print a formatted test header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}Testing: {test_name}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")

def generate_random_patient_data():
    """Generate random patient data for testing."""
    first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily", "James", "Anna"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # Generate random DOB (age between 18-80)
    year = random.randint(1943, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # Safe day to avoid month issues
    dob = f"{year:04d}-{month:02d}-{day:02d}"
    
    sex = random.choice(["Male", "Female", "Other"])
    
    return {
        "name": name,
        "dob": dob,
        "sex": sex
    }

def test_endpoint(method, endpoint, data=None, params=None, expected_status=200):
    """Generic function to test an endpoint."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, params=params)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, params=params)
        elif method.upper() == "DELETE":
            response = requests.delete(url, params=params)
        else:
            print_error(f"Unsupported method: {method}")
            return False
            
        print_info(f"{method.upper()} {endpoint}")
        if data:
            print_info(f"Request data: {json.dumps(data, indent=2)}")
        if params:
            print_info(f"Request params: {params}")
            
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == expected_status:
            print_success(f"✓ Expected status code {expected_status}")
            try:
                response_data = response.json()
                print_info(f"Response: {json.dumps(response_data, indent=2, default=str)[:500]}...")
                return response_data
            except:
                print_info(f"Response (text): {response.text[:200]}...")
                return response.text
        else:
            print_error(f"✗ Expected {expected_status}, got {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error(f"✗ Connection failed. Is the server running at {BASE_URL}?")
        return False
    except Exception as e:
        print_error(f"✗ Error: {str(e)}")
        return False

def test_health_endpoints():
    """Test health and status endpoints."""
    print_test_header("Health & Status Endpoints")
    
    # Test health endpoint
    test_endpoint("GET", "/health")
    
    # Test database test endpoint
    test_endpoint("GET", "/test_db")
    
    # Test API endpoints documentation
    test_endpoint("GET", "/api/endpoints")

def test_patient_crud_operations():
    """Test patient CRUD operations."""
    print_test_header("Patient CRUD Operations")
    
    # 1. CREATE - Add new patient with random data
    print_info("1. Testing CREATE - Adding new patient with random data")
    patient_data = generate_random_patient_data()
    create_response = test_endpoint("POST", "/db/new_patient", data=patient_data)
    
    # 2. READ - Get all patients
    print_info("2. Testing READ - Get all patients")
    test_endpoint("GET", "/db/get_all_patients", params={"limit": 10, "offset": 0})
    
    # 3. READ - Get specific patient details (ID 7)
    print_info(f"3. Testing READ - Get patient details for ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", "/db/get_patient_details", params={"patient_id": TEST_PATIENT_ID_GET})
    
    # 4. READ - Search patients
    print_info("4. Testing READ - Search patients")
    test_endpoint("GET", "/db/search_patients", params={"name": "John", "limit": 5})
    
    # 5. READ - Get complete patient profile (ID 7)
    print_info(f"5. Testing READ - Get complete patient profile for ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", f"/db/get_complete_patient_profile/{TEST_PATIENT_ID_GET}")
    
    # 6. UPDATE - Update patient (ID 6)
    print_info(f"6. Testing UPDATE - Update patient ID {TEST_PATIENT_ID_PUT}")
    update_data = generate_random_patient_data()
    test_endpoint("PUT", f"/db/update_patient/{TEST_PATIENT_ID_PUT}", data=update_data)
    
    # 7. DELETE - Delete patient (ID 1)
    print_info(f"7. Testing DELETE - Delete patient ID {TEST_PATIENT_ID_DELETE}")
    test_endpoint("DELETE", f"/db/delete_patient/{TEST_PATIENT_ID_DELETE}")

def test_medical_history_operations():
    """Test medical history operations."""
    print_test_header("Medical History Operations")
    
    # Add medical history for patient ID 7
    print_info(f"1. Adding medical history for patient ID {TEST_PATIENT_ID_GET}")
    medical_history_data = {
        "history_type": "condition",  # Use database enum value
        "history_item": "Diabetes Type 2",
        "history_details": "Controlled with medication",
        "history_date": "2020-03-15",
        "severity": "moderate",
        "is_active": True
    }
    test_endpoint("POST", f"/db/add_medical_history/{TEST_PATIENT_ID_GET}", data=medical_history_data)
    
    # Get medical history for patient ID 7
    print_info(f"2. Getting medical history for patient ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", "/db/get_medical_history", params={"patient_id": TEST_PATIENT_ID_GET})
    
    # Get medical history with AI summary
    print_info(f"3. Getting medical history with AI summary for patient ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", f"/get_medical_history/{TEST_PATIENT_ID_GET}")

def test_appointment_operations():
    """Test appointment operations."""
    print_test_header("Appointment Operations")
    
    # Add appointment for patient ID 7
    print_info(f"1. Adding appointment for patient ID {TEST_PATIENT_ID_GET}")
    appointment_data = {
        "appointment_date": "2024-09-20",
        "appointment_time": "10:30:00",
        "status": "Scheduled",
        "appointment_type": "routine_checkup",  # Use database enum value
        "doctor_name": "Dr. Smith",
        "notes": "Regular checkup"
    }
    appointment_response = test_endpoint("POST", f"/db/add_appointment/{TEST_PATIENT_ID_GET}", data=appointment_data)
    
    # Get appointments
    print_info("2. Getting appointments")
    test_endpoint("GET", "/get_n_appointments", params={"n": 10})
    
    # Add symptom to appointment (if appointment was created successfully)
    if appointment_response and isinstance(appointment_response, dict) and "appointment_id" in appointment_response:
        appointment_id = appointment_response["appointment_id"]
        print_info(f"3. Adding symptom to appointment ID {appointment_id}")
        symptom_data = {
            "appointment_id": appointment_id,
            "symptom_name": "Headache",
            "symptom_description": "Persistent headache for 3 days",
            "severity": "moderate",
            "duration": "3 days",
            "onset_type": "gradual"
        }
        test_endpoint("POST", "/db/add_symptom", data=symptom_data)
    
    # Get symptoms for patient ID 7
    print_info(f"4. Getting symptoms for patient ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", "/db/get_symptoms", params={"patient_id": TEST_PATIENT_ID_GET})

def test_medication_operations():
    """Test medication operations."""
    print_test_header("Medication Operations")
    
    # Add medication for patient ID 7
    print_info(f"1. Adding medication for patient ID {TEST_PATIENT_ID_GET}")
    medication_data = {
        "medicine_name": "Metformin",
        "is_continued": True,
        "prescribed_date": "2024-01-15",
        "dosage": "500mg",
        "frequency": "Twice daily",
        "prescribed_by": "Dr. Johnson"
    }
    test_endpoint("POST", f"/db/add_medication/{TEST_PATIENT_ID_GET}", data=medication_data)
    
    # Get medications for patient ID 7
    print_info(f"2. Getting medications for patient ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", "/db/get_medications", params={"patient_id": TEST_PATIENT_ID_GET})

def test_lab_report_operations():
    """Test lab report operations."""
    print_test_header("Lab Report Operations")
    
    # Add lab report for patient ID 7
    print_info(f"1. Adding lab report for patient ID {TEST_PATIENT_ID_GET}")
    lab_report_data = {
        "lab_date": "2024-09-10",
        "lab_type": "Blood Work",
        "ordering_doctor": "Dr. Wilson",
        "lab_facility": "Central Lab"
    }
    lab_report_response = test_endpoint("POST", f"/db/add_lab_report/{TEST_PATIENT_ID_GET}", data=lab_report_data)
    
    # Add lab finding (if lab report was created successfully)
    if lab_report_response and isinstance(lab_report_response, dict) and "lab_report_id" in lab_report_response:
        lab_report_id = lab_report_response["lab_report_id"]
        print_info(f"2. Adding lab finding to lab report ID {lab_report_id}")
        lab_finding_data = {
            "lab_report_id": lab_report_id,
            "test_name": "Glucose",
            "test_value": "95",
            "test_unit": "mg/dL",
            "reference_range": "70-100",
            "is_abnormal": False
        }
        test_endpoint("POST", "/db/add_lab_finding", data=lab_finding_data)
    
    # Get lab reports for patient ID 7
    print_info(f"3. Getting lab reports for patient ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", f"/get_n_lab_reports/{TEST_PATIENT_ID_GET}")
    
    # Get medical reports for patient ID 7
    print_info(f"4. Getting medical reports for patient ID {TEST_PATIENT_ID_GET}")
    test_endpoint("GET", "/db/get_medical_reports", params={"patient_id": TEST_PATIENT_ID_GET})

def test_agentic_operations():
    """Test agentic system operations."""
    print_test_header("Agentic System Operations")
    
    # Get models
    print_info("1. Getting available models")
    test_endpoint("GET", "/models")
    
    # Test assessment (mock)
    print_info("2. Testing assessment (mock)")
    assessment_data = {
        "patient_id": TEST_PATIENT_ID_GET,
        "query": "What is the overall health status of this patient?"
    }
    test_endpoint("POST", "/assess_mock", data=assessment_data)
    
    # Test frontend query generation
    print_info("3. Testing frontend query generation")
    test_endpoint("GET", "/frontend/get_query", params={"patient_id": TEST_PATIENT_ID_GET})

def test_additional_endpoints():
    """Test additional utility endpoints."""
    print_test_header("Additional Utility Endpoints")
    
    # Test various GET endpoints that don't require specific IDs
    endpoints_to_test = [
        ("/health", {}),
        ("/test_db", {}),
        ("/api/endpoints", {}),
        ("/models", {}),
    ]
    
    for endpoint, params in endpoints_to_test:
        test_endpoint("GET", endpoint, params=params)

def main():
    """Main function to run all tests."""
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 80)
    print("         MEDIMAX BACKEND API TRADITIONAL TESTING SUITE")
    print("=" * 80)
    print(f"{Colors.END}")
    print(f"{Colors.CYAN}Testing all endpoints in app.py{Colors.END}")
    print(f"{Colors.CYAN}Base URL: {BASE_URL}{Colors.END}")
    print(f"{Colors.CYAN}Test Patient IDs - GET: {TEST_PATIENT_ID_GET}, PUT: {TEST_PATIENT_ID_PUT}, DELETE: {TEST_PATIENT_ID_DELETE}{Colors.END}")
    
    # Check if server is running
    print_info("Checking if server is running...")
    if not test_endpoint("GET", "/health"):
        print_error("Server is not responding. Please start the server with: python app.py")
        sys.exit(1)
    
    print_success("Server is running!")
    
    # Run all test suites
    test_suites = [
        test_health_endpoints,
        test_patient_crud_operations,
        test_medical_history_operations,
        test_appointment_operations,
        test_medication_operations,
        test_lab_report_operations,
        test_agentic_operations,
        test_additional_endpoints
    ]
    
    successful_tests = 0
    total_tests = len(test_suites)
    
    for test_suite in test_suites:
        try:
            test_suite()
            successful_tests += 1
            print_success(f"✓ {test_suite.__name__} completed")
        except Exception as e:
            print_error(f"✗ {test_suite.__name__} failed: {str(e)}")
    
    # Final summary
    print(f"\n{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 80)
    print("                           TEST SUMMARY")
    print("=" * 80)
    print(f"{Colors.END}")
    
    if successful_tests == total_tests:
        print_success(f"All {total_tests} test suites completed successfully!")
    else:
        print_warning(f"{successful_tests}/{total_tests} test suites completed successfully")
    
    print(f"\n{Colors.BOLD}Test Configuration:{Colors.END}")
    print(f"  • Random data used for ADD operations")
    print(f"  • Patient ID {TEST_PATIENT_ID_GET} used for GET operations")
    print(f"  • Patient ID {TEST_PATIENT_ID_PUT} used for PUT operations")
    print(f"  • Patient ID {TEST_PATIENT_ID_DELETE} used for DELETE operations")
    
    print(f"\n{Colors.BOLD}Notes:{Colors.END}")
    print("  • Some tests may fail if patients don't exist in the database")
    print("  • DELETE operations are destructive - patient data will be removed")
    print("  • Ensure database is properly set up before running tests")
    
    print(f"\n{Colors.GREEN}Testing completed!{Colors.END}")

if __name__ == "__main__":
    main()