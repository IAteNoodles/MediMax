# MediMax Backend API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Configuration](#configuration)
3. [Authentication & CORS](#authentication--cors)
4. [Health & Status Endpoints](#health--status-endpoints)
5. [Patient Management](#patient-management)
6. [Medical Records Management](#medical-records-management)
7. [Appointment Management](#appointment-management)
8. [Medication Management](#medication-management)
9. [Symptom Management](#symptom-management)
10. [Lab Reports & Findings](#lab-reports--findings)
11. [Search & Analytics](#search--analytics)
12. [AI/Agentic System](#aiagentic-system)
13. [Data Models](#data-models)
14. [Error Handling](#error-handling)
15. [Database Schema Reference](#database-schema-reference)

---

## Overview

The MediMax Backend API is a comprehensive FastAPI-based healthcare management system that serves as a bridge between the frontend interface, database, and AI systems. It provides complete CRUD operations for patient management, medical records, appointments, medications, lab reports, and integrates with AI models for medical analysis.

### Base URL
```
http://127.0.0.1:8420
```

### Technology Stack
- **Framework**: FastAPI
- **Database**: MariaDB/MySQL
- **ORM**: PyMySQL (direct SQL queries)
- **AI Integration**: Ollama (MedGemma model)
- **Documentation**: Automatic OpenAPI/Swagger docs

---

## Configuration

### Environment Variables
The application requires the following environment variables in `.env`:

```env
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

### Server Configuration
- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 8420
- **CORS**: Enabled for frontend communication
- **Timeout**: 60 seconds for AI operations

---

## Authentication & CORS

### CORS Configuration
```python
origins = [
    "http://10.26.5.99:8501",  # Production frontend
    "http://localhost:8501",   # Local development
]
```

**Allowed Methods**: All HTTP methods  
**Allowed Headers**: All headers  
**Credentials**: Enabled

---

## Health & Status Endpoints

### GET `/health`
**Description**: Comprehensive health check for backend services and database connectivity.

**Parameters**: None

**Response Format**:
```json
{
  "status": "ok",
  "database": "ok|error: <details>",
  "agentic_system": "ok|error: <details>"
}
```

**Response Codes**:
- `200`: Service healthy
- `500`: Service issues detected

---

### GET `/test_db`
**Description**: Test database connection and retrieve table structure information.

**Parameters**: None

**Response Format**:
```json
{
  "connection_test": {"test": 1},
  "available_tables": ["Patient", "Medical_History", ...],
  "patient_table_structure": [
    {
      "Field": "patient_id",
      "Type": "int(11)",
      "Null": "NO",
      "Key": "PRI",
      "Default": null,
      "Extra": "auto_increment"
    }
  ]
}
```

**Response Codes**:
- `200`: Database accessible
- `500`: Database connection failed

---

## Patient Management

### POST `/db/new_patient`
**Description**: Create a new patient record in the system.

**Request Body** (`NewPatientRequest`):
```json
{
  "name": "string (required) - Full name of the patient",
  "dob": "string (required) - Date of birth in YYYY-MM-DD format",
  "sex": "string (required) - Gender: 'Male', 'Female', or 'Other'"
}
```

**Response Format**:
```json
{
  "success": true,
  "message": "Patient created successfully",
  "patient_id": 123,
  "data": {
    "name": "John Doe",
    "dob": "1990-01-01",
    "sex": "Male"
  }
}
```

**Response Codes**:
- `200`: Patient created successfully
- `400`: Invalid data (e.g., invalid sex value)
- `500`: Database error

**Validation Rules**:
- `name`: Non-empty string
- `dob`: Valid date in YYYY-MM-DD format
- `sex`: Must be one of ['Male', 'Female', 'Other']

---

### GET `/db/get_all_patients`
**Description**: Retrieve paginated list of all patients.

**Query Parameters**:
- `limit` (int, optional, default=50): Maximum number of patients to return
- `offset` (int, optional, default=0): Number of patients to skip for pagination

**Response Format**:
```json
{
  "total_count": 150,
  "current_page_count": 10,
  "patients": [
    {
      "patient_id": 1,
      "name": "John Doe",
      "dob": "1990-01-01",
      "sex": "Male",
      "created_at": "2025-09-14T10:00:00",
      "updated_at": "2025-09-14T10:00:00"
    }
  ]
}
```

**Response Codes**:
- `200`: Success
- `500`: Database error

---

### GET `/db/get_patient_details`
**Description**: Get basic details for a specific patient.

**Query Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient_id": 1,
  "name": "John Doe",
  "dob": "1990-01-01",
  "sex": "Male",
  "created_at": "2025-09-14T10:00:00",
  "updated_at": "2025-09-14T10:00:00"
}
```

**Response Codes**:
- `200`: Patient found
- `404`: Patient not found
- `500`: Database error

---

### PUT `/db/update_patient/{patient_id}`
**Description**: Update an existing patient's information.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient to update

**Request Body** (`NewPatientRequest`):
```json
{
  "name": "string (required) - Updated full name",
  "dob": "string (required) - Updated date of birth in YYYY-MM-DD format",
  "sex": "string (required) - Updated gender: 'Male', 'Female', or 'Other'"
}
```

**Response Format**:
```json
{
  "success": true,
  "message": "Patient updated successfully",
  "patient_id": 1,
  "updated_data": {
    "name": "John Smith",
    "dob": "1990-01-01",
    "sex": "Male"
  }
}
```

**Response Codes**:
- `200`: Patient updated successfully
- `404`: Patient not found
- `400`: Invalid data
- `500`: Database error

---

### DELETE `/db/delete_patient/{patient_id}`
**Description**: Delete a patient and all associated medical records (cascading delete).

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient to delete

**Response Format**:
```json
{
  "success": true,
  "message": "Patient and all related records deleted successfully",
  "patient_id": 1,
  "deleted_records": {
    "appointments": 5,
    "medical_history": 3,
    "medications": 2,
    "lab_reports": 4
  }
}
```

**Response Codes**:
- `200`: Patient deleted successfully
- `404`: Patient not found
- `500`: Database error

**Warning**: This operation is irreversible and removes all associated data.

---

### GET `/db/search_patients`
**Description**: Search patients using multiple criteria with pagination.

**Query Parameters**:
- `name` (string, optional): Search by patient name (partial match)
- `patient_id` (int, optional): Search by exact patient ID
- `sex` (string, optional): Filter by gender
- `limit` (int, optional, default=20): Maximum results to return
- `offset` (int, optional, default=0): Results to skip for pagination

**Response Format**:
```json
{
  "total_count": 25,
  "current_page_count": 10,
  "limit": 20,
  "offset": 0,
  "search_criteria": {
    "name": "John",
    "patient_id": null,
    "sex": null
  },
  "patients": [
    {
      "patient_id": 1,
      "name": "John Doe",
      "dob": "1990-01-01",
      "sex": "Male",
      "created_at": "2025-09-14T10:00:00",
      "updated_at": "2025-09-14T10:00:00"
    }
  ]
}
```

**Response Codes**:
- `200`: Search completed (even if no results)
- `500`: Database error

---

### GET `/db/get_complete_patient_profile/{patient_id}`
**Description**: Retrieve comprehensive patient profile including all medical records.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient": {
    "patient_id": 1,
    "name": "John Doe",
    "dob": "1990-01-01",
    "sex": "Male",
    "created_at": "2025-09-14T10:00:00",
    "updated_at": "2025-09-14T10:00:00"
  },
  "medical_history": [
    {
      "history_id": 1,
      "history_type": "allergy",
      "history_item": "Penicillin",
      "history_details": "Severe allergic reaction",
      "history_date": "2020-01-15",
      "severity": "severe",
      "is_active": true,
      "updated_at": "2025-09-14T10:00:00"
    }
  ],
  "medications": [
    {
      "medication_id": 1,
      "medicine_name": "Aspirin",
      "is_continued": true,
      "prescribed_date": "2025-01-01",
      "discontinued_date": null,
      "dosage": "100mg",
      "frequency": "Daily",
      "prescribed_by": "Dr. Smith"
    }
  ],
  "appointments": [
    {
      "appointment_id": 1,
      "appointment_date": "2025-09-20",
      "appointment_time": "10:30:00",
      "status": "Scheduled",
      "appointment_type": "consultation",
      "doctor_name": "Dr. Smith",
      "notes": "Regular checkup",
      "symptoms": [
        {
          "symptom_id": 1,
          "symptom_name": "Headache",
          "symptom_description": "Persistent headache",
          "severity": "moderate",
          "duration": "3 days",
          "onset_type": "gradual"
        }
      ]
    }
  ],
  "lab_reports": [
    {
      "lab_report_id": 1,
      "lab_date": "2025-09-10",
      "lab_type": "Blood Work",
      "ordering_doctor": "Dr. Wilson",
      "lab_facility": "Central Lab",
      "findings": [
        {
          "lab_finding_id": 1,
          "test_name": "Glucose",
          "test_value": "95",
          "test_unit": "mg/dL",
          "reference_range": "70-100",
          "is_abnormal": false,
          "abnormal_flag": null
        }
      ]
    }
  ],
  "summary": {
    "total_medical_history_items": 5,
    "total_medications": 3,
    "total_appointments": 8,
    "total_lab_reports": 4
  }
}
```

**Response Codes**:
- `200`: Profile retrieved successfully
- `404`: Patient not found
- `500`: Database error

---

## Medical Records Management

### POST `/db/add_medical_history/{patient_id}`
**Description**: Add a medical history record for a patient.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Request Body** (`MedicalHistoryRequest`):
```json
{
  "history_type": "string (required) - Type of history: 'allergy', 'surgery', 'condition', 'family_history', 'lifestyle', 'other'",
  "history_item": "string (required) - Name or title of the medical history item",
  "history_details": "string (optional) - Detailed description of the history item",
  "history_date": "string (optional) - Date in YYYY-MM-DD format when the event occurred",
  "severity": "string (optional, default='mild') - Severity level: 'mild', 'moderate', 'severe', 'critical'",
  "is_active": "boolean (optional, default=true) - Whether the condition is currently active"
}
```

**Input Mapping**: The API automatically maps `chronic_condition` to `condition` for database compatibility.

**Response Format**:
```json
{
  "success": true,
  "message": "Medical history added successfully",
  "history_id": 123,
  "patient_id": 1,
  "data": {
    "history_type": "condition",
    "history_item": "Diabetes Type 2",
    "history_details": "Controlled with medication",
    "history_date": "2020-03-15",
    "severity": "moderate",
    "is_active": true
  }
}
```

**Response Codes**:
- `200`: Medical history added successfully
- `404`: Patient not found
- `400`: Invalid history type or severity
- `500`: Database error

**Validation Rules**:
- `history_type`: Must be one of the allowed enum values
- `severity`: Must be one of ['mild', 'moderate', 'severe', 'critical']
- `history_date`: Must be valid date format if provided

---

### GET `/db/get_medical_history`
**Description**: Retrieve all medical history records for a patient.

**Query Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient_id": 1,
  "medical_history": [
    {
      "history_id": 1,
      "history_type": "condition",
      "history_item": "Diabetes Type 2",
      "history_details": "Controlled with medication",
      "history_date": "2020-03-15",
      "severity": "moderate",
      "is_active": true,
      "updated_at": "2025-09-14T10:00:00"
    }
  ]
}
```

**Response Codes**:
- `200`: Medical history retrieved successfully
- `500`: Database error

---

### GET `/get_medical_history/{patient_id}`
**Description**: Get medical history with AI-generated summary using MedGemma model.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient_id": 1,
  "patient_name": "John Doe",
  "medical_history": [
    {
      "history_id": 1,
      "history_type": "condition",
      "history_item": "Diabetes Type 2",
      "history_details": "Controlled with medication",
      "history_date": "2020-03-15",
      "severity": "moderate",
      "is_active": true,
      "updated_at": "2025-09-14T10:00:00"
    }
  ],
  "medical_history_count": 1,
  "summary": "AI-generated comprehensive medical summary highlighting key conditions, treatments, and health patterns"
}
```

**Response Codes**:
- `200`: Medical history with summary retrieved
- `404`: Patient not found
- `500`: Database or AI service error

---

## Appointment Management

### POST `/db/add_appointment/{patient_id}`
**Description**: Schedule a new appointment for a patient.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Request Body** (`AppointmentRequest`):
```json
{
  "appointment_date": "string (required) - Appointment date in YYYY-MM-DD format",
  "appointment_time": "string (optional) - Appointment time in HH:MM:SS format",
  "status": "string (optional, default='Scheduled') - Status: 'Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show'",
  "appointment_type": "string (optional, default='Regular') - Type: 'Regular', 'Emergency', 'Follow_up', 'Consultation', 'Surgery'",
  "doctor_name": "string (optional) - Name of the attending doctor",
  "notes": "string (optional) - Additional notes about the appointment"
}
```

**Input Mapping**: The API automatically maps appointment types:
- `Regular` → `routine_checkup`
- `Emergency` → `emergency`
- `Follow_up` → `follow_up`
- `Consultation` → `consultation`
- `Surgery` → `consultation`

**Response Format**:
```json
{
  "success": true,
  "message": "Appointment created successfully",
  "appointment_id": 123,
  "patient_id": 1,
  "data": {
    "appointment_date": "2025-09-20",
    "appointment_time": "10:30:00",
    "status": "Scheduled",
    "appointment_type": "consultation",
    "doctor_name": "Dr. Smith",
    "notes": "Regular checkup"
  }
}
```

**Response Codes**:
- `200`: Appointment created successfully
- `404`: Patient not found
- `400`: Invalid status or appointment type
- `500`: Database error

---

### GET `/get_n_appointments`
**Description**: Retrieve recent appointments with detailed information and symptoms.

**Query Parameters**:
- `n` (int, optional): Number of recent appointments to return. If not specified, returns all appointments.

**Response Format**:
```json
{
  "count": 10,
  "appointments": [
    {
      "appointment_id": 1,
      "patient_name": "John Doe",
      "patient_id": 1,
      "appointment_date": "2025-09-20",
      "appointment_time": "10:30:00",
      "status": "scheduled",
      "appointment_type": "consultation",
      "notes": "Regular checkup",
      "symptoms": [
        {
          "symptom_id": 1,
          "symptom_name": "Headache",
          "symptom_description": "Persistent headache for 3 days",
          "severity": "moderate",
          "duration": "3 days",
          "onset_type": "gradual"
        }
      ]
    }
  ]
}
```

**Response Codes**:
- `200`: Appointments retrieved successfully
- `500`: Database error

---

## Medication Management

### POST `/db/add_medication/{patient_id}`
**Description**: Add a medication record for a patient.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Request Body** (`MedicationRequest`):
```json
{
  "medicine_name": "string (required) - Name of the medication",
  "is_continued": "boolean (optional, default=true) - Whether the medication is currently being taken",
  "prescribed_date": "string (required) - Date prescribed in YYYY-MM-DD format",
  "discontinued_date": "string (optional) - Date discontinued in YYYY-MM-DD format",
  "dosage": "string (optional) - Dosage information (e.g., '500mg')",
  "frequency": "string (optional) - Frequency of intake (e.g., 'Twice daily')",
  "prescribed_by": "string (optional) - Name of the prescribing doctor"
}
```

**Response Format**:
```json
{
  "success": true,
  "message": "Medication added successfully",
  "medication_id": 123,
  "patient_id": 1,
  "data": {
    "medicine_name": "Metformin",
    "is_continued": true,
    "prescribed_date": "2024-01-15",
    "discontinued_date": null,
    "dosage": "500mg",
    "frequency": "Twice daily",
    "prescribed_by": "Dr. Johnson"
  }
}
```

**Response Codes**:
- `200`: Medication added successfully
- `404`: Patient not found
- `500`: Database error

---

### GET `/db/get_medications`
**Description**: Retrieve all medications for a patient with their purposes.

**Query Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient_id": 1,
  "medications": [
    {
      "medication_id": 1,
      "medicine_name": "Metformin",
      "is_continued": true,
      "prescribed_date": "2024-01-15",
      "discontinued_date": null,
      "dosage": "500mg",
      "frequency": "Twice daily",
      "prescribed_by": "Dr. Johnson",
      "purposes": [
        {
          "condition_name": "Diabetes Type 2",
          "purpose_description": "Blood glucose control"
        }
      ]
    }
  ]
}
```

**Response Codes**:
- `200`: Medications retrieved successfully
- `500`: Database error

---

## Symptom Management

### POST `/db/add_symptom`
**Description**: Add a symptom record to an existing appointment.

**Request Body** (`SymptomRequest`):
```json
{
  "appointment_id": "integer (required) - ID of the appointment to associate the symptom with",
  "symptom_name": "string (required) - Name of the symptom",
  "symptom_description": "string (optional) - Detailed description of the symptom",
  "severity": "string (optional, default='mild') - Severity: 'mild', 'moderate', 'severe', 'critical'",
  "duration": "string (optional) - How long the symptom has been present",
  "onset_type": "string (optional, default='gradual') - Onset type: 'sudden', 'gradual', 'chronic', 'intermittent'"
}
```

**Response Format**:
```json
{
  "success": true,
  "message": "Symptom added successfully",
  "symptom_id": 123,
  "appointment_id": 1,
  "data": {
    "appointment_id": 1,
    "symptom_name": "Headache",
    "symptom_description": "Persistent headache for 3 days",
    "severity": "moderate",
    "duration": "3 days",
    "onset_type": "gradual"
  }
}
```

**Response Codes**:
- `200`: Symptom added successfully
- `404`: Appointment not found
- `400`: Invalid severity or onset type
- `500`: Database error

**Validation Rules**:
- `severity`: Must be one of ['mild', 'moderate', 'severe', 'critical']
- `onset_type`: Must be one of ['sudden', 'gradual', 'chronic', 'intermittent']

---

### GET `/db/get_symptoms`
**Description**: Retrieve all symptoms for a patient across all appointments.

**Query Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient_id": 1,
  "symptoms": [
    {
      "symptom_name": "Headache",
      "symptom_description": "Persistent headache for 3 days",
      "severity": "moderate",
      "duration": "3 days",
      "onset_type": "gradual",
      "appointment_date": "2025-09-20",
      "appointment_type": "consultation"
    }
  ]
}
```

**Response Codes**:
- `200`: Symptoms retrieved successfully
- `404`: No symptoms found for patient
- `500`: Database error

---

## Lab Reports & Findings

### POST `/db/add_lab_report/{patient_id}`
**Description**: Create a new lab report for a patient.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Request Body** (`LabReportRequest`):
```json
{
  "lab_date": "string (required) - Date of lab work in YYYY-MM-DD format",
  "lab_type": "string (required) - Type of lab work (e.g., 'Blood Work', 'Urine Analysis')",
  "ordering_doctor": "string (optional) - Name of the doctor who ordered the lab",
  "lab_facility": "string (optional) - Name of the laboratory facility"
}
```

**Response Format**:
```json
{
  "success": true,
  "message": "Lab report created successfully",
  "lab_report_id": 123,
  "patient_id": 1,
  "data": {
    "lab_date": "2024-09-10",
    "lab_type": "Blood Work",
    "ordering_doctor": "Dr. Wilson",
    "lab_facility": "Central Lab"
  }
}
```

**Response Codes**:
- `200`: Lab report created successfully
- `404`: Patient not found
- `500`: Database error

---

### POST `/db/add_lab_finding`
**Description**: Add a specific finding/result to an existing lab report.

**Request Body** (`LabFindingRequest`):
```json
{
  "lab_report_id": "integer (required) - ID of the lab report to associate the finding with",
  "test_name": "string (required) - Name of the test (e.g., 'Glucose', 'Hemoglobin')",
  "test_value": "string (required) - Result value of the test",
  "test_unit": "string (optional) - Unit of measurement (e.g., 'mg/dL', 'g/dL')",
  "reference_range": "string (optional) - Normal reference range for the test",
  "is_abnormal": "boolean (optional, default=false) - Whether the result is abnormal",
  "abnormal_flag": "string (optional) - Type of abnormality: 'high', 'low', 'critical_high', 'critical_low'"
}
```

**Response Format**:
```json
{
  "success": true,
  "message": "Lab finding added successfully",
  "lab_finding_id": 123,
  "lab_report_id": 1,
  "data": {
    "lab_report_id": 1,
    "test_name": "Glucose",
    "test_value": "95",
    "test_unit": "mg/dL",
    "reference_range": "70-100",
    "is_abnormal": false,
    "abnormal_flag": null
  }
}
```

**Response Codes**:
- `200`: Lab finding added successfully
- `404`: Lab report not found
- `400`: Invalid abnormal flag
- `500`: Database error

**Validation Rules**:
- `abnormal_flag`: Must be one of ['high', 'low', 'critical_high', 'critical_low'] if provided

---

### GET `/get_n_lab_reports/{patient_id}`
**Description**: Retrieve recent lab reports with all findings for a patient.

**Path Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Query Parameters**:
- `n` (int, optional): Number of recent lab reports to return. If not specified, returns all reports.

**Response Format**:
```json
{
  "patient_id": 1,
  "patient_name": "John Doe",
  "lab_reports_count": 5,
  "lab_reports": [
    {
      "lab_report_id": 1,
      "lab_date": "2024-09-10",
      "lab_type": "Blood Work",
      "ordering_doctor": "Dr. Wilson",
      "lab_facility": "Central Lab",
      "findings": [
        {
          "lab_finding_id": 1,
          "test_name": "Glucose",
          "test_value": "95",
          "test_unit": "mg/dL",
          "reference_range": "70-100",
          "is_abnormal": false,
          "abnormal_flag": null
        }
      ]
    }
  ]
}
```

**Response Codes**:
- `200`: Lab reports retrieved successfully
- `404`: Patient not found
- `500`: Database error

---

### GET `/db/get_medical_reports`
**Description**: Retrieve all lab reports and medical reports for a patient.

**Query Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient_id": 1,
  "lab_reports": [
    {
      "lab_report_id": 1,
      "lab_date": "2024-09-10",
      "lab_type": "Blood Work",
      "ordering_doctor": "Dr. Wilson",
      "lab_facility": "Central Lab",
      "findings": [
        {
          "test_name": "Glucose",
          "test_value": "95",
          "test_unit": "mg/dL",
          "reference_range": "70-100",
          "is_abnormal": false
        }
      ]
    }
  ],
  "medical_reports": [
    {
      "report_id": 1,
      "report_type": "Radiology",
      "report_date": "2024-09-05",
      "complete_report": "Full report text...",
      "report_summary": "Brief summary...",
      "doctor_name": "Dr. Radiology"
    }
  ]
}
```

**Response Codes**:
- `200`: Medical reports retrieved successfully
- `500`: Database error

---

## Search & Analytics

### GET `/api/endpoints`
**Description**: Comprehensive API documentation endpoint listing all available endpoints, data models, and usage examples.

**Parameters**: None

**Response Format**: 
Returns complete API documentation with:
- Endpoint descriptions grouped by category
- Data model specifications
- Usage examples
- Parameter requirements

**Response Codes**:
- `200`: Documentation retrieved successfully

---

## AI/Agentic System

### GET `/models`
**Description**: Retrieve information about available AI models for medical predictions.

**Parameters**: None

**Response Format**:
```json
{
  "available_models": {
    "cardiovascular_risk": {
      "required_parameters": [
        "age", "gender", "height", "weight", "ap_hi", "ap_lo", 
        "cholesterol", "gluc", "smoke", "alco", "active"
      ],
      "description": "Cardiovascular disease risk prediction model",
      "tool": "Predict_Cardiovascular_Risk_With_Explanation"
    },
    "diabetes_risk": {
      "required_parameters": [
        "age", "gender", "hypertension", "heart_disease", 
        "smoking_history", "bmi", "HbA1c_level", "blood_glucose_level"
      ],
      "description": "Diabetes risk prediction model",
      "tool": "Predict_Diabetes_Risk_With_Explanation"
    }
  }
}
```

**Response Codes**:
- `200`: Models information retrieved
- `503`: Agentic server unavailable
- `500`: Service error

---

### POST `/assess`
**Description**: Forward patient assessment request to agentic server for AI analysis.

**Request Body** (`AssessmentRequest`):
```json
{
  "patient_text": "string (required) - Comprehensive patient information text",
  "query": "string (required) - Specific question or analysis request",
  "additional_notes": "string (optional) - Additional context or notes"
}
```

**Response Format**: Varies based on agentic server response

**Response Codes**:
- `200`: Assessment completed
- `503`: Agentic server unavailable
- `500`: Service error

---

### POST `/assess_mock`
**Description**: Send mock patient data for assessment testing.

**Request Body**:
```json
{
  "patient_id": "integer (optional, default=0) - Index of mock patient data to use",
  "query": "string (required) - Assessment query"
}
```

**Response Format**: Mock assessment results for testing

**Response Codes**:
- `200`: Mock assessment completed
- `400`: Invalid patient index
- `500`: File not found or service error

---

### GET `/frontend/get_query`
**Description**: Auto-generate comprehensive patient assessment query based on database records.

**Query Parameters**:
- `patient_id` (int, required): Unique identifier of the patient

**Response Format**:
```json
{
  "patient_text": "Patient is named John Doe, with date of birth 1990-01-01 and sex Male. Active medical conditions include: Diabetes Type 2. Current medications include: Metformin. Recent symptoms include: Headache, Fatigue. Recent lab reports: Blood Work (2024-09-10).",
  "query": "Comprehensive analysis of patient record and potential risks.",
  "additional_notes": "This query was auto-generated for patient_id 1."
}
```

**Response Codes**:
- `200`: Query generated successfully
- `404`: Patient not found
- `500`: Database error

---

## Data Models

### NewPatientRequest
```json
{
  "name": "string (required) - Full name of the patient",
  "dob": "string (required) - Date of birth in YYYY-MM-DD format",
  "sex": "string (required) - Gender: 'Male', 'Female', or 'Other'"
}
```

### MedicalHistoryRequest
```json
{
  "history_type": "string (required) - Type: 'allergy', 'surgery', 'condition', 'family_history', 'lifestyle', 'other'",
  "history_item": "string (required) - Name of the medical history item",
  "history_details": "string (optional) - Detailed description",
  "history_date": "string (optional) - Date in YYYY-MM-DD format",
  "severity": "string (optional, default='mild') - 'mild', 'moderate', 'severe', 'critical'",
  "is_active": "boolean (optional, default=true) - Whether currently active"
}
```

### AppointmentRequest
```json
{
  "appointment_date": "string (required) - Date in YYYY-MM-DD format",
  "appointment_time": "string (optional) - Time in HH:MM:SS format",
  "status": "string (optional, default='Scheduled') - 'Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show'",
  "appointment_type": "string (optional, default='Regular') - 'Regular', 'Emergency', 'Follow_up', 'Consultation', 'Surgery'",
  "doctor_name": "string (optional) - Name of attending doctor",
  "notes": "string (optional) - Additional notes"
}
```

### MedicationRequest
```json
{
  "medicine_name": "string (required) - Name of the medication",
  "is_continued": "boolean (optional, default=true) - Currently taking",
  "prescribed_date": "string (required) - Date in YYYY-MM-DD format",
  "discontinued_date": "string (optional) - Date in YYYY-MM-DD format",
  "dosage": "string (optional) - Dosage information",
  "frequency": "string (optional) - Frequency of intake",
  "prescribed_by": "string (optional) - Prescribing doctor name"
}
```

### SymptomRequest
```json
{
  "appointment_id": "integer (required) - Associated appointment ID",
  "symptom_name": "string (required) - Name of the symptom",
  "symptom_description": "string (optional) - Detailed description",
  "severity": "string (optional, default='mild') - 'mild', 'moderate', 'severe', 'critical'",
  "duration": "string (optional) - Duration of symptom",
  "onset_type": "string (optional, default='gradual') - 'sudden', 'gradual', 'chronic', 'intermittent'"
}
```

### LabReportRequest
```json
{
  "lab_date": "string (required) - Date in YYYY-MM-DD format",
  "lab_type": "string (required) - Type of lab work",
  "ordering_doctor": "string (optional) - Ordering doctor name",
  "lab_facility": "string (optional) - Lab facility name"
}
```

### LabFindingRequest
```json
{
  "lab_report_id": "integer (required) - Associated lab report ID",
  "test_name": "string (required) - Name of the test",
  "test_value": "string (required) - Test result value",
  "test_unit": "string (optional) - Unit of measurement",
  "reference_range": "string (optional) - Normal reference range",
  "is_abnormal": "boolean (optional, default=false) - Whether abnormal",
  "abnormal_flag": "string (optional) - 'high', 'low', 'critical_high', 'critical_low'"
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error description message"
}
```

### Common HTTP Status Codes

#### 200 - Success
- Operation completed successfully
- Data retrieved or modified as requested

#### 400 - Bad Request
- Invalid input data
- Validation errors
- Missing required fields
- Invalid enum values

#### 404 - Not Found
- Patient not found
- Appointment not found
- Lab report not found
- No records match search criteria

#### 500 - Internal Server Error
- Database connection issues
- SQL execution errors
- Unexpected system errors
- AI service failures

#### 503 - Service Unavailable
- Agentic server is unreachable
- External service dependencies down

### Error Examples

**Invalid Patient Data (400)**:
```json
{
  "detail": "Sex must be one of: ['Male', 'Female', 'Other']"
}
```

**Patient Not Found (404)**:
```json
{
  "detail": "Patient not found"
}
```

**Database Error (500)**:
```json
{
  "detail": "Error adding medical history: (1265, \"Data truncated for column 'history_type' at row 1\")"
}
```

---

## Database Schema Reference

### Core Tables

#### Patient
- `patient_id`: Primary key (auto-increment)
- `name`: VARCHAR - Full name
- `dob`: DATE - Date of birth
- `sex`: ENUM('Male', 'Female', 'Other')
- `created_at`: TIMESTAMP
- `updated_at`: TIMESTAMP

#### Medical_History
- `history_id`: Primary key
- `patient_id`: Foreign key to Patient
- `history_type`: ENUM('allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other')
- `history_item`: VARCHAR
- `history_details`: TEXT
- `history_date`: DATE
- `severity`: ENUM('mild', 'moderate', 'severe', 'critical')
- `is_active`: TINYINT(1)
- `updated_at`: TIMESTAMP

#### Appointment
- `appointment_id`: Primary key
- `patient_id`: Foreign key to Patient
- `appointment_date`: DATE
- `appointment_time`: TIME
- `status`: ENUM('Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show')
- `appointment_type`: ENUM('consultation', 'follow_up', 'emergency', 'routine_checkup')
- `doctor_name`: VARCHAR
- `notes`: TEXT

### Enum Mappings

**History Type Mapping**:
- User Input: `chronic_condition` → Database: `condition`
- Direct mappings: `allergy`, `surgery`, `family_history`, `lifestyle`, `other`

**Appointment Type Mapping**:
- User Input: `Regular` → Database: `routine_checkup`
- User Input: `Emergency` → Database: `emergency`
- User Input: `Follow_up` → Database: `follow_up`
- User Input: `Consultation` → Database: `consultation`
- User Input: `Surgery` → Database: `consultation`

---

## Usage Examples

### Create a New Patient
```bash
curl -X POST "http://127.0.0.1:8420/db/new_patient" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "dob": "1990-01-01", 
    "sex": "Male"
  }'
```

### Search Patients
```bash
curl -X GET "http://127.0.0.1:8420/db/search_patients?name=John&limit=10"
```

### Add Medical History
```bash
curl -X POST "http://127.0.0.1:8420/db/add_medical_history/1" \
  -H "Content-Type: application/json" \
  -d '{
    "history_type": "allergy",
    "history_item": "Penicillin",
    "history_details": "Severe allergic reaction",
    "severity": "severe",
    "is_active": true
  }'
```

### Schedule Appointment
```bash
curl -X POST "http://127.0.0.1:8420/db/add_appointment/1" \
  -H "Content-Type: application/json" \
  -d '{
    "appointment_date": "2025-09-25",
    "appointment_time": "14:30:00",
    "status": "Scheduled",
    "appointment_type": "Consultation",
    "doctor_name": "Dr. Smith"
  }'
```

### Get Complete Patient Profile
```bash
curl -X GET "http://127.0.0.1:8420/db/get_complete_patient_profile/1"
```

---

## Development & Testing

### Running the Server
```bash
python app.py
# Server starts on http://127.0.0.1:8420
```

### API Testing
```bash
# Run comprehensive tests
python test_api_traditional.py

# Run simple tests
python test_api_simple.py
```

### Interactive Documentation
- **Swagger UI**: http://127.0.0.1:8420/docs
- **ReDoc**: http://127.0.0.1:8420/redoc

---

This documentation covers all endpoints, parameters, request/response formats, and error handling for the MediMax Backend API. For additional support or clarification, refer to the inline code documentation or the automatic OpenAPI documentation available when the server is running.