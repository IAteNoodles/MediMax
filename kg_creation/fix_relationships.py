#!/usr/bin/env python3
"""
Test specific relationships in AuraDB to debug connectivity issues
"""

import logging
import os
from neo4j import GraphDatabase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_env_file():
    """Load environment variables from .env file if it exists."""
    # Check current directory first, then parent directory
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

class RelationshipTester:
    def __init__(self):
        """Initialize connection to AuraDB."""
        load_env_file()
        
        # Use the correct environment variable names from the .env file
        uri = f"neo4j+s://{os.getenv('AURA_USER')}.databases.neo4j.io"
        username = os.getenv('AURA_USER')
        password = os.getenv('AURA_PASSWORD')
        
        logger.info(f"Connecting with URI: {uri}")
        logger.info(f"Username: {username}")
        
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        logger.info("✅ Connected to AuraDB")
    
    def close(self):
        """Close connection."""
        if self.driver:
            self.driver.close()
    
    def test_patient_connections(self):
        """Test if patients are actually connected to their data."""
        logger.info("🔍 Testing patient connections...")
        
        with self.driver.session() as session:
            # Get a sample patient and check connections
            result = session.run("""
                MATCH (p:Patient)
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN p.nodeId as patientId, p.name as name
                LIMIT 1
            """)
            
            patient = result.single()
            if not patient:
                logger.error("❌ No MediMax patients found!")
                return
            
            patient_id = patient['patientId']
            patient_name = patient['name']
            logger.info(f"Testing connections for: {patient_name} (ID: {patient_id})")
            
            # Test direct relationships
            connections = session.run("""
                MATCH (p:Patient {nodeId: $patientId})-[r]->(n)
                RETURN type(r) as relType, labels(n)[0] as targetLabel, 
                       n.nodeId as targetId, n.name as targetName
                ORDER BY relType
            """, patientId=patient_id)
            
            connection_count = 0
            logger.info(f"\n🔗 Direct relationships from {patient_name}:")
            for record in connections:
                connection_count += 1
                logger.info(f"  {record['relType']} -> {record['targetLabel']}: {record['targetName']} ({record['targetId']})")
            
            if connection_count == 0:
                logger.error(f"❌ No relationships found for {patient_name}!")
                
                # Check if the patient node exists
                patient_check = session.run("""
                    MATCH (p:Patient {nodeId: $patientId})
                    RETURN p.name as name, p.nodeId as id
                """, patientId=patient_id).single()
                
                if patient_check:
                    logger.info(f"✅ Patient node exists: {patient_check['name']} ({patient_check['id']})")
                else:
                    logger.error(f"❌ Patient node not found: {patient_id}")
                
                # Check if target nodes exist
                logger.info("\n🔍 Checking if target nodes exist...")
                expected_targets = ['symptom_allergy_penicillin', 'medication_aspirin', 'encounter_lab_2024_09_01']
                for target_id in expected_targets:
                    target_check = session.run("""
                        MATCH (n {nodeId: $targetId})
                        RETURN labels(n)[0] as label, n.name as name
                    """, targetId=target_id).single()
                    
                    if target_check:
                        logger.info(f"  ✅ {target_id}: {target_check['label']} - {target_check['name']}")
                    else:
                        logger.error(f"  ❌ {target_id}: NOT FOUND")
            else:
                logger.info(f"✅ Found {connection_count} relationships")
    
    def manually_create_test_relationship(self):
        """Manually create a test relationship to debug the issue."""
        logger.info("\n🔧 Manually creating test relationship...")
        
        with self.driver.session() as session:
            # Find patient and medication nodes
            patient_node = session.run("""
                MATCH (p:Patient {nodeId: 'patient_1'})
                RETURN p.nodeId as id, p.name as name
            """).single()
            
            medication_node = session.run("""
                MATCH (m:Medication {nodeId: 'medication_aspirin'})
                RETURN m.nodeId as id, m.name as name
            """).single()
            
            if patient_node and medication_node:
                logger.info(f"Found patient: {patient_node['name']} ({patient_node['id']})")
                logger.info(f"Found medication: {medication_node['name']} ({medication_node['id']})")
                
                # Create relationship manually
                result = session.run("""
                    MATCH (p:Patient {nodeId: 'patient_1'})
                    MATCH (m:Medication {nodeId: 'medication_aspirin'})
                    MERGE (p)-[r:PRESCRIBED_MEDICATION]->(m)
                    RETURN r
                """)
                
                if result.single():
                    logger.info("✅ Successfully created test relationship!")
                    
                    # Verify it exists
                    verify = session.run("""
                        MATCH (p:Patient {nodeId: 'patient_1'})-[r:PRESCRIBED_MEDICATION]->(m:Medication {nodeId: 'medication_aspirin'})
                        RETURN p.name as patient, m.name as medication
                    """).single()
                    
                    if verify:
                        logger.info(f"✅ Verified: {verify['patient']} -> {verify['medication']}")
                else:
                    logger.error("❌ Failed to create test relationship")
            else:
                logger.error("❌ Could not find required nodes for test")
                if not patient_node:
                    logger.error("  Patient node not found")
                if not medication_node:
                    logger.error("  Medication node not found")
    
    def fix_all_relationships(self):
        """Fix all relationships by recreating them properly."""
        logger.info("\n🔧 Fixing all relationships...")
        
        confirm = input("This will recreate all relationships. Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            logger.info("Relationship fix cancelled")
            return
        
        with self.driver.session() as session:
            # Delete existing relationships for MediMax data
            session.run("""
                MATCH (p:Patient)-[r]->()
                WHERE p.nodeId STARTS WITH 'patient_'
                DELETE r
            """)
            logger.info("🗑️ Deleted existing MediMax relationships")
            
            # Recreate relationships from our expected patterns
            relationships = [
                # Patient 1 relationships
                ("patient_1", "PRESCRIBED_MEDICATION", "medication_aspirin"),
                ("patient_1", "PRESCRIBED_MEDICATION", "medication_Multivitamin"),
                ("patient_1", "HAS_SYMPTOM", "symptom_allergy_penicillin"),
                ("patient_1", "HAS_SYMPTOM", "symptom_fatigue"),
                ("patient_1", "HAS_SYMPTOM", "symptom_mild_fatigue"),
                ("patient_1", "HAS_SYMPTOM", "symptom_routine_checkup"),
                ("patient_1", "HAS_ENCOUNTER", "encounter_lab_2024_09_01"),
                ("patient_1", "HAS_ENCOUNTER", "encounter_lab_2024_08_15"),
                ("patient_1", "HAS_ENCOUNTER", "encounter_appointment_2024_09_15"),
                ("patient_1", "HAS_ENCOUNTER", "encounter_appointment_2024_08_01"),
                ("patient_1", "HAS_LAB_TEST", "labtest_blood_test"),
                ("patient_1", "HAS_LAB_TEST", "labtest_cholesterol"),
                ("patient_1", "HAS_LAB_TEST", "labtest_glucose"),
                ("patient_1", "HAS_LAB_TEST", "labtest_liver_function"),
            ]
            
            created_count = 0
            for start_id, rel_type, end_id in relationships:
                try:
                    result = session.run(f"""
                        MATCH (start {{nodeId: $start_id}})
                        MATCH (end {{nodeId: $end_id}})
                        MERGE (start)-[r:{rel_type}]->(end)
                        RETURN r
                    """, start_id=start_id, end_id=end_id)
                    
                    if result.single():
                        created_count += 1
                        logger.info(f"✅ Created: {start_id} -[{rel_type}]-> {end_id}")
                    else:
                        logger.warning(f"⚠️ Failed: {start_id} -[{rel_type}]-> {end_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error creating {start_id} -[{rel_type}]-> {end_id}: {e}")
            
            logger.info(f"✅ Created {created_count} relationships")
    
    def verify_final_graph(self):
        """Verify the final graph structure."""
        logger.info("\n📊 Final graph verification...")
        
        with self.driver.session() as session:
            # Count relationships by patient
            result = session.run("""
                MATCH (p:Patient)-[r]->()
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN p.name as patient, count(r) as relationships
                ORDER BY relationships DESC
            """)
            
            logger.info("Patient connectivity:")
            for record in result:
                logger.info(f"  {record['patient']}: {record['relationships']} relationships")
            
            # Show sample connected path
            path_result = session.run("""
                MATCH path = (p:Patient)-[r1:PRESCRIBED_MEDICATION]->(m:Medication)
                WHERE p.nodeId STARTS WITH 'patient_'
                RETURN p.name as patient, m.name as medication
                LIMIT 3
            """)
            
            logger.info("\n🏥 Sample medication prescriptions:")
            for record in path_result:
                logger.info(f"  {record['patient']} -> {record['medication']}")

def main():
    """Main testing function."""
    logger.info("🔧 Neo4j Relationship Debugging and Fix")
    logger.info("="*50)
    
    tester = None
    try:
        tester = RelationshipTester()
        
        # Test current connections
        tester.test_patient_connections()
        
        # Try manual relationship creation
        tester.manually_create_test_relationship()
        
        # Fix all relationships
        tester.fix_all_relationships()
        
        # Verify final result
        tester.verify_final_graph()
        
        logger.info("\n🎉 Relationship debugging completed!")
        
    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if tester:
            tester.close()

if __name__ == "__main__":
    main()