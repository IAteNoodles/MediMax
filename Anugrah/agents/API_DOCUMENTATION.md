# MediMax Multi-Agent Orchestration API

## 🚀 Overview

The MediMax Multi-Agent Orchestration API exposes your LangGraph-based multi-agent system as REST endpoints, allowing your backend server to integrate seamlessly with the intelligent medical assessment system using **natural language patient descriptions**.

## ✨ Key Features

- **🗣️ Natural Language Input**: Send free-form patient text instead of structured data
- **🧠 AI-Powered Data Extraction**: Groq LLM automatically extracts medical parameters from text
- **🤖 Multi-Agent Orchestration**: MainAgent → RouterAgent → ML Models → Medical Reports
- **📋 Comprehensive Reports**: Detailed medical assessments with recommendations
- **🔄 Flexible Integration**: Simple JSON API for easy backend integration

## 🏗️ Architecture

```
Backend Server → FastAPI → LangGraph Multi-Agent System → ML Models → Medical Reports
                   ↓
   Text Input → [MainAgent] → [RouterAgent] → [MCP Models] → [MedGemma]
              (Data Extraction)  (Model Routing)  (Predictions)   (Reports)
```

## 🔧 Setup & Installation

### 1. Install Dependencies
```bash
cd /home/anugrah-singh/Code/MediMax/Anugrah/agents
source .venv/bin/activate
pip install fastapi uvicorn requests
```

### 2. Set Environment Variables
```bash
export GROQ_API_KEY="your_actual_groq_api_key_here"
export MCP_BASE_URL="http://10.26.5.29:8000"
export MEDGEMMA_BASE_URL="http://10.26.5.29:11434"
export MEDIMAX_DEBUG="1"  # Optional: Enable debug mode
```

### 3. Start the API Server
```bash
python -m uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at:
- **API Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 📡 API Endpoints

### 1. Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agents_initialized": true,
  "services": {
    "mcp": "http://10.26.5.29:8000",
    "medgemma": "http://10.26.5.29:11434",
    "groq": "configured"
  }
}
```

### 2. Patient Assessment (Main Endpoint)

```http
POST /assess
Content-Type: application/json
```

**🆕 New Text-Based Request Format:**
```json
{
  "patient_text": "45-year-old male patient came in for routine check-up. He weighs 185 pounds and is 5'10\" tall. His blood pressure was measured at 140/90 mmHg. He has been smoking for 20 years and drinks alcohol occasionally. He doesn't exercise regularly. His cholesterol level is 240 mg/dL and blood glucose is 110 mg/dL. He has a family history of heart disease and is complaining of occasional chest pain and shortness of breath.",
  "query": "Assess cardiovascular risk for this patient",
  "additional_notes": "Patient seems concerned about family history of heart disease"
}
```

**✨ What Happens Automatically:**
1. **🧠 AI Data Extraction**: The MainAgent uses Groq LLM to extract structured medical parameters from the free-form text
2. **🔄 Intelligent Routing**: RouterAgent determines which ML models to invoke based on extracted data
3. **🏥 Model Execution**: Relevant medical risk models are called with structured parameters
4. **📋 Report Generation**: MedGemma generates comprehensive medical reports

**Response:**
```json
{
  "status": "complete",
  "need_more_data": false,
  "missing_parameters": [],
  "predictions": [
    {
      "model": "cardiovascular_risk",
      "prediction": null,
      "probability": null,
      "explanation": null,
      "raw": "Based on the provided data, the individual has a low risk of cardiovascular disease. However, recommendations include regular check-ups, preventive lifestyle changes, blood pressure management, and cholesterol management.",
      "error": "non_json_tool_output"
    }
  ],
  "report": "## Cardiovascular Risk Assessment Report\n\n**1. Patient Summary:**\n\nThe patient is a 45-year-old male presenting with a cardiovascular risk assessment. Key factors include elevated blood pressure (140/90 mmHg), elevated cholesterol (240 mg/dL), elevated glucose (110 mg/dL), and a history of smoking...\n\n**4. Recommendations:**\n\n* **Lifestyle Modifications:**\n    * **Smoking Cessation:** The patient should be strongly encouraged to quit smoking...",
  "follow_up_questions": [],
  "routing_explanation": "All required parameters are available for cardiovascular risk assessment.",
  "routing_summary": "A 45-year-old male with a history of hypertension, high cholesterol (240), and elevated glucose (110). He is a smoker and drinks alcohol, but is not physically active. Key risk factors include hypertension, high cholesterol, and smoking.",
  "action": "route_to_models",
  "debug_info": [
    "result_type: <class 'dict'>",
    "keys: ['status', 'action', 'missing_parameters', 'report', 'predictions', 'follow_up_questions', 'routing_explanation', 'routing_summary', 'need_more_data', 'debug_info']",
    "workflow: completed"
  ]
}
```

### 3. Request Format Details

#### Input Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patient_text` | string | ✅ Yes | Free-form patient information including history, symptoms, measurements, demographics, etc. |
| `query` | string | ✅ Yes | What kind of assessment is needed (e.g., "cardiovascular risk", "diabetes screening", "general health assessment") |
| `additional_notes` | string | ❌ No | Any additional context or specific concerns |

#### Example Patient Text Formats

**Cardiovascular Assessment:**
```
"45-year-old male, weight 185 lbs, height 5'10\", BP 140/90, smokes 1 pack/day, cholesterol 240, glucose 110, drinks socially, no regular exercise, family history of heart disease, occasional chest pain"
```

**Diabetes Screening:**
```
"62-year-old female, BMI 31, has high blood pressure, no heart disease, former smoker quit 5 years ago, HbA1c 6.8%, fasting glucose 125 mg/dL, family history of diabetes"
```

**General Assessment:**
```
"38-year-old non-smoking female athlete, normal weight, blood pressure 110/70, excellent cardiovascular fitness, no family history of chronic disease, routine wellness check"
```

### 4. Available Models Information

```http
GET /models
```

**Response:**
```json
{
  "available_models": {
    "cardiovascular_risk": {
      "required_parameters": ["age", "gender", "height", "weight", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active"],
      "description": "Cardiovascular disease risk prediction model",
      "tool": "Predict_Cardiovascular_Risk_With_Explanation"
    },
    "diabetes_risk": {
      "required_parameters": ["age", "gender", "hypertension", "heart_disease", "smoking_history", "bmi", "HbA1c_level", "blood_glucose_level"],
      "description": "Diabetes risk prediction model",
      "tool": "Predict_Diabetes_Risk_With_Explanation"
    }
  },
  "parameter_mappings": {
    "glucose": "gluc",
    "smoking": "smoke",
    "alcohol": "alco",
    "activity": "active"
  }
}
```

## 🔄 Integration Examples

### 1. Simple Text-Based Assessment

```python
import requests

def assess_patient_with_text(patient_description, assessment_type="cardiovascular risk"):
    """Assess patient using natural language description."""
    payload = {
        "patient_text": patient_description,
        "query": f"Assess {assessment_type}",
        "additional_notes": ""
    }
    
    response = requests.post(
        "http://localhost:8000/assess",
        json=payload,
        timeout=60  # LLM processing can take time
    )
    
    return response.json()

# Example usage with natural language
patient_description = """
45-year-old male patient came for routine check-up. 
Weight: 185 lbs, Height: 5'10"
Blood pressure: 140/90 mmHg
Smoking history: 20 years, 1 pack/day
Alcohol: occasionally on weekends
Exercise: sedentary lifestyle, no regular activity
Lab results: Cholesterol 240 mg/dL, Glucose 110 mg/dL
Family history: Father had heart attack at age 60
Current symptoms: Occasional chest pain, shortness of breath during stairs
"""

result = assess_patient_with_text(patient_description, "cardiovascular risk")

print(f"Status: {result['status']}")
print(f"Report: {result['report'][:200]}...")
```

### 2. Backend Server Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging

backend_app = FastAPI()

class PatientAssessmentRequest(BaseModel):
    patient_description: str
    assessment_type: str = "cardiovascular risk"
    additional_context: str = ""

class AssessmentResponse(BaseModel):
    success: bool
    assessment_complete: bool
    medical_report: str
    predictions: list
    recommendations: list
    error_message: str = ""

@backend_app.post("/medical-assessment", response_model=AssessmentResponse)
async def medical_assessment(request: PatientAssessmentRequest):
    """Process medical assessment using MediMax multi-agent system."""
    try:
        # Prepare request for MediMax agents
        medimax_payload = {
            "patient_text": request.patient_description,
            "query": f"Assess {request.assessment_type}",
            "additional_notes": request.additional_context
        }
        
        # Call MediMax API
        response = requests.post(
            "http://localhost:8000/assess",
            json=medimax_payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="MediMax API error")
            
        agent_result = response.json()
        
        # Extract recommendations from report
        recommendations = extract_recommendations(agent_result.get('report', ''))
        
        return AssessmentResponse(
            success=True,
            assessment_complete=agent_result['status'] == 'complete',
            medical_report=agent_result.get('report', ''),
            predictions=agent_result.get('predictions', []),
            recommendations=recommendations
        )
        
    except requests.exceptions.RequestException as e:
        logging.error(f"MediMax API request failed: {e}")
        return AssessmentResponse(
            success=False,
            assessment_complete=False,
            medical_report="",
            predictions=[],
            recommendations=[],
            error_message=f"Assessment service unavailable: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Assessment processing error: {e}")
        return AssessmentResponse(
            success=False,
            assessment_complete=False,
            medical_report="",
            predictions=[],
            recommendations=[],
            error_message=f"Internal processing error: {str(e)}"
        )

def extract_recommendations(report: str) -> list:
    """Extract recommendations from medical report."""
    recommendations = []
    if "Recommendations:" in report:
        # Simple extraction - you might want more sophisticated parsing
        rec_section = report.split("Recommendations:")[1].split("Follow-up:")[0]
        rec_items = [item.strip() for item in rec_section.split("*") if item.strip()]
        recommendations = rec_items[:10]  # Limit to top 10
    return recommendations
```

### 3. Real-world Integration Pattern

```python
class MediMaxService:
    """Service class for MediMax integration."""
    
    def __init__(self, api_base_url="http://localhost:8000"):
        self.api_base_url = api_base_url
        
    async def health_check(self):
        """Check if MediMax service is healthy."""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def assess_patient(self, patient_text: str, assessment_type: str = "general health"):
        """Perform patient assessment with retry logic."""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                payload = {
                    "patient_text": patient_text,
                    "query": f"Assess {assessment_type}",
                    "additional_notes": ""
                }
                
                response = requests.post(
                    f"{self.api_base_url}/assess",
                    json=payload,
                    timeout=120  # Longer timeout for LLM processing
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.warning(f"Assessment attempt {attempt + 1} failed: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logging.warning(f"Assessment attempt {attempt + 1} timed out")
                
            except Exception as e:
                logging.error(f"Assessment attempt {attempt + 1} error: {e}")
                
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return {"success": False, "error": "Assessment service unavailable after retries"}

# Usage in your application
medimax = MediMaxService()

patient_info = """
62-year-old female, BMI 28, hypertension controlled with medication,
no smoking history, family history of diabetes, HbA1c 6.5%, 
fasting glucose 115 mg/dL, reports increased thirst and frequent urination
"""

assessment = await medimax.assess_patient(patient_info, "diabetes risk")
```

## 🧪 Testing

### Using cURL

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Text-Based Assessment
```bash
# Cardiovascular risk assessment
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_text": "45-year-old male, weight 185 lbs, height 5 foot 10, BP 140/90, smokes, cholesterol 240, glucose 110, drinks alcohol occasionally, does not exercise",
    "query": "cardiovascular risk assessment",
    "additional_notes": "Patient concerned about family history"
  }'

# Diabetes screening  
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_text": "62-year-old female, BMI 31, has high blood pressure, former smoker, HbA1c 6.8%, fasting glucose 125 mg/dL, family history of diabetes",
    "query": "diabetes risk screening"
  }'
```

#### Using JSON File
```bash
# Create a test file
cat > patient_assessment.json << 'EOF'
{
  "patient_text": "38-year-old healthy female athlete, normal weight, blood pressure 110/70, non-smoker, excellent cardiovascular fitness, no chronic diseases, routine wellness check",
  "query": "general health assessment",
  "additional_notes": "Annual physical exam"
}
EOF

# Test the API
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d @patient_assessment.json
```

### Using Python Test Client

```bash
# Run the text-based test
python test_text_api.py

# Expected output format:
# ✅ Assessment successful!
# 📋 Status: complete
# 🎯 Action: route_to_models
# 🧠 Routing explanation: All required parameters are available...
# 📈 Predictions: [cardiovascular_risk model results]
# 📄 Medical report: ## Cardiovascular Risk Assessment Report...
```

## 🔍 Response Status Codes

- **200**: Success - Assessment completed or more data needed
- **400**: Bad Request - Invalid JSON or missing required fields
- **500**: Internal Server Error - Agent system or LLM processing failure
- **503**: Service Unavailable - Agents not initialized

## 🚦 Error Handling

The API returns structured error responses in the assessment format:

```json
{
  "status": "error",
  "need_more_data": false,
  "missing_parameters": [],
  "predictions": [],
  "report": null,
  "follow_up_questions": [],
  "routing_explanation": null,
  "routing_summary": null,
  "action": "error",
  "debug_info": ["error_type: ValidationError", "error: Request validation failed"]
}
```

Common error scenarios:
1. **Missing GROQ_API_KEY**: Agents won't initialize
2. **MCP service down**: Predictions will fail
3. **MedGemma service down**: Report generation will fail
4. **Invalid parameters**: Validation errors

## 🎯 Integration Benefits

1. **Stateless Operation**: Each request is independent
2. **Intelligent Routing**: LLM-based model selection
3. **Iterative Collection**: Handle missing parameters gracefully
4. **Debug Visibility**: Full execution transparency
5. **REST Standard**: Easy integration with any backend framework

## 🔧 Configuration

Environment variables:
- `GROQ_API_KEY`: Required for LLM agents
- `MCP_BASE_URL`: MCP service endpoint (default: http://10.26.5.29:8000)
- `MEDGEMMA_BASE_URL`: MedGemma service endpoint (default: http://10.26.5.29:11434)  
- `MEDIMAX_DEBUG`: Enable debug mode (set to "1")

## 📊 Performance Considerations

- **Timeout**: Default 60s for external service calls
- **Concurrency**: FastAPI handles concurrent requests
- **Caching**: Consider caching model specifications
- **Rate Limiting**: Implement if needed for production

## 🔒 Security (Production Considerations)

1. Add authentication/authorization
2. Input validation and sanitization
3. Rate limiting
4. HTTPS/TLS encryption
5. API key management
6. Request/response logging

## 🎉 Success

Your multi-agent orchestration system is now accessible as a REST API with **natural language processing capabilities**! Your backend server can:

✅ **Send free-form patient descriptions** instead of structured data  
✅ **AI-powered data extraction** using Groq LLM for medical parameter extraction  
✅ **Intelligent routing** to appropriate ML models based on available information  
✅ **Comprehensive medical assessments** with detailed reports and recommendations  
✅ **Flexible integration** with simple JSON API calls  
✅ **Debug transparency** with full workflow visibility  

## 🔬 Key Advantages

- **🗣️ Natural Language Interface**: No need to structure medical data—just describe the patient
- **🧠 AI Intelligence**: Groq LLM handles complex medical data extraction automatically
- **⚡ Streamlined Workflow**: One API call from text description to complete medical assessment
- **🏥 Production Ready**: Robust error handling, timeouts, and retry logic examples
- **📋 Comprehensive Output**: Risk predictions + detailed medical reports + recommendations

The LangGraph multi-agent system (**MainAgent** → **RouterAgent** → **MCP Models** → **MedGemma**) with AI-powered text processing is now fully exposed and ready for production backend integration!
