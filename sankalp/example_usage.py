"""
Example usage of the Cypher Query Generator
This file demonstrates how to use the CypherQueryGenerator class
"""

import os
from cypher import CypherQueryGenerator, generate_cypher_from_text

def main():
    """Main function demonstrating various usage patterns"""
    
    print("=== Cypher Query Generator Demo ===\n")
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key to run this demo.")
        print("You can set it with: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    try:
        # Method 1: Using the main class
        print("Method 1: Using CypherQueryGenerator class")
        print("-" * 40)
        
        generator = CypherQueryGenerator(temperature=0.0)  # Low temperature for consistent results
        
        # Set schema information for better query generation
        medical_schema = """
        Node Labels: Patient, Doctor, Disease, Treatment, Hospital, Medication
        Relationship Types: DIAGNOSED_WITH, TREATED_BY, WORKS_AT, PRESCRIBED, LOCATED_IN
        Property Keys: name, age, gender, specialization, address, dosage, date, severity
        """
        generator.set_schema_info(medical_schema)
        
        medical_queries = [
            "Find all patients diagnosed with diabetes",
            "Show doctors who specialize in cardiology",
            "Get medications prescribed for high blood pressure",
            "List hospitals in New York",
            "Find patients over 65 years old"
        ]
        
        for query in medical_queries:
            print(f"Query: {query}")
            cypher = generator.generate_cypher_query(query)
            print(f"Cypher: {cypher}")
            print(f"Valid: {generator.validate_cypher_syntax(cypher)}")
            print()
        
        print("\n" + "="*60 + "\n")
        
        # Method 2: Using the simple function
        print("Method 2: Using simple function")
        print("-" * 40)
        
        simple_queries = [
            "Find all nodes with name containing 'John'",
            "Show relationships between Person nodes",
            "Get nodes created in the last month"
        ]
        
        for query in simple_queries:
            print(f"Query: {query}")
            cypher = generate_cypher_from_text(query)
            print(f"Cypher: {cypher}")
            print()
            
        print("\n" + "="*60 + "\n")
        
        # Method 3: Interactive mode
        print("Method 3: Interactive Mode")
        print("-" * 40)
        print("Enter your natural language queries (type 'quit' to exit):")
        
        while True:
            user_input = input("\nYour query: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                try:
                    cypher = generator.generate_cypher_query(user_input)
                    print(f"Generated Cypher: {cypher}")
                    
                    if generator.validate_cypher_syntax(cypher):
                        print("✅ Syntax appears valid")
                    else:
                        print("⚠️  Syntax may have issues")
                        
                except Exception as e:
                    print(f"Error: {e}")
        
    except Exception as e:
        print(f"Error initializing generator: {e}")


def test_with_neo4j_connection():
    """
    Example of how to use the generator with actual Neo4j database
    Uncomment and modify connection details to test with real database
    """
    
    # Uncomment and modify these connection details
    # NEO4J_URI = "bolt://localhost:7687"
    # NEO4J_USERNAME = "neo4j"
    # NEO4J_PASSWORD = "your-password"
    
    # try:
    #     generator = CypherQueryGenerator()
    #     
    #     # Automatically get schema from database
    #     schema = generator.get_neo4j_schema(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
    #     generator.set_schema_info(schema)
    #     
    #     # Generate and test query
    #     user_query = "Find all nodes"
    #     cypher_query = generator.generate_cypher_query(user_query)
    #     
    #     print(f"Query: {user_query}")
    #     print(f"Generated Cypher: {cypher_query}")
    #     
    #     # Optionally, you could execute the query here
    #     # from neo4j import GraphDatabase
    #     # driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    #     # with driver.session() as session:
    #     #     result = session.run(cypher_query)
    #     #     for record in result:
    #     #         print(record)
    #     
    # except Exception as e:
    #     print(f"Error connecting to Neo4j: {e}")
    
    print("Neo4j connection example is commented out.")
    print("Uncomment and modify connection details in test_with_neo4j_connection() to test with real database.")


if __name__ == "__main__":
    main()
    print("\n" + "="*60 + "\n")
    test_with_neo4j_connection()