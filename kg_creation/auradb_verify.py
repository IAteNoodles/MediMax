#!/usr/bin/env python3
"""
AuraDB Data Verification and Cleanup Script
Check what data is in your AuraDB instance and optionally clean it up.
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
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

class AuraDBVerifier:
    def __init__(self):
        """Initialize connection to AuraDB."""
        load_env_file()
        
        uri = os.getenv('NEO4J_URI')
        username = os.getenv('NEO4J_USERNAME') 
        password = os.getenv('NEO4J_PASSWORD')
        
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("✅ Connected to AuraDB")
    
    def close(self):
        """Close connection."""
        if self.driver:
            self.driver.close()
    
    def analyze_data(self):
        """Analyze what's currently in the database."""
        logger.info("📊 Analyzing current database content...")
        
        with self.driver.session() as session:
            # Count all nodes by label
            result = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as label, count(n) as count 
                ORDER BY count DESC
            """)
            
            logger.info("\n🏷️  Node Labels and Counts:")
            total_nodes = 0
            node_counts = {}
            for record in result:
                label = record['label']
                count = record['count']
                node_counts[label] = count
                total_nodes += count
                logger.info(f"  {label}: {count}")
            
            # Count relationships by type
            rel_result = session.run("""
                MATCH ()-[r]->() 
                RETURN type(r) as rel_type, count(r) as count 
                ORDER BY count DESC
            """)
            
            logger.info("\n🔗 Relationship Types and Counts:")
            total_rels = 0
            rel_counts = {}
            for record in rel_result:
                rel_type = record['rel_type']
                count = record['count']
                rel_counts[rel_type] = count
                total_rels += count
                logger.info(f"  {rel_type}: {count}")
            
            logger.info(f"\n📈 Totals: {total_nodes} nodes, {total_rels} relationships")
            
            return node_counts, rel_counts
    
    def show_sample_nodes(self, label, limit=5):
        """Show sample nodes of a given label."""
        logger.info(f"\n📋 Sample {label} nodes:")
        
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH (n:{label}) 
                RETURN n.nodeId as nodeId, n.name as name, 
                       n.dob as dob, n.sex as sex
                LIMIT {limit}
            """)
            
            for record in result:
                logger.info(f"  ID: {record['nodeId']}, Name: {record['name']}, DOB: {record['dob']}, Sex: {record['sex']}")
    
    def check_medimax_data(self):
        """Check specifically for MediMax knowledge graph data."""
        logger.info("\n🏥 Checking for MediMax knowledge graph data...")
        
        with self.driver.session() as session:
            # Check for patients with our expected nodeId pattern
            medimax_patients = session.run("""
                MATCH (p:Patient) 
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN count(p) as count, collect(p.name)[0..5] as sample_names
            """).single()
            
            logger.info(f"  MediMax Patients: {medimax_patients['count']}")
            if medimax_patients['count'] > 0:
                logger.info(f"  Sample names: {medimax_patients['sample_names']}")
            
            # Check for symptoms
            symptoms = session.run("""
                MATCH (s:Symptom) 
                WHERE s.nodeId IS NOT NULL
                RETURN count(s) as count, collect(s.name)[0..5] as sample_names
            """).single()
            
            logger.info(f"  Symptoms: {symptoms['count']}")
            if symptoms['count'] > 0:
                logger.info(f"  Sample symptoms: {symptoms['sample_names']}")
            
            # Check relationships
            kg_rels = session.run("""
                MATCH (p:Patient)-[r]->()
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN type(r) as rel_type, count(r) as count
                ORDER BY count DESC
            """)
            
            logger.info("  MediMax Relationships:")
            for record in kg_rels:
                logger.info(f"    {record['rel_type']}: {record['count']}")
    
    def clean_non_medimax_data(self):
        """Remove data that's not part of the MediMax knowledge graph."""
        logger.info("\n🧹 Cleaning non-MediMax data...")
        
        confirm = input("This will delete non-MediMax data. Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            logger.info("Cleanup cancelled")
            return
        
        with self.driver.session() as session:
            # Delete nodes that don't have our nodeId pattern or are not medical
            deleted_nodes = session.run("""
                MATCH (n) 
                WHERE NOT (
                    (n.nodeId STARTS WITH 'patient_' OR 
                     n.nodeId STARTS WITH 'symptom_' OR 
                     n.nodeId STARTS WITH 'medication_' OR 
                     n.nodeId STARTS WITH 'encounter_' OR 
                     n.nodeId STARTS WITH 'labtest_') AND
                    labels(n)[0] IN ['Patient', 'Symptom', 'Medication', 'Encounter', 'LabTest']
                )
                DETACH DELETE n
                RETURN count(n) as deleted
            """).single()
            
            logger.info(f"✅ Deleted {deleted_nodes['deleted']} non-MediMax nodes")
    
    def show_patient_details(self, patient_name=None):
        """Show detailed information for a specific patient."""
        if not patient_name:
            # Show available patients
            with self.driver.session() as session:
                patients = session.run("""
                    MATCH (p:Patient) 
                    WHERE p.nodeId STARTS WITH 'patient_'
                    RETURN p.name as name
                    ORDER BY p.name
                """)
                
                logger.info("\n👥 Available MediMax patients:")
                patient_names = []
                for record in patients:
                    name = record['name']
                    patient_names.append(name)
                    logger.info(f"  - {name}")
                
                if patient_names:
                    patient_name = patient_names[0]  # Show first patient
                else:
                    logger.info("No MediMax patients found")
                    return
        
        logger.info(f"\n👤 Patient Details: {patient_name}")
        
        with self.driver.session() as session:
            # Get patient info and all connected data
            result = session.run("""
                MATCH (p:Patient {name: $name})
                OPTIONAL MATCH (p)-[:has_symptom]->(s:Symptom)
                OPTIONAL MATCH (p)-[:prescribed_medication]->(m:Medication)
                OPTIONAL MATCH (p)-[:has_encounter]->(e:Encounter)
                OPTIONAL MATCH (p)-[:has_lab_test]->(l:LabTest)
                RETURN p.dob as dob, p.sex as sex, p.remarks as remarks,
                       collect(DISTINCT s.name) as symptoms,
                       collect(DISTINCT m.name) as medications,
                       collect(DISTINCT e.name) as encounters,
                       collect(DISTINCT l.name) as lab_tests
            """, name=patient_name)
            
            record = result.single()
            if record:
                logger.info(f"  DOB: {record['dob']}")
                logger.info(f"  Sex: {record['sex']}")
                logger.info(f"  Remarks: {record['remarks']}")
                logger.info(f"  Symptoms: {[s for s in record['symptoms'] if s]}")
                logger.info(f"  Medications: {[m for m in record['medications'] if m]}")
                logger.info(f"  Encounters: {[e for e in record['encounters'] if e]}")
                logger.info(f"  Lab Tests: {[l for l in record['lab_tests'] if l]}")

def main():
    """Main verification function."""
    logger.info("🔍 AuraDB Data Verification and Cleanup")
    logger.info("="*50)
    
    verifier = None
    try:
        verifier = AuraDBVerifier()
        
        # Analyze current data
        node_counts, rel_counts = verifier.analyze_data()
        
        # Check for MediMax specific data
        verifier.check_medimax_data()
        
        # Show sample patient details
        verifier.show_patient_details()
        
        # Offer cleanup if there's unexpected data
        medical_labels = {'Patient', 'Symptom', 'Medication', 'Encounter', 'LabTest'}
        unexpected_labels = set(node_counts.keys()) - medical_labels
        
        if unexpected_labels:
            logger.info(f"\n⚠️  Found unexpected node types: {unexpected_labels}")
            logger.info("This suggests there's other data in your database.")
            
            cleanup = input("\nClean up non-MediMax data? (y/N): ").strip().lower()
            if cleanup == 'y':
                verifier.clean_non_medimax_data()
                logger.info("\n📊 Data after cleanup:")
                verifier.analyze_data()
        
        logger.info("\n✅ Verification completed!")
        logger.info("Your MediMax knowledge graph is successfully imported to AuraDB!")
        
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
    finally:
        if verifier:
            verifier.close()

if __name__ == "__main__":
    main()