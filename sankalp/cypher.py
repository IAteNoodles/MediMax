"""
Gemini-based Cypher Query Generator for Neo4j
This module provides functionality to generate runnable Cypher queries from natural language input
using Google's Gemini API.
"""

import os
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from neo4j import GraphDatabase

# Load environment variables
load_dotenv()


class CypherOutputParser:
    """Custom parser to clean and extract Cypher queries from Gemini output"""
    
    def parse(self, text: str) -> str:
        """
        Parse the Gemini output to extract clean Cypher query
        Removes markdown formatting, explanations, and other non-query text
        """
        # Remove markdown code blocks
        text = re.sub(r'```(?:cypher|sql)?\n?', '', text)
        text = re.sub(r'```', '', text)
        
        # Remove common prefixes and explanations
        text = re.sub(r'^.*(?:query|cypher).*?:', '', text, flags=re.IGNORECASE | re.MULTILINE)
        text = re.sub(r'^.*here.*?is.*?:', '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Split by lines and find the actual Cypher query
        lines = text.strip().split('\n')
        
        # Look for lines that start with Cypher keywords
        cypher_keywords = ['MATCH', 'CREATE', 'MERGE', 'DELETE', 'SET', 'REMOVE', 'WITH', 'RETURN', 'WHERE', 'ORDER', 'LIMIT', 'SKIP']
        query_lines = []
        found_cypher = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with Cypher keyword
            if any(line.upper().startswith(keyword) for keyword in cypher_keywords):
                query_lines.append(line)
                found_cypher = True
            elif found_cypher and not line.startswith('//') and not line.lower().startswith('this'):
                # Continue with query if we've found Cypher and it's not a comment or explanation
                if any(keyword in line.upper() for keyword in cypher_keywords):
                    query_lines.append(line)
                else:
                    # Stop if we hit explanatory text
                    break
        
        # Join the query lines
        if query_lines:
            result = ' '.join(query_lines).strip()
        else:
            # Fallback: return cleaned text if no specific pattern found
            result = text.strip()
        
        # Fix quote issues: replace escaped double quotes with single quotes
        result = re.sub(r'\\"', "'", result)  # Replace \" with '
        result = re.sub(r'"([^"]*)"(?=\s*[})])', r"'\1'", result)  # Replace "value" with 'value' when followed by } or )
        
        return result


class CypherQueryGenerator:
    """Main class for generating Cypher queries from natural language using Gemini"""
    
    def __init__(self, 
                 gemini_api_key: Optional[str] = None,
                 model_name: str = "gemini-2.5-flash-lite",
                 temperature: float = 0.1):
        """
        Initialize the Cypher query generator with Gemini
        
        Args:
            gemini_api_key: Google Gemini API key (if not provided, will look for GEMINI_API_KEY env var)
            model_name: Gemini model to use
            temperature: Temperature for generation (lower = more deterministic)
        """
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass it directly.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        self.parser = CypherOutputParser()
        self.schema_info = ""
        
    def set_schema_info(self, schema_info: str):
        """
        Set Neo4j database schema information to improve query generation
        
        Args:
            schema_info: String containing information about nodes, relationships, and properties
        """
        self.schema_info = schema_info
    
    def get_neo4j_schema(self, uri: str, username: str, password: str) -> str:
        """
        Automatically retrieve schema information from Neo4j database
        
        Args:
            uri: Neo4j database URI
            username: Database username
            password: Database password
            
        Returns:
            Schema information as string
        """
        try:
            driver = GraphDatabase.driver(uri, auth=(username, password))
            
            with driver.session() as session:
                # Get node labels
                result = session.run("CALL db.labels()")
                labels = [record["label"] for record in result]
                
                # Get relationship types
                result = session.run("CALL db.relationshipTypes()")
                relationships = [record["relationshipType"] for record in result]
                
                # Get property keys
                result = session.run("CALL db.propertyKeys()")
                properties = [record["propertyKey"] for record in result]
                
                schema = f"""
                Node Labels: {', '.join(labels)}
                Relationship Types: {', '.join(relationships)}
                Property Keys: {', '.join(properties)}
                """
                
            driver.close()
            return schema.strip()
            
        except Exception as e:
            print(f"Warning: Could not retrieve schema from Neo4j: {e}")
            return ""
    
    def generate_cypher_query(self, user_query: str, context: str = "") -> str:
        """
        Generate a Cypher query from natural language input using Gemini
        
        Args:
            user_query: Natural language query from user
            context: Additional context about the data or query requirements
            
        Returns:
            Clean, runnable Cypher query
        """
        # Create the prompt
        prompt = f"""
You are an expert in Neo4j Cypher query language. Your task is to convert natural language questions into valid, runnable Cypher queries.

Database Schema Information:
{self.schema_info}

Additional Context:
{context}

Rules for generating Cypher queries:
1. Generate ONLY the Cypher query - no explanations, markdown, or additional text
2. Ensure the query is syntactically correct and runnable
3. Use proper Cypher syntax with correct keywords (MATCH, RETURN, WHERE, etc.)
4. ALWAYS use single quotes for string literals (e.g., 'John', 'Patient', '7') - NEVER use double quotes or escaped quotes
5. Use double quotes only for property names that contain spaces or special characters
6. Always assign variables to relationships when they might be referenced (e.g., -[r:RELATIONSHIP_TYPE]-> instead of -[:RELATIONSHIP_TYPE]->)
7. Include appropriate LIMIT clauses when returning multiple results (default LIMIT 25 unless specified otherwise)
8. Use case-insensitive matching where appropriate with CONTAINS(), LOWER(), or regex
9. Follow Neo4j best practices for performance
10. For numeric properties, use numbers without quotes (e.g., {{patient_id: 7}}, not {{patient_id: '7'}})
11. When uncertain about data types, prefer string matching for IDs unless clearly numeric

Examples of correct syntax:
- MATCH (p:Patient {{patient_id: 7}})-[r:TAKES_MEDICATION]->(m:Medication) RETURN m.medicine_name
- MATCH (p:Person)-[r:HAS_CONDITION]->(c:Condition) WHERE p.name = 'John Smith' RETURN c.condition_name
- MATCH (n)-[r:RELATIONSHIP_TYPE]->(m) WHERE LOWER(n.property) CONTAINS LOWER('search_term') RETURN n, r, m LIMIT 10

User Question: {user_query}

Generate the Cypher query:"""

        # Generate using Gemini
        try:
            response = self.model.generate_content(prompt)
            cypher_query = self.parser.parse(response.text)
            return cypher_query
            
        except Exception as e:
            raise Exception(f"Error generating Cypher query with Gemini: {e}")
    
    def validate_cypher_syntax(self, cypher_query: str) -> bool:
        """
        Basic syntax validation for Cypher queries
        
        Args:
            cypher_query: The Cypher query to validate
            
        Returns:
            True if basic syntax appears valid, False otherwise
        """
        # Basic checks for Cypher syntax
        cypher_query = cypher_query.strip().upper()
        
        # Must contain at least one Cypher keyword
        cypher_keywords = ['MATCH', 'CREATE', 'MERGE', 'DELETE', 'SET', 'REMOVE', 'RETURN']
        if not any(keyword in cypher_query for keyword in cypher_keywords):
            return False
        
        # Basic bracket matching
        if cypher_query.count('(') != cypher_query.count(')'):
            return False
        if cypher_query.count('[') != cypher_query.count(']'):
            return False
        if cypher_query.count('{') != cypher_query.count('}'):
            return False
        
        return True


def create_cypher_generator(gemini_api_key: Optional[str] = None,
                          model_name: str = "gemini-2.0-flash-exp") -> CypherQueryGenerator:
    """
    Convenience function to create a CypherQueryGenerator instance
    
    Args:
        gemini_api_key: Google Gemini API key
        model_name: Gemini model to use
        
    Returns:
        Configured CypherQueryGenerator instance
    """
    return CypherQueryGenerator(gemini_api_key=gemini_api_key, model_name=model_name)


def generate_cypher_from_text(user_query: str, 
                            schema_info: str = "",
                            gemini_api_key: Optional[str] = None) -> str:
    """
    Simple function to generate Cypher query from text input using Gemini
    
    Args:
        user_query: Natural language query
        schema_info: Neo4j schema information
        gemini_api_key: Google Gemini API key
        
    Returns:
        Generated Cypher query
    """
    generator = create_cypher_generator(gemini_api_key)
    if schema_info:
        generator.set_schema_info(schema_info)
    
    return generator.generate_cypher_query(user_query)


if __name__ == "__main__":
    # Example usage
    try:
        # Initialize the generator
        generator = CypherQueryGenerator()
        
        # Example schema (you can set this based on your Neo4j database)
        sample_schema = """
        Node Labels: Person, Movie, Director, Actor
        Relationship Types: ACTED_IN, DIRECTED, FOLLOWS, LIKES
        Property Keys: name, title, year, born, rating
        """
        generator.set_schema_info(sample_schema)
        
        # Example queries
        test_queries = [
            "Find all movies released in 2020",
            "Show me actors who worked with Tom Hanks",
            "Get the top 5 highest rated movies",
            "Find directors born before 1960"
        ]
        
        print("=== Gemini Cypher Query Generator Examples ===\n")
        
        for query in test_queries:
            print(f"Natural Language: {query}")
            try:
                cypher_query = generator.generate_cypher_query(query)
                print(f"Generated Cypher: {cypher_query}")
                print(f"Syntax Valid: {generator.validate_cypher_syntax(cypher_query)}")
            except Exception as e:
                print(f"Error: {e}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Setup Error: {e}")
        print("Make sure to set your GEMINI_API_KEY environment variable.")
