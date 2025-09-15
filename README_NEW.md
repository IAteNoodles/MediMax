# MediMax - AI-Powered Healthcare Management System

![MediMax Logo](https://img.shields.io/badge/MediMax-Healthcare%20AI-blue?style=for-the-badge)

Welcome to **MediMax** - a cutting-edge, AI-powered healthcare management ecosystem that revolutionizes patient care through intelligent data management, predictive analytics, and multi-agent orchestration. This comprehensive platform integrates advanced machine learning models with atomic facts database design to provide healthcare professionals with unprecedented insights and decision-making capabilities.

## 🚀 Project Overview

MediMax is a sophisticated suite of interconnected microservices that work in harmony to deliver a powerful healthcare management solution. Built around a **microservices architecture**, each component serves a distinct purpose while seamlessly integrating with others to create a unified healthcare intelligence platform.

### 🎯 Core Features

- **🏥 Comprehensive Patient Management**: Complete lifecycle management with atomic facts database design across 11 normalized tables
- **🤖 Multi-Agent AI Orchestration**: LangGraph-powered intelligent agents using Groq LLaMA-3.1-8B for complex medical assessments
- **📊 Predictive ML Models**: XGBoost-based cardiovascular and diabetes risk prediction with SHAP explanations
- **💬 Conversational AI Interface**: Google Gemini-powered chat system with medical RAG (Retrieval-Augmented Generation)
- **🧠 Dynamic Knowledge Graphs**: Neo4j-based patient-centric medical knowledge graphs with 17+ relationship types
- **🔄 Model Context Protocol (MCP)**: Advanced tool orchestration for AI agents with FastMCP integration
- **📱 Modern React Frontend**: Responsive web interface with TailwindCSS and Vite build system
- **🔒 Enterprise Architecture**: Docker containerization with comprehensive API documentation

---

## 🏛️ System Architecture

The project consists of five integrated modules working together in a sophisticated microservices ecosystem:

```
┌─────────────────────────┐    ┌──────────────────────────┐    ┌─────────────────────────┐
│      Anugrah/           │    │    backend_abhishek/     │    │    backend_noodles/     │
│   Frontend & Agents     │◄──►│   Core API & Database    │◄──►│   Chat & MCP Server     │
│                         │    │                          │    │                         │
│ • React Frontend        │    │ • FastAPI Backend        │    │ • LangChain Chat API    │
│ • LangGraph Agents      │    │ • Patient CRUD Ops       │    │ • MCP Tool Server       │
│ • Streamlit Demo        │    │ • Neo4j Integration      │    │ • Knowledge Graph Gen   │
└─────────────────────────┘    └──────────────────────────┘    └─────────────────────────┘
           │                              │          │                        │
           ▼                              ▼          ▼                        ▼
┌─────────────────────────┐    ┌──────────────┐ ┌─────────────┐    ┌─────────────────────────┐
│     AI_Models/          │    │   MariaDB    │ │   Neo4j     │    │      sankalp/           │
│   ML Prediction APIs    │    │  (Atomic     │ │ (Knowledge  │    │  Medical RAG & Cypher   │
│                         │    │   Facts)     │ │   Graph)    │    │                         │
│ • Cardio Risk (XGBoost) │    │              │ │             │    │ • Medical Document RAG  │
│ • Diabetes Risk (XGBoost)│   │ 11 Tables    │ │ 18 Nodes    │    │ • NL → Cypher Queries   │
│ • SHAP Explanations     │    │ Patient-     │ │ 17 Relations│    │ • Gemini Integration    │
└─────────────────────────┘    │ Centric      │ │             │    └─────────────────────────┘
                               └──────────────┘ └─────────────┘
```

### 📂 Module Descriptions

#### **🎯 Anugrah/** - Multi-Agent Orchestration & Frontend
- **Tech Stack**: LangGraph, Groq LLaMA-3.1-8B, React, Vite, TailwindCSS, Streamlit
- **`agents/`**: Sophisticated multi-agent system for intelligent medical assessment with Main Agent and Router Agent coordination
- **`front-end/`**: Modern React application with user authentication, patient dashboard, and agentic interface

#### **🏥 backend_abhishek/** - Core Backend Services  
- **Tech Stack**: FastAPI, MariaDB/MySQL, Neo4j, MedGemma LLM, PyMySQL
- **Purpose**: Primary backend managing all CRUD operations, AI-powered summaries, and agentic system bridge
- **Features**: 50+ RESTful endpoints, health monitoring, comprehensive patient data aggregation

#### **💬 backend_noodles/** - Chat & MCP Intelligence
- **Tech Stack**: LangChain, Google Gemini-1.5-Flash, FastMCP, Neo4j, MySQL
- **`chat_api.py`**: Conversational AI agent with tool integration for complex medical queries
- **`mcp_server.py`**: Model Context Protocol server exposing database and ML model tools
- **Key Feature**: Dynamic knowledge graph creation from patient data

#### **🧠 AI_Models/** - Machine Learning Services
- **Tech Stack**: XGBoost, SHAP, FastAPI, scikit-learn, pandas
- **`cardio/`**: Cardiovascular disease risk prediction with 11 clinical features (Port 5002)
- **`diabetes/`**: Diabetes risk assessment with 8 metabolic parameters (Port 5003)
- **Features**: Risk categorization, SHAP explanations, clinical recommendations

#### **📚 sankalp/** - Medical RAG & Cypher Generation
- **Tech Stack**: Google Gemini, FAISS, LangChain, Neo4j, PyPDF, FastAPI
- **Medical RAG**: Retrieval-Augmented Generation from cardiovascular research papers
- **Cypher Generation**: Natural language to Neo4j Cypher query translation
- **Features**: Multi-tier fallback system, intelligent rate limiting, schema-aware queries

---

## 🛠️ Tech Stack Overview

| Component | Primary Technologies | Purpose |
|-----------|---------------------|---------|
| **Frontend** | React, Vite, TailwindCSS, JavaScript | Modern responsive web interface |
| **Backend APIs** | FastAPI, Python 3.8+, Pydantic | High-performance async REST APIs |
| **AI/ML Models** | XGBoost, SHAP, scikit-learn | Risk prediction with explanations |
| **LLM Integration** | Groq LLaMA-3.1-8B, Google Gemini, MedGemma | Multi-agent orchestration & chat |
| **Agent Framework** | LangGraph, LangChain, FastMCP | Intelligent agent coordination |
| **Databases** | MariaDB/MySQL, Neo4j AuraDB | Atomic facts & knowledge graphs |
| **Document Processing** | FAISS, PyPDF, LangChain | Medical document RAG system |
| **Infrastructure** | Docker, Docker Compose, uvicorn | Containerized microservices |

---

## 🚀 Installation and Setup

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** and npm (for frontend)
- **MariaDB/MySQL 8.0+** database server
- **Neo4j AuraDB** account (or local Neo4j installation)
- **API Keys**: Groq, Google Gemini

### 1. Environment Configuration

Create a `.env` file in the root directory:

```env
# Database Configuration (MariaDB/MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medimax_db
DB_USER=your_username
DB_PASSWORD=your_password

# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
AURA_USER=neo4j
AURA_PASSWORD=your_neo4j_password

# AI Service API Keys
GROQ_API_KEY=gsk_your_groq_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key
GEMINI_API_KEY=your_google_gemini_api_key

# Service URLs (default ports)
AGENTIC_ADDRESS=http://127.0.0.1:8000
BACKEND_ABHISHEK_URL=http://127.0.0.1:8821
MCP_SERVER_URL=http://127.0.0.1:8005
CARDIO_API_URL=http://127.0.0.1:5002
DIABETES_API_URL=http://127.0.0.1:5003
```

### 2. Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd MediMax

# Install Python dependencies (all modules)
pip install -r requirements.txt

# Install frontend dependencies
cd Anugrah/front-end
npm install
cd ../..
```

### 3. Database Setup

**MariaDB/MySQL Schema:**
```sql
-- Create database
CREATE DATABASE medimax_db;

-- Import the comprehensive schema (11 tables)
-- See Database_Schema_README.md for full schema details
```

**Neo4j Knowledge Graph:**
- Create a Neo4j AuraDB account or install locally
- The graph will be automatically populated by the MCP server

### 4. Start All Services

Run each service in a separate terminal:

**Terminal 1: AI Model APIs**
```bash
# Start Cardiovascular API
cd AI_Models/cardio
python cardiovascular_api.py  # Port 5002

# In another terminal: Start Diabetes API
cd AI_Models/diabetes
python diabetes_api.py        # Port 5003
```

**Terminal 2: MCP Server (Tool Orchestration)**
```bash
cd backend_noodles
python mcp_server.py          # Port 8005
```

**Terminal 3: Chat API (Conversational AI)**
```bash
cd backend_noodles
python chat_api.py            # Port 8000
```

**Terminal 4: Core Backend API**
```bash
cd backend_abhishek
python app.py                 # Port 8821
```

**Terminal 5: Agent System**
```bash
cd Anugrah/agents
python api_server.py          # Port 8001
```

**Terminal 6: Frontend**
```bash
cd Anugrah/front-end
npm run dev                   # Port 5173
```

**Terminal 7: Medical RAG & Cypher System**
```bash
cd sankalp
python fastapi_server.py      # Port 8000 (alternative config)
```

### 5. Health Check Verification

Verify all services are running:

```bash
# Core APIs
curl http://localhost:8821/health     # Backend API
curl http://localhost:8000/chat       # Chat API (POST)
curl http://localhost:8005            # MCP Server
curl http://localhost:8001/health     # Agent API

# ML Model APIs
curl http://localhost:5002/health     # Cardiovascular API
curl http://localhost:5003/health     # Diabetes API

# Frontend
# Visit http://localhost:5173 in browser
```

---

## 📊 Database Schemas

### MariaDB - Atomic Facts Schema (11 Tables)

**Core Patient Entity:**
- **`Patient`**: Demographics and identification
- **`Medical_History`**: Conditions, allergies, surgeries, family history
- **`Appointment`**: Scheduled visits with status tracking
- **`Appointment_Symptom`**: Detailed symptom records per appointment

**Medication Management:**
- **`Medication`**: Prescribed medications with continuity tracking
- **`Medication_Purpose`**: Multi-condition medication mapping

**Laboratory & Reports:**
- **`Lab_Report`**: Laboratory test metadata
- **`Lab_Finding`**: Individual test results with abnormality detection
- **`Report`**: Comprehensive medical reports (radiology, pathology, clinical)
- **`Report_Finding`**: Structured findings extraction

**Communication:**
- **`Chat_History`**: Patient-provider chat interactions

### Neo4j - Knowledge Graph Schema (18 Nodes, 17 Relationships)

**Primary Nodes:**
- `Patient`, `Symptom`, `MedicalHistory`, `Medication`, `LabFinding`
- `LabResult`, `LabReport`, `Treatment`, `Condition`, `Encounter`
- `Appointment`, `Person`, `Observation`, `LabStudy`, `DiagnosticStudy`

**Key Relationships:**
- `HAS_SYMPTOM` (Patient → Symptom): 104 relationships
- `TAKES_MEDICATION` (Patient → Medication): 70 relationships  
- `HAS_MEDICAL_HISTORY` (Patient → MedicalHistory): 64 relationships
- `CONTAINS_FINDING` (LabReport → LabFinding): 65 relationships
- `HAS_LAB_RESULT` (Patient → LabResult): 42 relationships
- `TREATS_CONDITION` (Medication → MedicalHistory): 28 relationships
- `MAY_INDICATE` (Symptom → Condition): Probabilistic clinical associations

---

## 🔧 API Endpoints Overview

### Core Backend API (Port 8821)
```bash
# Patient Management
GET  /db/get_all_patients                    # Paginated patient list
GET  /db/get_complete_patient_profile/{id}   # Comprehensive patient data
POST /db/new_patient                         # Create new patient
PUT  /db/update_patient/{id}                 # Update patient
DELETE /db/delete_patient/{id}               # Delete patient

# Medical Records
POST /db/add_medical_history/{id}            # Add medical history
POST /db/add_appointment/{id}                # Schedule appointment
POST /db/add_medication/{id}                 # Add medication
POST /db/add_lab_report/{id}                 # Create lab report

# AI Integration
GET  /get_medical_history/{id}               # AI-powered summary
POST /assess                                 # Forward to agent system
GET  /frontend/get_query                     # Auto-generate assessment query
```

### Chat API (Port 8000)
```bash
POST /chat          # Conversational AI with medical knowledge
```

### Agent System API (Port 8001)
```bash
POST /assess                    # Multi-agent medical assessment
POST /assess/cardiovascular     # Cardiovascular-specific assessment
POST /assess/diabetes           # Diabetes-specific assessment
GET  /models                    # Available model information
```

### MCP Server (Port 8005)
```bash
# Knowledge Graph Tools
POST /Create_Knowledge_Graph     # Build patient graph
POST /Run_Cypher_Query          # Execute Cypher queries
POST /Validate_Graph_Connectivity # Graph integrity check

# ML Model Tools
POST /Predict_Cardiovascular_Risk_With_Explanation
POST /Predict_Diabetes_Risk_With_Explanation

# Database Tools
POST /Get_Patient_Details        # Patient information
POST /Get_Patient_Symptoms       # Symptom records
POST /New_Patient               # Create patient
```

### AI Model APIs
```bash
# Cardiovascular API (Port 5002)
GET  /health                    # Health check
GET  /model/info               # Model information
POST /predict                  # Risk prediction

# Diabetes API (Port 5003)
GET  /health                   # Health check
GET  /model/info              # Model information  
POST /predict                 # Risk prediction
```

### Medical RAG & Cypher API (Port 8000 - sankalp)
```bash
# Medical Document RAG
POST /chat                     # Medical literature queries

# Cypher Generation
POST /generate_cypher          # NL → Cypher conversion
POST /generate_simple          # Simple Cypher generation
POST /kb                       # Knowledge base queries

# Documentation
GET  /docs                     # Interactive API docs
```

---

## 🧪 Usage Examples

### Multi-Agent Medical Assessment
```bash
curl -X POST "http://localhost:8001/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_text": "65-year-old male with chest pain, hypertension, diabetes. Blood pressure 160/95, BMI 28.5, HbA1c 7.2%"
  }'
```

### Cardiovascular Risk Prediction
```bash
curl -X POST "http://localhost:5002/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 65, "gender": 2, "height": 175, "weight": 85,
    "ap_hi": 160, "ap_lo": 95, "cholesterol": 2,
    "gluc": 2, "smoke": 0, "alco": 0, "active": 1
  }'
```

### Medical Document Query
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "12345",
    "message": "What are the latest guidelines for cardiovascular disease prevention?"
  }'
```

### Knowledge Graph Query
```bash
curl -X POST "http://localhost:8000/generate_cypher" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find all patients with diabetes who also have cardiovascular conditions"
  }'
```

---

## 🔒 Security & Configuration

### Environment Security
- **API Keys**: Store in environment variables, never in code
- **Database Credentials**: Encrypted connection strings
- **CORS Configuration**: Configurable for development/production
- **Rate Limiting**: Built-in quota management for AI services

### Production Configuration
```bash
# Production environment variables
NODE_ENV=production
FASTAPI_ENV=production
MAX_EMBEDDING_CHUNKS=500
ENABLE_CORS=false
LOG_LEVEL=INFO
```

---

## 🎯 Key Benefits

1. **🏥 Medical Domain Expertise**: Specialized for cardiovascular disease and clinical guidelines
2. **🤖 Advanced AI Integration**: Multi-agent coordination with multiple LLM providers
3. **📊 Predictive Analytics**: ML models with explainable AI (SHAP) for clinical decisions
4. **🧠 Knowledge Graph Intelligence**: Complex medical relationship modeling and querying
5. **🔄 Microservices Architecture**: Scalable, maintainable, and independently deployable services
6. **💬 Conversational Interface**: Natural language interaction with medical knowledge
7. **📱 Modern UX**: Responsive design with comprehensive API documentation
8. **⚡ Performance Optimized**: Async APIs, connection pooling, and intelligent caching

---

## 📚 Documentation

- **[Agent System Guide](./Anugrah/README.md)**: Multi-agent orchestration details
- **[Backend API Docs](./backend_abhishek/README.md)**: Core API documentation
- **[Chat & MCP Services](./backend_noodles/README.md)**: Conversational AI and MCP tools
- **[ML Models Guide](./AI_Models/)**: Cardiovascular and diabetes prediction APIs
- **[Medical RAG System](./sankalp/README.md)**: Document processing and Cypher generation
- **[Database Schema](./Database_Schema_README.md)**: Complete database documentation
- **[Neo4j Relationships](./NEO4J_RELATIONSHIP_SCHEMA.md)**: Knowledge graph schema

---

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/medical-enhancement`
3. Commit changes: `git commit -m 'Add medical enhancement'`
4. Push to branch: `git push origin feature/medical-enhancement`
5. Open Pull Request

### Code Standards
- **Python**: PEP 8 compliance with type hints
- **JavaScript**: ESLint configuration with Prettier
- **API Design**: OpenAPI/Swagger documentation
- **Testing**: Comprehensive unit and integration tests

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain & LangGraph**: Advanced LLM orchestration capabilities
- **FastAPI**: High-performance async web framework
- **Neo4j**: Powerful graph database for medical knowledge
- **XGBoost**: Robust machine learning framework
- **React & Vite**: Modern frontend development tools
- **Google Gemini & Groq**: Advanced language model providers

---

**Built with ❤️ for modern healthcare by the MediMax Team**

![Healthcare AI](https://img.shields.io/badge/Healthcare-AI%20Powered-green?style=for-the-badge)
![Microservices](https://img.shields.io/badge/Architecture-Microservices-orange?style=for-the-badge)
![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-blue?style=for-the-badge)
