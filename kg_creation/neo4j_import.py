#!/usr/bin/env python3
"""
Neo4j Knowledge Graph Import Script for MediMax
This script connects to Neo4j and imports the generated knowledge graph data.
"""

import logging
from neo4j import GraphDatabase
import csv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jImporter:
    def __init__(self, uri, username, password):
        """Initialize Neo4j connection."""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared existing data from Neo4j")
    
    def import_nodes(self, nodes_file):
        """Import nodes from CSV file."""
        logger.info(f"Importing nodes from {nodes_file}")
        
        with open(nodes_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            nodes_data = list(reader)
        
        with self.driver.session() as session:
            # Create nodes in batches
            batch_size = 100
            for i in range(0, len(nodes_data), batch_size):
                batch = nodes_data[i:i + batch_size]
                session.run("""
                    UNWIND $nodes as node
                    CREATE (n)
                    SET n = node,
                        n.nodeId = node.`nodeId:ID`,
                        n.label = node.`label:LABEL`,
                        n.historical = CASE WHEN node.`historical:boolean` = 'true' THEN true ELSE false END
                    WITH n, node.`label:LABEL` as label
                    CALL apoc.create.addLabels(n, [label]) YIELD node as labeled_node
                    RETURN count(labeled_node)
                """, nodes=batch)
        
        logger.info(f"Imported {len(nodes_data)} nodes")
    
    def import_relationships(self, rels_file):
        """Import relationships from CSV file."""
        logger.info(f"Importing relationships from {rels_file}")
        
        with open(rels_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rels_data = list(reader)
        
        with self.driver.session() as session:
            # Create relationships in batches
            batch_size = 100
            for i in range(0, len(rels_data), batch_size):
                batch = rels_data[i:i + batch_size]
                session.run("""
                    UNWIND $rels as rel
                    MATCH (start_node {nodeId: rel.`:START_ID`})
                    MATCH (end_node {nodeId: rel.`:END_ID`})
                    CALL apoc.create.relationship(start_node, rel.`:TYPE`, {
                        date: rel.date,
                        status: rel.status
                    }, end_node) YIELD rel as created_rel
                    RETURN count(created_rel)
                """, rels=batch)
        
        logger.info(f"Imported {len(rels_data)} relationships")
    
    def create_indexes(self):
        """Create indexes for better performance."""
        logger.info("Creating indexes")
        with self.driver.session() as session:
            # Create index on nodeId for fast lookups
            session.run("CREATE INDEX node_id_index IF NOT EXISTS FOR (n:Patient) ON (n.nodeId)")
            session.run("CREATE INDEX node_id_index2 IF NOT EXISTS FOR (n:Symptom) ON (n.nodeId)")
            session.run("CREATE INDEX node_id_index3 IF NOT EXISTS FOR (n:Medication) ON (n.nodeId)")
            session.run("CREATE INDEX node_id_index4 IF NOT EXISTS FOR (n:LabTest) ON (n.nodeId)")
            session.run("CREATE INDEX node_id_index5 IF NOT EXISTS FOR (n:Encounter) ON (n.nodeId)")
    
    def verify_import(self):
        """Verify the imported data."""
        with self.driver.session() as session:
            # Count nodes by label
            result = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as label, count(n) as count 
                ORDER BY count DESC
            """)
            
            logger.info("Imported data summary:")
            total_nodes = 0
            for record in result:
                label = record['label']
                count = record['count']
                total_nodes += count
                logger.info(f"  {label}: {count} nodes")
            
            # Count relationships
            rel_result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count ORDER BY count DESC")
            logger.info("Relationships:")
            total_rels = 0
            for record in rel_result:
                rel_type = record['rel_type']
                count = record['count']
                total_rels += count
                logger.info(f"  {rel_type}: {count} relationships")
            
            logger.info(f"Total: {total_nodes} nodes, {total_rels} relationships")

def main():
    """Main function to run the import."""
    # Neo4j connection details - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
    NEO4J_URI = "bolt://localhost:7687"  # For local Neo4j
    # NEO4J_URI = "neo4j+s://your-instance.databases.neo4j.io"  # For Neo4j Aura
    NEO4J_USERNAME = "neo4j"
    NEO4J_PASSWORD = "password"  # Change this to your actual password
    
    # File paths
    NODES_FILE = "neo4j_nodes.csv"
    RELATIONSHIPS_FILE = "neo4j_relationships.csv"
    
    # Check if files exist
    if not os.path.exists(NODES_FILE):
        logger.error(f"Nodes file not found: {NODES_FILE}")
        return
    
    if not os.path.exists(RELATIONSHIPS_FILE):
        logger.error(f"Relationships file not found: {RELATIONSHIPS_FILE}")
        return
    
    # Import data
    importer = None
    try:
        importer = Neo4jImporter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        importer.clear_database()
        
        # Create indexes first
        importer.create_indexes()
        
        # Import nodes and relationships
        importer.import_nodes(NODES_FILE)
        importer.import_relationships(RELATIONSHIPS_FILE)
        
        # Verify import
        importer.verify_import()
        
        logger.info("Import completed successfully!")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
    finally:
        if importer:
            importer.close()

if __name__ == "__main__":
    main()
