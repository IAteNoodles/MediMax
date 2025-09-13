
# --- Database Configuration & Connection Dependency ---
import pymysql
from fastapi import status, Depends

def get_db_connection():
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

"""
MediMax Backend API (Single File)
---------------------------------
- All endpoints in this file (FastAPI)
- Loads config from parent .env file
- Placeholder logic only; no real connections yet
- Ready for extension and containerization
"""

# --- Configuration ---
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Database config
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_DATABASE = os.getenv("DB_DATABASE", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Agentic and frontend config (placeholders for now)
AGENTIC_ADDRESS = os.getenv("AGENTIC_ADDRESS", "<AGENTIC_ADDRESS_PLACEHOLDER>")
FRONTEND_ADDRESS = os.getenv("FRONTEND_ADDRESS", "<FRONTEND_ADDRESS_PLACEHOLDER>")

app = FastAPI(title="MediMax Backend API", description="Bridge between Frontend, Database, and Agentic system.")

# --- Health Check ---
@app.get("/health")
def health_check():
    """Backend health and connectivity check."""
    # TODO: Add real DB and agentic connectivity checks
    return {
        "status": "ok",
        "database": "not checked",
        "agentic_system": "not checked"
    }

# --- Database Functions ---
class NewPatientRequest(BaseModel):
    # TODO: Define patient fields
    name: str
    age: int
    # ... add more fields as needed

@app.post("/db/new_patient")
def new_patient(req: NewPatientRequest):
    """Add a new patient (placeholder)."""
    # TODO: Connect to DB and insert patient
    return {"message": "New patient endpoint (placeholder)", "data": req.dict()}

# --- Patient Details Function ---
@app.get("/db/get_patient_details")
def get_patient_details(patient_id: int, db=Depends(get_db_connection)):
    try:
        with db:
            with db.cursor() as cursor:
                sql = (
                    "SELECT NAME, DOB, SEX, REMARKS "
                    "FROM Patient "
                    "WHERE Patient_ID = %s"
                )
                cursor.execute(sql, (patient_id,))
                result = cursor.fetchone()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
                return {
                    "Patient_ID": patient_id,
                    "NAME": result.get("NAME"),
                    "DOB": str(result.get("DOB")),
                    "SEX": result.get("SEX"),
                    "REMARKS": result.get("REMARKS")
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Symptoms Function ---
@app.get("/db/get_symptoms")
def get_symptoms(patient_id: int, db=Depends(get_db_connection)):
    """Fetch Symptoms from the Appointment table for a patient."""
    try:
        with db:
            with db.cursor() as cursor:
                sql = (
                    "SELECT Symptoms "
                    "FROM Appointment "
                    "WHERE Patient_ID = %s"
                )
                cursor.execute(sql, (patient_id,))
                results = cursor.fetchall()
                if not results:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No symptoms found for this patient.")
                symptoms_list = [row.get("Symptoms") for row in results]
                return {
                    "Patient_ID": patient_id,
                    "Symptoms": symptoms_list
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Medical Reports Function ---
@app.get("/db/get_medical_reports")
def get_medical_reports(patient_id: int, db=Depends(get_db_connection)):
    """Fetch all lab reports for a patient from the Lab_Reports table."""
    try:
        with db:
            with db.cursor() as cursor:
                sql = (
                    "SELECT Text, Date "
                    "FROM Lab_Reports "
                    "WHERE Patient_ID = %s"
                )
                cursor.execute(sql, (patient_id,))
                results = cursor.fetchall()
                if not results:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No lab reports found for this patient.")
                reports = [
                    {"Text": row["Text"], "Date": str(row["Date"])}
                    for row in results
                ]
                return {
                    "Patient_ID": patient_id,
                    "Lab_Reports": reports
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Frontend Query Function ---
@app.get("/frontend/get_query")
def get_query():
    """Get the query from the frontend (placeholder)."""
    # TODO: Integrate with frontend to receive real query
    return {
        "query": "Placeholder query from frontend. Replace with real integration."
    }

"""
MediMax Backend API (Single File)
---------------------------------
- All endpoints in this file (FastAPI)
- Loads config from parent .env file
- Placeholder logic only; no real connections yet
- Ready for extension and containerization
"""

# --- Configuration ---
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Database config
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_DATABASE = os.getenv("DB_DATABASE", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Agentic and frontend config (placeholders for now)
AGENTIC_ADDRESS = os.getenv("AGENTIC_ADDRESS", "<AGENTIC_ADDRESS_PLACEHOLDER>")
FRONTEND_ADDRESS = os.getenv("FRONTEND_ADDRESS", "<FRONTEND_ADDRESS_PLACEHOLDER>")

app = FastAPI(title="MediMax Backend API", description="Bridge between Frontend, Database, and Agentic system.")

# --- Health Check ---
@app.get("/health")
def health_check():
    """Backend health and connectivity check."""
    # TODO: Add real DB and agentic connectivity checks
    return {
        "status": "ok",
        "database": "not checked",
        "agentic_system": "not checked"
    }


# --- Database Functions ---

class NewPatientRequest(BaseModel):
    # TODO: Define patient fields
    name: str
    age: int
    # ... add more fields as needed

@app.post("/db/new_patient")
def new_patient(req: NewPatientRequest):
    """Add a new patient (placeholder)."""
    # TODO: Connect to DB and insert patient
    return {"message": "New patient endpoint (placeholder)", "data": req.dict()}


# --- Patient Details Function ---
@app.get("/db/get_patient_details")
def get_patient_details(patient_id: str, db=Depends(get_db_connection)):
    try:
        with db:
            with db.cursor() as cursor:
                sql = (
                    "SELECT NAME, DOB, SEX, REMARKS "
                    "FROM Patient "
                    "WHERE Patient_ID = %s"
                )
                cursor.execute(sql, (patient_id,))
                result = cursor.fetchone()
                if not result:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
                return {
                    "patient_id": patient_id,
                    "name": result.get("NAME"),
                    "dob": result.get("DOB"),
                    "sex": result.get("SEX"),
                    "remarks": result.get("REMARKS")
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import socket

    # Get the hostname and IP address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    print(f"Starting server at http://{ip_address}:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)