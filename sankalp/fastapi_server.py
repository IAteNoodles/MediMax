"""
FastAPI Server for Cypher Query Generation
This server provides a REST API endpoint to generate Cypher queries from natural language
using Google's Gemini API with async capabilities.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import httpx
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv()

# Import cypher module after loading environment
from cypher import CypherQueryGenerator, generate_cypher_from_text

# Try multiple chat implementations in order of preference
try:
    from optimized_chat import chat_with_documents
    print("✅ Using optimized RAG pipeline with smallest PDFs")
except Exception as e:
    print(f"⚠️  Optimized RAG pipeline failed to load: {e}")
    try:
        from chat import chat_with_documents
        print("✅ Using regular RAG pipeline")
    except Exception as e2:
        print(f"⚠️  Regular RAG pipeline failed to load: {e2}")
        try:
            from fallback_chat import fallback_chat_with_documents as chat_with_documents
            print("✅ Using fallback chat system (no embeddings)")
        except Exception as e3:
            print(f"⚠️  Fallback chat failed to load: {e3}")
            print("📝 Using mock RAG pipeline for testing")
            from mock_chat import mock_chat_with_documents as chat_with_documents

# Pydantic models for request/response validation
class QueryRequest(BaseModel):
    query: str
    db_schema: Optional[str] = ""
    context: Optional[str] = ""

class SimpleQueryRequest(BaseModel):
    query: str

class SchemaRequest(BaseModel):
    db_schema: str

class CypherValidationRequest(BaseModel):
    cypher: str

class ChatRequest(BaseModel):
    patient_id: str
    message: str

class ChatResponse(BaseModel):
    patient_id: str
    message: str
    reply: str

class KnowledgeBaseRequest(BaseModel):
    message: str

class KnowledgeBaseResponse(BaseModel):
    message: str
    cypher_query: str
    data: dict

class CypherResponse(BaseModel):
    success: bool
    cypher_query: str
    is_valid: bool
    original_query: str
    schema_used: bool
    context_used: bool

class ErrorResponse(BaseModel):
    success: bool
    error: str
    type: Optional[str] = None

class SuccessResponse(BaseModel):
    success: bool
    message: str

class ValidationResponse(BaseModel):
    success: bool
    is_valid: bool
    cypher_query: str

class HealthResponse(BaseModel):
    status: str
    message: str
    endpoints: dict

# Initialize FastAPI app
app = FastAPI(
    title="Cypher Query Generator API",
    description="Generate Neo4j Cypher queries from natural language using Google Gemini",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Cypher generator
try:
    cypher_generator = CypherQueryGenerator()
except Exception as e:
    print(f"Warning: Could not initialize Cypher generator: {e}")
    cypher_generator = None

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Cypher Query Generator API is running",
        endpoints={
            "health": "GET /",
            "generate_cypher": "POST /generate_cypher",
            "generate_simple": "POST /generate_simple",
            "set_schema": "POST /set_schema",
            "validate_cypher": "POST /validate_cypher",
            "chat": "POST /chat",
            "kb": "POST /kb",
            "docs": "GET /docs",
            "redoc": "GET /redoc"
        }
    )

@app.post("/generate_cypher")
async def generate_cypher(request: QueryRequest):
    """
    Generate Cypher query from natural language with full features
    
    - **query**: Natural language query (required)
    - **db_schema**: Neo4j database schema information (optional, uses medical schema by default)
    - **context**: Additional context for query generation (optional)
    """
    try:
        # Validate that generator is available
        if not cypher_generator:
            raise HTTPException(
                status_code=500,
                detail="Cypher generator not initialized. Check GEMINI_API_KEY."
            )
        
        # Default medical schema
        default_schema = """
Node Labels: Appointment, Condition, DiagnosticStudy, Encounter, LabFinding, LabReport, LabResult, LabStudy, LabTest, MedicalHistory, Medication, Observation, Patient, Patients, Person, Symptom, TestResult, Treatment

Relationship Types: CONTAINS_FINDING, CONTAINS_RESULT, DOCUMENTED_SYMPTOM, HAS_APPOINTMENT, HAS_CONDITION, HAS_ENCOUNTER, HAS_LAB_FINDING, HAS_LAB_REPORT, HAS_LAB_RESULT, HAS_LAB_STUDY, HAS_MEDICAL_HISTORY, HAS_SYMPTOM, INDICATES_CONDITION, MAY_INDICATE, REPORTED_SYMPTOM, TAKES_MEDICATION, TREATS_CONDITION

Property Keys: abnormal, abnormal_flag, age, appointment_date, appointment_id, appointment_time, appointment_type, benefit, category, city, clinical_notes, clinical_significance, complexity_score, condition_category, condition_name, condition_treated, condition_type, confidence, created_at, data, date, description, details, diagnosis_date, discontinued_date, dob, doctor, doctor_name, documented_by, dosage, dose, drug_name, duration, efficacy, encounter_date, encounter_status, encounter_type, entity_type, facility, flag, focus, frequency, full_name, gender, graph_center, historical, history_date, history_details, history_id, history_item, history_type, id, indication, interpretation, is_abnormal, is_active, is_chronic, is_continued, item, lab_date, lab_facility, lab_finding_id, lab_report_id, lab_type, last_updated, mechanism, medication_id, medicine_name, name, node_type, nodeld, nodes, normal_range, Object, observation_date, observation_name, observation_type, occupation, onset_date, onset_pattern, onset_type, ordering_doctor, ordering_provider, patient_id, prescribed_by, prescribed_date, prescriber, prescription_date, progression_time, properties, provider, reference_range, Relation, relationship_type, relationships, remarks, reported_date, result_date, result_name, result_sequence, result_status, result_type, result_value, risk_level, role, route, severity, sex, since, source_id, specialty, start_date, status, study_category, study_date, study_name, study_type, style, Subject, symptom_id, symptom_name, system, target, target_id, test_date, test_name, test_unit, test_value, time, trend, type, unit, value, visit_type, visualisation
"""
        
        # Set schema info - use provided schema or default medical schema
        schema_to_use = request.db_schema if request.db_schema else default_schema
        cypher_generator.set_schema_info(schema_to_use)
        
        # Generate the Cypher query
        cypher_query = cypher_generator.generate_cypher_query(request.query, request.context)
        
        # Validate the generated query
        is_valid = cypher_generator.validate_cypher_syntax(cypher_query)
        
        return CypherResponse(
            success=True,
            cypher_query=cypher_query,
            is_valid=is_valid,
            original_query=request.query,
            schema_used=True,  # Always true now since we use default or provided schema
            context_used=bool(request.context)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating Cypher query: {str(e)}"
        )

@app.post("/generate_simple")
async def generate_simple(request: SimpleQueryRequest):
    """
    Simple endpoint that accepts just a query string and returns plain text Cypher
    
    - **query**: Natural language query
    """
    try:
        # Use the simple function
        cypher_query = generate_cypher_from_text(request.query)
        return cypher_query
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating query: {str(e)}"
        )

@app.post("/set_schema", response_model=SuccessResponse)
async def set_schema(request: SchemaRequest):
    """
    Set the database schema for better query generation
    
    - **db_schema**: Neo4j database schema information
    """
    try:
        if not cypher_generator:
            raise HTTPException(
                status_code=500,
                detail="Cypher generator not initialized"
            )
        
        cypher_generator.set_schema_info(request.db_schema)
        
        return SuccessResponse(
            success=True,
            message="Schema updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error setting schema: {str(e)}"
        )

@app.post("/validate_cypher", response_model=ValidationResponse)
async def validate_cypher(request: CypherValidationRequest):
    """
    Validate Cypher query syntax
    
    - **cypher**: Cypher query to validate
    """
    try:
        if not cypher_generator:
            raise HTTPException(
                status_code=500,
                detail="Cypher generator not initialized"
            )
        
        is_valid = cypher_generator.validate_cypher_syntax(request.cypher)
        
        return ValidationResponse(
            success=True,
            is_valid=is_valid,
            cypher_query=request.cypher
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating query: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat with RAG pipeline using medical documents
    
    - **patient_id**: Unique identifier for the patient
    - **message**: User's message/question
    """
    try:
        # Generate response using RAG pipeline
        reply = chat_with_documents(request.message, request.patient_id)
        
        return ChatResponse(
            patient_id=request.patient_id,
            message=request.message,
            reply=reply
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

@app.post("/kb", response_model=KnowledgeBaseResponse)
async def knowledge_base_query(request: KnowledgeBaseRequest):
    """
    Knowledge Base Query endpoint - converts natural language to Cypher and executes it
    
    - **message**: Natural language query to convert to Cypher and execute
    """
    try:
        # Validate that cypher generator is available
        if not cypher_generator:
            raise HTTPException(
                status_code=500,
                detail="Cypher generator not initialized. Check GEMINI_API_KEY."
            )
        
        # Generate Cypher query from natural language
        cypher_query = cypher_generator.generate_cypher_query(request.message)
        logger.info(f"Generated Cypher query: {cypher_query}")
        
        # Validate the generated query
        is_valid = cypher_generator.validate_cypher_syntax(cypher_query)
        logger.info(f"Cypher query validation result: {is_valid}")
        
        if not is_valid:
            logger.error(f"Invalid Cypher query generated: {cypher_query}")
            raise HTTPException(
                status_code=400,
                detail=f"Generated invalid Cypher query: {cypher_query}"
            )
        
        # Send Cypher query to external endpoint
        external_endpoint = "http://10.26.5.29:8420/run_cypher_query"
        logger.info(f"Sending request to external endpoint: {external_endpoint}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Prepare the payload for the external service with correct parameter name
                payload = {
                    "cypher_query": f"{cypher_query}"  # Added double quotes around the cypher query
                }
                logger.info(f"Request payload: {payload}")
                
                # Send POST request to external endpoint
                response = await client.post(external_endpoint, json=payload)
                logger.info(f"External service response status: {response.status_code}")
                logger.info(f"External service response headers: {response.headers}")
                
                response.raise_for_status()
                
                # Get the response data
                external_data = response.json()
                logger.info(f"External service response data: {external_data}")
                
                return KnowledgeBaseResponse(
                    message=request.message,
                    cypher_query=cypher_query,
                    data=external_data
                )
                
            except httpx.TimeoutException as e:
                logger.error(f"Timeout connecting to external service: {e}")
                raise HTTPException(
                    status_code=504,
                    detail="Timeout while connecting to knowledge base service"
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from external service: {e.response.status_code} - {e.response.text}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Knowledge base service returned error: {e.response.status_code} - {e.response.text}"
                )
            except httpx.RequestError as e:
                logger.error(f"Request error to external service: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Failed to connect to knowledge base service: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Unexpected error during external request: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected error while communicating with knowledge base service: {str(e)}"
                )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in knowledge base endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing knowledge base query: {str(e)}"
        )

# Custom error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "available_endpoints": [
                "GET /",
                "POST /generate_cypher",
                "POST /generate_simple", 
                "POST /set_schema",
                "POST /validate_cypher",
                "POST /chat",
                "POST /kb",
                "GET /docs",
                "GET /redoc"
            ]
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong on the server"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Configuration
    host = os.getenv('FASTAPI_HOST', '0.0.0.0')  # Changed to 0.0.0.0 for network access
    port = int(os.getenv('FASTAPI_PORT', 8000))
    reload = os.getenv('FASTAPI_RELOAD', 'False').lower() == 'true'
    
    print(f"Starting Cypher Query Generator FastAPI Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    
    if not os.getenv('GEMINI_API_KEY'):
        print("WARNING: GEMINI_API_KEY not set. The server will start but API calls will fail.")
    
    print("\nAvailable endpoints:")
    print("- GET  /                 - Health check")
    print("- POST /generate_cypher  - Generate Cypher query (detailed)")
    print("- POST /generate_simple  - Generate Cypher query (simple)")
    print("- POST /set_schema       - Set database schema")
    print("- POST /validate_cypher  - Validate Cypher syntax")
    print("- POST /chat             - Chat with medical RAG pipeline")
    print("- POST /kb               - Knowledge base query (NL to Cypher)")
    print("- GET  /docs             - Interactive API documentation")
    print("- GET  /redoc            - Alternative API documentation")
    
    uvicorn.run(
        "fastapi_server:app",
        host=host,
        port=port,
        reload=reload
    )