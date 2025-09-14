#!/usr/bin/env python3
"""
Complete Knowledge Graph Rebuild for AuraDB
This script recreates the entire knowledge graph with proper connections for all patients.
"""

import logging
import os
import csv
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_paths = ['.env', '../.env']
    
    for env_file in env_paths:
        if os.path.exists(env_file):
            logger.info(f"Loading environment variables from {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"')
            return True
    return False

class CompleteGraphBuilder:
    def __init__(self):
        """Initialize connection to AuraDB."""
        load_env_file()
        
        uri = os.getenv('NEO4J_URI')
        username = os.getenv('NEO4J_USERNAME')
        password = os.getenv('NEO4J_PASSWORD')
        
        logger.info(f"Connecting to: {uri}")
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("✅ Connected to AuraDB")
    
    def close(self):
        """Close connection."""
        if self.driver:
            self.driver.close()
    
    def clear_and_rebuild(self):
        """Clear existing data and rebuild the complete knowledge graph."""
        logger.info("🗑️ Clearing existing MediMax data...")
        
        with self.driver.session() as session:
            # Delete all MediMax nodes and relationships
            result = session.run("""
                MATCH (n)
                WHERE n.nodeId IS NOT NULL AND (
                    n.nodeId STARTS WITH 'patient_' OR 
                    n.nodeId STARTS WITH 'symptom_' OR 
                    n.nodeId STARTS WITH 'medication_' OR 
                    n.nodeId STARTS WITH 'encounter_' OR 
                    n.nodeId STARTS WITH 'labtest_'
                )
                DETACH DELETE n
                RETURN count(n) as deleted
            """).single()
            
            logger.info(f"✅ Deleted {result['deleted']} existing MediMax nodes")
    
    def rebuild_from_csv(self):
        """Rebuild the complete graph from CSV files."""
        logger.info("🔄 Rebuilding knowledge graph from CSV files...")
        
        # First, reimport nodes
        self.import_nodes_fresh()
        
        # Then, reimport relationships
        self.import_relationships_fresh()
    
    def import_nodes_fresh(self):
        """Import all nodes from CSV."""
        logger.info("📥 Importing nodes...")
        
        nodes_file = "neo4j_nodes.csv"
        if not os.path.exists(nodes_file):
            logger.error(f"❌ Nodes file not found: {nodes_file}")
            return
        
        with open(nodes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            nodes_data = list(reader)
        
        with self.driver.session() as session:
            imported_count = 0
            
            for node_data in nodes_data:
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
                        if imported_count % 10 == 0:
                            logger.info(f"  Imported {imported_count} nodes...")
                    
                except Exception as e:
                    logger.error(f"Error creating node {node_data['nodeId:ID']}: {e}")
        
        logger.info(f"✅ Imported {imported_count} nodes")
    
    def import_relationships_fresh(self):
        """Import all relationships from CSV."""
        logger.info("🔗 Importing relationships...")
        
        rels_file = "neo4j_relationships.csv"
        if not os.path.exists(rels_file):
            logger.error(f"❌ Relationships file not found: {rels_file}")
            return
        
        with open(rels_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rels_data = list(reader)
        
        with self.driver.session() as session:
            imported_count = 0
            failed_count = 0
            
            for rel_data in rels_data:
                rel_type = rel_data[':TYPE'].upper().replace(' ', '_')  # Standardize relationship types
                start_id = rel_data[':START_ID']
                end_id = rel_data[':END_ID']
                
                query = f"""
                    MATCH (start {{nodeId: $start_id}})
                    MATCH (end {{nodeId: $end_id}})
                    MERGE (start)-[r:{rel_type} {{
                        date: $date,
                        status: $status
                    }}]->(end)
                    RETURN r
                """
                
                try:
                    result = session.run(query, {
                        'start_id': start_id,
                        'end_id': end_id,
                        'date': rel_data['date'] or None,
                        'status': rel_data['status'] or None
                    })
                    
                    if result.single():
                        imported_count += 1
                        if imported_count % 10 == 0:
                            logger.info(f"  Created {imported_count} relationships...")
                    else:
                        failed_count += 1
                        logger.warning(f"Failed: {start_id} -[{rel_type}]-> {end_id}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error creating {start_id} -[{rel_type}]-> {end_id}: {e}")
        
        logger.info(f"✅ Created {imported_count} relationships")
        if failed_count > 0:
            logger.warning(f"⚠️ Failed to create {failed_count} relationships")
    
    def verify_complete_graph(self):
        """Verify the complete knowledge graph structure."""
        logger.info("📊 Verifying complete knowledge graph...")
        
        with self.driver.session() as session:
            # Count nodes by type
            node_result = session.run("""
                MATCH (n)
                WHERE n.nodeId IS NOT NULL
                RETURN labels(n)[0] as label, count(n) as count
                ORDER BY count DESC
            """)
            
            logger.info("\n🏷️ Node counts:")
            total_nodes = 0
            for record in node_result:
                label = record['label']
                count = record['count']
                total_nodes += count
                logger.info(f"  {label}: {count}")
            
            # Count relationships by type
            rel_result = session.run("""
                MATCH (start)-[r]->(end)
                WHERE start.nodeId IS NOT NULL AND end.nodeId IS NOT NULL
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)
            
            logger.info("\n🔗 Relationship counts:")
            total_rels = 0
            for record in rel_result:
                rel_type = record['rel_type']
                count = record['count']
                total_rels += count
                logger.info(f"  {rel_type}: {count}")
            
            logger.info(f"\n📈 Total: {total_nodes} nodes, {total_rels} relationships")
            
            # Show patient connectivity
            patient_result = session.run("""
                MATCH (p:Patient)-[r]->()
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN p.name as patient, count(r) as connections
                ORDER BY connections DESC
            """)
            
            logger.info("\n👥 Patient connectivity:")
            for record in patient_result:
                logger.info(f"  {record['patient']}: {record['connections']} connections")
            
            # Show sample paths
            logger.info("\n🔍 Sample connected paths:")
            
            # Patient -> Medication paths
            med_paths = session.run("""
                MATCH (p:Patient)-[r:PRESCRIBED_MEDICATION]->(m:Medication)
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN p.name as patient, m.name as medication
                LIMIT 5
            """)
            
            logger.info("  Medication prescriptions:")
            for record in med_paths:
                logger.info(f"    {record['patient']} -> {record['medication']}")
            
            # Patient -> Symptom paths
            symptom_paths = session.run("""
                MATCH (p:Patient)-[r:HAS_SYMPTOM]->(s:Symptom)
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN p.name as patient, s.name as symptom
                LIMIT 5
            """)
            
            logger.info("  Patient symptoms:")
            for record in symptom_paths:
                logger.info(f"    {record['patient']} -> {record['symptom']}")
            
            return total_nodes, total_rels
    
    def create_indexes(self):
        """Create indexes for better performance."""
        logger.info("🔧 Creating indexes...")
        
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX nodeId_general IF NOT EXISTS FOR (n) ON (n.nodeId)",
                "CREATE INDEX patient_name IF NOT EXISTS FOR (n:Patient) ON (n.name)",
                "CREATE INDEX symptom_name IF NOT EXISTS FOR (n:Symptom) ON (n.name)",
                "CREATE INDEX medication_name IF NOT EXISTS FOR (n:Medication) ON (n.name)",
            ]
            
            for index_query in indexes:
                try:
                    session.run(index_query)
                    logger.info(f"  ✅ Index created")
                except Exception as e:
                    logger.warning(f"  ⚠️ Index warning: {e}")

def main():
    """Main rebuild function."""
    logger.info("🚀 Complete Knowledge Graph Rebuild")
    logger.info("="*50)
    
    builder = None
    try:
        builder = CompleteGraphBuilder()
        
        # Confirm rebuild
        print("⚠️ This will delete and recreate the entire MediMax knowledge graph.")
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            logger.info("❌ Rebuild cancelled")
            return
        
        # Clear and rebuild
        builder.clear_and_rebuild()
        
        # Create indexes
        builder.create_indexes()
        
        # Rebuild from CSV
        builder.rebuild_from_csv()
        
        # Verify results
        nodes_count, rels_count = builder.verify_complete_graph()
        
        if nodes_count > 0 and rels_count > 0:
            logger.info("\n🎉 Knowledge graph rebuild completed successfully!")
            logger.info("Your graph is now fully connected!")
            logger.info("\n🌐 You can now:")
            logger.info("  - View the graph in Neo4j Browser")
            logger.info("  - Run Cypher queries")
            logger.info("  - Explore patient relationships")
        else:
            logger.error("❌ Rebuild failed - no data created")
        
    except Exception as e:
        logger.error(f"❌ Rebuild failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if builder:
            builder.close()

if __name__ == "__main__":
    main()