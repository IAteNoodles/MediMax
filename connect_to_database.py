from fastmcp import FastMCP
import mariadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DB details
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))



mcp = FastMCP("Database")

@mcp.tool("ExecuteQuery")
def execute_query(query: str) -> dict:
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
