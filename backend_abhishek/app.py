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
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Database config
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_DATABASE = os.getenv("DB_DATABASE", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Agentic and frontend config
AGENTIC_ADDRESS = "http://10.26.5.99:8000"
FRONTEND_ADDRESS = "http://10.26.5.99:8501" # Default for Streamlit

app = FastAPI(title="MediMax Backend API", description="Bridge between Frontend, Database, and Agentic system.")

# --- CORS Configuration ---
# Allow requests from the Streamlit frontend
from fastapi.middleware.cors import CORSMiddleware

origins = [
    FRONTEND_ADDRESS,
    "http://localhost:8501",  # Also allow localhost for local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health Check ---
@app.get("/health")
async def health_check(db=Depends(get_db_connection)):
    """Backend health and connectivity check."""
    # --- Agentic System Check ---
    agentic_status = "not checked"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENTIC_ADDRESS}/health")
            if response.status_code == 200:
                agentic_status = "ok"
            else:
                agentic_status = f"error: status code {response.status_code}"
    except Exception as e:
        agentic_status = f"error: {str(e)}"

    # --- Database Check ---
    db_status = "not checked"
    try:
        if db.is_connected():
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            db_status = "ok"
        else:
            db_status = "error: not connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    finally:
        if db and db.is_connected():
            db.close()

    return {
        "status": "ok",
        "database": db_status,
        "agentic_system": agentic_status
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


# --- Agentic System Functions ---
class AssessmentRequest(BaseModel):
    patient_text: str
    query: str
    additional_notes: str | None = None

@app.get("/agentic/models")
async def get_models():
    """
    Retrieves information about the available models from the agentic server.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENTIC_ADDRESS}/models")
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to agentic server: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from agentic server: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/agentic/assess")
async def assess_patient(request: AssessmentRequest):
    """
    Forwards a patient assessment request to the agentic server.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AGENTIC_ADDRESS}/assess",
                json=request.dict()
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to agentic server: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from agentic server: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/agentic/assess_mock")
async def assess_patient_mock(patient_index: int = 0):
    """
    Sends a specific mock patient data from a JSON file to the agentic server for assessment.
    """
    try:
        # Load mock data from the JSON file
        with open(os.path.join(os.path.dirname(__file__), 'mock_data.json'), 'r') as f:
            mock_data_list = json.load(f)

        if not isinstance(mock_data_list, list) or not (0 <= patient_index < len(mock_data_list)):
            raise HTTPException(status_code=400, detail="Invalid patient index.")

        mock_data = mock_data_list[patient_index]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AGENTIC_ADDRESS}/assess",
                json=mock_data
            )
            response.raise_for_status()
            return response.json()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="mock_data.json not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding mock_data.json.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to agentic server: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from agentic server: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


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
def get_query(patient_id: int, db=Depends(get_db_connection)):
    """
    Constructs a comprehensive patient summary and a query based on database records.
    """
    patient_text_parts = []
    
    # 1. Get Patient Details
    try:
        details = get_patient_details(patient_id, db)
        patient_text_parts.append(
            f"Patient is named {details.get('NAME')}, with date of birth {details.get('DOB')} and sex {details.get('SEX')}."
        )
        if details.get('REMARKS'):
            patient_text_parts.append(f"General remarks: {details.get('REMARKS')}.")
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="Patient not found.")
        # Re-raise other exceptions
        raise

    # 2. Get Symptoms
    try:
        symptoms_data = get_symptoms(patient_id, db)
        if symptoms_data and symptoms_data.get('Symptoms'):
            symptoms_str = ", ".join(symptoms_data['Symptoms'])
            patient_text_parts.append(f"Reported symptoms include: {symptoms_str}.")
    except HTTPException as e:
        # It's okay if no symptoms are found, just note it.
        if e.status_code != 404:
            raise

    # 3. Get Medical Reports
    try:
        reports_data = get_medical_reports(patient_id, db)
        if reports_data and reports_data.get('Lab_Reports'):
            patient_text_parts.append("Recent lab reports are as follows:")
            for report in reports_data['Lab_Reports']:
                patient_text_parts.append(f"- Report from {report.get('Date')}: {report.get('Text')}")
    except HTTPException as e:
        # It's okay if no reports are found.
        if e.status_code != 404:
            raise

    # Combine into a single text
    patient_text = " ".join(patient_text_parts)
    
    return {
        "patient_text": patient_text,
        "query": "Comprehensive analysis of patient record and potential risks.",
        "additional_notes": f"This query was auto-generated for patient_id {patient_id}."
    }



if __name__ == "__main__":
    import uvicorn
    import socket

    # Get the hostname and IP address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    print(f"Starting server at http://{ip_address}:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)