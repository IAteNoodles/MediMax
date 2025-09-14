# API Testing Documentation

## Overview
This directory contains comprehensive test scripts for the MediMax Backend API. The tests cover all endpoints defined in `app.py`.

## Test Files

### 1. `test_api_traditional.py`
- **Comprehensive testing suite** with detailed output and colored formatting
- Tests all endpoints with proper error handling
- Includes detailed response logging
- Uses configuration-based patient IDs for different operations

### 2. `test_api_simple.py`
- **Lightweight testing script** for quick validation
- Simpler output format
- Essential endpoint coverage
- Perfect for CI/CD or quick checks

## Test Configuration

Both test scripts use the following patient ID configuration:
- **ADD operations**: Random patient data generated for each test
- **GET operations**: Patient ID 7
- **PUT operations**: Patient ID 6  
- **DELETE operations**: Patient ID 1

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r test_requirements.txt
```

### 2. Start the Server
```bash
python app.py
```
Server should be running on `http://127.0.0.1:8420`

### 3. Run Tests

#### Option A: Comprehensive Test Suite
```bash
python test_api_traditional.py
```

#### Option B: Simple Test Suite  
```bash
python test_api_simple.py
```

## Endpoints Tested

### Health & Status
- `GET /health` - Backend health check
- `GET /test_db` - Database connectivity test
- `GET /api/endpoints` - API documentation

### Patient Management
- `POST /db/new_patient` - Create new patient (random data)
- `GET /db/get_all_patients` - Get all patients
- `GET /db/get_patient_details` - Get patient details (ID 7)
- `GET /db/search_patients` - Search patients by name
- `GET /db/get_complete_patient_profile/{id}` - Complete profile (ID 7)
- `PUT /db/update_patient/{id}` - Update patient (ID 6)
- `DELETE /db/delete_patient/{id}` - Delete patient (ID 1)

### Medical Records
- `POST /db/add_medical_history/{id}` - Add medical history (ID 7)
- `GET /db/get_medical_history` - Get medical history (ID 7)
- `GET /get_medical_history/{id}` - Get history with AI summary (ID 7)

### Appointments
- `POST /db/add_appointment/{id}` - Add appointment (ID 7)
- `GET /get_n_appointments` - Get appointments
- `POST /db/add_symptom` - Add symptom to appointment
- `GET /db/get_symptoms` - Get patient symptoms (ID 7)

### Medications
- `POST /db/add_medication/{id}` - Add medication (ID 7)
- `GET /db/get_medications` - Get patient medications (ID 7)

### Lab Reports
- `POST /db/add_lab_report/{id}` - Add lab report (ID 7)
- `POST /db/add_lab_finding` - Add lab finding
- `GET /get_n_lab_reports/{id}` - Get lab reports (ID 7)
- `GET /db/get_medical_reports` - Get medical reports (ID 7)

### AI/Agentic System
- `GET /models` - Get available AI models
- `POST /assess` - Patient assessment (when agentic server available)
- `POST /assess_mock` - Mock assessment
- `GET /frontend/get_query` - Generate frontend query (ID 7)

## Expected Behaviors

### Successful Operations
- Status codes 200-299
- Valid JSON responses
- Proper data validation

### Error Cases
- Missing patients return 404
- Invalid data returns 400
- Database errors return 500

## Notes

### Database Requirements
- Ensure MariaDB is running
- Database should have existing patients with IDs 6 and 7
- Patient ID 1 will be deleted during testing

### Random Data Generation
For ADD operations, the tests generate random:
- Patient names from predefined lists
- Birth dates (ages 18-80)
- Sex values (Male/Female/Other)
- Medical data with realistic values

### Dependencies
Tests require the `requests` library for HTTP operations.

## Troubleshooting

### Server Connection Issues
1. Verify server is running: `python app.py`
2. Check server URL in test scripts (default: `http://127.0.0.1:8420`)
3. Ensure no firewall blocking port 8420

### Database Errors
1. Check database connection in app.py
2. Verify patient IDs 6 and 7 exist in database
3. Check database schema matches expectations

### Test Failures
1. Some tests may fail if test patients don't exist
2. DELETE operations are destructive - patient data will be removed
3. Network timeouts may occur with slow database operations

## Customization

### Changing Test Patient IDs
Edit the configuration variables at the top of each test file:
```python
TEST_PATIENT_ID_GET = 7    # For GET operations
TEST_PATIENT_ID_PUT = 6    # For PUT operations  
TEST_PATIENT_ID_DELETE = 1 # For DELETE operations
```

### Changing Server URL
Modify the `BASE_URL` variable:
```python
BASE_URL = "http://127.0.0.1:8420"
```

### Adding New Tests
Follow the existing pattern in either test file:
```python
def test_new_endpoint():
    """Test description."""
    test_endpoint("GET", "/new/endpoint", params={"param": "value"})
```