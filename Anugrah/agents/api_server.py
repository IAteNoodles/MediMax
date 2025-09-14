"""
FastAPI server to expose the MediMax multi-agent orchestration system.
Provides REST endpoints for backend integration.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uvicorn
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from medimax.graph import build_graph, GraphState
from medimax.util.specs_loader import ModelSpecs
from medimax.mcp.client import MCPClient
from medimax.llm.medgemma import MedGemmaClient
from medimax.llm.groq_client import GroqLLM

# Global variables for agents
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agents on startup and cleanup on shutdown."""
    try:
        print("🚀 Initializing MediMax multi-agent system...")
        
        # Configuration
        specs_path = 'medimax/specs/model_specs.yaml'
        mcp_url = os.getenv('MCP_BASE_URL', 'http://10.26.5.29:8000')
        medgemma_url = os.getenv('MEDGEMMA_BASE_URL', 'http://10.26.5.29:11434')
        
        # Build the graph with correct parameters
        graph = build_graph(
            specs_path=specs_path,
            mcp_url=mcp_url,
            medgemma_url=medgemma_url,
            use_groq=True
        )
        
        app_state['graph'] = graph
        app_state['specs_path'] = specs_path
        
        print("✅ Multi-agent system initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        raise
    
    yield
    
    # Cleanup
    try:
        print("🧹 Cleanup completed")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="MediMax Multi-Agent Orchestration API",
    description="REST API for medical risk assessment using LLM-based agent orchestration",
    version="1.0.0",
    lifespan=lifespan
)

# Request/Response models
class PatientData(BaseModel):
    """Patient data for medical assessment - accepts free-form text."""
    patient_text: str = Field(..., description="Free-form patient information including history, symptoms, measurements, etc.")
    query: str = Field(default="Assess medical risk", description="What kind of assessment is needed")
    
    # Optional: Allow some structured data if backend wants to provide it
    additional_notes: str = Field(default="", description="Any additional notes or context")

class PredictionResult(BaseModel):
    """Model prediction result."""
    model: str
    prediction: Optional[str] = None
    probability: Optional[float] = None
    explanation: Optional[str] = None
    raw: Optional[str] = None
    error: Optional[str] = None

class AssessmentResponse(BaseModel):
    """Response from the multi-agent assessment."""
    status: str = Field(..., description="Assessment status")
    need_more_data: bool = Field(..., description="Whether more patient data is needed")
    missing_parameters: List[str] = Field(default_factory=list, description="List of missing required parameters")
    
    predictions: List[PredictionResult] = Field(default_factory=list, description="Model predictions")
    report: Optional[str] = Field(None, description="Generated medical report")
    follow_up_questions: List[str] = Field(default_factory=list, description="Follow-up questions")
    
    routing_explanation: Optional[str] = Field(None, description="LLM routing decision explanation")
    routing_summary: Optional[str] = Field(None, description="Clinical summary from MainAgent")
    
    action: Optional[str] = Field(None, description="Agent action taken")
    debug_info: List[str] = Field(default_factory=list, description="Debug information (if enabled)")

class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    agents_initialized: bool
    services: Dict[str, str]

# API Endpoints

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        agents_initialized=bool(app_state.get('graph')),
        services={
            "mcp": os.getenv('MCP_BASE_URL', 'http://10.26.5.29:8000'),
            "medgemma": os.getenv('MEDGEMMA_BASE_URL', 'http://10.26.5.29:11434'),
            "groq": "configured" if os.getenv('GROQ_API_KEY') else "missing"
        }
    )

@app.post("/assess", response_model=AssessmentResponse)
async def assess_patient(data: PatientData) -> AssessmentResponse:
    """Assess patient using multi-agent system with text-based input."""
    try:
        graph = app_state.get('graph')
        if not graph:
            raise HTTPException(status_code=500, detail="Agent system not initialized")
        
        print(f"[API] Received assessment request")
        print(f"[API] Patient text: {data.patient_text[:200]}...")
        print(f"[API] Query: {data.query}")
        
        # Convert to dict format for agent system
        payload_data = {
            "patient_text": data.patient_text,
            "query": data.query,
            "additional_notes": data.additional_notes
        }
        
        # Create GraphState input format
        graph_input = {"payload": payload_data}
        
        # Run the multi-agent workflow
        result_state = await graph.ainvoke(graph_input)
        
        # Extract result from state
        if hasattr(result_state, 'result'):
            result = result_state.result
        elif isinstance(result_state, dict) and 'result' in result_state:
            result = result_state['result']
        else:
            result = result_state
        
        print(f"[API] Agent system result type: {type(result)}")
        print(f"[API] Agent system result: {result}")
        
        # Handle different result formats and convert to AssessmentResponse format
        if isinstance(result, dict):
            return AssessmentResponse(
                status=result.get('status', 'completed'),
                need_more_data=result.get('need_more_data', False),
                missing_parameters=result.get('missing_parameters', []),
                predictions=result.get('predictions', []),
                report=result.get('report'),
                follow_up_questions=result.get('follow_up_questions', []),
                routing_explanation=result.get('routing_explanation'),
                routing_summary=result.get('routing_summary'),
                action=result.get('action'),
                debug_info=[f"result_type: {type(result)}", f"keys: {list(result.keys()) if hasattr(result, 'keys') else []}", "workflow: completed"]
            )
        else:
            return AssessmentResponse(
                status='completed',
                need_more_data=False,
                missing_parameters=[],
                predictions=[],
                report=str(result),
                follow_up_questions=[],
                routing_explanation=None,
                routing_summary=None,
                action='complete',
                debug_info=[f"result_type: {type(result)}", f"raw_result: {str(result)}", "workflow: completed"]
            )
            
    except Exception as e:
        print(f"[API ERROR] Assessment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return AssessmentResponse(
            status='error',
            need_more_data=False,
            missing_parameters=[],
            predictions=[],
            report=None,
            follow_up_questions=[],
            routing_explanation=None,
            routing_summary=None,
            action='error',
            debug_info=[f"error_type: {type(e).__name__}", f"error: {str(e)}"]
        )

@app.post("/assess/cardiovascular", response_model=AssessmentResponse)
async def assess_cardiovascular_risk(patient_data: PatientData):
    """
    Specialized endpoint for cardiovascular risk assessment.
    Adds specific routing hint for cardiovascular models.
    """
    
    # Add cardiovascular-specific context to the query
    enhanced_data = patient_data.model_copy()
    enhanced_data.query = f"Cardiovascular risk assessment: {enhanced_data.query}"
    
    return await assess_patient(enhanced_data)

@app.post("/assess/diabetes", response_model=AssessmentResponse)
async def assess_diabetes_risk(patient_data: PatientData):
    """
    Specialized endpoint for diabetes risk assessment.
    Adds specific routing hint for diabetes models.
    """
    
    # Add diabetes-specific context to the query
    enhanced_data = patient_data.model_copy()
    enhanced_data.query = f"Diabetes risk assessment: {enhanced_data.query}"
    
    return await assess_patient(enhanced_data)

@app.get("/models", response_model=Dict[str, Any])
async def get_available_models():
    """Get information about available models and their requirements."""
    
    if 'specs_path' not in app_state:
        raise HTTPException(status_code=503, detail="Model specifications not loaded")
    
    try:
        # Load specs to get model information
        specs = ModelSpecs(app_state['specs_path'])
        
        # Extract model information
        models_info = {}
        for model in specs.models:
            model_name = model.get('name')
            if model_name:
                models_info[model_name] = {
                    'required_parameters': model.get('parameters', []),
                    'description': model.get('description', f'{model_name} prediction model'),
                    'tool': model.get('tool', 'Unknown')
                }
    except Exception as e:
        # Fallback information if specs loading fails
        models_info = {
            'cardiovascular_risk': {
                'required_parameters': ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active'],
                'description': 'Cardiovascular disease risk prediction model',
                'tool': 'Predict_Cardiovascular_Risk_With_Explanation'
            },
            'diabetes_risk': {
                'required_parameters': ['age', 'gender', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level'],
                'description': 'Diabetes risk prediction model', 
                'tool': 'Predict_Diabetes_Risk_With_Explanation'
            }
        }
    
    return {
        'available_models': models_info,
        'parameter_mappings': {
            'glucose': 'gluc',
            'smoking': 'smoke',
            'alcohol': 'alco',
            'activity': 'active'
        }
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )

if __name__ == "__main__":
    # Check if GROQ_API_KEY is loaded from .env
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key:
        print("❌ GROQ_API_KEY not found in environment or .env file!")
        print("   Please check your .env file contains: GROQ_API_KEY=your_key_here")
        exit(1)
    else:
        print(f"✅ GROQ_API_KEY loaded: {groq_key[:10]}...{groq_key[-4:]}")
    
    # Enable debug mode if requested
    if os.getenv('MEDIMAX_DEBUG') == '1':
        print("🐛 Debug mode enabled")
    
    print("🌐 Starting MediMax Multi-Agent API Server...")
    print(f"📍 MCP Service: {os.getenv('MCP_BASE_URL', 'http://10.26.5.29:8000')}")
    print(f"📍 MedGemma Service: {os.getenv('MEDGEMMA_BASE_URL', 'http://10.26.5.29:11434')}")
    print("🚀 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
