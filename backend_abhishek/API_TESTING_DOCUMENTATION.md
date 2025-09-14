# MediMax API Testing Documentation

## Table of Contents
1. [Overview](#overview)
2. [Test Files](#test-files)
3. [Test Configuration](#test-configuration)
4. [Running Tests](#running-tests)
5. [Test Results Interpretation](#test-results-interpretation)
6. [Test Data Specifications](#test-data-specifications)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The MediMax API testing suite provides comprehensive validation of all backend endpoints, ensuring proper functionality, data integrity, and error handling. The suite includes two main test files with different levels of detail and output formatting.

### Testing Philosophy
- **Comprehensive Coverage**: Tests all 27+ API endpoints
- **Data Validation**: Verifies request/response formats and data integrity
- **Error Handling**: Tests both success and failure scenarios
- **Real Database**: Uses actual database connections for realistic testing
- **Configurable**: Easy to modify patient IDs and test data

---

## Test Files

### 1. test_api_traditional.py
**Purpose**: Comprehensive API testing with detailed logging and colored output

**Features**:
- ✅ **Colored Output**: Green for success, red for failures, yellow for warnings
- ✅ **Detailed Logging**: Full request/response information
- ✅ **Error Analysis**: Comprehensive error reporting and debugging info
- ✅ **Progress Tracking**: Real-time test progress with counts
- ✅ **Response Validation**: Checks status codes and response structures
- ✅ **Timing Information**: Response time measurements
- ✅ **Professional Formatting**: Clean, readable output format

**Key Characteristics**:
```python
# Configuration
BASE_URL = "http://127.0.0.1:8420"
PATIENT_ID_FOR_GET = 7      # Patient ID used for GET operations
PATIENT_ID_FOR_PUT = 6      # Patient ID used for PUT operations  
PATIENT_ID_FOR_DELETE = 1   # Patient ID used for DELETE operations

# Test Categories
- Health & Status Endpoints (2 tests)
- Patient Management (6 tests)
- Medical Records (3 tests)
- Appointments (2 tests)
- Medications (2 tests)
- Symptoms (2 tests)
- Lab Reports (4 tests)
- Search & Analytics (4 tests)
- AI/Agentic System (4 tests)
```

### 2. test_api_simple.py
**Purpose**: Lightweight testing script for quick validation

**Features**:
- ⚡ **Fast Execution**: Minimal output for quick checks
- 🎯 **Essential Coverage**: Tests core functionality only
- 📊 **Summary Report**: Concise pass/fail statistics
- 🔧 **Easy Integration**: Simple to integrate into CI/CD pipelines
- 💾 **Resource Efficient**: Lower memory and CPU usage

**Key Characteristics**:
```python
# Simplified Output
✓ GET /health - OK
✓ POST /db/new_patient - OK
✗ GET /db/get_patient_details - Failed: 404

# Quick Statistics
Total Tests: 15
Passed: 13
Failed: 2
Success Rate: 86.7%
```

---

## Test Configuration

### Patient ID Configuration
The tests use specific patient IDs for different operations to avoid conflicts:

```python
# Patient ID Assignments
PATIENT_ID_FOR_GET = 7      # Used for: 
                           # - get_patient_details
                           # - get_complete_patient_profile
                           # - get_medical_history
                           # - get_symptoms
                           # - get_medications
                           # - get_medical_reports
                           # - get_n_lab_reports

PATIENT_ID_FOR_PUT = 6      # Used for:
                           # - update_patient

PATIENT_ID_FOR_DELETE = 1   # Used for:
                           # - delete_patient (WARNING: Destructive!)

# Random Data Generation for POST operations
# New patients, appointments, medications, etc. use randomly generated data
```

### Base URL Configuration
```python
BASE_URL = "http://127.0.0.1:8420"  # Default local development server
```

### Test Data Examples

#### Patient Data Generation
```python
def generate_random_patient_data():
    """Generate realistic random patient data for testing."""
    names = ["John Smith", "Jane Doe", "Michael Johnson", "Sarah Wilson", 
             "David Brown", "Emily Davis", "James Miller", "Lisa Garcia"]
    
    return {
        "name": random.choice(names),
        "dob": f"{random.randint(1950, 2005)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
        "sex": random.choice(["Male", "Female", "Other"])
    }
```

#### Medical History Data
```python
def generate_medical_history_data():
    """Generate realistic medical history data."""
    return {
        "history_type": random.choice(["allergy", "surgery", "condition", "family_history"]),
        "history_item": random.choice(["Hypertension", "Diabetes", "Asthma", "Heart Disease"]),
        "history_details": "Medical condition details",
        "severity": random.choice(["mild", "moderate", "severe"]),
        "is_active": random.choice([True, False])
    }
```

#### Appointment Data
```python
def generate_appointment_data():
    """Generate realistic appointment data."""
    future_date = datetime.now() + timedelta(days=random.randint(1, 30))
    
    return {
        "appointment_date": future_date.strftime("%Y-%m-%d"),
        "appointment_time": f"{random.randint(9, 17):02d}:{random.choice(['00', '30'])}:00",
        "status": random.choice(["Scheduled", "Confirmed", "Pending"]),
        "appointment_type": random.choice(["Regular", "Emergency", "Follow_up", "Consultation"]),
        "doctor_name": random.choice(["Dr. Smith", "Dr. Johnson", "Dr. Wilson"]),
        "notes": "Test appointment notes"
    }
```

---

## Running Tests

### Prerequisites
1. **MediMax Backend Server**: Must be running on http://127.0.0.1:8420
2. **Database**: MariaDB/MySQL database must be accessible
3. **Python Dependencies**: Install required packages

```bash
# Install dependencies
pip install requests colorama

# Start the backend server (in another terminal)
cd backend_abhishek
python app.py
```

### Running Traditional Tests
```bash
# Navigate to backend directory
cd backend_abhishek

# Run comprehensive tests
python test_api_traditional.py

# Expected output:
# ==================== API TESTING STARTED ====================
# [1/29] Testing GET /health...
# ✅ SUCCESS: GET /health (Status: 200)
# Response: {'status': 'ok', 'database': 'ok'}
# ...
```

### Running Simple Tests
```bash
# Navigate to backend directory
cd backend_abhishek

# Run lightweight tests
python test_api_simple.py

# Expected output:
# Testing MediMax API Endpoints...
# ✓ GET /health - OK
# ✓ POST /db/new_patient - OK
# ...
# 
# Summary: 25/27 tests passed (92.6% success rate)
```

### Automated Testing
```bash
# Run both test suites sequentially
python test_api_traditional.py && python test_api_simple.py

# Run with output redirection
python test_api_traditional.py > test_results.log 2>&1
```

---

## Test Results Interpretation

### Success Indicators

#### Traditional Tests
```
✅ SUCCESS: GET /health (Status: 200)
Response: {'status': 'ok', 'database': 'ok'}
Response Time: 0.123s
```

#### Simple Tests
```
✓ GET /health - OK
```

### Failure Indicators

#### Traditional Tests
```
❌ FAILED: GET /db/get_patient_details (Status: 404)
Error: Patient not found
Response Time: 0.089s
Full Response: {"detail": "Patient not found"}
```

#### Simple Tests
```
✗ GET /db/get_patient_details - Failed: 404
```

### Warning Indicators
```
⚠️  WARNING: POST /db/add_appointment/{patient_id} (Status: 500)
Possible Issue: Database enum validation error
```

### Test Statistics
```
==================== TEST SUMMARY ====================
Total Tests: 29
✅ Passed: 27
❌ Failed: 2
⚠️  Warnings: 0
Success Rate: 93.1%
Total Duration: 15.67s
==================== TESTING COMPLETED ====================
```

---

## Test Data Specifications

### Database Enum Values
The tests use specific enum values that match the database schema:

#### Medical History Types
```python
VALID_HISTORY_TYPES = [
    "allergy",          # Allergic reactions and sensitivities
    "surgery",          # Surgical procedures and operations
    "family_history",   # Hereditary and family medical history
    "condition",        # Medical conditions and diagnoses
    "lifestyle",        # Lifestyle-related health factors
    "other"             # Miscellaneous medical history
]
```

#### Appointment Types
```python
VALID_APPOINTMENT_TYPES = [
    "Regular",          # Maps to 'routine_checkup' in database
    "Emergency",        # Maps to 'emergency' in database
    "Follow_up",        # Maps to 'follow_up' in database
    "Consultation",     # Maps to 'consultation' in database
    "Surgery"           # Maps to 'consultation' in database
]
```

#### Severity Levels
```python
VALID_SEVERITIES = [
    "mild",             # Low impact on patient
    "moderate",         # Medium impact on patient
    "severe",           # High impact on patient
    "critical"          # Life-threatening or urgent
]
```

#### Appointment Status
```python
VALID_STATUSES = [
    "Scheduled",        # Appointment booked
    "Confirmed",        # Appointment confirmed by patient
    "Pending",          # Awaiting confirmation
    "Completed",        # Appointment finished
    "Cancelled",        # Appointment cancelled
    "No_Show"           # Patient didn't attend
]
```

#### Symptom Onset Types
```python
VALID_ONSET_TYPES = [
    "sudden",           # Rapid onset
    "gradual",          # Slow development
    "chronic",          # Long-term persistent
    "intermittent"      # Comes and goes
]
```

### Test Data Validation
```python
def validate_patient_data(data):
    """Validate patient data meets requirements."""
    assert "name" in data and len(data["name"]) > 0
    assert "dob" in data and re.match(r'\d{4}-\d{2}-\d{2}', data["dob"])
    assert "sex" in data and data["sex"] in ["Male", "Female", "Other"]

def validate_appointment_data(data):
    """Validate appointment data meets requirements."""
    assert "appointment_date" in data
    assert "appointment_type" in data and data["appointment_type"] in VALID_APPOINTMENT_TYPES
    assert "status" in data and data["status"] in VALID_STATUSES
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Connection Refused Error
```
Error: Connection refused to http://127.0.0.1:8420
```
**Solution**: Ensure the backend server is running
```bash
cd backend_abhishek
python app.py
```

#### 2. Database Connection Error
```
Error: Database connection failed
```
**Solutions**:
- Check database server is running
- Verify `.env` file configuration
- Test database connection manually

#### 3. Patient Not Found (404)
```
Error: Patient not found for ID 7
```
**Solutions**:
- Create test patients first:
```bash
curl -X POST "http://127.0.0.1:8420/db/new_patient" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Patient", "dob": "1990-01-01", "sex": "Male"}'
```
- Update test configuration with existing patient IDs

#### 4. Enum Validation Errors
```
Error: Data truncated for column 'history_type'
```
**Solutions**:
- Use correct enum values from the specification
- Check database schema for allowed values
- Update test data to match schema

#### 5. Import Errors
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: Install required dependencies
```bash
pip install requests colorama
```

### Debug Mode
Enable debug mode in tests for detailed information:

```python
# In test files, set debug flag
DEBUG_MODE = True

# This will show:
# - Full request headers
# - Complete response bodies
# - Stack traces for errors
# - Database query information
```

### Test Database Setup
For isolated testing, create a test database:

```sql
-- Create test database
CREATE DATABASE medimax_test;
USE medimax_test;

-- Run your schema creation scripts
-- Insert test data as needed
```

Update test configuration:
```python
TEST_BASE_URL = "http://127.0.0.1:8420"  # Use test database
```

### Continuous Integration
Example GitHub Actions workflow:

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start API server
        run: python app.py &
      - name: Wait for server
        run: sleep 10
      - name: Run tests
        run: python test_api_simple.py
```

---

## Performance Testing

### Load Testing
For performance testing, modify the test files:

```python
import concurrent.futures
import time

def load_test_endpoint(endpoint, iterations=100):
    """Test endpoint performance under load."""
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(test_endpoint, endpoint) for _ in range(iterations)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    success_count = sum(1 for r in results if r['status'] == 'success')
    
    print(f"Load Test Results for {endpoint}:")
    print(f"  Total Requests: {iterations}")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {iterations - success_count}")
    print(f"  Total Time: {end_time - start_time:.2f}s")
    print(f"  Requests/Second: {iterations / (end_time - start_time):.2f}")
```

---

This testing documentation provides comprehensive guidance for validating the MediMax API functionality, ensuring robust and reliable healthcare data management.