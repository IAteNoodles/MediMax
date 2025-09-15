# FastAPI Gemini Cypher Query Generator

A high-performance Python implementation that converts natural language queries into runnable Neo4j Cypher queries using Google's Gemini API, served through a modern FastAPI REST API with automatic documentation.

## 🚀 Features

- **⚡ FastAPI Performance**: Async endpoints for high-performance API operations
- **🤖 Google Gemini Integration**: Uses Google's advanced Gemini models for query generation
- **📚 Auto Documentation**: Built-in interactive API docs at `/docs` and `/redoc`
- **🔧 Clean Output**: Automatically removes markdown formatting and extracts only executable Cypher queries
- **🎯 Schema-Aware**: Incorporates Neo4j database schema information for better query generation
- **✅ Type Safety**: Full Pydantic models for request/response validation
- **🌐 CORS Support**: Built-in CORS middleware for web applications
- **📊 Multiple Interfaces**: Simple functions, class-based interface, and modern REST API

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

3. **Get a Gemini API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Quick Start

### 1. Start the FastAPI Server

```bash
python fastapi_server.py
```

The server will start at `http://127.0.0.1:8000` with:
- **API Documentation**: `http://127.0.0.1:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://127.0.0.1:8000/redoc` (ReDoc)
- **Health Check**: `http://127.0.0.1:8000/`

### 2. Interactive API Documentation

Visit `http://127.0.0.1:8000/docs` for interactive API documentation where you can:
- Explore all endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specification

### 3. Make API Requests

**Simple Query Generation:**
```bash
curl -X POST "http://127.0.0.1:8000/generate_simple" \
     -H "Content-Type: application/json" \
     -d '{"query": "Find all movies from 2020"}'
```

**Advanced Query with Schema:**
```bash
curl -X POST "http://127.0.0.1:8000/generate_cypher" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "Show me actors who worked with Tom Hanks",
       "schema": "Node Labels: Person, Movie\nRelationship Types: ACTED_IN",
       "context": "Movie database with actors and films"
     }'
```

## API Endpoints

### Health Check
```http
GET /
```
Returns server status and available endpoints.

**Response:**
```json
{
  "status": "healthy",
  "message": "Cypher Query Generator API is running",
  "endpoints": {
    "health": "GET /",
    "generate_cypher": "POST /generate_cypher",
    "generate_simple": "POST /generate_simple",
    "set_schema": "POST /set_schema",
    "validate_cypher": "POST /validate_cypher",
    "docs": "GET /docs",
    "redoc": "GET /redoc"
  }
}
```

### Generate Cypher (Detailed)
```http
POST /generate_cypher
```

**Request Body:**
```json
{
  "query": "Find all users named John",
  "schema": "Node Labels: User, Post...",  // optional
  "context": "Additional context..."       // optional
}
```

**Response:**
```json
{
  "success": true,
  "cypher_query": "MATCH (u:User) WHERE u.name = 'John' RETURN u",
  "is_valid": true,
  "original_query": "Find all users named John",
  "schema_used": true,
  "context_used": false
}
```

### Generate Cypher (Simple)
```http
POST /generate_simple
```

**Request Body:**
```json
{
  "query": "Find all movies from 2020"
}
```

**Response:** Plain text Cypher query
```
MATCH (m:Movie) WHERE m.year = 2020 RETURN m
```

### Set Schema
```http
POST /set_schema
```

**Request Body:**
```json
{
  "schema": "Node Labels: User, Post, Comment\nRelationship Types: CREATED, LIKES\nProperty Keys: name, title, content"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Schema updated successfully"
}
```

### Validate Cypher
```http
POST /validate_cypher
```

**Request Body:**
```json
{
  "cypher": "MATCH (n:Person) RETURN n"
}
```

**Response:**
```json
{
  "success": true,
  "is_valid": true,
  "cypher_query": "MATCH (n:Person) RETURN n"
}
```

## Python Client Usage

### Direct Import
```python
from cypher import generate_cypher_from_text

# Simple usage
query = generate_cypher_from_text("Find all users named John")
print(query)
# Output: MATCH (n:User) WHERE n.name = 'John' RETURN n
```

### HTTP Client
```python
import requests

# Test the API
response = requests.post(
    "http://127.0.0.1:8000/generate_cypher",
    json={
        "query": "Show me top 10 rated movies",
        "schema": "Node Labels: Movie\nProperty Keys: title, rating"
    }
)

result = response.json()
if result["success"]:
    print(f"Cypher: {result['cypher_query']}")
    print(f"Valid: {result['is_valid']}")
```

### Test Client
```python
# Run comprehensive tests
python client_example.py

# Interactive mode
python client_example.py interactive
```

## Advanced Features

### Async Python Client
```python
import httpx
import asyncio

async def generate_async_query():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/generate_simple",
            json={"query": "Find all active users"}
        )
        return response.text

# Usage
cypher_query = asyncio.run(generate_async_query())
print(cypher_query)
```

### Schema Management
```python
import requests

# Set schema for session
schema_response = requests.post(
    "http://127.0.0.1:8000/set_schema",
    json={
        "schema": """
        Node Labels: Patient, Doctor, Disease, Treatment
        Relationship Types: DIAGNOSED_WITH, TREATED_BY, PRESCRIBED
        Property Keys: name, age, specialization, severity, date
        """
    }
)

# Now all subsequent queries will use this schema
query_response = requests.post(
    "http://127.0.0.1:8000/generate_simple",
    json={"query": "Find all patients with diabetes"}
)
```

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# FastAPI Server Settings
FASTAPI_HOST=127.0.0.1      # Server host
FASTAPI_PORT=8000           # Server port  
FASTAPI_RELOAD=false        # Auto-reload on code changes

# Neo4j Database (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### Production Deployment

```bash
# Production server with Gunicorn
pip install gunicorn
gunicorn fastapi_server:app -w 4 -k uvicorn.workers.UvicornWorker

# Docker deployment
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## File Structure

```
sankalp/
├── cypher.py              # Core Gemini-powered generator
├── fastapi_server.py      # FastAPI REST API server
├── client_example.py      # API client examples and testing
├── example_usage.py       # Direct Python usage examples
├── flask_server.py        # Legacy Flask server (optional)
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── README_GEMINI.md      # Previous documentation
└── README_FASTAPI.md     # This documentation
```

## Key Improvements over Flask

1. **⚡ Performance**: Async endpoints for better concurrency
2. **📚 Auto Documentation**: Built-in Swagger UI and ReDoc
3. **🔒 Type Safety**: Pydantic models for request/response validation
4. **🛠️ Modern Stack**: Latest FastAPI with uvicorn server
5. **📊 Better Error Handling**: Structured HTTP exceptions
6. **🚀 Production Ready**: Easy deployment with uvicorn/gunicorn

## Error Handling

FastAPI provides structured error responses:

```python
try:
    response = requests.post("http://127.0.0.1:8000/generate_cypher", 
                           json={"query": "Find all users"})
    response.raise_for_status()  # Raises HTTPError for bad status codes
    
    result = response.json()
    print(f"Generated: {result['cypher_query']}")
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    print(f"Detail: {e.response.json()}")
except Exception as e:
    print(f"Error: {e}")
```

## Best Practices

1. **🔑 API Key Security**: Use environment variables, never commit keys
2. **📋 Schema Information**: Always provide schema for better accuracy
3. **🎯 Low Temperature**: Use temperature 0.0-0.2 for consistent results
4. **✅ Validate Queries**: Use the validation endpoint before execution
5. **🔄 Async Clients**: Use async HTTP clients for better performance
6. **📊 Monitor Usage**: Track API usage and Gemini costs
7. **🧪 Test First**: Validate queries on sample data before production

## Monitoring and Logs

```python
# Enable uvicorn logging
uvicorn fastapi_server:app --log-level info

# Custom logging in your application
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

## Getting Started Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set Gemini API key in `.env` file
- [ ] Start server: `python fastapi_server.py`
- [ ] Visit docs: `http://127.0.0.1:8000/docs`
- [ ] Test API: `python client_example.py`
- [ ] Try interactive mode: `python client_example.py interactive`

## Support and Documentation

- **API Docs**: `http://127.0.0.1:8000/docs` (when server is running)
- **Alternative Docs**: `http://127.0.0.1:8000/redoc`
- **Test Examples**: Run `python client_example.py`
- **Health Check**: `curl http://127.0.0.1:8000/`

## License

This project is open source. Please check the license file for details.