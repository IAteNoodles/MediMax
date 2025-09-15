"""
Flask Server for Cypher Query Generation
This server provides a REST API endpoint to generate Cypher queries from natural language
using Google's Gemini API.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from cypher import CypherQueryGenerator, generate_cypher_from_text

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the Cypher generator
try:
    cypher_generator = CypherQueryGenerator()
except Exception as e:
    print(f"Warning: Could not initialize Cypher generator: {e}")
    cypher_generator = None


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Cypher Query Generator API is running',
        'endpoints': {
            'generate_cypher': 'POST /generate_cypher',
            'health': 'GET /'
        }
    })


@app.route('/generate_cypher', methods=['POST'])
def generate_cypher():
    """
    Generate Cypher query from natural language
    
    Expected JSON payload:
    {
        "query": "Find all users named John",
        "schema": "Node Labels: User, Post...",  // optional
        "context": "Additional context..."       // optional
    }
    
    Returns:
    {
        "success": true,
        "cypher_query": "MATCH (u:User) WHERE u.name = 'John' RETURN u",
        "is_valid": true,
        "original_query": "Find all users named John"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Extract required and optional fields
        user_query = data.get('query')
        schema_info = data.get('schema', '')
        context = data.get('context', '')
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Missing required field: query'
            }), 400
        
        # Validate that generator is available
        if not cypher_generator:
            return jsonify({
                'success': False,
                'error': 'Cypher generator not initialized. Check GEMINI_API_KEY.'
            }), 500
        
        # Set schema info if provided
        if schema_info:
            cypher_generator.set_schema_info(schema_info)
        
        # Generate the Cypher query
        cypher_query = cypher_generator.generate_cypher_query(user_query, context)
        
        # Validate the generated query
        is_valid = cypher_generator.validate_cypher_syntax(cypher_query)
        
        return jsonify({
            'success': True,
            'cypher_query': cypher_query,
            'is_valid': is_valid,
            'original_query': user_query,
            'schema_used': bool(schema_info),
            'context_used': bool(context)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'generation_error'
        }), 500


@app.route('/generate_simple', methods=['POST'])
def generate_simple():
    """
    Simple endpoint that accepts just a query string
    
    Expected JSON payload:
    {
        "query": "Find all users named John"
    }
    
    Returns just the Cypher query as a string
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('query'):
            return jsonify({
                'error': 'Missing query field'
            }), 400
        
        user_query = data['query']
        
        # Use the simple function
        cypher_query = generate_cypher_from_text(user_query)
        
        return cypher_query, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/set_schema', methods=['POST'])
def set_schema():
    """
    Set the database schema for better query generation
    
    Expected JSON payload:
    {
        "schema": "Node Labels: User, Post..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('schema'):
            return jsonify({
                'success': False,
                'error': 'Missing schema field'
            }), 400
        
        if not cypher_generator:
            return jsonify({
                'success': False,
                'error': 'Cypher generator not initialized'
            }), 500
        
        schema_info = data['schema']
        cypher_generator.set_schema_info(schema_info)
        
        return jsonify({
            'success': True,
            'message': 'Schema updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/validate_cypher', methods=['POST'])
def validate_cypher():
    """
    Validate Cypher query syntax
    
    Expected JSON payload:
    {
        "cypher": "MATCH (n) RETURN n"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('cypher'):
            return jsonify({
                'success': False,
                'error': 'Missing cypher field'
            }), 400
        
        if not cypher_generator:
            return jsonify({
                'success': False,
                'error': 'Cypher generator not initialized'
            }), 500
        
        cypher_query = data['cypher']
        is_valid = cypher_generator.validate_cypher_syntax(cypher_query)
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'cypher_query': cypher_query
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'POST /generate_cypher',
            'POST /generate_simple',
            'POST /set_schema',
            'POST /validate_cypher'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server'
    }), 500


if __name__ == '__main__':
    # Configuration
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Cypher Query Generator API Server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug: {debug}")
    
    if not os.getenv('GEMINI_API_KEY'):
        print("WARNING: GEMINI_API_KEY not set. The server will start but API calls will fail.")
    
    print("\nAvailable endpoints:")
    print("- GET  /                 - Health check")
    print("- POST /generate_cypher  - Generate Cypher query (detailed)")
    print("- POST /generate_simple  - Generate Cypher query (simple)")
    print("- POST /set_schema       - Set database schema")
    print("- POST /validate_cypher  - Validate Cypher syntax")
    
    app.run(host=host, port=port, debug=debug)