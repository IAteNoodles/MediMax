# MediMax Backend API Endpoints

## Updated Endpoints Based on Correct Database Schema

### Core Database Endpoints
- `GET /db/get_patient_details?patient_id={id}` - Get patient basic information
- `GET /db/get_medical_history?patient_id={id}` - Get patient medical history
- `GET /db/get_medications?patient_id={id}` - Get patient medications
- `GET /db/get_symptoms?patient_id={id}` - Get patient symptoms from appointments
- `GET /db/get_medical_reports?patient_id={id}` - Get lab reports and medical reports

### New Enhanced Endpoints
- `GET /get_n_appointments?n={count}` - Get appointments with detailed symptoms
- `GET /get_medical_history/{patient_id}` - Get medical history with AI summary
- `GET /get_n_lab_reports/{patient_id}?n={count}` - Get lab reports with findings

### Utility Endpoints
- `GET /health` - Health check for database and services
- `GET /test_db` - Database connection and table structure test
- `GET /frontend/get_query?patient_id={id}` - Generate comprehensive patient summary

### Database Schema Corrections Made:
1. **Patient Table**: Fixed column names to match actual schema
   - `patient_id` (not Patient_ID)
   - `name` (not NAME)
   - `dob` (not DOB)
   - `sex` (not SEX)
   - Removed non-existent `REMARKS` column

2. **Symptoms**: Now properly queries `Appointment_Symptom` table with JOIN to `Appointment`

3. **Medical Reports**: Now properly queries both `Lab_Report` and `Report` tables with their findings

4. **Added Missing Endpoints**: Medical history and medications endpoints

All endpoints now use the correct table and column names as per the Database_Schema_README.md