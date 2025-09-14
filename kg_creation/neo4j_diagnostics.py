#!/usr/bin/env python3
"""
Neo4j Connection Diagnostics Script
This script helps diagnose and fix Neo4j connection issues.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_neo4j_installation():
    """Check if Neo4j is installed and running."""
    logger.info("Checking Neo4j installation...")
    
    try:
        import subprocess
        
        # Check if Neo4j service is running (Windows)
        result = subprocess.run(['sc', 'query', 'Neo4j'], 
                              capture_output=True, text=True, shell=True)
        
        if 'RUNNING' in result.stdout:
            logger.info("✓ Neo4j service is running")
        else:
            logger.warning("⚠ Neo4j service is not running")
            logger.info("To start Neo4j:")
            logger.info("  - Option 1: Open Neo4j Desktop and start your database")
            logger.info("  - Option 2: Run 'neo4j start' in command prompt (if installed via command line)")
            logger.info("  - Option 3: Start the Neo4j service in Windows Services")
            
    except Exception as e:
        logger.warning(f"Could not check Neo4j service status: {e}")

def check_python_driver():
    """Check if Neo4j Python driver is installed."""
    logger.info("Checking Neo4j Python driver...")
    
    try:
        import neo4j
        logger.info(f"✓ Neo4j Python driver installed (version: {neo4j.__version__})")
        return True
    except ImportError:
        logger.error("✗ Neo4j Python driver not installed")
        logger.info("To install: pip install neo4j")
        return False

def test_connection(uri="bolt://localhost:7687", username="neo4j", password="password"):
    """Test connection to Neo4j database."""
    logger.info(f"Testing connection to {uri}...")
    
    try:
        from neo4j import GraphDatabase
        
        # Try to connect
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        
        # Test a simple query
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            if record and record["test"] == 1:
                logger.info("✓ Neo4j connection successful!")
                
                # Get database info
                result = session.run("CALL dbms.components() YIELD name, versions, edition")
                for record in result:
                    logger.info(f"  Database: {record['name']} {record['versions'][0]} ({record['edition']})")
                
                driver.close()
                return True
            
    except Exception as e:
        logger.error(f"✗ Neo4j connection failed: {e}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "authentication" in error_str or "credentials" in error_str:
            logger.info("💡 Authentication issue - check username/password")
            logger.info("   Default: username='neo4j', password='neo4j' (change on first login)")
        elif "connection refused" in error_str or "cannot connect" in error_str:
            logger.info("💡 Connection refused - Neo4j may not be running")
            logger.info("   Check if Neo4j is started and listening on the correct port")
        elif "ssl" in error_str or "certificate" in error_str:
            logger.info("💡 SSL/Certificate issue - try different connection URI")
            logger.info("   For local: bolt://localhost:7687")
            logger.info("   For remote: neo4j+s://your-instance.databases.neo4j.io")
        
        return False

def create_connection_config():
    """Create a configuration file for Neo4j connection."""
    config_content = """# Neo4j Connection Configuration
# Update these values with your actual Neo4j settings

[DEFAULT]
# For local Neo4j installation
NEO4J_URI = bolt://localhost:7687
NEO4J_USERNAME = neo4j
NEO4J_PASSWORD = password

# For Neo4j Aura (cloud)
# NEO4J_URI = neo4j+s://your-instance.databases.neo4j.io
# NEO4J_USERNAME = neo4j
# NEO4J_PASSWORD = your-password

# For Neo4j Enterprise with different ports
# NEO4J_URI = bolt://localhost:7688
# NEO4J_USERNAME = neo4j
# NEO4J_PASSWORD = your-password
"""
    
    with open('neo4j_config.ini', 'w') as f:
        f.write(config_content)
    
    logger.info("✓ Created neo4j_config.ini - update it with your credentials")

def get_connection_suggestions():
    """Provide suggestions for fixing Neo4j connection."""
    logger.info("\n" + "="*60)
    logger.info("NEO4J CONNECTION TROUBLESHOOTING GUIDE")
    logger.info("="*60)
    
    logger.info("\n1. INSTALLATION CHECK:")
    logger.info("   • Download Neo4j Desktop from: https://neo4j.com/download/")
    logger.info("   • Or install via command line: choco install neo4j-community (Windows)")
    
    logger.info("\n2. STARTING NEO4J:")
    logger.info("   • Neo4j Desktop: Create/Start a database project")
    logger.info("   • Command line: neo4j start")
    logger.info("   • Windows Service: Start 'Neo4j' service")
    
    logger.info("\n3. DEFAULT CREDENTIALS:")
    logger.info("   • Username: neo4j")
    logger.info("   • Default Password: neo4j (you'll be prompted to change it)")
    logger.info("   • After first login, use your new password")
    
    logger.info("\n4. CONNECTION URIS:")
    logger.info("   • Local: bolt://localhost:7687")
    logger.info("   • Local with encryption: neo4j://localhost:7687")
    logger.info("   • Neo4j Aura: neo4j+s://xxx.databases.neo4j.io")
    
    logger.info("\n5. PYTHON DRIVER:")
    logger.info("   • Install: pip install neo4j")
    logger.info("   • Verify: python -c \"import neo4j; print(neo4j.__version__)\"")
    
    logger.info("\n6. FIREWALL/NETWORK:")
    logger.info("   • Ensure port 7687 is open")
    logger.info("   • Check Windows Firewall settings")
    logger.info("   • For cloud instances, check security groups")

def main():
    """Main diagnostic function."""
    logger.info("Neo4j Connection Diagnostics Starting...")
    logger.info("="*50)
    
    # Check Neo4j installation
    check_neo4j_installation()
    print()
    
    # Check Python driver
    if not check_python_driver():
        logger.info("\nInstalling Neo4j driver...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'neo4j'])
            logger.info("✓ Neo4j driver installed successfully")
        except Exception as e:
            logger.error(f"Failed to install neo4j driver: {e}")
            return
    print()
    
    # Test connection with default settings
    success = test_connection()
    print()
    
    # If connection failed, try common alternatives
    if not success:
        logger.info("Trying alternative connection settings...")
        
        # Try with default neo4j password
        success = test_connection(password="neo4j")
        
        if not success:
            # Try different URI
            success = test_connection(uri="neo4j://localhost:7687")
        
        if not success:
            # Try different port
            success = test_connection(uri="bolt://localhost:7688")
    
    # Create config file
    create_connection_config()
    print()
    
    # Show troubleshooting guide
    if not success:
        get_connection_suggestions()
    else:
        logger.info("🎉 Neo4j connection is working! You can now run:")
        logger.info("   python neo4j_import.py")

if __name__ == "__main__":
    main()