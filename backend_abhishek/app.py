# --- Database Configuration & Connection Dependency ---
import pymysql
from fastapi import status, Depends, HTTPException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Establish a database connection to MariaDB/MySQL.
    
    Returns:
        pymysql.Connection: Database connection object with cursor factory.
        
    Raises:
        HTTPException: If database connection fails (status 500).
    """
    logger.info("Attempting to establish database connection.")
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("Database connection established successfully.")
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
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

from ollama import Client

medgemma = Client()

# Load .env from parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Database config
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Agentic and frontend config
AGENTIC_ADDRESS = "http://10.26.5.99:8000"
FRONTEND_ADDRESS = "http://10.26.5.99:8501" # Default for Streamlit


from fastmcp import FastMCP
import mariadb
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, ConfigurationError
from neo4j.time import Date, DateTime, Time, Duration
from datetime import datetime, date, time
import json

AURA_USER = os.getenv('AURA_USER')
AURA_PASSWORD = os.getenv('AURA_PASSWORD')

# Custom JSON encoder for Neo4j types
class Neo4jJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, (Date, DateTime)):
            return obj.isoformat()
        elif isinstance(obj, Time):
            return obj.isoformat()
        elif isinstance(obj, Duration):
            return str(obj)
        elif isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, '__str__'):
            return str(obj)
        return super().default(obj)

def serialize_neo4j_result(result):
    """Convert Neo4j result to JSON-serializable format"""
    def convert_value(value):
        if value is None:
            return None
        elif isinstance(value, (Date, DateTime, Time, Duration, date, datetime, time)):
            return str(value)
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_value(v) for v in value]
        elif hasattr(value, '__str__'):
            return str(value)
        return value
    
    if isinstance(result, dict):
        return {k: convert_value(v) for k, v in result.items()}
    elif isinstance(result, list):
        return [convert_value(item) for item in result]
    return convert_value(result)

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://98d1982d.databases.neo4j.io"
AUTH = (AURA_USER, AURA_PASSWORD)


app = FastAPI(title="MediMax Backend API", description="Bridge between Frontend, Database, and Agentic system.")

# --- Pydantic Models ---
class CypherQueryRequest(BaseModel):
    cypher_query: str

class NewPatientRequest(BaseModel):
    name: str
    dob: str  # Format: YYYY-MM-DD
    sex: str  # 'Male', 'Female', 'Other'

# --- CORS Configuration ---
# Allow requests from the Streamlit frontend
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]

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
    """
    Health check endpoint for backend service and database connectivity.
    
    Args:
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Health status containing:
            - status (str): Overall service status ('ok' or 'error')
            - database (str): Database connectivity status
            
    Raises:
        HTTPException: If health check fails (status 500).
    """
    """Backend health and connectivity check."""
    logger.info("Performing health check.")
    # --- Agentic System Check ---
    agentic_status = "not checked"
    logger.info("Checking agentic system status.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENTIC_ADDRESS}/health")
            if response.status_code == 200:
                agentic_status = "ok"
                logger.info("Agentic system is OK.")
            else:
                agentic_status = f"error: status code {response.status_code}"
                logger.warning(f"Agentic system returned status code {response.status_code}.")
    except Exception as e:
        agentic_status = f"error: {str(e)}"
        logger.error(f"Error checking agentic system: {e}")

    # --- Database Check ---
    db_status = "not checked"
    logger.info("Checking database status.")
    try:
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            db_status = "ok"
            logger.info("Database connection is OK.")
        else:
            db_status = "error: not connected"
            logger.warning("Database not connected for health check.")
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Error checking database connection: {e}")
    finally:
        if db:
            db.close()
    
    logger.info("Health check completed.")
    return {
        "status": "ok",
        "database": db_status,
        "agentic_system": agentic_status
    }

def get_neo4j_driver():
    """Create and return a Neo4j driver with proper configuration for Aura"""
    uri = URI
    user = AURA_USER
    password = AURA_PASSWORD
    
    if not all([uri, user, password]):
        raise HTTPException(status_code=500, detail="Missing Neo4j credentials")
    
    # Configuration optimized for Neo4j Aura
    driver_config = {
        "max_connection_lifetime": 30 * 60,  # 30 minutes
        "max_connection_pool_size": 50,
        "connection_acquisition_timeout": 60,  # 60 seconds
        "connection_timeout": 30,  # 30 seconds
        "max_retry_time": 30,
        "encrypted": True,  # Required for Aura
        "trust": "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"
    }
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password), **driver_config)
        logger.info(f"Neo4j driver created for URI: {uri}")
        return driver
    except Exception as e:
        logger.error(f"Failed to create Neo4j driver: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create Neo4j driver: {str(e)}")

def verify_neo4j_connection(driver, max_retries=3, retry_delay=2):
    """Verify Neo4j connection with retry logic"""
    import time
    for attempt in range(max_retries):
        try:
            logger.info(f"Verifying Neo4j connectivity (attempt {attempt + 1}/{max_retries})")
            
            # Use a session to verify connectivity instead of driver.verify_connectivity()
            with driver.session() as session:
                session.run("RETURN 1 AS test").consume()
            
            logger.info("Neo4j connectivity verified successfully")
            return True
        except Exception as e:
            logger.warning(f"Neo4j connectivity attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                logger.error("Max retries exceeded for Neo4j connectivity")
                raise
    
    return False

@app.post("/run_cypher_query")
async def run_cypher_query(request: CypherQueryRequest):
    """
    Execute a Cypher query on the Neo4j database with improved error handling.
    
    Args:
        request (CypherQueryRequest): JSON request containing:
            - cypher_query (str): The Cypher query to execute.
        
    Returns:
        dict: The result of the query or an error message.
    """
    logger.info(f"Executing Cypher query: {request.cypher_query}")
    
    # Log connection details (without password)
    logger.info(f"Neo4j URI: {URI}")
    logger.info(f"Neo4j User: {AURA_USER}")
    logger.info("Neo4j Password is set." if AURA_PASSWORD else "Neo4j Password is NOT set.")
    
    driver = None
    try:
        # Create driver with improved configuration
        driver = get_neo4j_driver()
        
        # Verify connectivity with retry logic
        verify_neo4j_connection(driver)
        
        # Execute the query with session management
        with driver.session() as session:
            logger.info("Executing Cypher query in session")
            result = session.run(request.cypher_query)
            records = [record.data() for record in result]
            
            logger.info(f"Query executed successfully. Retrieved {len(records)} records")
            
            # Apply serialization to handle Neo4j temporal types
            serialized_records = serialize_neo4j_result(records)
            
            return {"status": "success", "results": serialized_records, "count": len(serialized_records)}
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        error_msg = f"Error executing Cypher query: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}
    
    finally:
        # Ensure driver is properly closed
        if driver:
            try:
                driver.close()
                logger.info("Neo4j driver closed")
            except Exception as e:
                logger.warning(f"Error closing Neo4j driver: {str(e)}")

# --- Database Functions ---
@app.post("/db/new_patient")
def new_patient(req: NewPatientRequest, db=Depends(get_db_connection)):
    """
    Create a new patient record in the database.
    
    Args:
        req (NewPatientRequest): Patient data containing:
            - name (str): Full name of the patient
            - dob (str): Date of birth in YYYY-MM-DD format
            - sex (str): Gender ('Male', 'Female', or 'Other')
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether operation succeeded
            - message (str): Success message
            - patient_id (int): ID of created patient
            - data (dict): Original request data
            
    Raises:
        HTTPException: If patient creation fails or validation error (status 400/500).
    """
    """Add a new patient to the database."""
    try:
        cursor = db.cursor()
        
        # Validate sex field
        valid_sex_values = ['Male', 'Female', 'Other']
        if req.sex not in valid_sex_values:
            raise HTTPException(status_code=400, detail=f"Sex must be one of: {valid_sex_values}")
        
        # Insert new patient
        query = """
        INSERT INTO Patient (name, dob, sex, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        """
        cursor.execute(query, (req.name, req.dob, req.sex))
        
        # Get the inserted patient ID
        patient_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        return {
            "success": True,
            "message": "Patient created successfully",
            "patient_id": patient_id,
            "patient_data": {
                "name": req.name,
                "dob": req.dob,
                "sex": req.sex
            }
        }
        
    except Exception as e:
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating patient: {str(e)}")
    finally:
        if db:
            db.close()


# --- Additional Patient Management Endpoints ---

@app.get("/db/get_all_patients")
def get_all_patients(limit: int = 50, offset: int = 0, db=Depends(get_db_connection)):
    """
    Retrieve a paginated list of all patients.
    
    Args:
        limit (int, optional): Maximum number of patients to return. Defaults to 50.
        offset (int, optional): Number of patients to skip for pagination. Defaults to 0.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - total_count (int): Total number of patients in database
            - current_page_count (int): Number of patients in current response
            - patients (list): List of patient records with basic information
            
    Raises:
        HTTPException: If database query fails (status 500).
    """
    """Get all patients with pagination."""
    logger.info(f"Fetching all patients with limit={limit}, offset={offset}.")
    try:
        cursor = db.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM Patient")
        total_count = cursor.fetchone()["total"]
        
        # Get patients with pagination
        query = """
        SELECT patient_id, name, dob, sex, created_at, updated_at
        FROM Patient
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        cursor.execute(query, (limit, offset))
        patients = cursor.fetchall()
        cursor.close()
        logger.info(f"Found {len(patients)} patients.")
        
        # Format dates as strings
        for patient in patients:
            if patient["dob"]:
                patient["dob"] = str(patient["dob"])
            if patient["created_at"]:
                patient["created_at"] = str(patient["created_at"])
            if patient["updated_at"]:
                patient["updated_at"] = str(patient["updated_at"])
        
        logger.info("Successfully fetched and formatted patient list.")
        return {
            "total_count": total_count,
            "current_page_count": len(patients),
            "limit": limit,
            "offset": offset,
            "patients": patients
        }
        
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching patients: {str(e)}")
    finally:
        if db:
            db.close()


@app.put("/db/update_patient/{patient_id}")
def update_patient(patient_id: int, req: NewPatientRequest, db=Depends(get_db_connection)):
    """
    Update an existing patient's information.
    
    Args:
        patient_id (int): Unique identifier of the patient to update.
        req (NewPatientRequest): Updated patient data containing:
            - name (str): Updated full name
            - dob (str): Updated date of birth in YYYY-MM-DD format
            - sex (str): Updated gender ('Male', 'Female', or 'Other')
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether update succeeded
            - message (str): Success message
            - patient_id (int): ID of updated patient
            - updated_data (dict): Updated patient information
            
    Raises:
        HTTPException: If patient not found (status 404) or update fails (status 500).
    """
    """Update an existing patient."""
    logger.info(f"Updating patient with ID: {patient_id}")
    try:
        cursor = db.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patient WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            logger.warning(f"Patient with ID {patient_id} not found for update.")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Validate sex field
        valid_sex_values = ['Male', 'Female', 'Other']
        if req.sex not in valid_sex_values:
            logger.warning(f"Invalid sex value '{req.sex}' provided for patient {patient_id}.")
            raise HTTPException(status_code=400, detail=f"Sex must be one of: {valid_sex_values}")
        
        # Update patient
        query = """
        UPDATE Patient 
        SET name = %s, dob = %s, sex = %s, updated_at = NOW()
        WHERE patient_id = %s
        """
        cursor.execute(query, (req.name, req.dob, req.sex, patient_id))
        db.commit()
        cursor.close()
        
        logger.info(f"Patient {patient_id} updated successfully.")
        return {
            "success": True,
            "message": "Patient updated successfully",
            "patient_id": patient_id,
            "updated_data": {
                "name": req.name,
                "dob": req.dob,
                "sex": req.sex
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating patient: {str(e)}")
    finally:
        if db:
            db.close()


@app.delete("/db/delete_patient/{patient_id}")
def delete_patient(patient_id: int, db=Depends(get_db_connection)):
    """
    Delete a patient and all related records (cascading delete).
    
    Args:
        patient_id (int): Unique identifier of the patient to delete.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether deletion succeeded
            - message (str): Success message
            - patient_id (int): ID of deleted patient
            - deleted_records (dict): Count of related records deleted
            
    Raises:
        HTTPException: If patient not found (status 404) or deletion fails (status 500).
        
    Warning:
        This operation is irreversible and removes all associated medical data.
    """
    logger.info(f"Attempting to delete patient with ID: {patient_id} and all related records.")
    try:
        cursor = db.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patient WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            logger.warning(f"Patient with ID {patient_id} not found for deletion.")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Delete related records first (due to foreign key constraints)
        delete_queries = [
            "DELETE FROM Chat_History WHERE patient_id = %s",
            "DELETE FROM Report_Finding WHERE report_id IN (SELECT report_id FROM Report WHERE patient_id = %s)",
            "DELETE FROM Report WHERE patient_id = %s",
            "DELETE FROM Lab_Finding WHERE lab_report_id IN (SELECT lab_report_id FROM Lab_Report WHERE patient_id = %s)",
            "DELETE FROM Lab_Report WHERE patient_id = %s",
            "DELETE FROM Medication_Purpose WHERE medication_id IN (SELECT medication_id FROM Medication WHERE patient_id = %s)",
            "DELETE FROM Medication WHERE patient_id = %s",
            "DELETE FROM Appointment_Symptom WHERE appointment_id IN (SELECT appointment_id FROM Appointment WHERE patient_id = %s)",
            "DELETE FROM Appointment WHERE patient_id = %s",
            "DELETE FROM Medical_History WHERE patient_id = %s",
            "DELETE FROM Patient WHERE patient_id = %s"
        ]
        
        for query in delete_queries:
            logger.info(f"Executing delete query for patient {patient_id}: {query.split('WHERE')[0]}")
            cursor.execute(query, (patient_id,))
        
        db.commit()
        cursor.close()
        
        logger.info(f"Patient {patient_id} and all related records deleted successfully.")
        return {
            "success": True,
            "message": f"Patient {patient_id} and all related records deleted successfully",
            "patient_id": patient_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting patient: {str(e)}")
    finally:
        if db:
            db.close()


# --- Medical Record Management Endpoints ---

class MedicalHistoryRequest(BaseModel):
    history_type: str  # 'allergy', 'surgery', 'chronic_condition', 'family_history', 'lifestyle'
    history_item: str
    history_details: str = None
    history_date: str = None  # Format: YYYY-MM-DD
    severity: str = 'mild'  # 'Mild', 'Moderate', 'Severe', 'Critical'
    is_active: bool = True

@app.post("/db/add_medical_history/{patient_id}")
def add_medical_history(patient_id: int, req: MedicalHistoryRequest, db=Depends(get_db_connection)):
    """
    Add a medical history record for a patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        req (MedicalHistoryRequest): Medical history data containing:
            - history_type (str): Type of history ('allergy', 'surgery', 'condition', etc.)
            - history_item (str): Name/title of the medical history item
            - history_details (str, optional): Detailed description
            - history_date (str, optional): Date when event occurred (YYYY-MM-DD)
            - severity (str, optional): Severity level ('mild', 'moderate', 'severe', 'critical')
            - is_active (bool, optional): Whether condition is currently active
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether addition succeeded
            - message (str): Success message
            - history_id (int): ID of created medical history record
            - patient_id (int): ID of associated patient
            - data (dict): Original request data
            
    Raises:
        HTTPException: If patient not found (status 404), validation error (status 400), 
                      or database error (status 500).
                      
    Note:
        API automatically maps 'chronic_condition' to 'condition' for database compatibility.
    """
    logger.info(f"Adding medical history for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patient WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            logger.warning(f"Patient with ID {patient_id} not found when adding medical history.")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Validate enums (match actual database enum values)
        valid_types = ['allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other']
        valid_severities = ['mild', 'moderate', 'severe', 'critical']
        
        # Map user input to database values
        history_type_mapping = {
            'chronic_condition': 'condition',
            'condition': 'condition',
            'allergy': 'allergy',
            'surgery': 'surgery', 
            'family_history': 'family_history',
            'lifestyle': 'lifestyle',
            'other': 'other'
        }
        
        mapped_history_type = history_type_mapping.get(req.history_type, req.history_type)
        if mapped_history_type not in valid_types:
            logger.warning(f"Invalid history type '{req.history_type}' for patient {patient_id}.")
            raise HTTPException(status_code=400, detail=f"History type must be one of: {list(history_type_mapping.keys())}")
        
        if req.severity.lower() not in valid_severities:
            logger.warning(f"Invalid severity '{req.severity}' for patient {patient_id}.")
            raise HTTPException(status_code=400, detail=f"Severity must be one of: {valid_severities}")
        
        # Insert medical history (use mapped value)
        query = """
        INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, 
                                   history_date, severity, is_active, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (
            patient_id,
            mapped_history_type,  # Use mapped value
            req.history_item,
            req.history_details,
            req.history_date,
            req.severity.lower(),
            1 if req.is_active else 0
        ))
        
        history_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        logger.info(f"Medical history record {history_id} added for patient {patient_id}.")
        return {
            "success": True,
            "message": "Medical history added successfully",
            "history_id": history_id,
            "patient_id": patient_id,
            "data": req.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding medical history for patient {patient_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding medical history: {str(e)}")
    finally:
        if db:
            db.close()


class AppointmentRequest(BaseModel):
    appointment_date: str  # Format: YYYY-MM-DD
    appointment_time: str = None  # Format: HH:MM:SS
    status: str = 'Scheduled'  # 'Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show'
    appointment_type: str = 'Regular'  # 'Regular', 'Emergency', 'Follow_up', 'Consultation', 'Surgery'
    doctor_name: str = None
    notes: str = None

@app.post("/db/add_appointment/{patient_id}")
def add_appointment(patient_id: int, req: AppointmentRequest, db=Depends(get_db_connection)):
    """
    Schedule a new appointment for a patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        req (AppointmentRequest): Appointment data containing:
            - appointment_date (str): Date of appointment (YYYY-MM-DD)
            - appointment_time (str, optional): Time of appointment (HH:MM:SS)
            - status (str, optional): Appointment status (default: 'Scheduled')
            - appointment_type (str, optional): Type of appointment (default: 'Regular')
            - doctor_name (str, optional): Name of attending physician
            - notes (str, optional): Additional appointment notes
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether appointment creation succeeded
            - message (str): Success message
            - appointment_id (int): ID of created appointment
            - patient_id (int): ID of associated patient
            - data (dict): Original request data
            
    Raises:
        HTTPException: If patient not found (status 404), validation error (status 400),
                      or database error (status 500).
                      
    Note:
        API automatically maps appointment types to database values:
        'Regular' -> 'routine_checkup', 'Emergency' -> 'emergency', etc.
    """
    logger.info(f"Adding appointment for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patient WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            logger.warning(f"Patient with ID {patient_id} not found when adding appointment.")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Validate enums (match actual database enum values)
        valid_statuses = ['Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show']
        valid_types_db = ['consultation', 'follow_up', 'emergency', 'routine_checkup']
        
        # Map user input to database values
        appointment_type_mapping = {
            'Regular': 'routine_checkup',
            'routine_checkup': 'routine_checkup',
            'Emergency': 'emergency', 
            'emergency': 'emergency',
            'Follow_up': 'follow_up',
            'follow_up': 'follow_up',
            'Consultation': 'consultation',
            'consultation': 'consultation',
            'Surgery': 'consultation'  # Map Surgery to consultation as closest match
        }
        
        if req.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")
        
        mapped_appointment_type = appointment_type_mapping.get(req.appointment_type, req.appointment_type.lower())
        if mapped_appointment_type not in valid_types_db:
            logger.warning(f"Invalid appointment type '{req.appointment_type}' for patient {patient_id}.")
            raise HTTPException(status_code=400, detail=f"Appointment type must be one of: {list(appointment_type_mapping.keys())}")
        
        # Insert appointment (use mapped value)
        query = """
        INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, 
                               appointment_type, doctor_name, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            patient_id,
            req.appointment_date,
            req.appointment_time,
            req.status,
            mapped_appointment_type,  # Use mapped value
            req.doctor_name,
            req.notes
        ))
        
        appointment_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        logger.info(f"Appointment {appointment_id} created for patient {patient_id}.")
        return {
            "success": True,
            "message": "Appointment created successfully",
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "data": req.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment for patient {patient_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating appointment: {str(e)}")
    finally:
        if db:
            db.close()


class MedicationRequest(BaseModel):
    medicine_name: str
    is_continued: bool = True
    prescribed_date: str  # Format: YYYY-MM-DD
    discontinued_date: str = None  # Format: YYYY-MM-DD
    dosage: str = None
    frequency: str = None
    prescribed_by: str = None

@app.post("/db/add_medication/{patient_id}")
def add_medication(patient_id: int, req: MedicationRequest, db=Depends(get_db_connection)):
    """
    Add a medication record for a patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        req (MedicationRequest): Medication data containing:
            - medicine_name (str): Name of the medication
            - is_continued (bool, optional): Whether medication is currently taken (default: True)
            - prescribed_date (str): Date medication was prescribed (YYYY-MM-DD)
            - discontinued_date (str, optional): Date medication was discontinued (YYYY-MM-DD)
            - dosage (str, optional): Dosage information (e.g., '500mg')
            - frequency (str, optional): Frequency of intake (e.g., 'Twice daily')
            - prescribed_by (str, optional): Name of prescribing doctor
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether medication addition succeeded
            - message (str): Success message
            - medication_id (int): ID of created medication record
            - patient_id (int): ID of associated patient
            - data (dict): Original request data
            
    Raises:
        HTTPException: If patient not found (status 404) or database error (status 500).
    """
    logger.info(f"Adding medication for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patient WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            logger.warning(f"Patient with ID {patient_id} not found when adding medication.")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Insert medication
        query = """
        INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date,
                              discontinued_date, dosage, frequency, prescribed_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            patient_id,
            req.medicine_name,
            1 if req.is_continued else 0,
            req.prescribed_date,
            req.discontinued_date,
            req.dosage,
            req.frequency,
            req.prescribed_by
        ))
        
        medication_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        logger.info(f"Medication record {medication_id} added for patient {patient_id}.")
        return {
            "success": True,
            "message": "Medication added successfully",
            "medication_id": medication_id,
            "patient_id": patient_id,
            "data": req.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding medication for patient {patient_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding medication: {str(e)}")
    finally:
        if db:
            db.close()


class SymptomRequest(BaseModel):
    appointment_id: int
    symptom_name: str
    symptom_description: str = None
    severity: str = 'mild'  # 'Mild', 'Moderate', 'Severe', 'Critical'
    duration: str = None
    onset_type: str = 'gradual'  # 'Sudden', 'Gradual', 'Chronic', 'Intermittent'

@app.post("/db/add_symptom")
def add_symptom(req: SymptomRequest, db=Depends(get_db_connection)):
    """
    Add a symptom record to an existing appointment.
    
    Args:
        req (SymptomRequest): Symptom data containing:
            - appointment_id (int): ID of appointment to associate symptom with
            - symptom_name (str): Name of the symptom
            - symptom_description (str, optional): Detailed description of symptom
            - severity (str, optional): Severity level ('mild', 'moderate', 'severe', 'critical')
            - duration (str, optional): How long symptom has been present
            - onset_type (str, optional): Onset type ('sudden', 'gradual', 'chronic', 'intermittent')
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether symptom addition succeeded
            - message (str): Success message
            - symptom_id (int): ID of created symptom record
            - appointment_id (int): ID of associated appointment
            - data (dict): Original request data
            
    Raises:
        HTTPException: If appointment not found (status 404), validation error (status 400),
                      or database error (status 500).
    """
    logger.info(f"Adding symptom to appointment ID: {req.appointment_id}")
    try:
        cursor = db.cursor()
        
        # Check if appointment exists
        cursor.execute("SELECT appointment_id FROM Appointment WHERE appointment_id = %s", (req.appointment_id,))
        if not cursor.fetchone():
            logger.warning(f"Appointment with ID {req.appointment_id} not found when adding symptom.")
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Validate enums
        valid_severities = ['mild', 'moderate', 'severe', 'critical']
        valid_onset_types = ['sudden', 'gradual', 'chronic', 'intermittent']
        
        if req.severity.lower() not in valid_severities:
            logger.warning(f"Invalid severity '{req.severity}' for appointment {req.appointment_id}.")
            raise HTTPException(status_code=400, detail=f"Severity must be one of: {valid_severities}")
        
        if req.onset_type.lower() not in valid_onset_types:
            logger.warning(f"Invalid onset type '{req.onset_type}' for appointment {req.appointment_id}.")
            raise HTTPException(status_code=400, detail=f"Onset type must be one of: {valid_onset_types}")
        
        # Insert symptom
        query = """
        INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description,
                                       severity, duration, onset_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            req.appointment_id,
            req.symptom_name,
            req.symptom_description,
            req.severity.lower(),
            req.duration,
            req.onset_type.lower()
        ))
        
        symptom_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        logger.info(f"Symptom {symptom_id} added to appointment {req.appointment_id}.")
        return {
            "success": True,
            "message": "Symptom added successfully",
            "symptom_id": symptom_id,
            "appointment_id": req.appointment_id,
            "data": req.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding symptom to appointment {req.appointment_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding symptom: {str(e)}")
    finally:
        if db:
            db.close()


class LabReportRequest(BaseModel):
    lab_date: str  # Format: YYYY-MM-DD
    lab_type: str
    ordering_doctor: str = None
    lab_facility: str = None

@app.post("/db/add_lab_report/{patient_id}")
def add_lab_report(patient_id: int, req: LabReportRequest, db=Depends(get_db_connection)):
    """
    Create a new lab report for a patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        req (LabReportRequest): Lab report data containing:
            - lab_date (str): Date of lab work (YYYY-MM-DD)
            - lab_type (str): Type of lab work (e.g., 'Blood Work', 'Urine Analysis')
            - ordering_doctor (str, optional): Name of doctor who ordered the lab
            - lab_facility (str, optional): Name of laboratory facility
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether lab report creation succeeded
            - message (str): Success message
            - lab_report_id (int): ID of created lab report
            - patient_id (int): ID of associated patient
            - data (dict): Original request data
            
    Raises:
        HTTPException: If patient not found (status 404) or database error (status 500).
    """
    logger.info(f"Creating lab report for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        
        # Check if patient exists
        cursor.execute("SELECT patient_id FROM Patient WHERE patient_id = %s", (patient_id,))
        if not cursor.fetchone():
            logger.warning(f"Patient with ID {patient_id} not found when creating lab report.")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Insert lab report
        query = """
        INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            patient_id,
            req.lab_date,
            req.lab_type,
            req.ordering_doctor,
            req.lab_facility
        ))
        
        lab_report_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        logger.info(f"Lab report {lab_report_id} created for patient {patient_id}.")
        return {
            "success": True,
            "message": "Lab report created successfully",
            "lab_report_id": lab_report_id,
            "patient_id": patient_id,
            "data": req.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lab report for patient {patient_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating lab report: {str(e)}")
    finally:
        if db:
            db.close()


class LabFindingRequest(BaseModel):
    lab_report_id: int
    test_name: str
    test_value: str
    test_unit: str = None
    reference_range: str = None
    is_abnormal: bool = False
    abnormal_flag: str = None  # 'High', 'Low', 'Critical_High', 'Critical_Low'

@app.post("/db/add_lab_finding")
def add_lab_finding(req: LabFindingRequest, db=Depends(get_db_connection)):
    """
    Add a specific finding/result to an existing lab report.
    
    Args:
        req (LabFindingRequest): Lab finding data containing:
            - lab_report_id (int): ID of lab report to associate finding with
            - test_name (str): Name of the test (e.g., 'Glucose', 'Hemoglobin')
            - test_value (str): Result value of the test
            - test_unit (str, optional): Unit of measurement (e.g., 'mg/dL', 'g/dL')
            - reference_range (str, optional): Normal reference range for the test
            - is_abnormal (bool, optional): Whether result is abnormal (default: False)
            - abnormal_flag (str, optional): Type of abnormality ('high', 'low', etc.)
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - success (bool): Whether lab finding addition succeeded
            - message (str): Success message
            - lab_finding_id (int): ID of created lab finding
            - lab_report_id (int): ID of associated lab report
            - data (dict): Original request data
            
    Raises:
        HTTPException: If lab report not found (status 404), validation error (status 400),
                      or database error (status 500).
    """
    logger.info(f"Adding lab finding to lab report ID: {req.lab_report_id}")
    try:
        cursor = db.cursor()
        
        # Check if lab report exists
        cursor.execute("SELECT lab_report_id FROM Lab_Report WHERE lab_report_id = %s", (req.lab_report_id,))
        if not cursor.fetchone():
            logger.warning(f"Lab report with ID {req.lab_report_id} not found when adding finding.")
            raise HTTPException(status_code=404, detail="Lab report not found")
        
        # Validate abnormal flag
        if req.abnormal_flag:
            valid_flags = ['high', 'low', 'critical_high', 'critical_low']
            if req.abnormal_flag.lower() not in valid_flags:
                logger.warning(f"Invalid abnormal flag '{req.abnormal_flag}' for lab report {req.lab_report_id}.")
                raise HTTPException(status_code=400, detail=f"Abnormal flag must be one of: {valid_flags}")
        
        # Insert lab finding
        query = """
        INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit,
                               reference_range, is_abnormal, abnormal_flag)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            req.lab_report_id,
            req.test_name,
            req.test_value,
            req.test_unit,
            req.reference_range,
            1 if req.is_abnormal else 0,
            req.abnormal_flag.lower() if req.abnormal_flag else None
        ))
        
        lab_finding_id = cursor.lastrowid
        db.commit()
        cursor.close()
        
        logger.info(f"Lab finding {lab_finding_id} added to lab report {req.lab_report_id}.")
        return {
            "success": True,
            "message": "Lab finding added successfully",
            "lab_finding_id": lab_finding_id,
            "lab_report_id": req.lab_report_id,
            "data": req.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding lab finding to report {req.lab_report_id}: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding lab finding: {str(e)}")
    finally:
        if db:
            db.close()


# --- Comprehensive Patient Search ---

@app.get("/db/search_patients")
def search_patients(name: str = None, patient_id: int = None, sex: str = None, 
                   limit: int = 20, offset: int = 0, db=Depends(get_db_connection)):
    """
    Search patients using multiple criteria with pagination support.
    
    Args:
        name (str, optional): Search by patient name (partial match). Defaults to None.
        patient_id (int, optional): Search by exact patient ID. Defaults to None.
        sex (str, optional): Filter by gender ('Male', 'Female', 'Other'). Defaults to None.
        limit (int, optional): Maximum number of results to return. Defaults to 20.
        offset (int, optional): Number of results to skip for pagination. Defaults to 0.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - total_count (int): Total number of matching patients
            - current_page_count (int): Number of patients in current response
            - limit (int): Applied limit value
            - offset (int): Applied offset value
            - search_criteria (dict): Search parameters used
            - patients (list): List of matching patient records
            
    Raises:
        HTTPException: If database query fails (status 500).
    """
    logger.info(f"Searching for patients with criteria: name='{name}', patient_id={patient_id}, sex='{sex}'")
    try:
        cursor = db.cursor()
        
        # Build dynamic query
        where_conditions = []
        params = []
        
        if name:
            where_conditions.append("name LIKE %s")
            params.append(f"%{name}%")
        
        if patient_id:
            where_conditions.append("patient_id = %s")
            params.append(patient_id)
        
        if sex:
            where_conditions.append("sex = %s")
            params.append(sex)
        
        where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Count total matching records
        count_query = f"SELECT COUNT(*) as total FROM Patient{where_clause}"
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()["total"]
        logger.info(f"Found {total_count} total matching patients.")
        
        # Get matching patients
        query = f"""
        SELECT patient_id, name, dob, sex, created_at, updated_at
        FROM Patient{where_clause}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        cursor.execute(query, params)
        patients = cursor.fetchall()
        cursor.close()
        logger.info(f"Returning {len(patients)} patients for current page.")
        
        # Format dates
        for patient in patients:
            if patient["dob"]:
                patient["dob"] = str(patient["dob"])
            if patient["created_at"]:
                patient["created_at"] = str(patient["created_at"])
            if patient["updated_at"]:
                patient["updated_at"] = str(patient["updated_at"])
        
        return {
            "total_count": total_count,
            "current_page_count": len(patients),
            "limit": limit,
            "offset": offset,
            "search_criteria": {
                "name": name,
                "patient_id": patient_id,
                "sex": sex
            },
            "patients": patients
        }
        
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching patients: {str(e)}")
    finally:
        if db:
            db.close()


@app.get("/db/get_complete_patient_profile/{patient_id}")
def get_complete_patient_profile(patient_id: int, db=Depends(get_db_connection)):
    """
    Retrieve comprehensive patient profile including all medical records.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Complete patient profile containing:
            - patient (dict): Basic patient information
            - medical_history (list): All medical history records
            - medications (list): All medication records
            - appointments (list): All appointments with associated symptoms
            - lab_reports (list): All lab reports with findings
            - summary (dict): Count statistics for each data type
            
    Raises:
        HTTPException: If patient not found (status 404) or database error (status 500).
    """
    logger.info(f"Fetching complete profile for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        
        # Get patient basic info
        cursor.execute("""
            SELECT patient_id, name, dob, sex, created_at, updated_at
            FROM Patient WHERE patient_id = %s
        """, (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            logger.warning(f"Patient with ID {patient_id} not found for profile retrieval.")
            raise HTTPException(status_code=404, detail="Patient not found")
        
        logger.info(f"Found patient {patient['name']}.")
        # Format patient dates
        if patient["dob"]:
            patient["dob"] = str(patient["dob"])
        if patient["created_at"]:
            patient["created_at"] = str(patient["created_at"])
        if patient["updated_at"]:
            patient["updated_at"] = str(patient["updated_at"])
        
        # Get medical history
        logger.info(f"Fetching medical history for patient {patient_id}.")
        cursor.execute("""
            SELECT history_id, history_type, history_item, history_details,
                   history_date, severity, is_active, updated_at
            FROM Medical_History WHERE patient_id = %s
            ORDER BY history_date DESC, updated_at DESC
        """, (patient_id,))
        medical_history = cursor.fetchall()
        logger.info(f"Found {len(medical_history)} medical history records.")
        
        # Get medications
        logger.info(f"Fetching medications for patient {patient_id}.")
        cursor.execute("""
            SELECT medication_id, medicine_name, is_continued, prescribed_date,
                   discontinued_date, dosage, frequency, prescribed_by
            FROM Medication WHERE patient_id = %s
            ORDER BY prescribed_date DESC
        """, (patient_id,))
        medications = cursor.fetchall()
        logger.info(f"Found {len(medications)} medication records.")
        
        # Get appointments with symptoms
        logger.info(f"Fetching appointments and symptoms for patient {patient_id}.")
        cursor.execute("""
            SELECT a.appointment_id, a.appointment_date, a.appointment_time,
                   a.status, a.appointment_type, a.doctor_name, a.notes,
                   s.symptom_id, s.symptom_name, s.symptom_description,
                   s.severity, s.duration, s.onset_type
            FROM Appointment a
            LEFT JOIN Appointment_Symptom s ON a.appointment_id = s.appointment_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """, (patient_id,))
        appointment_results = cursor.fetchall()
        logger.info(f"Found {len(appointment_results)} appointment/symptom rows.")
        
        # Group appointments with their symptoms
        appointments = {}
        for row in appointment_results:
            apt_id = row["appointment_id"]
            if apt_id not in appointments:
                appointments[apt_id] = {
                    "appointment_id": apt_id,
                    "appointment_date": str(row["appointment_date"]),
                    "appointment_time": str(row["appointment_time"]) if row["appointment_time"] else None,
                    "status": row["status"],
                    "appointment_type": row["appointment_type"],
                    "doctor_name": row["doctor_name"],
                    "notes": row["notes"],
                    "symptoms": []
                }
            
            if row["symptom_id"]:
                appointments[apt_id]["symptoms"].append({
                    "symptom_id": row["symptom_id"],
                    "symptom_name": row["symptom_name"],
                    "symptom_description": row["symptom_description"],
                    "severity": row["severity"],
                    "duration": row["duration"],
                    "onset_type": row["onset_type"]
                })
        
        # Get lab reports with findings
        logger.info(f"Fetching lab reports and findings for patient {patient_id}.")
        cursor.execute("""
            SELECT lr.lab_report_id, lr.lab_date, lr.lab_type, lr.ordering_doctor, lr.lab_facility,
                   lf.lab_finding_id, lf.test_name, lf.test_value, lf.test_unit,
                   lf.reference_range, lf.is_abnormal, lf.abnormal_flag
            FROM Lab_Report lr
            LEFT JOIN Lab_Finding lf ON lr.lab_report_id = lf.lab_report_id
            WHERE lr.patient_id = %s
            ORDER BY lr.lab_date DESC
        """, (patient_id,))
        lab_results = cursor.fetchall()
        logger.info(f"Found {len(lab_results)} lab report/finding rows.")
        
        # Group lab reports with their findings
        lab_reports = {}
        for row in lab_results:
            report_id = row["lab_report_id"]
            if report_id not in lab_reports:
                lab_reports[report_id] = {
                    "lab_report_id": report_id,
                    "lab_date": str(row["lab_date"]),
                    "lab_type": row["lab_type"],
                    "ordering_doctor": row["ordering_doctor"],
                    "lab_facility": row["lab_facility"],
                    "findings": []
                }
            
            if row["lab_finding_id"]:
                lab_reports[report_id]["findings"].append({
                    "lab_finding_id": row["lab_finding_id"],
                    "test_name": row["test_name"],
                    "test_value": row["test_value"],
                    "test_unit": row["test_unit"],
                    "reference_range": row["reference_range"],
                    "is_abnormal": bool(row["is_abnormal"]),
                    "abnormal_flag": row["abnormal_flag"]
                })
        
        cursor.close()
        
        logger.info(f"Successfully compiled complete profile for patient {patient_id}.")
        return {
            "patient": patient,
            "medical_history": medical_history,
            "medications": medications,
            "appointments": list(appointments.values()),
            "lab_reports": list(lab_reports.values()),
            "summary": {
                "total_medical_history_items": len(medical_history),
                "total_medications": len(medications),
                "total_appointments": len(appointments),
                "total_lab_reports": len(lab_reports)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching complete profile for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching complete patient profile: {str(e)}")
    finally:
        if db:
            db.close()


@app.get("/api/endpoints")
def list_api_endpoints():
    """
    List all available API endpoints with descriptions and data models.
    
    Returns:
        dict: Comprehensive API documentation containing:
            - message (str): API title and description
            - version (str): API version
            - endpoints (dict): Categorized endpoint descriptions
            - data_models (dict): Request/response model specifications
            - usage_examples (dict): Example API calls
    """
    return {
        "message": "MediMax Backend API Endpoints",
        "version": "1.0.0",
        "endpoints": {
            "health_and_testing": {
                "GET /health": "Backend health and connectivity check",
                "GET /test_db": "Test database connection and show table structure"
            },
            "patient_management": {
                "POST /db/new_patient": "Add a new patient to the database",
                "GET /db/get_patient_details": "Get basic patient details by patient_id",
                "GET /db/get_all_patients": "Get all patients with pagination (limit, offset)",
                "GET /db/search_patients": "Search patients by name, patient_id, or sex",
                "PUT /db/update_patient/{patient_id}": "Update an existing patient",
                "DELETE /db/delete_patient/{patient_id}": "Delete a patient and all related records",
                "GET /db/get_complete_patient_profile/{patient_id}": "Get complete patient profile with all medical records"
            },
            "medical_records": {
                "GET /db/get_symptoms": "Get symptoms for a patient from appointments",
                "GET /db/get_medical_reports": "Get medical reports for a patient",
                "GET /get_medical_history/{patient_id}": "Get medical history with AI-generated summary",
                "POST /db/add_medical_history/{patient_id}": "Add medical history for a patient"
            },
            "appointments": {
                "GET /get_n_appointments": "Get appointments with detailed symptom information",
                "POST /db/add_appointment/{patient_id}": "Add an appointment for a patient",
                "POST /db/add_symptom": "Add a symptom to an appointment"
            },
            "medications": {
                "GET /get_medications/{patient_id}": "Get medications for a patient",
                "POST /db/add_medication/{patient_id}": "Add medication for a patient"
            },
            "lab_reports": {
                "GET /get_n_lab_reports/{patient_id}": "Get lab reports with findings",
                "POST /db/add_lab_report/{patient_id}": "Add a lab report for a patient",
                "POST /db/add_lab_finding": "Add a lab finding to a lab report"
            },
            "agentic_system": {
                "GET /models": "Get information about available AI models",
                "POST /assess": "Forward patient assessment request to agentic server",
                "GET /get_query/{patient_id}": "Auto-generate assessment query for a patient"
            }
        },
        "data_models": {
            "NewPatientRequest": {
                "name": "string",
                "dob": "string (YYYY-MM-DD)",
                "sex": "string (Male/Female/Other)"
            },
            "MedicalHistoryRequest": {
                "history_type": "string (allergy/surgery/chronic_condition/family_history/lifestyle)",
                "history_item": "string",
                "history_details": "string (optional)",
                "history_date": "string (YYYY-MM-DD, optional)",
                "severity": "string (mild/moderate/severe/critical)",
                "is_active": "boolean"
            },
            "AppointmentRequest": {
                "appointment_date": "string (YYYY-MM-DD)",
                "appointment_time": "string (HH:MM:SS, optional)",
                "status": "string (Scheduled/Confirmed/Pending/Completed/Cancelled/No_Show)",
                "appointment_type": "string (Regular/Emergency/Follow_up/Consultation/Surgery)",
                "doctor_name": "string (optional)",
                "notes": "string (optional)"
            },
            "MedicationRequest": {
                "medicine_name": "string",
                "is_continued": "boolean",
                "prescribed_date": "string (YYYY-MM-DD)",
                "discontinued_date": "string (YYYY-MM-DD, optional)",
                "dosage": "string (optional)",
                "frequency": "string (optional)",
                "prescribed_by": "string (optional)"
            },
            "SymptomRequest": {
                "appointment_id": "integer",
                "symptom_name": "string",
                "symptom_description": "string (optional)",
                "severity": "string (mild/moderate/severe/critical)",
                "duration": "string (optional)",
                "onset_type": "string (sudden/gradual/chronic/intermittent)"
            },
            "LabReportRequest": {
                "lab_date": "string (YYYY-MM-DD)",
                "lab_type": "string",
                "ordering_doctor": "string (optional)",
                "lab_facility": "string (optional)"
            },
            "LabFindingRequest": {
                "lab_report_id": "integer",
                "test_name": "string",
                "test_value": "string",
                "test_unit": "string (optional)",
                "reference_range": "string (optional)",
                "is_abnormal": "boolean",
                "abnormal_flag": "string (high/low/critical_high/critical_low, optional)"
            }
        },
        "usage_examples": {
            "create_patient": "POST /db/new_patient with {\"name\": \"John Doe\", \"dob\": \"1990-01-01\", \"sex\": \"Male\"}",
            "get_appointments": "GET /get_n_appointments?n=5",
            "search_patients": "GET /db/search_patients?name=John&limit=10",
            "get_patient_profile": "GET /db/get_complete_patient_profile/1"
        }
    }


# --- Agentic System Functions ---
class AssessmentRequest(BaseModel):
    patient_text: str
    query: str
    additional_notes: str | None = None

@app.get("/models")
async def get_models():
    """
    Retrieve information about available AI models from the agentic server.
    
    Returns:
        dict: Available AI models information including capabilities and parameters.
        
    Raises:
        HTTPException: If agentic server unavailable (status 503) or request fails (status 500).
    """
    logger.info("Requesting models from agentic server.")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{AGENTIC_ADDRESS}/models")
            response.raise_for_status()
            logger.info("Successfully retrieved models from agentic server.")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to agentic server for models: {e}")
        raise HTTPException(status_code=503, detail=f"Error connecting to agentic server: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Agentic server returned an error for models request: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from agentic server: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while getting models: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/assess")
async def assess_patient(request: AssessmentRequest):
    """
    Forward patient assessment request to the agentic server for AI analysis.
    
    Args:
        request (AssessmentRequest): Assessment data containing:
            - patient_text (str): Comprehensive patient information text
            - query (str): Specific question or analysis request
            - additional_notes (str, optional): Additional context or notes
            
    Returns:
        dict: AI assessment results from agentic server.
        
    Raises:
        HTTPException: If agentic server unavailable (status 503) or request fails (status 500).
    """
    logger.info("Forwarding patient assessment request to agentic server.")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AGENTIC_ADDRESS}/assess",
                json=request.dict()
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            logger.info("Successfully received assessment from agentic server.")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Error connecting to agentic server for assessment: {e}")
        raise HTTPException(status_code=503, detail=f"Error connecting to agentic server: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Agentic server returned an error for assessment: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from agentic server: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during assessment: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/assess_mock")
async def assess_patient_mock(patient_index: int = 0):
    """
    Send mock patient data for assessment testing purposes.
    
    Args:
        patient_index (int, optional): Index of mock patient data to use. Defaults to 0.
        
    Returns:
        dict: Mock assessment results for testing.
        
    Raises:
        HTTPException: If invalid patient index (status 400), mock data file not found (status 500),
                      or agentic server unavailable (status 503).
    """
    logger.info(f"Performing mock assessment for patient index: {patient_index}")
    try:
        # Load mock data from the JSON file
        mock_file_path = os.path.join(os.path.dirname(__file__), 'mock_data.json')
        logger.info(f"Loading mock data from {mock_file_path}")
        with open(mock_file_path, 'r') as f:
            mock_data_list = json.load(f)

        if not isinstance(mock_data_list, list) or not (0 <= patient_index < len(mock_data_list)):
            logger.warning(f"Invalid patient index {patient_index} requested for mock assessment.")
            raise HTTPException(status_code=400, detail="Invalid patient index.")

        mock_data = mock_data_list[patient_index]
        logger.info("Successfully loaded mock data.")

        async with httpx.AsyncClient(timeout=60.0) as client:
            logger.info("Sending mock data to agentic server for assessment.")
            response = await client.post(
                f"{AGENTIC_ADDRESS}/assess",
                json=mock_data
            )
            response.raise_for_status()
            logger.info("Successfully received mock assessment from agentic server.")
            return response.json()
    except FileNotFoundError:
        logger.error("mock_data.json not found.")
        raise HTTPException(status_code=500, detail="mock_data.json not found.")
    except json.JSONDecodeError:
        logger.error("Error decoding mock_data.json.")
        raise HTTPException(status_code=500, detail="Error decoding mock_data.json.")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to agentic server for mock assessment: {e}")
        raise HTTPException(status_code=503, detail=f"Error connecting to agentic server: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Agentic server returned an error for mock assessment: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error from agentic server: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during mock assessment: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# --- Patient Details Function ---
@app.get("/db/get_patient_details")
def get_patient_details(patient_id: int, db=Depends(get_db_connection)):
    """
    Get basic details for a specific patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Patient basic information containing:
            - patient_id (int): Patient's unique identifier
            - name (str): Patient's full name
            - dob (str): Date of birth
            - sex (str): Gender
            - created_at (str): Record creation timestamp
            - updated_at (str): Last update timestamp
            - summary (str): Brief summary of patient info
            
    Raises:
        HTTPException: If patient not found (status 404) or database error (status 500).
    """
    logger.info(f"Fetching details for patient ID: {patient_id}")
    try:
        with db:
            with db.cursor() as cursor:
                sql = (
                    "SELECT patient_id, name, dob, sex, created_at, updated_at, Summary "
                    "FROM Patient "
                    "WHERE patient_id = %s"
                )
                cursor.execute(sql, (patient_id,))
                result = cursor.fetchone()
                if not result:
                    logger.warning(f"Patient with ID {patient_id} not found.")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
                
                logger.info(f"Successfully fetched details for patient {patient_id}.")
                return {
                    "patient_id": result.get("patient_id"),
                    "name": result.get("name"),
                    "dob": str(result.get("dob")) if result.get("dob") else None,
                    "sex": result.get("sex"),
                    "created_at": str(result.get("created_at")) if result.get("created_at") else None,
                    "updated_at": str(result.get("updated_at")) if result.get("updated_at") else None,
                    "summary": str(result.get("Summary")) if result.get("Summary") else None
                
                }
    except Exception as e:
        logger.error(f"Error fetching details for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Symptoms Function ---
@app.get("/db/get_symptoms")
def get_symptoms(patient_id: int, db=Depends(get_db_connection)):
    """
    Fetch all symptoms for a patient across all appointments.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - patient_id (int): ID of the patient
            - symptoms (list): List of symptoms with details including:
                - symptom_name (str): Name of the symptom
                - symptom_description (str): Detailed description
                - severity (str): Severity level
                - duration (str): Duration of symptom
                - onset_type (str): Type of onset
                - appointment_date (str): Date of related appointment
                - appointment_type (str): Type of related appointment
                
    Raises:
        HTTPException: If no symptoms found (status 404) or database error (status 500).
    """
    logger.info(f"Fetching symptoms for patient ID: {patient_id}")
    try:
        with db:
            with db.cursor() as cursor:
                sql = (
                    "SELECT s.symptom_name, s.symptom_description, s.severity, s.duration, s.onset_type, "
                    "a.appointment_date, a.appointment_type "
                    "FROM Appointment_Symptom s "
                    "JOIN Appointment a ON s.appointment_id = a.appointment_id "
                    "WHERE a.patient_id = %s"
                )
                cursor.execute(sql, (patient_id,))
                results = cursor.fetchall()
                if not results:
                    logger.info(f"No symptoms found for patient {patient_id}.")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No symptoms found for this patient.")
                
                symptoms_list = []
                for row in results:
                    symptoms_list.append({
                        "symptom_name": row.get("symptom_name"),
                        "symptom_description": row.get("symptom_description"),
                        "severity": row.get("severity"),
                        "duration": row.get("duration"),
                        "onset_type": row.get("onset_type"),
                        "appointment_date": str(row.get("appointment_date")) if row.get("appointment_date") else None,
                        "appointment_type": row.get("appointment_type")
                    })
                
                logger.info(f"Found {len(symptoms_list)} symptoms for patient {patient_id}.")
                return {
                    "patient_id": patient_id,
                    "symptoms": symptoms_list
                }
    except Exception as e:
        logger.error(f"Error fetching symptoms for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Medical Reports Function ---
@app.get("/db/get_medical_reports")
def get_medical_reports(patient_id: int, db=Depends(get_db_connection)):
    """
    Fetch all lab reports and medical reports for a patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - patient_id (int): ID of the patient
            - lab_reports (list): List of lab reports with findings
            - medical_reports (list): List of general medical reports
            
    Raises:
        HTTPException: If database error occurs (status 500).
    """
    logger.info(f"Fetching all medical reports for patient ID: {patient_id}")
    try:
        with db:
            with db.cursor() as cursor:
                # Get Lab Reports with findings
                logger.info(f"Fetching lab reports for patient {patient_id}.")
                lab_sql = (
                    "SELECT lr.lab_report_id, lr.lab_date, lr.lab_type, lr.ordering_doctor, lr.lab_facility, "
                    "lf.test_name, lf.test_value, lf.test_unit, lf.reference_range, lf.is_abnormal "
                    "FROM Lab_Report lr "
                    "LEFT JOIN Lab_Finding lf ON lr.lab_report_id = lf.lab_report_id "
                    "WHERE lr.patient_id = %s "
                    "ORDER BY lr.lab_date DESC"
                )
                cursor.execute(lab_sql, (patient_id,))
                lab_results = cursor.fetchall()
                logger.info(f"Found {len(lab_results)} lab report rows for patient {patient_id}.")
                
                # Get Medical Reports
                logger.info(f"Fetching general medical reports for patient {patient_id}.")
                report_sql = (
                    "SELECT report_id, report_type, report_date, complete_report, report_summary, doctor_name "
                    "FROM Report "
                    "WHERE patient_id = %s "
                    "ORDER BY report_date DESC"
                )
                cursor.execute(report_sql, (patient_id,))
                medical_results = cursor.fetchall()
                logger.info(f"Found {len(medical_results)} general medical reports for patient {patient_id}.")
                
                # Process lab reports
                lab_reports = {}
                for row in lab_results:
                    report_id = row["lab_report_id"]
                    if report_id not in lab_reports:
                        lab_reports[report_id] = {
                            "lab_report_id": report_id,
                            "lab_date": str(row["lab_date"]),
                            "lab_type": row["lab_type"],
                            "ordering_doctor": row["ordering_doctor"],
                            "lab_facility": row["lab_facility"],
                            "findings": []
                        }
                    
                    if row["test_name"]:
                        lab_reports[report_id]["findings"].append({
                            "test_name": row["test_name"],
                            "test_value": row["test_value"],
                            "test_unit": row["test_unit"],
                            "reference_range": row["reference_range"],
                            "is_abnormal": bool(row["is_abnormal"])
                        })
                
                # Process medical reports
                medical_reports = []
                for row in medical_results:
                    medical_reports.append({
                        "report_id": row["report_id"],
                        "report_type": row["report_type"],
                        "report_date": str(row["report_date"]) if row["report_date"] else None,
                        "complete_report": row["complete_report"],
                        "report_summary": row["report_summary"],
                        "doctor_name": row["doctor_name"]
                    })
                
                logger.info(f"Successfully processed all reports for patient {patient_id}.")
                return {
                    "patient_id": patient_id,
                    "lab_reports": list(lab_reports.values()),
                    "medical_reports": medical_reports
                }
    except Exception as e:
        logger.error(f"Error fetching medical reports for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Medical History Function ---
@app.get("/db/get_medical_history")
def get_medical_history(patient_id: int, db=Depends(get_db_connection)):
    """
    Fetch all medical history records for a patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - patient_id (int): ID of the patient
            - medical_history (list): List of medical history records with details
            
    Raises:
        HTTPException: If database error occurs (status 500).
    """
    logger.info(f"Fetching medical history for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        sql = (
            "SELECT history_id, history_type, history_item, history_details, "
            "history_date, severity, is_active, updated_at "
            "FROM Medical_History "
            "WHERE patient_id = %s "
            "ORDER BY history_date DESC, updated_at DESC"
        )
        cursor.execute(sql, (patient_id,))
        results = cursor.fetchall()
        
        history_list = []
        for row in results:
            history_list.append({
                "history_id": row["history_id"],
                "history_type": row["history_type"],
                "history_item": row["history_item"],
                "history_details": row["history_details"],
                "history_date": str(row["history_date"]) if row["history_date"] else None,
                "severity": row["severity"],
                "is_active": bool(row["is_active"]),
                "updated_at": str(row["updated_at"]) if row["updated_at"] else None
            })
        
        cursor.close()
        
        logger.info(f"Found {len(history_list)} medical history records for patient {patient_id}.")
        return {
            "patient_id": patient_id,
            "medical_history": history_list
        }
        
    except Exception as e:
        logger.error(f"Error fetching medical history for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()

# --- Medications Function ---
@app.get("/db/get_medications")
def get_medications(patient_id: int, db=Depends(get_db_connection)):
    """
    Fetch all medications for a patient with their purposes.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - patient_id (int): ID of the patient
            - medications (list): List of medications with details including purposes
            
    Raises:
        HTTPException: If database error occurs (status 500).
    """
    logger.info(f"Fetching medications for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        sql = (
            "SELECT m.medication_id, m.medicine_name, m.is_continued, m.prescribed_date, "
            "m.discontinued_date, m.dosage, m.frequency, m.prescribed_by, "
            "mp.condition_name, mp.purpose_description "
            "FROM Medication m "
            "LEFT JOIN Medication_Purpose mp ON m.medication_id = mp.medication_id "
            "WHERE m.patient_id = %s "
            "ORDER BY m.prescribed_date DESC"
        )
        cursor.execute(sql, (patient_id,))
        results = cursor.fetchall()
        
        medications = {}
        for row in results:
            med_id = row["medication_id"]
            if med_id not in medications:
                medications[med_id] = {
                    "medication_id": med_id,
                    "medicine_name": row["medicine_name"],
                    "is_continued": bool(row["is_continued"]),
                    "prescribed_date": str(row["prescribed_date"]) if row["prescribed_date"] else None,
                    "discontinued_date": str(row["discontinued_date"]) if row["discontinued_date"] else None,
                    "dosage": row["dosage"],
                    "frequency": row["frequency"],
                    "prescribed_by": row["prescribed_by"],
                    "purposes": []
                }
            
            if row["condition_name"]:
                medications[med_id]["purposes"].append({
                    "condition_name": row["condition_name"],
                    "purpose_description": row["purpose_description"]
                })
        
        cursor.close()
        
        logger.info(f"Found {len(medications)} unique medications for patient {patient_id}.")
        return {
            "patient_id": patient_id,
            "medications": list(medications.values())
        }
        
    except Exception as e:
        logger.error(f"Error fetching medications for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if db:
            db.close()

# --- Frontend Query Function ---
@app.get("/frontend/get_query")
def get_query(patient_id: int):
    """
    Auto-generate comprehensive patient assessment query based on database records.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        
    Returns:
        dict: Generated query data containing:
            - patient_text (str): Comprehensive patient summary text
            - query (str): Standard assessment query
            - additional_notes (str): Auto-generation metadata
            
    Raises:
        HTTPException: If patient not found (status 404) or database/AI error (status 500).
        
    Note:
        Automatically aggregates patient demographics, medical history, medications,
        symptoms, and lab reports into a cohesive summary for AI analysis.
    """
    logger.info(f"Auto-generating query for patient ID: {patient_id}")
    patient_text_parts = []
    
    # 1. Get Patient Details
    logger.info(f"Step 1: Fetching patient details for patient {patient_id}.")
    try:
        db = get_db_connection()
        details = get_patient_details(patient_id, db)
        patient_text_parts.append(
            f"Patient is named {details.get('name')}, with date of birth {details.get('dob')} and sex {details.get('sex')}."
        )
        logger.info("Patient details fetched.")
        # Note: No REMARKS field in the new schema
    except HTTPException as e:
        if e.status_code == 404:
            logger.warning(f"Patient {patient_id} not found during query generation.")
            raise HTTPException(status_code=404, detail="Patient not found.")
        # Re-raise other exceptions
        logger.error(f"Error fetching patient details for query generation: {e.detail}")
        raise
    finally:
        if 'db' in locals():
            db.close()

    # 2. Get Medical History
    logger.info(f"Step 2: Fetching medical history for patient {patient_id}.")
    try:
        db = get_db_connection()
        history_data = get_medical_history(patient_id, db)
        if history_data and history_data.get('medical_history'):
            active_conditions = [h for h in history_data['medical_history'] if h.get('is_active')]
            if active_conditions:
                conditions_str = ", ".join([h.get('history_item') for h in active_conditions])
                patient_text_parts.append(f"Active medical conditions include: {conditions_str}.")
                logger.info("Added active medical conditions to query text.")
    except HTTPException as e:
        if e.status_code != 404:
            logger.error(f"Error fetching medical history for query generation: {e.detail}")
            raise
        else:
            logger.info("No medical history found, skipping.")
    finally:
        if 'db' in locals():
            db.close()

    # 3. Get Current Medications
    logger.info(f"Step 3: Fetching current medications for patient {patient_id}.")
    try:
        db = get_db_connection()
        meds_data = get_medications(patient_id, db)
        if meds_data and meds_data.get('medications'):
            current_meds = [m for m in meds_data['medications'] if m.get('is_continued')]
            if current_meds:
                meds_str = ", ".join([m.get('medicine_name') for m in current_meds])
                patient_text_parts.append(f"Current medications include: {meds_str}.")
                logger.info("Added current medications to query text.")
    except HTTPException as e:
        if e.status_code != 404:
            logger.error(f"Error fetching medications for query generation: {e.detail}")
            raise
        else:
            logger.info("No current medications found, skipping.")
    finally:
        if 'db' in locals():
            db.close()

    # 4. Get Recent Symptoms (simplified)
    logger.info(f"Step 4: Fetching recent symptoms for patient {patient_id}.")
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT DISTINCT s.symptom_name 
            FROM Appointment_Symptom s
            JOIN Appointment a ON s.appointment_id = a.appointment_id
            WHERE a.patient_id = %s 
            ORDER BY a.appointment_date DESC 
            LIMIT 5
        """, (patient_id,))
        symptoms = cursor.fetchall()
        if symptoms:
            symptoms_str = ", ".join([s['symptom_name'] for s in symptoms])
            patient_text_parts.append(f"Recent symptoms include: {symptoms_str}.")
            logger.info("Added recent symptoms to query text.")
        cursor.close()
    except Exception as e:
        # It's okay if no symptoms are found
        logger.info(f"No symptoms found or error during fetch, skipping. Error: {e}")
        pass
    finally:
        if 'db' in locals():
            db.close()

    # 5. Get Recent Lab Reports (simplified)
    logger.info(f"Step 5: Fetching recent lab reports for patient {patient_id}.")
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("""
            SELECT lab_type, lab_date 
            FROM Lab_Report 
            WHERE patient_id = %s 
            ORDER BY lab_date DESC 
            LIMIT 3
        """, (patient_id,))
        lab_reports = cursor.fetchall()
        if lab_reports:
            reports_str = ", ".join([f"{r['lab_type']} ({r['lab_date']})" for r in lab_reports])
            patient_text_parts.append(f"Recent lab reports: {reports_str}.")
            logger.info("Added recent lab reports to query text.")
        cursor.close()
    except Exception as e:
        # It's okay if no reports are found
        logger.info(f"No lab reports found or error during fetch, skipping. Error: {e}")
        pass
    finally:
        if 'db' in locals():
            db.close()

    # Combine into a single text
    patient_text = " ".join(patient_text_parts)
    logger.info(f"Final generated query text for patient {patient_id}: '{patient_text}'")
    
    return {
        "patient_text": patient_text,
        "query": "Comprehensive analysis of patient record and potential risks.",
        "additional_notes": f"This query was auto-generated for patient_id {patient_id}."
    }


# --- New API Endpoints ---

@app.get("/test_db")
def test_database_connection(db=Depends(get_db_connection)):
    """
    Test database connection and retrieve table structure information.
    
    Args:
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Database test results containing:
            - connection_test (dict): Basic connectivity test result
            - available_tables (list): List of all database tables
            - patient_table_structure (list): Structure of Patient table if exists
            
    Raises:
        HTTPException: If database test fails (status 500).
    """
    logger.info("Performing database connection test.")
    try:
        cursor = db.cursor()
        
        # Test basic connection
        cursor.execute("SELECT 1 as test")
        test_result = cursor.fetchone()
        
        # Get table list
        logger.info("Fetching list of tables.")
        cursor.execute("SHOW TABLES")
        tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
        logger.info(f"Found tables: {tables}")
        
        # Get Patient table structure if it exists
        patient_structure = []
        if 'Patient' in tables:
            logger.info("Describing 'Patient' table structure.")
            cursor.execute("DESCRIBE Patient")
            patient_structure = cursor.fetchall()
        
        cursor.close()
        
        logger.info("Database test completed successfully.")
        return {
            "connection_test": test_result,
            "available_tables": tables,
            "patient_table_structure": patient_structure
        }
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")
    finally:
        if db:
            db.close()

@app.get("/get_n_appointments")
def get_n_appointments(n: int = None, db=Depends(get_db_connection)):
    """
    Retrieve recent appointments with detailed symptom information.
    
    Args:
        n (int, optional): Number of recent appointments to return. If None, returns all.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - count (int): Number of appointments returned
            - appointments (list): List of appointments with patient details and symptoms
            
    Raises:
        HTTPException: If database error occurs (status 500).
        
    Note:
        Returns appointments ordered by date (most recent first) with grouped symptoms.
    """
    logger.info(f"Fetching {'all' if n is None else n} appointments.")
    try:
        cursor = db.cursor()
        
        if n is not None:
            # Get latest n appointments with detailed symptoms
            query = """
            SELECT 
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.appointment_type,
                a.notes,
                p.name as patient_name,
                p.patient_id,
                s.symptom_id,
                s.symptom_name,
                s.symptom_description,
                s.severity,
                s.duration,
                s.onset_type
            FROM 
                Appointment a
            JOIN 
                Patient p ON a.patient_id = p.patient_id
            LEFT JOIN 
                Appointment_Symptom s ON a.appointment_id = s.appointment_id
            ORDER BY 
                a.appointment_date DESC, a.appointment_time DESC
            LIMIT %s
            """
            cursor.execute(query, (n,))
        else:
            # Get all appointments with detailed symptoms
            query = """
            SELECT 
                a.appointment_id,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.appointment_type,
                a.notes,
                p.name as patient_name,
                p.patient_id,
                s.symptom_id,
                s.symptom_name,
                s.symptom_description,
                s.severity,
                s.duration,
                s.onset_type
            FROM 
                Appointment a
            JOIN 
                Patient p ON a.patient_id = p.patient_id
            LEFT JOIN 
                Appointment_Symptom s ON a.appointment_id = s.appointment_id
            ORDER BY 
                a.appointment_date DESC, a.appointment_time DESC
            """
            cursor.execute(query)
        
        results = cursor.fetchall()
        logger.info(f"Found {len(results)} appointment rows from database.")
        
        # Group symptoms by appointment
        appointments = {}
        for row in results:
            appointment_id = row["appointment_id"]
            
            if appointment_id not in appointments:
                appointments[appointment_id] = {
                    "appointment_id": appointment_id,
                    "patient_name": row["patient_name"],
                    "patient_id": row["patient_id"],
                    "appointment_date": str(row["appointment_date"]),
                    "appointment_time": str(row["appointment_time"]) if row["appointment_time"] else None,
                    "status": row["status"],
                    "appointment_type": row["appointment_type"],
                    "notes": row["notes"],
                    "symptoms": []
                }
            
            # Add symptom details if they exist
            if row["symptom_id"]:
                symptom = {
                    "symptom_id": row["symptom_id"],
                    "symptom_name": row["symptom_name"],
                    "symptom_description": row["symptom_description"],
                    "severity": row["severity"],
                    "duration": row["duration"],
                    "onset_type": row["onset_type"]
                }
                appointments[appointment_id]["symptoms"].append(symptom)
        
        # Convert to list and sort by date
        formatted_appointments = list(appointments.values())
        formatted_appointments.sort(key=lambda x: x["appointment_date"], reverse=True)
        
        # Apply limit after grouping if specified
        if n is not None:
            formatted_appointments = formatted_appointments[:n]
        
        return {
            "count": len(formatted_appointments),
            "appointments": formatted_appointments
        }
        
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching appointments: {str(e)}")
    finally:
        if db:
            db.close()


@app.get("/get_medical_history/{patient_id}")
async def get_medical_history_summary(patient_id: int, db=Depends(get_db_connection)):
    """
    Get medical history for a patient with AI-generated summary using MedGemma model.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - patient_id (int): ID of the patient
            - patient_name (str): Name of the patient
            - medical_history (list): Complete medical history records
            - medical_history_count (int): Total number of history items
            - summary (str): AI-generated concise medical summary
            
    Raises:
        HTTPException: If patient not found (status 404) or database/AI error (status 500).
        
    Note:
        Uses Ollama MedGemma model to generate medically relevant summaries.
    """
    logger.info(f"Fetching medical history with summary for patient ID: {patient_id}")
    try:
        cursor = db.cursor()
        
        # Get medical history
        query = """
        SELECT 
            history_id,
            history_type,
            history_item,
            history_details,
            history_date,
            severity,
            is_active,
            updated_at
        FROM Medical_History 
        WHERE patient_id = %s
        ORDER BY history_date DESC, updated_at DESC
        """
        cursor.execute(query, (patient_id,))
        medical_history = cursor.fetchall()
        
        # Get patient info
        patient_query = "SELECT name, dob, sex FROM Patient WHERE patient_id = %s"
        cursor.execute(patient_query, (patient_id,))
        patient_info = cursor.fetchone()
        cursor.close()
        
        if not patient_info:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        if not medical_history:
            return {
                "patient_id": patient_id,
                "patient_name": patient_info["name"],
                "medical_history": [],
                "summary": "No medical history available for this patient."
            }
        
        # Format medical history for LLM
        history_text = f"Patient: {patient_info['name']}, DOB: {patient_info['dob']}, Sex: {patient_info['sex']}\n\n"
        history_text += "Medical History:\n"
        
        for item in medical_history:
            history_text += f"- {item['history_type'].title()}: {item['history_item']}\n"
            if item['history_details']:
                history_text += f"  Details: {item['history_details']}\n"
            if item['history_date']:
                history_text += f"  Date: {item['history_date']}\n"
            history_text += f"  Severity: {item['severity']}, Active: {'Yes' if item['is_active'] else 'No'}\n\n"
        
        # Call Ollama medgemma model for summary
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                ollama_request = {
                    "model": "alibayram/medgemma:4b",
                    "prompt": f"Please provide a medically concise summary of the following patient's medical history. Focus on significant conditions, chronological progression, and current active issues:\n\n{history_text}",
                    "stream": False
                }
                
                response = await client.post("http://localhost:11434/api/generate", json=ollama_request)
                response.raise_for_status()
                
                ollama_response = response.json()
                summary = ollama_response.get("response", "Unable to generate summary")
                
        except Exception as e:
            # Fallback if Ollama is not available
            summary = f"LLM summary unavailable ({str(e)}). Raw medical history provided."
        
        return {
            "patient_id": patient_id,
            "patient_name": patient_info["name"],
            "medical_history": medical_history,
            "medical_history_count": len(medical_history),
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching medical history: {str(e)}")
    finally:
        if db:
            db.close()


@app.get("/get_n_lab_reports/{patient_id}")
def get_n_lab_reports(patient_id: int, n: int = None, db=Depends(get_db_connection)):
    """
    Get recent lab reports with findings for a patient.
    
    Args:
        patient_id (int): Unique identifier of the patient.
        n (int, optional): Number of recent lab reports to return. If None, returns all.
        db (pymysql.Connection): Database connection dependency.
        
    Returns:
        dict: Response containing:
            - patient_id (int): ID of the patient
            - patient_name (str): Name of the patient
            - lab_reports_count (int): Total number of lab reports
            - lab_reports (list): List of lab reports with associated findings
            
    Raises:
        HTTPException: If patient not found (status 404) or database error (status 500).
        
    Note:
        Returns lab reports ordered by date (most recent first) with grouped findings.
    """
    logger.info(f"Fetching {'all' if n is None else n} lab reports for patient ID: {patient_id}.")
    try:
        cursor = db.cursor()
        
        # First, get patient info to verify patient exists
        patient_query = "SELECT name FROM Patient WHERE patient_id = %s"
        cursor.execute(patient_query, (patient_id,))
        patient_info = cursor.fetchone()
        
        if not patient_info:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get lab reports with findings
        if n is not None:
            query = """
            SELECT 
                lr.lab_report_id,
                lr.lab_date,
                lr.lab_type,
                lr.ordering_doctor,
                lr.lab_facility,
                lf.lab_finding_id,
                lf.test_name,
                lf.test_value,
                lf.test_unit,
                lf.reference_range,
                lf.is_abnormal,
                lf.abnormal_flag
            FROM 
                Lab_Report lr
            LEFT JOIN 
                Lab_Finding lf ON lr.lab_report_id = lf.lab_report_id
            WHERE 
                lr.patient_id = %s
            ORDER BY 
                lr.lab_date DESC
            LIMIT %s
            """
            cursor.execute(query, (patient_id, n))
        else:
            query = """
            SELECT 
                lr.lab_report_id,
                lr.lab_date,
                lr.lab_type,
                lr.ordering_doctor,
                lr.lab_facility,
                lf.lab_finding_id,
                lf.test_name,
                lf.test_value,
                lf.test_unit,
                lf.reference_range,
                lf.is_abnormal,
                lf.abnormal_flag
            FROM 
                Lab_Report lr
            LEFT JOIN 
                Lab_Finding lf ON lr.lab_report_id = lf.lab_report_id
            WHERE 
                lr.patient_id = %s
            ORDER BY 
                lr.lab_date DESC
            """
            cursor.execute(query, (patient_id,))
        
        results = cursor.fetchall()
        logger.info(f"Found {len(results)} lab report rows from database.")
        
        # Group findings by lab report
        lab_reports = {}
        for row in results:
            report_id = row["lab_report_id"]
            
            if report_id not in lab_reports:
                lab_reports[report_id] = {
                    "lab_report_id": report_id,
                    "lab_date": str(row["lab_date"]),
                    "lab_type": row["lab_type"],
                    "ordering_doctor": row["ordering_doctor"],
                    "lab_facility": row["lab_facility"],
                    "findings": []
                }
            
            # Add finding if it exists
            if row["lab_finding_id"]:
                finding = {
                    "lab_finding_id": row["lab_finding_id"],
                    "test_name": row["test_name"],
                    "test_value": row["test_value"],
                    "test_unit": row["test_unit"],
                    "reference_range": row["reference_range"],
                    "is_abnormal": bool(row["is_abnormal"]),
                    "abnormal_flag": row["abnormal_flag"]
                }
                lab_reports[report_id]["findings"].append(finding)
        
        # Limit to n reports if specified
        report_list = list(lab_reports.values())
        if n is not None:
            report_list = report_list[:n]
            
        cursor.close()
        
        logger.info(f"Processed into {len(report_list)} unique lab reports.")
        return {
            "count": len(report_list),
            "lab_reports": report_list
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lab reports for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching lab reports: {str(e)}")
    finally:
        if db:
            db.close()



if __name__ == "__main__":
    import uvicorn
    import socket

    # Get the hostname and IP address
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    print(f"Starting server at http://{ip_address}:8821")
    uvicorn.run(app, host="0.0.0.0",port=8821)
