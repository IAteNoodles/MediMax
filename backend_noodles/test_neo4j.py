#!/usr/bin/env python3
"""
Neo4j Connection Test
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

def test_neo4j_connection():
    # Load environment variables
    load_dotenv(dotenv_path=os.path.join('..', '.env'))
    
    print('🧪 Testing Neo4j Connection...')
    print('=' * 40)
    
    aura_user = os.getenv('AURA_USER')
    aura_password = os.getenv('AURA_PASSWORD')
    
    print(f'AURA_USER: {aura_user}')
    print(f'AURA_PASSWORD: {"*" * len(aura_password) if aura_password else "NOT SET"}')
    
    try:
        driver = GraphDatabase.driver(
            'neo4j+s://98d1982d.databases.neo4j.io',
            auth=(aura_user, aura_password)
        )
        
        # Test the connection
        with driver.session() as session:
            result = session.run('RETURN "Hello, Neo4j!" AS message')
            record = result.single()
            print(f'✅ Neo4j connection successful: {record["message"]}')
            
            # Test creating and deleting a test node
            session.run('CREATE (test:TestNode {name: "connection_test"})')
            result = session.run('MATCH (test:TestNode {name: "connection_test"}) RETURN test.name AS name')
            record = result.single()
            print(f'✅ Test node created: {record["name"]}')
            
            # Clean up test node
            session.run('MATCH (test:TestNode {name: "connection_test"}) DELETE test')
            print('✅ Test node cleaned up')
        
        driver.close()
        print('✅ Neo4j authentication and operations working correctly')
        return True
        
    except Exception as e:
        print(f'❌ Neo4j connection failed: {e}')
        return False

if __name__ == "__main__":
    test_neo4j_connection()