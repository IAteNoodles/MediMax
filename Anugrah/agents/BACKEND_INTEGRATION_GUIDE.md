# 🌐 MediMax Multi-Agent API - Backend Integration Guide

## 🚀 Network-Accessible API Endpoints

Your MediMax Multi-Agent System is now running on **all network interfaces** and accessible from any machine on your network.

### 📡 Base URLs

```
Local Access:     http://localhost:8000
Network Access:   http://YOUR_MACHINE_IP:8000
```

*Replace `YOUR_MACHINE_IP` with your actual machine's IP address*

## 🔗 Available Endpoints

### 1. Health Check Endpoint
```http
GET /health
```

**Purpose**: Check if the multi-agent system is running and initialized

**Example Request**:
```bash
curl http://YOUR_MACHINE_IP:8000/health
```

**Response**:
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

### 2. Patient Assessment Endpoint (Main)
```http
POST /assess
Content-Type: application/json
```

**Purpose**: Perform intelligent medical assessment using natural language patient descriptions

#### Request Format

```json
{
  "patient_text": "STRING - Free-form patient description (REQUIRED)",
  "query": "STRING - Type of assessment needed (REQUIRED)",
  "additional_notes": "STRING - Optional additional context"
}
```

#### Request Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `patient_text` | string | ✅ **YES** | Natural language patient description including demographics, symptoms, measurements, history | `"45-year-old male, weight 185 lbs, height 5'10\", BP 140/90, smoker, cholesterol 240"` |
| `query` | string | ✅ **YES** | Assessment type or medical question | `"cardiovascular risk assessment"`, `"diabetes screening"`, `"general health check"` |
| `additional_notes` | string | ❌ No | Extra context or specific concerns | `"Patient concerned about family history"` |

#### Example Requests

**Cardiovascular Risk Assessment**:
```json
{
  "patient_text": "45-year-old male, weight 185 lbs, height 5 foot 10, BP 140/90, smokes 1 pack/day for 20 years, cholesterol 240 mg/dL, glucose 110 mg/dL, drinks alcohol occasionally, no regular exercise, family history of heart disease, occasional chest pain",
  "query": "cardiovascular risk assessment",
  "additional_notes": "Patient very concerned about recent chest pains"
}
```

**Diabetes Screening**:
```json
{
  "patient_text": "62-year-old female, BMI 31, has high blood pressure controlled with medication, former smoker quit 5 years ago, HbA1c 6.8%, fasting glucose 125 mg/dL, family history of diabetes, reports increased thirst and frequent urination",
  "query": "diabetes risk screening",
  "additional_notes": "Recent symptoms suggest possible diabetes"
}
```

**General Health Assessment**:
```json
{
  "patient_text": "38-year-old healthy female athlete, normal weight, blood pressure 110/70, non-smoker, excellent cardiovascular fitness, no chronic diseases, regular exercise 5x/week",
  "query": "general health assessment",
  "additional_notes": "Annual physical exam"
}
```

#### Response Format

```json
{
  "status": "complete|need_more_data|error",
  "need_more_data": false,
  "missing_parameters": [],
  "predictions": [
    {
      "model": "cardiovascular_risk|diabetes_risk",
      "prediction": "RISK_LEVEL or null",
      "probability": "NUMERIC_PROBABILITY or null", 
      "explanation": "MODEL_EXPLANATION or null",
      "raw": "RAW_MODEL_OUTPUT",
      "error": "ERROR_MESSAGE or null"
    }
  ],
  "report": "COMPREHENSIVE_MEDICAL_REPORT_IN_MARKDOWN",
  "follow_up_questions": ["QUESTION_1", "QUESTION_2"],
  "routing_explanation": "LLM_ROUTING_DECISION_EXPLANATION",
  "routing_summary": "CLINICAL_SUMMARY_OF_PATIENT",
  "action": "route_to_models|need_more_data|complete|error",
  "debug_info": ["DEBUG_MESSAGE_1", "DEBUG_MESSAGE_2"]
}
```

### 3. Available Models Information
```http
GET /models
```

**Purpose**: Get information about available ML models and their requirements

**Response**:
```json
{
  "available_models": {
    "cardiovascular_risk": {
      "required_parameters": ["age", "gender", "height", "weight", "ap_hi", "ap_lo", "cholesterol", "gluc", "smoke", "alco", "active"],
      "description": "Cardiovascular disease risk prediction model"
    },
    "diabetes_risk": {
      "required_parameters": ["age", "gender", "hypertension", "heart_disease", "smoking_history", "bmi", "HbA1c_level", "blood_glucose_level"],
      "description": "Diabetes risk prediction model"
    }
  }
}
```

## 🔌 Backend Integration Examples

### Node.js/Express Integration

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const MEDIMAX_API_BASE = 'http://YOUR_MACHINE_IP:8000';

// Health check endpoint
app.get('/api/health', async (req, res) => {
  try {
    const response = await axios.get(`${MEDIMAX_API_BASE}/health`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'MediMax service unavailable' });
  }
});

// Patient assessment endpoint
app.post('/api/assess-patient', async (req, res) => {
  try {
    const { patientDescription, assessmentType, notes } = req.body;
    
    const payload = {
      patient_text: patientDescription,
      query: assessmentType || 'general health assessment',
      additional_notes: notes || ''
    };
    
    const response = await axios.post(`${MEDIMAX_API_BASE}/assess`, payload, {
      timeout: 60000, // 60 second timeout for LLM processing
      headers: { 'Content-Type': 'application/json' }
    });
    
    res.json({
      success: true,
      assessment: response.data
    });
    
  } catch (error) {
    console.error('Assessment error:', error.message);
    res.status(500).json({
      success: false,
      error: 'Assessment failed',
      details: error.response?.data || error.message
    });
  }
});

app.listen(3000, () => {
  console.log('Backend server running on port 3000');
});
```

### Python/FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import asyncio

app = FastAPI()

MEDIMAX_API_BASE = "http://YOUR_MACHINE_IP:8000"

class AssessmentRequest(BaseModel):
    patient_description: str
    assessment_type: str = "general health assessment"
    notes: str = ""

@app.get("/api/health")
async def health_check():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{MEDIMAX_API_BASE}/health", timeout=10)
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail="MediMax service unavailable")

@app.post("/api/assess-patient")
async def assess_patient(request: AssessmentRequest):
    payload = {
        "patient_text": request.patient_description,
        "query": request.assessment_type,
        "additional_notes": request.notes
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{MEDIMAX_API_BASE}/assess",
                json=payload,
                timeout=60.0  # 60 second timeout
            )
            
            return {
                "success": True,
                "assessment": response.json()
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Assessment failed: {str(e)}"
            )
```

### PHP Integration

```php
<?php
class MediMaxAPI {
    private $baseUrl;
    
    public function __construct($baseUrl = 'http://YOUR_MACHINE_IP:8000') {
        $this->baseUrl = $baseUrl;
    }
    
    public function healthCheck() {
        return $this->makeRequest('GET', '/health');
    }
    
    public function assessPatient($patientText, $query, $additionalNotes = '') {
        $payload = [
            'patient_text' => $patientText,
            'query' => $query,
            'additional_notes' => $additionalNotes
        ];
        
        return $this->makeRequest('POST', '/assess', $payload);
    }
    
    private function makeRequest($method, $endpoint, $data = null) {
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->baseUrl . $endpoint,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 60,
            CURLOPT_CUSTOMREQUEST => $method,
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
            CURLOPT_POSTFIELDS => $data ? json_encode($data) : null
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception("API request failed with code: $httpCode");
        }
        
        return json_decode($response, true);
    }
}

// Usage example
$medimax = new MediMaxAPI();

try {
    $assessment = $medimax->assessPatient(
        "45-year-old male, BP 140/90, smoker, cholesterol 240",
        "cardiovascular risk assessment",
        "Patient concerned about chest pains"
    );
    
    echo json_encode($assessment, JSON_PRETTY_PRINT);
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
?>
```

## 🧪 Testing Your Integration

### Quick Test Commands

```bash
# Replace YOUR_MACHINE_IP with your actual IP address

# Health check
curl http://YOUR_MACHINE_IP:8000/health

# Simple assessment
curl -X POST http://YOUR_MACHINE_IP:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_text": "45-year-old male, weight 185 lbs, BP 140/90, smoker",
    "query": "cardiovascular risk assessment"
  }'

# Full assessment with notes
curl -X POST http://YOUR_MACHINE_IP:8000/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_text": "62-year-old female, BMI 31, hypertension, former smoker, HbA1c 6.8%, glucose 125",
    "query": "diabetes risk screening",
    "additional_notes": "Recent symptoms suggest diabetes"
  }'
```

## 🚦 Error Handling

### HTTP Status Codes
- **200**: Success - Request completed
- **400**: Bad Request - Invalid JSON or missing fields
- **500**: Internal Server Error - Processing failure
- **503**: Service Unavailable - Agents not initialized

### Error Response Format
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
  "debug_info": ["error_type: ValidationError", "error: Details..."]
}
```

## 🔒 Production Recommendations

1. **Add Authentication**: Implement API keys or JWT tokens
2. **Rate Limiting**: Prevent API abuse
3. **HTTPS**: Use SSL/TLS in production
4. **Monitoring**: Log requests and monitor performance
5. **Load Balancing**: Scale horizontally if needed
6. **Firewall**: Restrict network access as needed

## 📊 Performance Notes

- **Typical Response Time**: 5-15 seconds (includes LLM processing)
- **Timeout Recommendation**: Set client timeouts to 60+ seconds
- **Concurrent Requests**: Server handles multiple concurrent assessments
- **Rate Limiting**: Consider implementing based on your needs

Your MediMax Multi-Agent API is now ready for production backend integration! 🚀
