#!/usr/bin/env python3
"""
Simplified Atomic Facts Knowledge Graph Creator for MediMax using MCP
====================================================================

This script creates a knowledge graph from the atomic facts database schema
using the existing MCP database connection.
"""

import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from neo4j import GraphDatabase
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplifiedKGCreator:
    def __init__(self):
        load_dotenv()
        
        # Neo4j connection
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_user = os.getenv('NEO4J_USERNAME')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')
        self.neo4j_driver = None
        
    def connect_neo4j(self):
        """Connect to Neo4j database"""
        try:
            self.neo4j_driver = GraphDatabase.driver(
                self.neo4j_uri, 
                auth=(self.neo4j_user, self.neo4j_password)
            )
            with self.neo4j_driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Connected to Neo4j AuraDB")
            return True
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {e}")
            return False
    
    def clear_neo4j(self):
        """Clear existing data in Neo4j"""
        with self.neo4j_driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("🗑️ Cleared existing Neo4j data")
    
    def create_patient_nodes(self):
        """Create patient nodes"""
        logger.info("👥 Creating patient nodes...")
        
        # This would normally use a database query, but for demo let's create manually
        # In a real implementation, you'd query the database here
        
        patients = [
            {"id": 1, "name": "John Doe", "dob": "1985-03-15", "sex": "Male"},
            {"id": 2, "name": "Jane Smith", "dob": "1990-07-22", "sex": "Female"},
            {"id": 3, "name": "Robert Johnson", "dob": "1978-11-05", "sex": "Male"},
            {"id": 4, "name": "Emily Davis", "dob": "1992-02-14", "sex": "Female"},
            {"id": 5, "name": "Michael Wilson", "dob": "1980-05-12", "sex": "Male"}
        ]
        
        with self.neo4j_driver.session() as session:
            for patient in patients:
                query = """
                CREATE (p:Patient)
                SET p.nodeId = $nodeId,
                    p.name = $name,
                    p.dob = $dob,
                    p.sex = $sex
                """
                session.run(query,
                           nodeId=f"patient_{patient['id']}",
                           name=patient['name'],
                           dob=patient['dob'],
                           sex=patient['sex'])
        
        logger.info(f"✅ Created {len(patients)} patient nodes")
    
    def create_medication_nodes_and_relationships(self):
        """Create medication nodes and relationships"""
        logger.info("💊 Creating medication nodes and relationships...")
        
        # Sample medication data (in real implementation, query from database)
        medications = [
            {"patient_id": 1, "med_id": 1, "name": "Aspirin", "dosage": "81mg", "condition": "Cardiovascular Protection"},
            {"patient_id": 1, "med_id": 2, "name": "Multivitamin", "dosage": "1 tablet", "condition": "Nutritional Support"},
            {"patient_id": 2, "med_id": 3, "name": "Lisinopril", "dosage": "10mg", "condition": "Hypertension"},
            {"patient_id": 2, "med_id": 4, "name": "Metformin", "dosage": "500mg", "condition": "Type 2 Diabetes"},
            {"patient_id": 3, "med_id": 5, "name": "Metformin", "dosage": "1000mg", "condition": "Type 2 Diabetes"},
            {"patient_id": 3, "med_id": 6, "name": "Insulin", "dosage": "20 units", "condition": "Type 2 Diabetes"},
            {"patient_id": 5, "med_id": 7, "name": "Metoprolol", "dosage": "50mg", "condition": "Hypertension"},
            {"patient_id": 5, "med_id": 8, "name": "Atorvastatin", "dosage": "20mg", "condition": "High Cholesterol"}
        ]
        
        with self.neo4j_driver.session() as session:
            # Create medication nodes
            for med in medications:
                query = """
                CREATE (m:Medication)
                SET m.nodeId = $nodeId,
                    m.name = $name,
                    m.dosage = $dosage
                """
                session.run(query,
                           nodeId=f"medication_{med['med_id']}",
                           name=med['name'],
                           dosage=med['dosage'])
                
                # Create condition nodes (if not exists)
                condition_id = med['condition'].lower().replace(' ', '_')
                query = """
                MERGE (c:MedicalCondition {nodeId: $nodeId})
                SET c.name = $name
                """
                session.run(query,
                           nodeId=f"condition_{condition_id}",
                           name=med['condition'])
                
                # Create Patient -> Medication relationship
                query = """
                MATCH (p:Patient {nodeId: $patientId})
                MATCH (m:Medication {nodeId: $medicationId})
                CREATE (p)-[:PRESCRIBED]->(m)
                """
                session.run(query,
                           patientId=f"patient_{med['patient_id']}",
                           medicationId=f"medication_{med['med_id']}")
                
                # Create Medication -> Condition relationship
                query = """
                MATCH (m:Medication {nodeId: $medicationId})
                MATCH (c:MedicalCondition {nodeId: $conditionId})
                CREATE (m)-[:TREATS]->(c)
                """
                session.run(query,
                           medicationId=f"medication_{med['med_id']}",
                           conditionId=f"condition_{condition_id}")
        
        logger.info(f"✅ Created {len(medications)} medication nodes and relationships")
    
    def create_history_nodes_and_relationships(self):
        """Create medical history nodes and relationships"""
        logger.info("📋 Creating medical history nodes...")
        
        history_items = [
            {"patient_id": 1, "hist_id": 1, "item": "Penicillin allergy", "type": "allergy"},
            {"patient_id": 2, "hist_id": 2, "item": "Hypertension", "type": "condition"},
            {"patient_id": 3, "hist_id": 3, "item": "Sulfa drug allergy", "type": "allergy"},
            {"patient_id": 3, "hist_id": 4, "item": "Type 2 Diabetes", "type": "condition"},
            {"patient_id": 4, "hist_id": 5, "item": "Pregnancy", "type": "condition"},
            {"patient_id": 5, "hist_id": 6, "item": "Aspirin allergy", "type": "allergy"},
            {"patient_id": 5, "hist_id": 7, "item": "Coronary Artery Disease", "type": "condition"}
        ]
        
        with self.neo4j_driver.session() as session:
            for history in history_items:
                # Create history node
                query = """
                CREATE (h:MedicalHistory)
                SET h.nodeId = $nodeId,
                    h.name = $name,
                    h.type = $type
                """
                session.run(query,
                           nodeId=f"history_{history['hist_id']}",
                           name=history['item'],
                           type=history['type'])
                
                # Create Patient -> History relationship
                query = """
                MATCH (p:Patient {nodeId: $patientId})
                MATCH (h:MedicalHistory {nodeId: $historyId})
                CREATE (p)-[:HAS_HISTORY]->(h)
                """
                session.run(query,
                           patientId=f"patient_{history['patient_id']}",
                           historyId=f"history_{history['hist_id']}")
        
        logger.info(f"✅ Created {len(history_items)} medical history nodes")
    
    def create_appointment_and_symptom_nodes(self):
        """Create appointment and symptom nodes"""
        logger.info("📅 Creating appointment and symptom nodes...")
        
        appointments = [
            {"patient_id": 1, "appt_id": 1, "date": "2024-09-15", "doctor": "Dr. Smith"},
            {"patient_id": 2, "appt_id": 2, "date": "2024-09-20", "doctor": "Dr. Johnson"},
            {"patient_id": 3, "appt_id": 3, "date": "2024-09-25", "doctor": "Dr. Wilson"},
            {"patient_id": 4, "appt_id": 4, "date": "2024-09-30", "doctor": "Dr. Martinez"},
            {"patient_id": 5, "appt_id": 5, "date": "2024-10-01", "doctor": "Dr. Brown"}
        ]
        
        symptoms = [
            {"appt_id": 1, "symptom_id": 1, "name": "Fatigue", "severity": "mild"},
            {"appt_id": 2, "symptom_id": 2, "name": "Dizziness", "severity": "moderate"},
            {"appt_id": 2, "symptom_id": 3, "name": "High Blood Pressure", "severity": "moderate"},
            {"appt_id": 3, "symptom_id": 4, "name": "Pain", "severity": "moderate"},
            {"appt_id": 4, "symptom_id": 5, "name": "Nausea", "severity": "mild"},
            {"appt_id": 5, "symptom_id": 6, "name": "Chest Pain", "severity": "moderate"},
            {"appt_id": 5, "symptom_id": 7, "name": "Shortness of Breath", "severity": "mild"}
        ]
        
        with self.neo4j_driver.session() as session:
            # Create appointment nodes
            for appt in appointments:
                query = """
                CREATE (a:Appointment)
                SET a.nodeId = $nodeId,
                    a.name = $name,
                    a.date = $date,
                    a.doctor = $doctor
                """
                session.run(query,
                           nodeId=f"appointment_{appt['appt_id']}",
                           name=f"Appointment on {appt['date']}",
                           date=appt['date'],
                           doctor=appt['doctor'])
                
                # Create Patient -> Appointment relationship
                query = """
                MATCH (p:Patient {nodeId: $patientId})
                MATCH (a:Appointment {nodeId: $appointmentId})
                CREATE (p)-[:HAS_APPOINTMENT]->(a)
                """
                session.run(query,
                           patientId=f"patient_{appt['patient_id']}",
                           appointmentId=f"appointment_{appt['appt_id']}")
            
            # Create symptom nodes and relationships
            for symptom in symptoms:
                query = """
                CREATE (s:Symptom)
                SET s.nodeId = $nodeId,
                    s.name = $name,
                    s.severity = $severity
                """
                session.run(query,
                           nodeId=f"symptom_{symptom['symptom_id']}",
                           name=symptom['name'],
                           severity=symptom['severity'])
                
                # Create Appointment -> Symptom relationship
                query = """
                MATCH (a:Appointment {nodeId: $appointmentId})
                MATCH (s:Symptom {nodeId: $symptomId})
                CREATE (a)-[:REPORTED_SYMPTOM]->(s)
                """
                session.run(query,
                           appointmentId=f"appointment_{symptom['appt_id']}",
                           symptomId=f"symptom_{symptom['symptom_id']}")
        
        logger.info(f"✅ Created {len(appointments)} appointments and {len(symptoms)} symptoms")
    
    def create_lab_nodes(self):
        """Create lab report and finding nodes"""
        logger.info("🧪 Creating lab report nodes...")
        
        lab_reports = [
            {"patient_id": 1, "lab_id": 1, "date": "2024-09-01", "type": "Blood Panel"},
            {"patient_id": 2, "lab_id": 2, "date": "2024-08-15", "type": "Basic Metabolic Panel"},
            {"patient_id": 3, "lab_id": 3, "date": "2024-08-20", "type": "Glucose Tolerance Test"},
            {"patient_id": 4, "lab_id": 4, "date": "2024-08-25", "type": "Prenatal Panel"},
            {"patient_id": 5, "lab_id": 5, "date": "2024-08-30", "type": "Cardiac Enzymes"}
        ]
        
        lab_findings = [
            {"lab_id": 1, "finding_id": 1, "test": "Glucose", "value": "95 mg/dL", "abnormal": False},
            {"lab_id": 1, "finding_id": 2, "test": "Cholesterol", "value": "180 mg/dL", "abnormal": False},
            {"lab_id": 2, "finding_id": 3, "test": "Glucose", "value": "180 mg/dL", "abnormal": True},
            {"lab_id": 3, "finding_id": 4, "test": "Glucose (2hr)", "value": "220 mg/dL", "abnormal": True},
            {"lab_id": 4, "finding_id": 5, "test": "Hemoglobin", "value": "11.5 g/dL", "abnormal": True},
            {"lab_id": 5, "finding_id": 6, "test": "Troponin I", "value": "0.02 ng/mL", "abnormal": False}
        ]
        
        with self.neo4j_driver.session() as session:
            # Create lab report nodes
            for lab in lab_reports:
                query = """
                CREATE (l:LabReport)
                SET l.nodeId = $nodeId,
                    l.name = $name,
                    l.date = $date,
                    l.type = $type
                """
                session.run(query,
                           nodeId=f"lab_report_{lab['lab_id']}",
                           name=f"{lab['type']} on {lab['date']}",
                           date=lab['date'],
                           type=lab['type'])
                
                # Create Patient -> Lab Report relationship
                query = """
                MATCH (p:Patient {nodeId: $patientId})
                MATCH (l:LabReport {nodeId: $labId})
                CREATE (p)-[:HAS_LAB_REPORT]->(l)
                """
                session.run(query,
                           patientId=f"patient_{lab['patient_id']}",
                           labId=f"lab_report_{lab['lab_id']}")
            
            # Create lab finding nodes and relationships
            for finding in lab_findings:
                query = """
                CREATE (f:LabFinding)
                SET f.nodeId = $nodeId,
                    f.name = $name,
                    f.test_name = $test_name,
                    f.value = $value,
                    f.is_abnormal = $abnormal
                """
                session.run(query,
                           nodeId=f"lab_finding_{finding['finding_id']}",
                           name=f"{finding['test']}: {finding['value']}",
                           test_name=finding['test'],
                           value=finding['value'],
                           abnormal=finding['abnormal'])
                
                # Create Lab Report -> Finding relationship
                query = """
                MATCH (l:LabReport {nodeId: $labId})
                MATCH (f:LabFinding {nodeId: $findingId})
                CREATE (l)-[:CONTAINS_FINDING]->(f)
                """
                session.run(query,
                           labId=f"lab_report_{finding['lab_id']}",
                           findingId=f"lab_finding_{finding['finding_id']}")
        
        logger.info(f"✅ Created {len(lab_reports)} lab reports and {len(lab_findings)} findings")
    
    def verify_graph(self):
        """Verify the created graph"""
        logger.info("📊 Verifying knowledge graph...")
        
        with self.neo4j_driver.session() as session:
            # Count nodes by type
            node_query = """
            MATCH (n)
            RETURN labels(n)[0] as label, COUNT(n) as count
            ORDER BY count DESC
            """
            results = session.run(node_query)
            
            logger.info("\n🏷️ Node counts:")
            total_nodes = 0
            for record in results:
                count = record['count']
                total_nodes += count
                logger.info(f"  {record['label']}: {count}")
            
            # Count relationships
            rel_query = "MATCH ()-[r]->() RETURN COUNT(r) as count"
            rel_result = session.run(rel_query)
            total_relationships = rel_result.single()['count']
            
            logger.info(f"\n📈 Total: {total_nodes} nodes, {total_relationships} relationships")
            
            # Test a specific patient's connections
            patient_query = """
            MATCH (p:Patient {name: 'John Doe'})-[r]->(connected)
            RETURN type(r) as relationship, connected.name as target
            ORDER BY relationship
            """
            results = session.run(patient_query)
            connections = list(results)
            
            logger.info(f"\n👤 John Doe's connections ({len(connections)} total):")
            for record in connections:
                logger.info(f"  -[{record['relationship']}]-> {record['target']}")
    
    def create_complete_atomic_kg(self):
        """Create the complete atomic facts knowledge graph"""
        logger.info("🚀 Creating Complete Atomic Facts Knowledge Graph")
        logger.info("=" * 60)
        
        if not self.connect_neo4j():
            return False
        
        try:
            # Clear existing data
            self.clear_neo4j()
            
            # Create all node types and relationships
            self.create_patient_nodes()
            self.create_medication_nodes_and_relationships()
            self.create_history_nodes_and_relationships()
            self.create_appointment_and_symptom_nodes()
            self.create_lab_nodes()
            
            # Verify the result
            self.verify_graph()
            
            logger.info("\n🎉 Atomic Facts Knowledge Graph Created Successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating knowledge graph: {e}")
            return False
        
        finally:
            if self.neo4j_driver:
                self.neo4j_driver.close()

def main():
    creator = SimplifiedKGCreator()
    success = creator.create_complete_atomic_kg()
    
    if success:
        print("""
🎉 Atomic Facts Knowledge Graph Created Successfully!

🌐 View in Neo4j Browser at your AuraDB instance
🔍 Try these sample queries:

1. See the complete graph structure:
   MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50

2. Find all medications for a patient:
   MATCH (p:Patient {name: 'John Doe'})-[:PRESCRIBED]->(m:Medication)-[:TREATS]->(c:MedicalCondition)
   RETURN p.name, m.name, m.dosage, c.name

3. Find patients with allergies:
   MATCH (p:Patient)-[:HAS_HISTORY]->(h:MedicalHistory)
   WHERE h.type = 'allergy'
   RETURN p.name, h.name

4. Find abnormal lab results:
   MATCH (p:Patient)-[:HAS_LAB_REPORT]->(l:LabReport)-[:CONTAINS_FINDING]->(f:LabFinding)
   WHERE f.is_abnormal = true
   RETURN p.name, f.test_name, f.value

5. Find patients by symptoms:
   MATCH (p:Patient)-[:HAS_APPOINTMENT]->(a:Appointment)-[:REPORTED_SYMPTOM]->(s:Symptom)
   WHERE s.name CONTAINS 'Pain'
   RETURN p.name, s.name, s.severity

✨ This demonstrates the power of atomic facts in knowledge graphs!
Each piece of medical information is now a connected, queryable node.
        """)
    else:
        print("❌ Failed to create knowledge graph")

if __name__ == "__main__":
    main()