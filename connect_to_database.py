from fastmcp import FastMCP
import mariadb
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.time import Date, DateTime, Time, Duration
from datetime import datetime, date, time
import json

# Load environment variables
load_dotenv()

# Get DB details
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

AURA_USER = os.getenv('AURA_USER')
AURA_PASSWORD = os.getenv('AURA_PASSWORD')

# Custom JSON encoder for Neo4j types
class Neo4jJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, (Date, DateTime)):
            return obj.isoformat()
        elif isinstance(obj, Time):
            return obj.isoformat()
        elif isinstance(obj, Duration):
            return str(obj)
        elif isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, '__str__'):
            return str(obj)
        return super().default(obj)

def serialize_neo4j_result(result):
    """Convert Neo4j result to JSON-serializable format"""
    def convert_value(value):
        if value is None:
            return None
        elif isinstance(value, (Date, DateTime, Time, Duration, date, datetime, time)):
            return str(value)
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_value(v) for v in value]
        elif hasattr(value, '__str__'):
            return str(value)
        return value
    
    if isinstance(result, dict):
        return {k: convert_value(v) for k, v in result.items()}
    elif isinstance(result, list):
        return [convert_value(item) for item in result]
    return convert_value(result)

# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j+s://98d1982d.databases.neo4j.io"
AUTH = (AURA_USER, AURA_PASSWORD)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()


mcp = FastMCP("Database")


@mcp.tool("ExcecuteQuery_Neo4j")
def execute_query_neo4j(cypher_query: str) -> dict:
    """
    Execute a Cypher query on the Neo4j database.
    
    Args:
        cypher_query (str): The Cypher query to execute.
        
    Returns:
        dict: The result of the query or an error message.
    """
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            with driver.session() as session:
                result = session.run(cypher_query)
                records = [record.data() for record in result]
                # Apply serialization to handle Neo4j temporal types
                serialized_records = serialize_neo4j_result(records)
                return {"results": serialized_records, "count": len(serialized_records)}
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}

@mcp.tool("ExecuteQuery_MariaDB")
def execute_query_mariadb(query: str) -> dict:
    """
    Execute a SQL query on the MariaDB database.
    
    Args:
        query (str): The SQL query to execute.
        
    Returns:
        dict: The result of the query or an error message.
    """
    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        return {"error": "Database configuration incomplete. Check .env file."}
    
    conn = None
    try:
        conn = mariadb.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            # For SELECT queries, fetch results
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return {"results": results, "count": len(results)}
        else:
            # For other queries (INSERT, UPDATE, DELETE), commit and return affected rows
            conn.commit()
            return {"message": "Query executed successfully", "affected_rows": cursor.rowcount}
            
    except mariadb.Error as e:
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print(f"Database Config - Host: {DB_HOST}, User: {DB_USER}, DB: {DB_NAME}, Port: {DB_PORT}")
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8069,
        log_level="debug"
    )
