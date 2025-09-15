# MediMax Chat & MCP Services - Conversational AI Healthcare Interface

## 💬 Overview

The Chat & MCP Services (`backend_noodles`) represent the intelligent conversational layer of MediMax, combining LangChain-powered natural language processing with the Model Context Protocol (MCP) for seamless AI tool orchestration. This component enables healthcare professionals to interact with patient data and AI models through natural language conversations.

## 🎯 Core Responsibilities

- **Conversational AI Interface**: Natural language interaction with medical data
- **Tool Orchestration**: MCP-based coordination of AI prediction models
- **Knowledge Graph Integration**: Direct access to Neo4j patient graphs
- **Memory Management**: Persistent conversation context across sessions
- **Multi-Model Coordination**: Seamless integration of cardiovascular and diabetes prediction

## 🏗️ Architecture

### Service Architecture
```
┌─────────────────────────────────────┐
│          Frontend Clients           │
│    (React, Streamlit, Mobile)       │
└─────────────────┬───────────────────┘
                  │ HTTP POST /chat
┌─────────────────▼───────────────────┐
│            Chat API                 │
│          (port 8000)                │
│                                     │
│ ├── LangChain Agent                 │
│ ├── Google Gemini 1.5 Flash        │
│ ├── Conversation Memory             │
│ └── MCP Client Integration          │
└─────────────────┬───────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────┐
│           MCP Server                │
│          (port 8005)                │
│                                     │
│ ├── Neo4j Knowledge Graph          │
│ ├── Patient Data Retrieval         │
│ ├── Prediction Tools               │
│ └── Graph Management               │
└─────────────────┬───────────────────┘
                  │ HTTP Requests
┌─────────────────▼───────────────────┐
│        AI Prediction Services       │
│   Cardio (5002) | Diabetes (5003)   │
└─────────────────────────────────────┘
```

### Technology Stack
- **Chat API**: FastAPI with LangChain integration
- **LLM**: Google Generative AI (Gemini-1.5-Flash)
- **Agent Framework**: LangChain Structured Chat Agent
- **Memory**: ConversationBufferMemory for context persistence
- **MCP Server**: FastMCP for tool orchestration
- **Knowledge Graph**: Neo4j for patient-centric data

## 🤖 Chat API Service (`chat_api.py`)

### Core Features

#### LangChain Agent Configuration
```python
# Structured agent for JSON tool handling
agent = initialize_agent(
    tools=tools,
    llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash"),
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    memory=ConversationBufferMemory(
        memory_key="chat_history", 
        return_messages=True
    ),
    verbose=True
)
```

#### Asynchronous Tool Integration
```python
async def get_mcp_tools() -> List[BaseTool]:
    """Fetch tools from MCP server asynchronously"""
    client = MultiServerMCPClient({
        "Hospital": {
            "url": "http://127.0.0.1:8005/mcp/",
            "transport": "streamable_http"
        }
    })
    return await client.get_tools()
```

### API Endpoints

#### Chat Interface
```http
POST /chat
Content-Type: application/json

Request:
{
  "message": "What medications is patient 20 currently taking?"
}

Response:
{
  "response": "Patient 20 (James Chen) is currently taking the following medications: Prednisone, Ibuprofen, Cyclobenzaprine, and Loratadine. These medications were retrieved from the knowledge graph and appear to be for managing inflammation, pain, muscle relaxation, and allergies respectively."
}
```

### Conversation Flow
1. **Message Reception**: User sends natural language query
2. **Agent Processing**: LangChain agent analyzes intent and context
3. **Tool Selection**: Agent selects appropriate MCP tools
4. **Tool Execution**: Tools query databases or prediction models
5. **Response Generation**: Agent synthesizes natural language response
6. **Memory Update**: Conversation context preserved for follow-up

## 🔧 MCP Server (`mcp_server.py`)

### Tool Orchestration

The MCP Server exposes sophisticated tools for medical data access and AI model integration:

#### Knowledge Graph Tools
```python
@mcp.tool("Run_Cypher_Query")
def run_cypher_query(cypher: str) -> dict:
    """Execute Cypher queries against Neo4j knowledge graph"""
    # Automatic query validation and deprecated function fixes
    # Returns structured results with error handling

@mcp.tool("Create_Knowledge_Graph")
def create_knowledge_graph(patient_id: int) -> dict:
    """Generate comprehensive patient knowledge graph"""
    # Creates patient-centric graph with medical relationships

@mcp.tool("Validate_Graph_Connectivity")
def validate_graph_connectivity() -> dict:
    """Ensure all graph nodes are properly connected"""
    # Graph integrity validation and orphan node detection
```

#### Patient Data Retrieval Tools
```python
@mcp.tool("Get_Patient_Details")
def get_patient_details(patient_id: str) -> dict:
    """Retrieve comprehensive patient information"""

@mcp.tool("Get_Patient_Medical_Reports")
def get_patient_medical_reports(patient_id: int) -> dict:
    """Fetch all medical reports for a patient"""

@mcp.tool("Get_Patient_Symptoms")
def get_patient_symptoms(patient_id: int) -> dict:
    """Get symptom history from appointments"""
```

#### AI Prediction Tools
```python
@mcp.tool("Predict_Cardiovascular_Risk_With_Explanation")
def predict_cardiovascular_risk_with_explanation(
    age: float, gender: int, height: float, weight: float,
    ap_hi: int, ap_lo: int, cholesterol: int, gluc: int,
    smoke: int, alco: int, active: int
) -> dict:
    """Comprehensive cardiovascular risk assessment with SHAP explanations"""

@mcp.tool("Predict_Diabetes_Risk_With_Explanation")
def predict_diabetes_risk_with_explanation(
    age: float, gender: str, hypertension: int, heart_disease: int,
    smoking_history: str, bmi: float, HbA1c_level: float,
    blood_glucose_level: float
) -> dict:
    """Advanced diabetes risk prediction with feature importance"""
```

## 🧠 Knowledge Graph Management

### Patient-Centric Graph Creation
```python
def create_patient_knowledge_graph(self, patient_data: dict):
    """Create optimized patient-centric medical knowledge graph"""
    # 1. Central Patient node creation
    # 2. Medical history relationship mapping
    # 3. Medication and treatment connections
    # 4. Lab result and report integration
    # 5. Symptom and appointment linkage
    # 6. Temporal relationship establishment
```

### Graph Structure
- **18 Node Types**: Patient, Medication, Condition, Symptom, LabResult, etc.
- **17 Relationship Types**: TAKES_MEDICATION, HAS_CONDITION, REPORTED_SYMPTOM, etc.
- **Hierarchical Design**: Lab data follows Report → Study → Result hierarchy
- **Temporal Tracking**: All relationships include timestamps

### Neo4j Integration
```python
class KnowledgeGraphManager:
    def __init__(self):
        self.neo4j_uri = "neo4j+s://98d1982d.databases.neo4j.io"
        self.neo4j_user = os.getenv("AURA_USER")
        self.neo4j_password = os.getenv("AURA_PASSWORD")
    
    def connect_neo4j(self):
        """Establish secure connection to Neo4j AuraDB"""
        
    def create_patient_graph(self, patient_id: int):
        """Generate comprehensive patient knowledge graph"""
```

## 📊 Data Flow & Integration

### Conversation Memory Management
```python
# Persistent conversation context
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Context-aware responses
"Based on our previous discussion about patient 20..."
```

### Multi-Service Integration
1. **Chat Request**: Natural language query received
2. **Intent Analysis**: Agent determines required tools
3. **Data Retrieval**: MCP tools query databases
4. **Model Invocation**: AI predictions when needed
5. **Graph Queries**: Complex relationship traversals
6. **Response Synthesis**: Natural language generation

### Error Handling & Recovery
```python
def handle_exceptions(func):
    """Comprehensive error handling decorator"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return {"error": f"Failed to execute {func.__name__}: {str(e)}"}
    return wrapper
```

## 🔧 Configuration & Setup

### Environment Configuration
```bash
# Google AI Configuration
GOOGLE_API_KEY=your_google_generative_ai_key

# MCP Server Configuration
MCP_SERVER_URL=http://127.0.0.1:8005/mcp/

# Neo4j Configuration
AURA_USER=your_neo4j_username
AURA_PASSWORD=your_neo4j_password

# Database Configuration
DB_HOST=your_mariadb_host
DB_PORT=3305
DB_NAME=Hospital_controlmet
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

### Service Startup
```bash
# Start MCP Server (Port 8005)
cd backend_noodles
python mcp_server.py

# Start Chat API (Port 8000)
python chat_api.py
```

### Docker Deployment
```yaml
# docker-compose.backend.yml
services:
  mcp-server:
    build:
      context: ./backend_noodles
      dockerfile: Dockerfile.mcp_server
    ports:
      - "8005:8005"
    
  chat-api:
    build:
      context: ./backend_noodles
      dockerfile: Dockerfile.chat_api
    ports:
      - "8000:8000"
    depends_on:
      - mcp-server
```

## 🧪 Testing & Validation

### Health Checks
```http
GET /health (MCP Server)
Response: {
  "status": "healthy",
  "neo4j_connection": "connected",
  "database_connection": "active",
  "available_tools": 15
}
```

### Conversation Testing
```json
{
  "message": "Show me the cardiovascular risk for a 45-year-old male with high blood pressure"
}

Response: {
  "response": "Based on the cardiovascular risk assessment model, I'll need some additional information to provide an accurate prediction. For a 45-year-old male with high blood pressure, the model requires:\n\n- Height and weight (for BMI calculation)\n- Specific blood pressure readings (systolic/diastolic)\n- Cholesterol level\n- Glucose level\n- Smoking status\n- Alcohol consumption\n- Physical activity level\n\nWould you like me to use typical values for an initial assessment, or do you have specific measurements?"
}
```

### Tool Integration Testing
```python
# Test MCP tool availability
async def test_mcp_tools():
    tools = await get_mcp_tools()
    assert len(tools) > 0
    assert any(tool.name == "Run_Cypher_Query" for tool in tools)
```

## 🚀 Performance Optimization

### Asynchronous Processing
- **Non-blocking I/O**: FastAPI async endpoints
- **Concurrent Tool Execution**: Parallel MCP tool invocation
- **Memory Management**: Efficient conversation context handling

### Caching Strategies
- **LLM Response Caching**: Common query response caching
- **Knowledge Graph Caching**: Frequently accessed patient graphs
- **Model Prediction Caching**: Risk assessment result caching

### Connection Management
- **Neo4j Connection Pooling**: Efficient graph database access
- **HTTP Client Reuse**: Persistent connections to AI services
- **Memory Optimization**: Conversation history truncation

## 🔐 Security Features

### Input Validation
- **Query Sanitization**: Cypher injection prevention
- **Parameter Validation**: Type checking and bounds validation
- **Rate Limiting**: Request throttling for API protection

### Authentication Integration
```python
# Future authentication middleware
async def verify_api_key(api_key: str = Header(...)):
    if api_key not in valid_api_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

## 📈 Integration Examples

### Frontend Integration
```javascript
// React component integration
const chatWithMediMax = async (message) => {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  });
  return await response.json();
};
```

### Agent System Integration
```python
# Multi-agent orchestration
async def coordinate_with_chat_service(patient_data):
    chat_response = await chat_api_client.post("/chat", {
        "message": f"Analyze patient {patient_data['id']} for risk factors"
    })
    return chat_response.json()
```

---

**Part of the MediMax Healthcare Platform - Enabling natural language interaction with medical AI systems**