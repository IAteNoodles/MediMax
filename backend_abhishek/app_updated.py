"""
MediMax Backend API - Updated for Rich Patient Database
-------------------------------------------------------
- FastAPI backend with comprehensive patient data endpoints
- Updated for atomic facts database schema
- Supports rich patient knowledge graph data
"""

# --- Database Configuration & Connection Dependency ---
import pymysql
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Database config - Updated for current schema
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_DATABASE = os.getenv("DB_NAME", "Hospital_controlmet")  # Updated to use DB_NAME from .env
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Agentic and frontend config
AGENTIC_ADDRESS = os.getenv("AGENTIC_ADDRESS", "<AGENTIC_ADDRESS_PLACEHOLDER>")
FRONTEND_ADDRESS = os.getenv("FRONTEND_ADDRESS", "<FRONTEND_ADDRESS_PLACEHOLDER>")

app = FastAPI(
    title="MediMax Backend API", 
    description="Bridge between Frontend, Database, and Agentic system - Rich Patient Data Support",
    version="2.0.0"
)

def get_db_connection():
    """Get database connection with updated configuration"""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

# --- Pydantic Models ---
class PatientResponse(BaseModel):
    patient_id: int
    name: str
    dob: str
    sex: str
    created_at: str

class MedicalHistoryResponse(BaseModel):
    history_id: int
    history_type: str
    history_item: str
    history_details: str
    severity: str
    history_date: str

class MedicationResponse(BaseModel):
    medication_id: int
    medicine_name: str
    dosage: str
    frequency: str
    prescribed_date: str
    prescribed_by: str
    is_continued: bool
    condition_name: Optional[str] = None
    purpose_description: Optional[str] = None

class AppointmentResponse(BaseModel):
    appointment_id: int
    appointment_date: str
    appointment_time: str
    doctor_name: str
    appointment_type: str
    status: str
    symptoms: List[dict] = []

class LabReportResponse(BaseModel):
    lab_report_id: int
    lab_date: str
    lab_type: str
    ordering_doctor: str
    lab_facility: str
    findings: List[dict] = []

class NewPatientRequest(BaseModel):
    name: str
    dob: str
    sex: str

# --- Health Check ---
@app.get("/health")
def health_check():
    """Backend health and connectivity check with database validation"""
    try:
        # Test database connection
        db = get_db_connection()
        with db:
            with db.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as patient_count FROM Patient")
                result = cursor.fetchone()
                patient_count = result['patient_count']
        
        return {
            "status": "ok",
            "database": "connected",
            "patient_count": patient_count,
            "database_name": DB_DATABASE,
            "agentic_system": "not checked"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": f"connection failed: {str(e)}",
            "agentic_system": "not checked"
        }

# --- Patient Management Endpoints ---
@app.get("/db/patients", response_model=List[PatientResponse])
def get_all_patients(db=Depends(get_db_connection)):
    """Get list of all patients"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM Patient ORDER BY patient_id DESC")
                results = cursor.fetchall()
                return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/patient/{patient_id}", response_model=PatientResponse)
def get_patient_details(patient_id: int, db=Depends(get_db_connection)):
    """Get detailed patient information"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Patient WHERE patient_id = %s",
                    (patient_id,)
                )
                result = cursor.fetchone()
                if not result:
                    raise HTTPException(status_code=404, detail="Patient not found")
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/patient/{patient_id}/medical_history", response_model=List[MedicalHistoryResponse])
def get_patient_medical_history(patient_id: int, db=Depends(get_db_connection)):
    """Get patient's medical history"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Medical_History WHERE patient_id = %s ORDER BY history_date DESC",
                    (patient_id,)
                )
                results = cursor.fetchall()
                return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/patient/{patient_id}/medications", response_model=List[MedicationResponse])
def get_patient_medications(patient_id: int, db=Depends(get_db_connection)):
    """Get patient's medications with purposes"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute("""
                    SELECT m.*, mp.condition_name, mp.purpose_description 
                    FROM Medication m 
                    LEFT JOIN Medication_Purpose mp ON m.medication_id = mp.medication_id 
                    WHERE m.patient_id = %s 
                    ORDER BY m.prescribed_date DESC
                """, (patient_id,))
                results = cursor.fetchall()
                return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/patient/{patient_id}/appointments", response_model=List[AppointmentResponse])
def get_patient_appointments(patient_id: int, db=Depends(get_db_connection)):
    """Get patient's appointments with symptoms"""
    try:
        with db:
            with db.cursor() as cursor:
                # Get appointments
                cursor.execute(
                    "SELECT * FROM Appointment WHERE patient_id = %s ORDER BY appointment_date DESC",
                    (patient_id,)
                )
                appointments = cursor.fetchall()
                
                # Get symptoms for each appointment
                for appointment in appointments:
                    cursor.execute(
                        "SELECT * FROM Appointment_Symptom WHERE appointment_id = %s",
                        (appointment['appointment_id'],)
                    )
                    symptoms = cursor.fetchall()
                    appointment['symptoms'] = symptoms
                
                return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/patient/{patient_id}/lab_reports", response_model=List[LabReportResponse])
def get_patient_lab_reports(patient_id: int, db=Depends(get_db_connection)):
    """Get patient's lab reports with findings"""
    try:
        with db:
            with db.cursor() as cursor:
                # Get lab reports
                cursor.execute(
                    "SELECT * FROM Lab_Report WHERE patient_id = %s ORDER BY lab_date DESC",
                    (patient_id,)
                )
                lab_reports = cursor.fetchall()
                
                # Get findings for each lab report
                for report in lab_reports:
                    cursor.execute(
                        "SELECT * FROM Lab_Finding WHERE lab_report_id = %s",
                        (report['lab_report_id'],)
                    )
                    findings = cursor.fetchall()
                    report['findings'] = findings
                
                return lab_reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/patient/{patient_id}/chat_history")
def get_patient_chat_history(patient_id: int, db=Depends(get_db_connection)):
    """Get patient's chat/communication history"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM Chat_History WHERE patient_id = %s ORDER BY timestamp DESC",
                    (patient_id,)
                )
                results = cursor.fetchall()
                return {
                    "patient_id": patient_id,
                    "chat_messages": results
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/patient/{patient_id}/summary")
def get_patient_summary(patient_id: int, db=Depends(get_db_connection)):
    """Get comprehensive patient summary for knowledge graph"""
    try:
        with db:
            with db.cursor() as cursor:
                # Get patient basic info
                cursor.execute("SELECT * FROM Patient WHERE patient_id = %s", (patient_id,))
                patient = cursor.fetchone()
                if not patient:
                    raise HTTPException(status_code=404, detail="Patient not found")
                
                # Get counts for different data types
                cursor.execute("SELECT COUNT(*) as count FROM Medical_History WHERE patient_id = %s", (patient_id,))
                medical_history_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM Medication WHERE patient_id = %s", (patient_id,))
                medication_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM Appointment WHERE patient_id = %s", (patient_id,))
                appointment_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM Lab_Report WHERE patient_id = %s", (patient_id,))
                lab_report_count = cursor.fetchone()['count']
                
                cursor.execute("""
                    SELECT COUNT(*) as count FROM Lab_Finding lf 
                    JOIN Lab_Report lr ON lf.lab_report_id = lr.lab_report_id 
                    WHERE lr.patient_id = %s
                """, (patient_id,))
                lab_finding_count = cursor.fetchone()['count']
                
                cursor.execute("""
                    SELECT COUNT(*) as count FROM Appointment_Symptom aps 
                    JOIN Appointment a ON aps.appointment_id = a.appointment_id 
                    WHERE a.patient_id = %s
                """, (patient_id,))
                symptom_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM Chat_History WHERE patient_id = %s", (patient_id,))
                chat_count = cursor.fetchone()['count']
                
                return {
                    "patient": patient,
                    "data_summary": {
                        "medical_history_count": medical_history_count,
                        "medication_count": medication_count,
                        "appointment_count": appointment_count,
                        "lab_report_count": lab_report_count,
                        "lab_finding_count": lab_finding_count,
                        "symptom_count": symptom_count,
                        "chat_message_count": chat_count
                    }
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/db/new_patient", response_model=PatientResponse)
def create_new_patient(req: NewPatientRequest, db=Depends(get_db_connection)):
    """Create a new patient"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Patient (name, dob, sex, created_at) VALUES (%s, %s, %s, NOW())",
                    (req.name, req.dob, req.sex)
                )
                patient_id = cursor.lastrowid
                db.commit()
                
                # Fetch the created patient
                cursor.execute("SELECT * FROM Patient WHERE patient_id = %s", (patient_id,))
                result = cursor.fetchone()
                return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Legacy Endpoints (for backward compatibility) ---
@app.get("/db/get_patient_details")
def get_patient_details_legacy(patient_id: int, db=Depends(get_db_connection)):
    """Legacy endpoint - redirects to new format"""
    return get_patient_details(patient_id, db)

@app.get("/db/get_symptoms")
def get_symptoms_legacy(patient_id: int, db=Depends(get_db_connection)):
    """Legacy symptoms endpoint - updated for new schema"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute("""
                    SELECT aps.symptom_name, aps.symptom_description, aps.severity, a.appointment_date
                    FROM Appointment_Symptom aps
                    JOIN Appointment a ON aps.appointment_id = a.appointment_id
                    WHERE a.patient_id = %s
                    ORDER BY a.appointment_date DESC
                """, (patient_id,))
                results = cursor.fetchall()
                
                if not results:
                    raise HTTPException(status_code=404, detail="No symptoms found for this patient")
                
                return {
                    "patient_id": patient_id,
                    "symptoms": results
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/get_medical_reports")
def get_medical_reports_legacy(patient_id: int, db=Depends(get_db_connection)):
    """Legacy medical reports endpoint - updated for new schema"""
    try:
        with db:
            with db.cursor() as cursor:
                cursor.execute("""
                    SELECT lr.lab_type, lr.lab_date, lr.ordering_doctor, lr.lab_facility,
                           GROUP_CONCAT(CONCAT(lf.test_name, ': ', lf.test_value, ' ', lf.test_unit) SEPARATOR '; ') as findings
                    FROM Lab_Report lr
                    LEFT JOIN Lab_Finding lf ON lr.lab_report_id = lf.lab_report_id
                    WHERE lr.patient_id = %s
                    GROUP BY lr.lab_report_id
                    ORDER BY lr.lab_date DESC
                """, (patient_id,))
                results = cursor.fetchall()
                
                if not results:
                    raise HTTPException(status_code=404, detail="No lab reports found for this patient")
                
                reports = [
                    {
                        "text": f"{row['lab_type']} - {row['findings'] or 'No findings'}",
                        "date": str(row["lab_date"]),
                        "doctor": row["ordering_doctor"],
                        "facility": row["lab_facility"]
                    }
                    for row in results
                ]
                
                return {
                    "patient_id": patient_id,
                    "lab_reports": reports
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Frontend Integration ---
@app.get("/frontend/get_query")
def get_query():
    """Get the query from the frontend (placeholder)."""
    return {
        "query": "Updated backend ready for rich patient data queries. Integration with frontend pending."
    }

# --- Knowledge Graph Integration ---
@app.get("/db/patient/{patient_id}/knowledge_graph_ready")
def check_knowledge_graph_ready(patient_id: int, db=Depends(get_db_connection)):
    """Check if patient has sufficient data for knowledge graph creation"""
    try:
        summary = get_patient_summary(patient_id, db)
        data_summary = summary["data_summary"]
        
        # Define minimum requirements for meaningful knowledge graph
        requirements = {
            "medical_history": data_summary["medical_history_count"] >= 2,
            "medications": data_summary["medication_count"] >= 3,
            "appointments": data_summary["appointment_count"] >= 1,
            "lab_reports": data_summary["lab_report_count"] >= 1
        }
        
        all_requirements_met = all(requirements.values())
        
        return {
            "patient_id": patient_id,
            "patient_name": summary["patient"]["name"],
            "knowledge_graph_ready": all_requirements_met,
            "requirements_status": requirements,
            "data_summary": data_summary,
            "recommendation": "Ready for Create_Knowledge_Graph() function" if all_requirements_met else "Add more patient data for richer knowledge graph"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import socket

    # Get the hostname and IP address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    print(f"🚀 MediMax Backend API v2.0 - Rich Patient Data Support")
    print(f"📊 Database: {DB_DATABASE}")
    print(f"🌐 Starting server at http://{ip_address}:8000")
    print(f"📖 API Documentation: http://{ip_address}:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)