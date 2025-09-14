#!/usr/bin/env python3
"""
AuraDB Connection Test Script
Test your Neo4j AuraDB connection and credentials.
"""

import logging
import os
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = '.env'
    if os.path.exists(env_file):
        logger.info(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def test_auradb_connection():
    """Test connection to Neo4j AuraDB."""
    logger.info("🔍 Testing Neo4j AuraDB connection...")
    
    # Load .env file if it exists
    load_env_file()
    
    # Get credentials from environment
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME') 
    password = os.getenv('NEO4J_PASSWORD')
    
    # Check if credentials are set
    if not uri:
        logger.error("❌ NEO4J_URI not set")
        return False
    if not username:
        logger.error("❌ NEO4J_USERNAME not set")
        return False
    if not password:
        logger.error("❌ NEO4J_PASSWORD not set")
        return False
    
    logger.info(f"🌐 URI: {uri}")
    logger.info(f"👤 Username: {username}")
    logger.info(f"🔑 Password: {'*' * len(password)}")
    
    try:
        # Test connection
        logger.info("🔌 Attempting connection...")
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        # Verify connectivity
        driver.verify_connectivity()
        logger.info("✅ Connection successful!")
        
        # Test a simple query
        with driver.session() as session:
            result = session.run("RETURN 'Hello AuraDB!' as message, datetime() as timestamp")
            record = result.single()
            if record:
                logger.info(f"📩 Test query result: {record['message']}")
                logger.info(f"⏰ Server time: {record['timestamp']}")
            
            # Get database info
            try:
                db_info = session.run("CALL dbms.components() YIELD name, versions, edition")
                for record in db_info:
                    logger.info(f"🗄️  Database: {record['name']} {record['versions'][0]} ({record['edition']})")
            except Exception as e:
                logger.info(f"ℹ️  Database info not available: {e}")
            
            # Count existing data
            try:
                node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                logger.info(f"📊 Current data: {node_count} nodes, {rel_count} relationships")
            except Exception as e:
                logger.info(f"ℹ️  Could not count existing data: {e}")
        
        driver.close()
        logger.info("🎉 AuraDB connection test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "authentication" in error_str or "credentials" in error_str:
            logger.info("💡 Authentication failed - check username/password")
        elif "ssl" in error_str or "certificate" in error_str:
            logger.info("💡 SSL issue - ensure you're using neo4j+s:// for AuraDB")
        elif "connection refused" in error_str or "cannot connect" in error_str:
            logger.info("💡 Connection refused - check if AuraDB instance is running")
            logger.info("   Also check if your IP is whitelisted in AuraDB console")
        elif "routing" in error_str:
            logger.info("💡 Routing issue - try using bolt+s:// instead of neo4j+s://")
        
        return False

def show_setup_help():
    """Show help for setting up environment variables."""
    logger.info("\n" + "="*60)
    logger.info("SETUP INSTRUCTIONS")
    logger.info("="*60)
    
    logger.info("\n🔧 Option 1: Set environment variables in PowerShell")
    logger.info('$env:NEO4J_URI="neo4j+s://your-instance.databases.neo4j.io"')
    logger.info('$env:NEO4J_USERNAME="neo4j"')
    logger.info('$env:NEO4J_PASSWORD="your-password"')
    
    logger.info("\n🔧 Option 2: Create .env file")
    logger.info("Create a file named '.env' with:")
    logger.info("NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io")
    logger.info("NEO4J_USERNAME=neo4j")
    logger.info("NEO4J_PASSWORD=your-password")
    
    logger.info("\n📋 AuraDB Connection Details:")
    logger.info("1. Log into https://console.neo4j.io")
    logger.info("2. Click on your database instance")
    logger.info("3. Copy the connection URI (starts with neo4j+s://)")
    logger.info("4. Use 'neo4j' as username (default)")
    logger.info("5. Use the password you set when creating the instance")
    
    logger.info("\n🔒 Security Notes:")
    logger.info("• Ensure your IP is whitelisted in AuraDB console")
    logger.info("• Use neo4j+s:// (secure) for AuraDB connections")
    logger.info("• Never commit credentials to version control")

def main():
    """Main function."""
    logger.info("🚀 Neo4j AuraDB Connection Test")
    logger.info("="*50)
    
    success = test_auradb_connection()
    
    if not success:
        show_setup_help()
    else:
        logger.info("\n✅ Your AuraDB connection is working!")
        logger.info("You can now run: python auradb_import.py")

if __name__ == "__main__":
    main()