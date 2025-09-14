import csv
import json
import logging
from typing import Dict, List, Tuple
import os
import sys

# Add parent directory to path to import from create_kg_production
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from create_kg_production import create_knowledge_graph_for_patient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('unified_kg_export.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_single_unified_csv():
    """
    Create a single unified CSV file that contains both nodes and relationships
    in a format that's easy to import into Neo4j or other graph databases.
    """
    logger.info("Creating unified CSV for all patients")
    
    # Generate knowledge graphs for all patients
    patient_ids = [1, 2, 3, 4, 5]
    all_nodes = []
    all_relationships = []
    
    for patient_id in patient_ids:
        try:
            logger.info(f"Processing Patient {patient_id}")
            nodes, relationships = create_knowledge_graph_for_patient(patient_id)
            all_nodes.extend(nodes)
            all_relationships.extend(relationships)
        except Exception as e:
            logger.error(f"Failed to process Patient {patient_id}: {e}")
    
    # Create unified CSV with all data
    unified_filename = 'medimax_unified_knowledge_graph.csv'
    
    with open(unified_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'id', 'name', 'type', 'category', 'source_id', 'target_id', 
            'relationship_type', 'date', 'status', 'details', 'properties'
        ])
        
        # Write nodes
        for node in all_nodes:
            properties = node.get('properties', {})
            properties_json = json.dumps(properties) if properties else ''
            
            writer.writerow([
                node['id'],
                node['name'], 
                'NODE',
                node['label'],
                '', '', '',  # Empty relationship fields for nodes
                properties.get('date', ''),
                properties.get('status', ''),
                properties.get('details', ''),
                properties_json
            ])
        
        # Write relationships
        for rel in all_relationships:
            properties = rel.get('properties', {})
            properties_json = json.dumps(properties) if properties else ''
            
            writer.writerow([
                f"{rel['start_id']}_{rel['type']}_{rel['end_id']}",  # Unique relationship ID
                f"{rel['type']} relationship",
                'RELATIONSHIP',
                rel['type'],
                rel['start_id'],
                rel['target_id'] if 'target_id' in rel else rel['end_id'],
                rel['type'],
                properties.get('date', ''),
                properties.get('status', ''),
                properties.get('details', ''),
                properties_json
            ])
    
    logger.info(f"Created unified CSV: {unified_filename}")
    logger.info(f"Total records: {len(all_nodes)} nodes + {len(all_relationships)} relationships = {len(all_nodes) + len(all_relationships)}")
    
    return unified_filename

def create_neo4j_import_files():
    """
    Create optimized CSV files for Neo4j bulk import with proper formatting.
    """
    logger.info("Creating Neo4j optimized import files")
    
    # Generate knowledge graphs for all patients
    patient_ids = [1, 2, 3, 4, 5]
    all_nodes = []
    all_relationships = []
    
    for patient_id in patient_ids:
        try:
            logger.info(f"Processing Patient {patient_id}")
            nodes, relationships = create_knowledge_graph_for_patient(patient_id)
            all_nodes.extend(nodes)
            all_relationships.extend(relationships)
        except Exception as e:
            logger.error(f"Failed to process Patient {patient_id}: {e}")
    
    # Remove duplicates while preserving order
    seen_nodes = set()
    unique_nodes = []
    for node in all_nodes:
        if node['id'] not in seen_nodes:
            unique_nodes.append(node)
            seen_nodes.add(node['id'])
    
    seen_rels = set()
    unique_relationships = []
    for rel in all_relationships:
        rel_key = f"{rel['start_id']}_{rel['type']}_{rel['end_id']}"
        if rel_key not in seen_rels:
            unique_relationships.append(rel)
            seen_rels.add(rel_key)
    
    # Create nodes CSV for Neo4j
    nodes_filename = 'neo4j_nodes.csv'
    with open(nodes_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['nodeId:ID', 'name', 'label:LABEL', 'dob', 'sex', 'remarks', 'type', 'date', 'status', 'details', 'historical:boolean'])
        
        for node in unique_nodes:
            props = node.get('properties', {})
            writer.writerow([
                node['id'],
                node['name'],
                node['label'],
                props.get('dob', ''),
                props.get('sex', ''),
                props.get('remarks', ''),
                props.get('type', ''),
                props.get('date', ''),
                props.get('status', ''),
                props.get('details', ''),
                'true' if props.get('historical') else 'false'
            ])
    
    # Create relationships CSV for Neo4j  
    rels_filename = 'neo4j_relationships.csv'
    with open(rels_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([':START_ID', ':TYPE', ':END_ID', 'date', 'status'])
        
        for rel in unique_relationships:
            props = rel.get('properties', {})
            writer.writerow([
                rel['start_id'],
                rel['type'],
                rel['end_id'],
                props.get('date', ''),
                props.get('status', '')
            ])
    
    logger.info(f"Created Neo4j import files:")
    logger.info(f"  - {nodes_filename}: {len(unique_nodes)} unique nodes")
    logger.info(f"  - {rels_filename}: {len(unique_relationships)} unique relationships")
    
    return nodes_filename, rels_filename

def create_neo4j_connection_script():
    """
    Create a Python script to connect to Neo4j and import the data.
    """
    script_content = '''#!/usr/bin/env python3
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
'''
    
    with open('neo4j_import.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    logger.info("Created neo4j_import.py script")

def create_cypher_queries():
    """
    Create a file with useful Cypher queries for exploring the knowledge graph.
    """
    queries_content = '''-- MediMax Knowledge Graph Cypher Queries
-- Use these queries in Neo4j Browser or Neo4j Desktop

-- 1. Overview: Count all nodes by type
MATCH (n) 
RETURN labels(n)[0] as NodeType, count(n) as Count 
ORDER BY Count DESC;

-- 2. Overview: Count all relationships by type
MATCH ()-[r]->() 
RETURN type(r) as RelationshipType, count(r) as Count 
ORDER BY Count DESC;

-- 3. Find all patients and their basic info
MATCH (p:Patient) 
RETURN p.name, p.dob, p.sex, p.remarks 
ORDER BY p.name;

-- 4. Find all symptoms for a specific patient
MATCH (p:Patient)-[:has_symptom]->(s:Symptom) 
WHERE p.name = "John Doe"
RETURN p.name, s.name, s.type;

-- 5. Find all medications prescribed to patients
MATCH (p:Patient)-[:prescribed_medication]->(m:Medication) 
RETURN p.name, m.name, m.details, m.prescription_date 
ORDER BY p.name, m.prescription_date;

-- 6. Find patients with diabetes
MATCH (p:Patient)-[:has_symptom]->(s:Symptom) 
WHERE toLower(s.name) CONTAINS "diabetes"
RETURN p.name, s.name;

-- 7. Find patients with allergies
MATCH (p:Patient)-[:has_symptom]->(s:Symptom) 
WHERE s.type = "allergy"
RETURN p.name, s.name;

-- 8. Find all lab tests and their encounters
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)-[:contains_test]->(l:LabTest)
RETURN p.name, e.date, e.type, l.name
ORDER BY p.name, e.date;

-- 9. Find patients and their appointment history
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)
WHERE e.type = "appointment"
RETURN p.name, e.date, e.status, e.type
ORDER BY p.name, e.date;

-- 10. Find complex paths: Patient -> Symptoms -> Medications
MATCH path = (p:Patient)-[:has_symptom]->(s:Symptom), (p)-[:prescribed_medication]->(m:Medication)
RETURN p.name, s.name, m.name
ORDER BY p.name;

-- 11. Find patients with multiple conditions
MATCH (p:Patient)-[:has_symptom]->(s:Symptom)
WHERE s.type = "condition"
WITH p, count(s) as condition_count
WHERE condition_count > 1
MATCH (p)-[:has_symptom]->(s:Symptom)
WHERE s.type = "condition"
RETURN p.name, collect(s.name) as conditions, condition_count
ORDER BY condition_count DESC;

-- 12. Find medication interactions (patients taking multiple medications)
MATCH (p:Patient)-[:prescribed_medication]->(m:Medication)
WITH p, collect(m.name) as medications, count(m) as med_count
WHERE med_count > 1
RETURN p.name, medications, med_count
ORDER BY med_count DESC;

-- 13. Find recent lab tests (last 6 months)
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)-[:contains_test]->(l:LabTest)
WHERE e.type = "laboratory" AND e.date >= "2024-03-01"
RETURN p.name, e.date, l.name, l.details
ORDER BY e.date DESC;

-- 14. Find patients by age (approximate, using DOB)
MATCH (p:Patient)
WHERE p.dob IS NOT NULL
WITH p, duration.between(date(p.dob), date()).years as age
RETURN p.name, p.dob, age
ORDER BY age DESC;

-- 15. Network analysis: Find highly connected patients
MATCH (p:Patient)-[r]-()
WITH p, count(r) as connection_count
RETURN p.name, connection_count
ORDER BY connection_count DESC
LIMIT 10;

-- 16. Find diagnostic patterns: Symptoms -> Lab Tests
MATCH (p:Patient)-[:has_symptom]->(s:Symptom), (p)-[:has_lab_test]->(l:LabTest)
RETURN s.name as Symptom, collect(DISTINCT l.name) as LabTests
ORDER BY Symptom;

-- 17. Find treatment patterns: Symptoms -> Medications
MATCH (p:Patient)-[:has_symptom]->(s:Symptom), (p)-[:prescribed_medication]->(m:Medication)
RETURN s.name as Symptom, collect(DISTINCT m.name) as Medications
ORDER BY Symptom;

-- 18. Timeline view: Patient's medical history
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)
WHERE p.name = "John Doe" AND e.date IS NOT NULL
OPTIONAL MATCH (e)-[:contains_test]->(l:LabTest)
OPTIONAL MATCH (e)-[:contains_symptom]->(s:Symptom)
RETURN e.date, e.type, e.status, collect(DISTINCT l.name) as lab_tests, collect(DISTINCT s.name) as symptoms
ORDER BY e.date;

-- 19. Find potential risk factors (patients with multiple risk symptoms)
MATCH (p:Patient)-[:has_symptom]->(s:Symptom)
WHERE s.name IN ["Hypertension", "Diabetes Type 2", "Coronary Artery Disease", "High Cholesterol"]
WITH p, collect(s.name) as risk_factors, count(s) as risk_count
WHERE risk_count >= 2
RETURN p.name, risk_factors, risk_count
ORDER BY risk_count DESC;

-- 20. Export data for analysis
MATCH (p:Patient)-[r]->(n)
RETURN p.name as Patient, type(r) as Relationship, labels(n)[0] as TargetType, n.name as TargetName
ORDER BY Patient, Relationship;
'''
    
    with open('knowledge_graph_queries.cypher', 'w', encoding='utf-8') as f:
        f.write(queries_content)
    
    logger.info("Created knowledge_graph_queries.cypher file")

def main():
    """Main function to create all export formats."""
    logger.info("Starting comprehensive knowledge graph export")
    
    try:
        # Create unified CSV
        unified_file = create_single_unified_csv()
        logger.info(f"✓ Created unified CSV: {unified_file}")
        
        # Create Neo4j optimized files
        nodes_file, rels_file = create_neo4j_import_files()
        logger.info(f"✓ Created Neo4j files: {nodes_file}, {rels_file}")
        
        # Create Neo4j connection script
        create_neo4j_connection_script()
        logger.info("✓ Created Neo4j import script")
        
        # Create Cypher queries
        create_cypher_queries()
        logger.info("✓ Created Cypher queries file")
        
        logger.info("\n" + "="*50)
        logger.info("KNOWLEDGE GRAPH EXPORT COMPLETED")
        logger.info("="*50)
        logger.info("Files created:")
        logger.info(f"  1. {unified_file} - Single unified CSV")
        logger.info(f"  2. {nodes_file} - Neo4j nodes")
        logger.info(f"  3. {rels_file} - Neo4j relationships")
        logger.info("  4. neo4j_import.py - Python import script")
        logger.info("  5. knowledge_graph_queries.cypher - Query examples")
        logger.info("\nTo import into Neo4j:")
        logger.info("  1. Update neo4j_import.py with your Neo4j credentials")
        logger.info("  2. Install neo4j driver: pip install neo4j")
        logger.info("  3. Run: python neo4j_import.py")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise

if __name__ == "__main__":
    main()