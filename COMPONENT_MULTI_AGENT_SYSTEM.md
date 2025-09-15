# MediMax Multi-Agent Orchestration - LLM-Powered Clinical Intelligence

## 🤖 Overview

The Multi-Agent Orchestration system (`Anugrah/agents`) represents the cognitive layer of MediMax, implementing LLM-based intelligent agents that coordinate medical assessments, risk predictions, and clinical decision-making. Built on LangGraph with Groq's LLaMA-3.1-8B model, this system provides human-like reasoning for complex healthcare scenarios.

## 🎯 Core Responsibilities

- **Intelligent Medical Assessment**: LLM-powered analysis of patient data and clinical context
- **Multi-Agent Coordination**: Orchestrated decision-making between specialized medical agents
- **Clinical Routing**: Smart selection of appropriate AI models based on patient context
- **Medical Report Generation**: AI-generated comprehensive medical assessments
- **Risk Stratification**: Intelligent risk assessment with explanatory reasoning

## 🏗️ Architecture

### Agent System Architecture
```
┌─────────────────────────────────────┐
│        Frontend Interfaces          │
│  React App | Streamlit Demo UI      │
└─────────────────┬───────────────────┘
                  │ HTTP REST API
┌─────────────────▼───────────────────┐
│         Agent API Server            │
│          (port 8001)                │
│                                     │
│ ├── FastAPI Endpoints              │
│ ├── Request Validation             │
│ ├── Response Formatting            │
│ └── Error Handling                 │
└─────────────────┬───────────────────┘
                  │ LangGraph State
┌─────────────────▼───────────────────┐
│       LangGraph Orchestration       │
│                                     │
│ ├── GraphState Management          │
│ ├── Agent Transitions              │
│ ├── Workflow Coordination          │
│ └── State Persistence              │
└─────────────────┬───────────────────┘
                  │ Agent Communication
┌─────────────────▼───────────────────┐
│          Main Agent                 │
│     (LLM: Groq LLaMA-3.1-8B)       │
│                                     │
│ ├── Clinical Context Analysis      │
│ ├── Data Completeness Assessment   │
│ ├── Orchestration Decisions        │
│ └── Medical Reasoning              │
└─────────────────┬───────────────────┘
                  │ Clinical Routing
┌─────────────────▼───────────────────┐
│         Router Agent                │
│     (LLM: Groq LLaMA-3.1-8B)       │
│                                     │
│ ├── Model Selection Logic          │
│ ├── Parameter Validation           │
│ ├── Multi-Model Coordination       │
│ └── Result Synthesis               │
└─────────────────┬───────────────────┘
                  │ External Calls
┌─────────────────▼───────────────────┐
│       External Services             │
│                                     │
│ ├── MCP Chat Interface             │
│ ├── MedGemma Report Generation      │
│ ├── Cardiovascular Prediction      │
│ └── Diabetes Risk Assessment       │
└─────────────────────────────────────┘
```

### Technology Stack
- **Agent Framework**: LangGraph for state-based orchestration
- **LLM Provider**: Groq API with LLaMA-3.1-8B-Instant model
- **API Framework**: FastAPI for REST endpoints
- **State Management**: Persistent graph state across agent interactions
- **Medical AI**: MedGemma for medical report generation
- **Model Integration**: MCP protocol for prediction services

## 🧠 Agent Intelligence System

### Main Agent (`MainAgent`)

The MainAgent serves as the orchestration intelligence, making high-level decisions about patient assessment workflows.

#### Core Responsibilities
```python
class MainAgent:
    """LLM-powered orchestration agent for medical assessments"""
    
    def analyze_patient_context(self, patient_data: dict) -> dict:
        """
        Analyze patient data using LLM reasoning
        - Clinical context understanding
        - Data completeness assessment
        - Risk factor identification
        - Orchestration strategy selection
        """
        
    def make_orchestration_decision(self, context: dict) -> str:
        """
        LLM-based decision making for workflow routing
        Returns: "route_to_models" | "need_more_data" | "complete"
        """
```

#### LLM Decision Making Process
```yaml
LLM Analysis Prompt:
  Context: "55-year-old male with hypertension, chest pain symptoms"
  Task: "Determine appropriate medical assessment workflow"
  
LLM Reasoning:
  - "Patient presents cardiovascular risk factors"
  - "Blood pressure and symptom data available"
  - "Sufficient data for cardiovascular risk assessment"
  - "Route to specialized models for prediction"
  
Decision Output:
  action: "route_to_models"
  reasoning: "Patient has sufficient cardiovascular parameters..."
  next_agent: "RouterAgent"
```

### Router Agent (`RouterAgent`)

The RouterAgent provides specialized clinical routing and model coordination based on LLM analysis of medical requirements.

#### Clinical Intelligence
```python
class RouterAgent:
    """LLM-powered clinical routing and model coordination"""
    
    def evaluate_model_requirements(self, patient_data: dict, models: dict) -> dict:
        """
        LLM analysis of model requirements vs available data
        - Parameter gap analysis
        - Clinical relevance assessment
        - Model selection reasoning
        """
        
    def coordinate_model_invocations(self, selected_models: list) -> dict:
        """
        Intelligent model invocation with clinical context
        - Sequential vs parallel execution
        - Parameter optimization
        - Result synthesis
        """
```

#### Model Selection Logic
```yaml
LLM Clinical Routing:
  Input: 
    patient_context: "Diabetes family history, elevated glucose"
    available_parameters: ["age", "bmi", "glucose_level", "family_history"]
    model_requirements:
      cardiovascular: ["age", "bp_systolic", "bp_diastolic", "cholesterol"]
      diabetes: ["age", "bmi", "glucose_level", "hba1c_level"]
  
  LLM Analysis:
    - "Missing BP and cholesterol for cardiovascular model"
    - "Has key parameters for diabetes assessment"
    - "Family history indicates diabetes focus appropriate"
  
  Decision:
    selected_models: ["diabetes_risk"]
    reasoning: "Sufficient diabetes parameters, missing cardio data"
    next_actions: ["invoke_diabetes_model", "generate_medical_report"]
```

## 📊 LangGraph State Management

### GraphState Schema
```python
class GraphState(TypedDict):
    """Comprehensive state for multi-agent coordination"""
    
    # Input Data
    payload: Dict[str, Any]              # Original patient data
    
    # Analysis Results
    status: str                          # "need_more_data" | "route_to_models" | "complete"
    action: str                          # Current workflow action
    
    # Clinical Context
    missing_parameters: List[str]        # Required but missing data points
    clinical_context: str                # LLM-generated clinical summary
    
    # Model Coordination
    predictions: List[Dict[str, Any]]    # AI model prediction results
    model_explanations: Dict[str, str]   # SHAP and model explanations
    
    # Medical Intelligence
    report: str                          # Generated medical assessment
    follow_up_questions: List[str]       # Clinical follow-up recommendations
    
    # Agent Reasoning
    routing_explanation: str             # LLM reasoning for decisions
    routing_summary: str                 # Clinical context summary
    
    # Workflow Management
    result: Optional[Dict[str, Any]]     # Final assessment result
```

### State Transitions
```python
def build_graph() -> StateGraph:
    """Build LangGraph workflow with agent transitions"""
    
    workflow = StateGraph(GraphState)
    
    # Agent Nodes
    workflow.add_node("main_agent", main_agent_node)
    workflow.add_node("router_agent", router_agent_node)
    workflow.add_node("end", end_node)
    
    # Conditional Transitions
    workflow.add_conditional_edges(
        "main_agent",
        lambda state: state["action"],
        {
            "route_to_models": "router_agent",
            "need_more_data": "end",
            "complete": "end"
        }
    )
    
    workflow.add_edge("router_agent", "end")
    workflow.set_entry_point("main_agent")
    
    return workflow.compile()
```

## 🔌 API Interface

### REST Endpoints

#### Medical Assessment
```http
POST /assess
Content-Type: application/json

Request:
{
  "patient_text": "55-year-old male with history of hypertension, presenting with chest pain and shortness of breath. Blood pressure 160/95, BMI 28.5, non-smoker, family history of heart disease.",
  "query": "Assess cardiovascular risk and provide recommendations",
  "additional_notes": "Patient reports symptoms worsening over past week"
}

Response:
{
  "status": "complete",
  "action": "route_to_models",
  "predictions": [
    {
      "model": "cardiovascular_risk",
      "prediction": "High Risk",
      "probability": 0.78,
      "explanation": "Primary risk factors: hypertension, family history, symptoms..."
    }
  ],
  "report": "## Cardiovascular Risk Assessment\n\n**Patient Profile:** 55-year-old male with established hypertension...",
  "clinical_context": "Patient presents with classic cardiovascular risk profile...",
  "follow_up_questions": [
    "Any recent changes in exercise tolerance?",
    "Current medications for hypertension management?",
    "Previous cardiac imaging or stress tests?"
  ],
  "routing_explanation": "Patient has sufficient cardiovascular parameters including BP, age, and symptoms. Cardiovascular model appropriate for risk stratification.",
  "routing_summary": "55M with hypertension, chest symptoms, requires cardiovascular risk assessment"
}
```

#### Specialized Assessments
```http
POST /assess/cardiovascular
POST /assess/diabetes
```

### Request Processing Flow
1. **Input Validation**: Pydantic model validation for patient data
2. **Graph Initialization**: LangGraph state creation with patient context
3. **Main Agent Analysis**: LLM-powered clinical context analysis
4. **Routing Decision**: Intelligent workflow routing based on data completeness
5. **Model Coordination**: Router agent coordinates appropriate AI models
6. **Report Generation**: MedGemma creates comprehensive medical assessment
7. **Response Synthesis**: Structured response with clinical reasoning

## 🤖 LLM Integration

### Groq LLaMA Integration
```python
class GroqLLM:
    """Groq API client for LLaMA-3.1-8B model"""
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"
    
    async def generate_response(self, prompt: str, context: dict) -> str:
        """Generate LLM response with medical context"""
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a medical AI assistant..."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent medical reasoning
            max_tokens=1000
        )
        return completion.choices[0].message.content
```

### Medical Reasoning Prompts
```python
CLINICAL_ANALYSIS_PROMPT = """
Analyze the following patient information and determine the appropriate medical assessment workflow:

Patient Data: {patient_text}
Assessment Request: {query}

Consider:
1. Available clinical parameters
2. Missing critical information
3. Most appropriate risk assessment models
4. Clinical urgency and relevance

Respond with structured analysis including:
- Clinical context summary
- Data completeness assessment
- Recommended action (route_to_models/need_more_data/complete)
- Reasoning for decision
"""

MODEL_SELECTION_PROMPT = """
Given the patient context and available data, determine which AI models to invoke:

Patient Context: {clinical_context}
Available Parameters: {available_params}
Model Requirements: {model_specs}

Analyze:
1. Parameter sufficiency for each model
2. Clinical relevance of each assessment
3. Missing critical parameters
4. Optimal model selection strategy

Provide structured response with model selection reasoning.
"""
```

## 🔧 Configuration & Setup

### Environment Configuration
```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key

# MCP Integration
MCP_CHAT_URL=http://127.0.0.1:8000/chat

# MedGemma Configuration
MEDGEMMA_BASE_URL=http://localhost:11434/v1
MEDGEMMA_API_KEY=your_medgemma_key

# Service Endpoints
CARDIOVASCULAR_API=http://localhost:5002
DIABETES_API=http://localhost:5003
```

### Model Specifications
```yaml
# medimax/specs/model_specs.yaml
cardiovascular_risk:
  required_parameters:
    - age
    - gender
    - ap_hi (systolic BP)
    - ap_lo (diastolic BP)
    - cholesterol
  optional_parameters:
    - smoke
    - alco
    - active
  clinical_context: "Cardiovascular disease risk assessment"

diabetes_risk:
  required_parameters:
    - age
    - gender
    - bmi
    - blood_glucose_level
  optional_parameters:
    - smoking_history
    - hypertension
    - heart_disease
  clinical_context: "Type 2 diabetes risk prediction"
```

## 🧪 Testing & Validation

### Agent Testing
```python
# test_orchestration.py
async def test_complete_workflow():
    """Test end-to-end multi-agent workflow"""
    
    patient_data = {
        "patient_text": "45-year-old female with diabetes family history...",
        "query": "Assess diabetes risk"
    }
    
    graph = build_graph()
    result = await graph.ainvoke({"payload": patient_data})
    
    assert result["status"] == "complete"
    assert len(result["predictions"]) > 0
    assert result["report"] is not None
```

### LLM Response Validation
```python
def test_llm_reasoning():
    """Validate LLM generates appropriate medical reasoning"""
    
    response = main_agent.analyze_context(patient_data)
    
    assert "clinical_context" in response
    assert response["action"] in ["route_to_models", "need_more_data", "complete"]
    assert len(response["reasoning"]) > 50  # Substantial reasoning provided
```

## 🚀 Performance Optimization

### Async Processing
- **Concurrent Model Invocation**: Parallel AI model execution
- **Non-blocking LLM Calls**: Asynchronous Groq API integration
- **State Persistence**: Efficient graph state management

### Caching Strategies
- **LLM Response Caching**: Cache common clinical reasoning patterns
- **Model Result Caching**: Cache prediction results for identical parameters
- **Report Template Caching**: Reuse medical report structures

### Resource Management
- **Connection Pooling**: Efficient HTTP client management
- **Memory Optimization**: Graph state cleanup after completion
- **Rate Limiting**: Groq API rate limit compliance

## 📈 Integration Examples

### Backend Integration
```python
# Integration with main backend
async def get_ai_assessment(patient_id: int):
    """Get AI assessment for existing patient"""
    
    # Fetch patient data from backend
    patient_data = await backend_client.get_patient_profile(patient_id)
    
    # Format for agent system
    assessment_request = {
        "patient_text": format_patient_summary(patient_data),
        "query": "Comprehensive health risk assessment"
    }
    
    # Get AI assessment
    result = await agent_client.assess_patient(assessment_request)
    return result
```

### Frontend Integration
```javascript
// React component for AI assessment
const getAIAssessment = async (patientData) => {
  const response = await fetch('http://localhost:8001/assess', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      patient_text: patientData.summary,
      query: 'General health assessment',
      additional_notes: patientData.notes
    })
  });
  
  const assessment = await response.json();
  return assessment;
};
```

## 🔐 Security & Compliance

### Data Protection
- **PHI Handling**: Secure processing of protected health information
- **API Key Management**: Secure storage of LLM API credentials
- **Input Sanitization**: Validation of all patient data inputs

### HIPAA Considerations
- **Data Minimization**: Only process necessary patient information
- **Audit Logging**: Comprehensive logs of all AI assessments
- **Access Controls**: Restricted access to agent system endpoints

---

**Part of the MediMax Healthcare Platform - Intelligent AI agents for comprehensive medical assessment and decision support**