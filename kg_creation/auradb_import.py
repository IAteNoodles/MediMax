#!/usr/bin/env python3
"""
Neo4j Knowledge Graph Import Script for MediMax (AuraDB Compatible)
This script connects to Neo4j AuraDB and imports the generated knowledge graph data.
"""

import logging
import csv
import os
import sys
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuraDBImporter:
    def __init__(self):
        """Initialize Neo4j AuraDB connection using environment variables."""
        try:
            # Get credentials from environment variables
            self.uri = os.getenv('NEO4J_URI')
            self.username = os.getenv('NEO4J_USERNAME') 
            self.password = os.getenv('NEO4J_PASSWORD')
            
            if not all([self.uri, self.username, self.password]):
                raise ValueError("Missing Neo4j credentials in environment variables")
            
            logger.info(f"Connecting to AuraDB at: {self.uri}")
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            self.driver.verify_connectivity()
            logger.info("✓ Successfully connected to Neo4j AuraDB")
            
        except Exception as e:
            logger.error(f"✗ Failed to connect to Neo4j AuraDB: {e}")
            logger.info("\nTo fix this, set environment variables:")
            logger.info("  NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io")
            logger.info("  NEO4J_USERNAME=neo4j")
            logger.info("  NEO4J_PASSWORD=your-password")
            raise
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        logger.info("Clearing existing data from AuraDB...")
        with self.driver.session() as session:
            # Delete in batches to avoid memory issues
            while True:
                result = session.run("MATCH (n) WITH n LIMIT 1000 DETACH DELETE n RETURN count(n) as deleted")
                deleted = result.single()["deleted"]
                if deleted == 0:
                    break
                logger.info(f"Deleted {deleted} nodes...")
        logger.info("✓ Database cleared")
    
    def create_indexes(self):
        """Create indexes for better performance."""
        logger.info("Creating indexes...")
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX nodeId_index IF NOT EXISTS FOR (n) ON (n.nodeId)",
                "CREATE INDEX patient_nodeId IF NOT EXISTS FOR (n:Patient) ON (n.nodeId)",
                "CREATE INDEX symptom_nodeId IF NOT EXISTS FOR (n:Symptom) ON (n.nodeId)",
                "CREATE INDEX medication_nodeId IF NOT EXISTS FOR (n:Medication) ON (n.nodeId)",
                "CREATE INDEX labtest_nodeId IF NOT EXISTS FOR (n:LabTest) ON (n.nodeId)",
                "CREATE INDEX encounter_nodeId IF NOT EXISTS FOR (n:Encounter) ON (n.nodeId)"
            ]
            
            for index_query in indexes:
                try:
                    session.run(index_query)
                except Exception as e:
                    logger.warning(f"Index creation warning: {e}")
        
        logger.info("✓ Indexes created")
    
    def import_nodes(self, nodes_file):
        """Import nodes from CSV file (no APOC required)."""
        logger.info(f"Importing nodes from {nodes_file}")
        
        with open(nodes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            nodes_data = list(reader)
        
        logger.info(f"Found {len(nodes_data)} nodes to import")
        
        with self.driver.session() as session:
            batch_size = 50
            imported_count = 0
            
            for i in range(0, len(nodes_data), batch_size):
                batch = nodes_data[i:i + batch_size]
                
                for node_data in batch:
                    label = node_data['label:LABEL']
                    query = f"""
                        CREATE (n:{label} {{
                            nodeId: $nodeId,
                            name: $name,
                            dob: $dob,
                            sex: $sex,
                            remarks: $remarks,
                            type: $type,
                            date: $date,
                            status: $status,
                            details: $details,
                            historical: $historical
                        }})
                        RETURN n.nodeId as created_id
                    """
                    
                    try:
                        result = session.run(query, {
                            'nodeId': node_data['nodeId:ID'],
                            'name': node_data['name'],
                            'dob': node_data['dob'] or None,
                            'sex': node_data['sex'] or None,
                            'remarks': node_data['remarks'] or None,
                            'type': node_data['type'] or None,
                            'date': node_data['date'] or None,
                            'status': node_data['status'] or None,
                            'details': node_data['details'] or None,
                            'historical': node_data['historical:boolean'] == 'true'
                        })
                        
                        if result.single():
                            imported_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error creating node {node_data['nodeId:ID']}: {e}")
                
                logger.info(f"Imported batch {i//batch_size + 1}: processed {len(batch)} nodes (Total successful: {imported_count})")
        
        logger.info(f"✓ Imported {imported_count} nodes successfully")
    
    def import_relationships(self, rels_file):
        """Import relationships from CSV file (AuraDB compatible)."""
        logger.info(f"Importing relationships from {rels_file}")
        
        with open(rels_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rels_data = list(reader)
        
        logger.info(f"Found {len(rels_data)} relationships to import")
        
        with self.driver.session() as session:
            batch_size = 50
            imported_count = 0
            
            for i in range(0, len(rels_data), batch_size):
                batch = rels_data[i:i + batch_size]
                
                # Create relationships without APOC
                for rel_data in batch:
                    rel_type = rel_data[':TYPE']
                    start_id = rel_data[':START_ID']
                    end_id = rel_data[':END_ID']
                    
                    query = f"""
                        MATCH (start_node {{nodeId: $start_id}})
                        MATCH (end_node {{nodeId: $end_id}})
                        CREATE (start_node)-[r:{rel_type} {{
                            date: $date,
                            status: $status
                        }}]->(end_node)
                        RETURN r
                    """
                    
                    try:
                        result = session.run(query, {
                            'start_id': start_id,
                            'end_id': end_id,
                            'date': rel_data['date'],
                            'status': rel_data['status']
                        })
                        
                        if result.single():
                            imported_count += 1
                        else:
                            logger.warning(f"Failed to create relationship: {start_id} -[{rel_type}]-> {end_id}")
                            
                    except Exception as e:
                        logger.error(f"Error creating relationship {start_id} -[{rel_type}]-> {end_id}: {e}")
                
                logger.info(f"Imported batch {i//batch_size + 1}: processed {len(batch)} relationships (Total successful: {imported_count})")
        
        logger.info(f"✓ Imported {imported_count} relationships successfully")
    
    def verify_import(self):
        """Verify the imported data."""
        logger.info("Verifying import...")
        
        with self.driver.session() as session:
            # Count nodes by label
            result = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as label, count(n) as count 
                ORDER BY count DESC
            """)
            
            logger.info("📊 Imported data summary:")
            total_nodes = 0
            for record in result:
                label = record['label']
                count = record['count']
                total_nodes += count
                logger.info(f"  {label}: {count} nodes")
            
            # Count relationships
            rel_result = session.run("""
                MATCH ()-[r]->() 
                RETURN type(r) as rel_type, count(r) as count 
                ORDER BY count DESC
            """)
            
            logger.info("🔗 Relationships:")
            total_rels = 0
            for record in rel_result:
                rel_type = record['rel_type']
                count = record['count']
                total_rels += count
                logger.info(f"  {rel_type}: {count} relationships")
            
            logger.info(f"📈 Total: {total_nodes} nodes, {total_rels} relationships")
            
            # Additional verification queries
            if total_rels == 0:
                logger.warning("⚠️  No relationships found! Checking node connectivity...")
                
                # Check if nodes exist
                node_sample = session.run("MATCH (n) RETURN n.nodeId as nodeId, labels(n)[0] as label LIMIT 5")
                logger.info("Sample nodes:")
                for record in node_sample:
                    logger.info(f"  {record['nodeId']} ({record['label']})")
            
            return total_nodes, total_rels

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
        return True
    return False

def check_environment():
    """Check if environment variables are set."""
    required_vars = ['NEO4J_URI', 'NEO4J_USERNAME', 'NEO4J_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error("❌ Missing environment variables:")
        for var in missing_vars:
            logger.error(f"  {var}")
        
        logger.info("\n💡 To set environment variables in PowerShell:")
        logger.info("  $env:NEO4J_URI='neo4j+s://your-instance.databases.neo4j.io'")
        logger.info("  $env:NEO4J_USERNAME='neo4j'")
        logger.info("  $env:NEO4J_PASSWORD='your-password'")
        
        logger.info("\n💡 Or create a .env file with:")
        logger.info("  NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io")
        logger.info("  NEO4J_USERNAME=neo4j")
        logger.info("  NEO4J_PASSWORD=your-password")
        
        return False
    
    logger.info("✓ Environment variables found")
    return True

def main():
    """Main function to run the import."""
    logger.info("🚀 Starting Neo4j AuraDB import...")
    
    # Load .env file if it exists
    load_env_file()
    
    # Check environment variables
    if not check_environment():
        return
    
    # File paths
    NODES_FILE = "neo4j_nodes.csv"
    RELATIONSHIPS_FILE = "neo4j_relationships.csv"
    
    # Check if files exist
    if not os.path.exists(NODES_FILE):
        logger.error(f"❌ Nodes file not found: {NODES_FILE}")
        logger.info("Run 'python unified_export.py' to generate the files")
        return
    
    if not os.path.exists(RELATIONSHIPS_FILE):
        logger.error(f"❌ Relationships file not found: {RELATIONSHIPS_FILE}")
        logger.info("Run 'python unified_export.py' to generate the files")
        return
    
    # Import data
    importer = None
    try:
        importer = AuraDBImporter()
        
        # Clear existing data (comment out if you want to keep existing data)
        confirm = input("⚠️  Clear existing data? (y/N): ").strip().lower()
        if confirm == 'y':
            importer.clear_database()
        
        # Create indexes first
        importer.create_indexes()
        
        # Import nodes
        importer.import_nodes(NODES_FILE)
        
        # Import relationships
        importer.import_relationships(RELATIONSHIPS_FILE)
        
        # Verify import
        nodes_count, rels_count = importer.verify_import()
        
        if nodes_count > 0 and rels_count > 0:
            logger.info("🎉 Import completed successfully!")
        elif nodes_count > 0:
            logger.warning("⚠️  Nodes imported but no relationships. Check node IDs in CSV files.")
        else:
            logger.error("❌ Import failed - no data imported")
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if importer:
            importer.close()

if __name__ == "__main__":
    main()