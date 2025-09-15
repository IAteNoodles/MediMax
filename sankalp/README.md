# Sankalp - Medical RAG & Cypher Query Generation System

The `sankalp` directory is a comprehensive medical knowledge processing and query generation system that combines **Retrieval-Augmented Generation (RAG)** with **Natural Language to Cypher Query Translation**. It serves as an intelligent interface layer that can understand medical queries in natural language and either retrieve relevant information from medical documents or convert questions into executable Neo4j Cypher queries.

## 🏗️ System Architecture

The system is built around two core capabilities:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Sankalp System Architecture                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────┐      ┌─────────────────────────────────┐   │
│  │     RAG Pipeline        │      │    Cypher Query Generator       │   │
│  │                         │      │                                 │   │
│  │ • Medical PDFs → FAISS  │      │ • Natural Language → Cypher    │   │
│  │ • Gemini Embeddings     │◄────►│ • Neo4j Schema-Aware           │   │
│  │ • Context Retrieval     │      │ • Gemini-Powered Generation    │   │
│  │ • Response Generation   │      │ • Syntax Validation            │   │
│  └─────────────────────────┘      └─────────────────────────────────┘   │
│                 │                                    │                  │
│                 ▼                                    ▼                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              FastAPI Server (Primary Interface)                 │   │
│  │                                                                 │   │
│  │ • /chat      - Medical RAG responses                           │   │
│  │ • /generate_cypher - NL to Cypher conversion                   │   │
│  │ • /kb        - Knowledge base query execution                  │   │
│  │ • /docs      - Interactive API documentation                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧠 Core Functionality

### What This System Essentially Does:

**Sankalp** is a **Medical Intelligence Gateway** that bridges the gap between natural language medical queries and structured medical knowledge. It serves two primary functions:

1. **Medical Document RAG System**: Processes cardiovascular disease research papers and clinical guidelines, creating a searchable knowledge base using FAISS vector embeddings. When asked medical questions, it retrieves relevant context from these documents and generates comprehensive, evidence-based responses using Google's Gemini AI.

2. **Natural Language to Cypher Translator**: Converts plain English questions about patient data into executable Neo4j Cypher queries. This allows clinicians to query the knowledge graph using everyday language instead of learning Cypher syntax.

---

## 🛠️ Tech Stack

### Core Technologies:
- **LLM Provider**: Google Gemini (gemini-pro, gemini-2.5-flash-lite) via `google-generativeai`
- **Embeddings**: Google Gemini embeddings (`models/embedding-001`) via `langchain-google-genai`
- **Vector Database**: FAISS (Facebook AI Similarity Search) for document embeddings
- **Document Processing**: LangChain (`langchain-community`) with PyPDF for PDF processing
- **Web Framework**: FastAPI with uvicorn for high-performance async API
- **Graph Database Interface**: Neo4j driver for Cypher query validation and execution
- **Legacy Support**: Flask server implementation for backward compatibility

### Key Libraries:
```python
# AI & ML
google-generativeai>=0.8.0      # Gemini API integration
langchain>=0.1.0                # RAG framework
langchain-google-genai>=1.0.0   # Gemini embeddings
sentence-transformers>=2.2.2    # Alternative embeddings
faiss-cpu>=1.7.4               # Vector similarity search

# Document Processing
pypdf>=3.17.0                  # PDF document loading
langchain-community>=0.1.0     # Document loaders

# Web Framework
fastapi>=0.104.0               # Modern async API framework
uvicorn[standard]>=0.24.0      # ASGI server
pydantic>=2.0.0                # Data validation

# Database
neo4j>=5.0.0                   # Neo4j graph database driver

# Utilities
python-dotenv>=1.0.0           # Environment variable management
```

---

## 📁 File Structure & Components

### **Core RAG Pipeline (`chat.py`)**
The main medical RAG implementation with comprehensive features:
- **MedicalRAGPipeline Class**: Full-featured RAG system with FAISS vector store
- **PDF Processing**: Loads medical PDFs, splits into chunks, creates embeddings
- **Smart Retrieval**: Context-aware document retrieval with similarity search
- **Rate Limiting**: Handles Gemini API quota limits with exponential backoff
- **Persistent Storage**: Saves vector store to disk for faster startup

### **Optimized RAG (`optimized_chat.py`)**
Lightweight version for production use:
- **Smallest PDFs Only**: Processes only the 5 smallest medical PDFs by file size
- **Batch Processing**: Efficient batch embedding with rate limiting (25 docs/batch)
- **Production Ready**: Optimized for API quota management and fast responses

### **Fallback System (`fallback_chat.py`)**
Quota-exhaustion fallback with built-in medical knowledge:
- **No Embeddings Required**: Works when API quotas are exceeded
- **Curated Medical Knowledge**: Built-in cardiovascular disease information
- **Graceful Degradation**: Seamless fallback when primary systems fail

### **Mock System (`mock_chat.py`)**
Testing and development mock implementation:
- **No API Calls**: Generates sample responses for testing
- **Development Support**: Enables development without API costs

### **Cypher Query Generation (`cypher.py`)**
Natural language to Neo4j Cypher translation:
- **CypherQueryGenerator Class**: Gemini-powered query generation
- **CypherOutputParser Class**: Cleans LLM output to extract pure Cypher
- **Schema Integration**: Uses Neo4j schema for accurate query generation
- **Syntax Validation**: Basic Cypher syntax checking before execution

### **API Servers**

#### **FastAPI Server (`fastapi_server.py`) - Primary Interface**
Modern, production-ready API with comprehensive endpoints:

```python
# Core Endpoints
GET  /                    # Health check and endpoint discovery
POST /generate_cypher     # Detailed Cypher generation with schema
POST /generate_simple     # Simple NL → Cypher conversion
POST /set_schema         # Update Neo4j schema information
POST /validate_cypher    # Validate Cypher query syntax

# Medical RAG Endpoints  
POST /chat               # Medical document RAG chat interface
POST /kb                 # Knowledge base query (NL → Cypher → Execute)

# Documentation
GET  /docs               # Interactive Swagger UI documentation
GET  /redoc              # Alternative ReDoc documentation
```

#### **Flask Server (`flask_server.py`) - Legacy Support**
Simpler Flask implementation for backward compatibility:
- Basic Cypher generation endpoints
- CORS enabled for web applications
- Minimal configuration requirements

### **Testing & Utilities**

#### **Client Examples (`client_example.py`)**
Comprehensive API testing and usage examples:
- **Health Check Testing**: Verify server availability
- **Endpoint Testing**: Test all API endpoints with sample data
- **Interactive Mode**: Command-line interface for testing
- **Network Configuration**: Network access setup and troubleshooting

#### **Network Configuration (`network_config.py`)**
Network setup and connectivity helper:
- **IP Detection**: Automatic local IP address discovery
- **Firewall Guidance**: OS-specific firewall configuration instructions
- **Connection Testing**: Network connectivity verification
- **Mobile Access**: QR code suggestions for mobile device access

#### **Test Scripts**
- **`test_rag.py`**: RAG pipeline testing with small datasets
- **`test_external_endpoint.py`**: External Neo4j service connectivity testing
- **`test_kb_endpoint.py`**: Knowledge base endpoint comprehensive testing
- **`test_minimal_embedding.py`**: Minimal batch embedding verification

---

## 🚀 Setup and Installation

### 1. Prerequisites
```bash
# Python 3.8+ required
python --version

# Create virtual environment (recommended)
python -m venv sankalp_env
source sankalp_env/bin/activate  # Linux/Mac
# or
sankalp_env\Scripts\activate     # Windows
```

### 2. Install Dependencies
```bash
cd sankalp
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the `sankalp` directory:
```env
# Required: Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: FastAPI Server Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
FASTAPI_RELOAD=false

# Optional: Neo4j Database (for Cypher execution)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
AURA_USER=neo4j
AURA_PASSWORD=your_neo4j_password

# Optional: Embedding Limits (for quota management)
MAX_EMBEDDING_CHUNKS=200
```

### 4. Prepare Medical Documents
```bash
# Create data directory and add PDF files
mkdir data
# Add your medical PDF documents to the data/ folder
# The system will automatically process all PDFs found
```

### 5. Start the System
```bash
# Primary FastAPI server (recommended)
python fastapi_server.py

# Server will start at: http://0.0.0.0:8000
# API Documentation: http://localhost:8000/docs
```

---

## 🔧 Usage Examples

### Medical RAG Chat
```bash
# Chat with medical documents
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "patient_id": "12345",
       "message": "What are the main risk factors for cardiovascular disease?"
     }'
```

### Natural Language to Cypher
```bash
# Simple Cypher generation
curl -X POST "http://localhost:8000/generate_simple" \
     -H "Content-Type: application/json" \
     -d '{"query": "Find all patients with diabetes"}'

# Advanced with schema
curl -X POST "http://localhost:8000/generate_cypher" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Show me patients with high blood pressure",
       "db_schema": "Node Labels: Patient, Condition...",
       "context": "Medical database with patient records"
     }'
```

### Knowledge Base Query (NL → Cypher → Execute)
```bash
# End-to-end natural language query execution
curl -X POST "http://localhost:8000/kb" \
     -H "Content-Type: application/json" \
     -d '{"message": "Find all patients diagnosed with hypertension"}'
```

### Python Integration
```python
import requests

# Medical chat
response = requests.post("http://localhost:8000/chat", json={
    "patient_id": "patient_001",
    "message": "What lifestyle changes can help prevent heart disease?"
})
print(response.json()["reply"])

# Cypher generation
response = requests.post("http://localhost:8000/generate_simple", json={
    "query": "Find all medications for cardiovascular conditions"
})
print(response.text)  # Returns pure Cypher query
```

---

## 🧪 Testing and Development

### Run Comprehensive Tests
```bash
# Test all API endpoints
python client_example.py

# Interactive testing mode
python client_example.py interactive

# Network configuration check
python network_config.py

# Test specific components
python test_rag.py              # RAG pipeline testing
python test_kb_endpoint.py      # KB endpoint testing
python test_minimal_embedding.py # Embedding system testing
```

### Development Workflow
```bash
# 1. Start with mock system for development
# Edit mock_chat.py to return sample responses

# 2. Test with minimal embeddings
python test_minimal_embedding.py

# 3. Use optimized RAG for production
# Ensures efficient API usage and fast responses

# 4. Enable fallback system for reliability
# Automatically handles quota exhaustion gracefully
```

---

## 📊 System Features

### **Intelligent Fallback Chain**
1. **Primary**: Full RAG pipeline with all medical documents
2. **Optimized**: Lightweight RAG with essential documents only
3. **Fallback**: Built-in medical knowledge when APIs are unavailable
4. **Mock**: Sample responses for testing and development

### **Production-Ready Features**
- **Rate Limiting**: Automatic API quota management with exponential backoff
- **Error Handling**: Comprehensive error handling with graceful degradation
- **Caching**: Vector store persistence for faster startup times
- **Monitoring**: Detailed logging and request tracking
- **Documentation**: Auto-generated API documentation with Swagger UI

### **Medical Domain Optimization**
- **Cardiovascular Focus**: Specialized for cardiovascular disease research
- **Clinical Guidelines**: Processes both research papers and clinical guidelines
- **Patient Context**: Optional patient ID for personalized responses
- **Evidence-Based**: Responses include source citations and medical references

---

## 🔗 Integration with MediMax

Sankalp integrates seamlessly with the broader MediMax ecosystem:

- **Backend Integration**: Provides intelligent query capabilities to `backend_abhishek`
- **Agent Integration**: Powers the Cypher generation in `backend_noodles` MCP server
- **Frontend Support**: RESTful API endpoints for `Anugrah/front-end` integration
- **Knowledge Graph**: Direct Neo4j integration with the MediMax knowledge graph

---

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production
```env
GEMINI_API_KEY=your_production_api_key
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
MAX_EMBEDDING_CHUNKS=500
NEO4J_URI=your_production_neo4j_uri
```

### Monitoring and Logging
```python
# Built-in logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request tracking and performance monitoring available
# Check fastapi_server.py for implementation details
```

---

## 🎯 Key Benefits

1. **Medical Expertise**: Specialized for cardiovascular disease and clinical guidelines
2. **Dual Capability**: Both document retrieval and query generation in one system
3. **Production Ready**: Comprehensive error handling, rate limiting, and monitoring
4. **Developer Friendly**: Extensive testing tools and documentation
5. **Scalable Architecture**: Modular design with multiple fallback options
6. **Cost Efficient**: Optimized API usage with intelligent caching and batching

---

## 📚 API Documentation

When the FastAPI server is running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/`

These provide complete API documentation with request/response examples and the ability to test endpoints directly in the browser.

---

## 🛡️ Security and Best Practices

- **API Key Management**: Store API keys in environment variables, never in code
- **Rate Limiting**: Built-in quota management prevents API abuse
- **Input Validation**: Pydantic models ensure type safety and data validation
- **Error Handling**: No sensitive information exposed in error messages
- **CORS Configuration**: Configurable CORS settings for web application security

The Sankalp system represents a sophisticated integration of modern AI capabilities with medical domain expertise, providing a robust foundation for intelligent medical query processing within the MediMax ecosystem.