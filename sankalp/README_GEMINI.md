# Gemini-Powered Cypher Query Generator with Flask API

A Python implementation that converts natural language queries into runnable Neo4j Cypher queries using Google's Gemini API, served through a Flask REST API.

## Features

- **🤖 Google Gemini Integration**: Uses Google's advanced Gemini models for query generation
- **🔧 Clean Output**: Automatically removes markdown formatting and extracts only executable Cypher queries
- **🎯 Schema-Aware**: Incorporates Neo4j database schema information for better query generation
- **✅ Syntax Validation**: Basic validation to ensure generated queries are syntactically correct
- **🌐 REST API**: Flask server with multiple endpoints for different use cases
- **🔄 Multiple Interfaces**: Simple functions, class-based interface, and REST API

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

### 1. Direct Python Usage

```python
from cypher import generate_cypher_from_text

# Simple usage
query = generate_cypher_from_text("Find all users named John")
print(query)
# Output: MATCH (n:User) WHERE n.name = 'John' RETURN n
```

### 2. Flask API Server

**Start the server:**
```bash
python flask_server.py
```

**Make API requests:**
```bash
curl -X POST http://127.0.0.1:5000/generate_simple \
     -H "Content-Type: application/json" \
     -d '{"query": "Find all movies from 2020"}'
```

### 3. Python Client

```python
import requests

response = requests.post(
    "http://127.0.0.1:5000/generate_cypher",
    json={
        "query": "Show me actors who worked with Tom Hanks",
        "schema": "Node Labels: Person, Movie\\nRelationship Types: ACTED_IN"
    }
)

result = response.json()
print(f"Cypher: {result['cypher_query']}")
```

## API Endpoints

### Health Check
```http
GET /
```
Returns server status and available endpoints.

### Generate Cypher (Detailed)
```http
POST /generate_cypher
Content-Type: application/json

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
Content-Type: application/json

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
Content-Type: application/json

{
    "schema": "Node Labels: User, Post, Comment..."
}
```

### Validate Cypher
```http
POST /validate_cypher
Content-Type: application/json

{
    "cypher": "MATCH (n:Person) RETURN n"
}
```

## Examples

### Medical Database Example

```python
from cypher import CypherQueryGenerator

generator = CypherQueryGenerator()

# Set medical database schema
medical_schema = """
Node Labels: Patient, Doctor, Disease, Treatment, Hospital, Medication
Relationship Types: DIAGNOSED_WITH, TREATED_BY, WORKS_AT, PRESCRIBED, LOCATED_IN
Property Keys: name, age, gender, specialization, address, dosage, date, severity
"""
generator.set_schema_info(medical_schema)

# Generate queries
queries = [
    "Find all patients diagnosed with diabetes",
    "Show doctors who specialize in cardiology",
    "Get medications prescribed for high blood pressure"
]

for q in queries:
    cypher = generator.generate_cypher_query(q)
    print(f"Query: {q}")
    print(f"Cypher: {cypher}")
    print()
```

### Flask API Testing

```python
# Test the API client
python client_example.py

# Interactive mode
python client_example.py interactive
```

## Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional Flask settings
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false

# Optional Neo4j settings
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### Gemini Model Configuration

```python
# Use different Gemini models
generator = CypherQueryGenerator(model_name="gemini-2.0-flash-exp")  # Fast
generator = CypherQueryGenerator(model_name="gemini-1.5-pro")        # More accurate

# Adjust creativity
generator = CypherQueryGenerator(temperature=0.0)   # Deterministic
generator = CypherQueryGenerator(temperature=0.7)   # More creative
```

## File Structure

```
sankalp/
├── cypher.py           # Main Gemini-powered generator
├── flask_server.py     # Flask REST API server
├── client_example.py   # API client examples and testing
├── example_usage.py    # Direct Python usage examples
├── requirements.txt    # Dependencies
├── .env.example       # Environment template
└── README_cypher.md   # This documentation
```

## Key Improvements from OpenAI Version

1. **🔄 Gemini Integration**: Replaced OpenAI with Google's Gemini API
2. **🌐 REST API**: Added Flask server for web-based access
3. **🧹 Better Parsing**: Improved output cleaning for Gemini responses
4. **📡 Multiple Endpoints**: Different endpoints for different use cases
5. **✅ Enhanced Testing**: Comprehensive test client with examples

## Output Cleaning

The system automatically cleans Gemini output:

**Gemini Output:**
```
Here is the Cypher query you requested:

```cypher
MATCH (n:Person) WHERE n.name = 'John' RETURN n
```

This query will find all Person nodes with the name 'John'.
```

**Cleaned Output:**
```
MATCH (n:Person) WHERE n.name = 'John' RETURN n
```

## Error Handling

The system includes comprehensive error handling:

```python
try:
    response = requests.post("http://127.0.0.1:5000/generate_cypher", 
                           json={"query": "Find all users"})
    result = response.json()
    
    if result['success']:
        print(f"Cypher: {result['cypher_query']}")
    else:
        print(f"Error: {result['error']}")
        
except requests.exceptions.ConnectionError:
    print("Server not running")
except Exception as e:
    print(f"Request error: {e}")
```

## Best Practices

1. **🔑 API Key Security**: Never commit API keys to version control
2. **📋 Provide Schema**: Always set schema information for better accuracy
3. **🎯 Low Temperature**: Use temperature 0.0-0.2 for consistent results
4. **✅ Validate Queries**: Always validate generated queries before execution
5. **🧪 Test First**: Test generated queries on sample data before production use

## Limitations

- Requires Google Gemini API key (has usage costs)
- Generated queries should be tested before production use
- Complex queries may require human review
- Schema information significantly improves accuracy

## Getting Started

1. **Set up Gemini API:**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

2. **Test direct usage:**
   ```bash
   python -c "from cypher import generate_cypher_from_text; print(generate_cypher_from_text('Find all users'))"
   ```

3. **Start the Flask server:**
   ```bash
   python flask_server.py
   ```

4. **Test the API:**
   ```bash
   python client_example.py
   ```

## Support

- Check the examples in `client_example.py` for API usage
- Run `python flask_server.py` and visit `http://127.0.0.1:5000/` for API documentation
- Use the interactive mode: `python client_example.py interactive`

## License

This project is open source. Please check the license file for details.