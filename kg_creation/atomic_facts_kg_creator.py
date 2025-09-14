#!/usr/bin/env python3
"""
Atomic Facts Knowledge Graph Creator for MediMax
================================================================

This script creates a knowledge graph from the new atomic facts-based 
database schema where each piece of medical information is already 
stored as an atomic fact.

Author: GitHub Copilot
Date: September 14, 2025
"""

import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from neo4j import GraphDatabase
import mysql.connector
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AtomicFactsKGCreator:
    def __init__(self):
        load_dotenv()
        
        # Database connections
        self.mysql_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'MediMax')
        }
        
        # Neo4j connection
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_user = os.getenv('NEO4J_USERNAME')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        self.mysql_conn = None
        self.neo4j_driver = None
        
    def connect_mysql(self):
        """Connect to MySQL database"""
        try:
            self.mysql_conn = mysql.connector.connect(**self.mysql_config)
            logger.info("✅ Connected to MySQL database")
            return True
        except Exception as e:
            logger.error(f"❌ MySQL connection failed: {e}")
            return False
    
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
    
    def create_kg_for_patient(self, patient_id):
        """Create knowledge graph for a specific patient"""
        logger.info(f"🔄 Creating knowledge graph for patient {patient_id}")
        
        nodes = []
        relationships = []
        
        cursor = self.mysql_conn.cursor(dictionary=True)
        
        # 1. Get Patient node
        cursor.execute("SELECT * FROM Patient WHERE patient_id = %s", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            logger.error(f"❌ Patient {patient_id} not found")
            return None, None
        
        # Add patient node
        patient_node = {
            'id': f"patient_{patient_id}",
            'name': patient['name'],
            'type': 'Patient',
            'properties': {
                'dob': str(patient['dob']) if patient['dob'] else None,
                'sex': patient['sex'],
                'created_at': str(patient['created_at'])
            }
        }
        nodes.append(patient_node)
        
        # 2. Get Medications and their purposes
        cursor.execute("""
            SELECT m.*, mp.condition_name, mp.purpose_description
            FROM Medication m
            LEFT JOIN Medication_Purpose mp ON m.medication_id = mp.medication_id
            WHERE m.patient_id = %s
        """, (patient_id,))
        
        medications = cursor.fetchall()
        
        for med in medications:
            # Medication node
            med_node = {
                'id': f"medication_{med['medication_id']}",
                'name': med['medicine_name'],
                'type': 'Medication',
                'properties': {
                    'dosage': med['dosage'],
                    'frequency': med['frequency'],
                    'is_continued': med['is_continued'],
                    'prescribed_date': str(med['prescribed_date']),
                    'prescribed_by': med['prescribed_by']
                }
            }
            nodes.append(med_node)
            
            # Patient -> Medication relationship
            relationships.append({
                'source': f"patient_{patient_id}",
                'target': f"medication_{med['medication_id']}",
                'type': 'PRESCRIBED',
                'properties': {
                    'date': str(med['prescribed_date']),
                    'prescribed_by': med['prescribed_by']
                }
            })
            
            # Medical condition node and relationship (if exists)
            if med['condition_name']:
                condition_id = f"condition_{med['condition_name'].lower().replace(' ', '_')}"
                
                # Check if condition node already exists
                condition_exists = any(node['id'] == condition_id for node in nodes)
                if not condition_exists:
                    condition_node = {
                        'id': condition_id,
                        'name': med['condition_name'],
                        'type': 'MedicalCondition',
                        'properties': {
                            'description': med['purpose_description']
                        }
                    }
                    nodes.append(condition_node)
                
                # Medication -> Condition relationship
                relationships.append({
                    'source': f"medication_{med['medication_id']}",
                    'target': condition_id,
                    'type': 'TREATS',
                    'properties': {
                        'description': med['purpose_description']
                    }
                })
        
        # 3. Get Medical History
        cursor.execute("SELECT * FROM Medical_History WHERE patient_id = %s", (patient_id,))
        history_items = cursor.fetchall()
        
        for history in history_items:
            history_node = {
                'id': f"history_{history['history_id']}",
                'name': history['history_item'],
                'type': 'MedicalHistory',
                'properties': {
                    'history_type': history['history_type'],
                    'details': history['history_details'],
                    'severity': history['severity'],
                    'is_active': history['is_active'],
                    'history_date': str(history['history_date']) if history['history_date'] else None
                }
            }
            nodes.append(history_node)
            
            # Patient -> History relationship
            relationships.append({
                'source': f"patient_{patient_id}",
                'target': f"history_{history['history_id']}",
                'type': 'HAS_HISTORY',
                'properties': {
                    'type': history['history_type'],
                    'is_active': history['is_active']
                }
            })
        
        # 4. Get Appointments and Symptoms
        cursor.execute("SELECT * FROM Appointment WHERE patient_id = %s", (patient_id,))
        appointments = cursor.fetchall()
        
        for appointment in appointments:
            appointment_node = {
                'id': f"appointment_{appointment['appointment_id']}",
                'name': f"Appointment on {appointment['appointment_date']}",
                'type': 'Appointment',
                'properties': {
                    'date': str(appointment['appointment_date']),
                    'time': str(appointment['appointment_time']) if appointment['appointment_time'] else None,
                    'status': appointment['status'],
                    'type': appointment['appointment_type'],
                    'doctor': appointment['doctor_name']
                }
            }
            nodes.append(appointment_node)
            
            # Patient -> Appointment relationship
            relationships.append({
                'source': f"patient_{patient_id}",
                'target': f"appointment_{appointment['appointment_id']}",
                'type': 'HAS_APPOINTMENT',
                'properties': {
                    'date': str(appointment['appointment_date']),
                    'status': appointment['status']
                }
            })
            
            # Get symptoms for this appointment
            cursor.execute("SELECT * FROM Appointment_Symptom WHERE appointment_id = %s", 
                         (appointment['appointment_id'],))
            symptoms = cursor.fetchall()
            
            for symptom in symptoms:
                symptom_node = {
                    'id': f"symptom_{symptom['symptom_id']}",
                    'name': symptom['symptom_name'],
                    'type': 'Symptom',
                    'properties': {
                        'description': symptom['symptom_description'],
                        'severity': symptom['severity'],
                        'duration': symptom['duration'],
                        'onset_type': symptom['onset_type']
                    }
                }
                nodes.append(symptom_node)
                
                # Appointment -> Symptom relationship
                relationships.append({
                    'source': f"appointment_{appointment['appointment_id']}",
                    'target': f"symptom_{symptom['symptom_id']}",
                    'type': 'REPORTED_SYMPTOM',
                    'properties': {
                        'severity': symptom['severity'],
                        'duration': symptom['duration']
                    }
                })
        
        # 5. Get Lab Reports and Findings
        cursor.execute("SELECT * FROM Lab_Report WHERE patient_id = %s", (patient_id,))
        lab_reports = cursor.fetchall()
        
        for lab_report in lab_reports:
            lab_report_node = {
                'id': f"lab_report_{lab_report['lab_report_id']}",
                'name': f"{lab_report['lab_type']} on {lab_report['lab_date']}",
                'type': 'LabReport',
                'properties': {
                    'date': str(lab_report['lab_date']),
                    'type': lab_report['lab_type'],
                    'doctor': lab_report['ordering_doctor'],
                    'facility': lab_report['lab_facility']
                }
            }
            nodes.append(lab_report_node)
            
            # Patient -> Lab Report relationship
            relationships.append({
                'source': f"patient_{patient_id}",
                'target': f"lab_report_{lab_report['lab_report_id']}",
                'type': 'HAS_LAB_REPORT',
                'properties': {
                    'date': str(lab_report['lab_date']),
                    'doctor': lab_report['ordering_doctor']
                }
            })
            
            # Get lab findings
            cursor.execute("SELECT * FROM Lab_Finding WHERE lab_report_id = %s", 
                         (lab_report['lab_report_id'],))
            lab_findings = cursor.fetchall()
            
            for finding in lab_findings:
                finding_node = {
                    'id': f"lab_finding_{finding['lab_finding_id']}",
                    'name': f"{finding['test_name']}: {finding['test_value']} {finding['test_unit'] or ''}",
                    'type': 'LabFinding',
                    'properties': {
                        'test_name': finding['test_name'],
                        'value': finding['test_value'],
                        'unit': finding['test_unit'],
                        'reference_range': finding['reference_range'],
                        'is_abnormal': finding['is_abnormal'],
                        'abnormal_flag': finding['abnormal_flag']
                    }
                }
                nodes.append(finding_node)
                
                # Lab Report -> Finding relationship
                relationships.append({
                    'source': f"lab_report_{lab_report['lab_report_id']}",
                    'target': f"lab_finding_{finding['lab_finding_id']}",
                    'type': 'CONTAINS_FINDING',
                    'properties': {
                        'is_abnormal': finding['is_abnormal'],
                        'abnormal_flag': finding['abnormal_flag']
                    }
                })
        
        # 6. Get Chat History
        cursor.execute("SELECT * FROM Chat_History WHERE patient_id = %s ORDER BY timestamp", 
                      (patient_id,))
        chat_messages = cursor.fetchall()
        
        for chat in chat_messages:
            chat_node = {
                'id': f"chat_{chat['chat_id']}",
                'name': chat['message_text'][:50] + "..." if len(chat['message_text']) > 50 else chat['message_text'],
                'type': 'ChatMessage',
                'properties': {
                    'message_text': chat['message_text'],
                    'message_type': chat['message_type'],
                    'timestamp': str(chat['timestamp']),
                    'session_id': chat['session_id']
                }
            }
            nodes.append(chat_node)
            
            # Patient -> Chat relationship
            relationships.append({
                'source': f"patient_{patient_id}",
                'target': f"chat_{chat['chat_id']}",
                'type': 'HAS_CHAT',
                'properties': {
                    'message_type': chat['message_type'],
                    'timestamp': str(chat['timestamp'])
                }
            })
        
        cursor.close()
        
        logger.info(f"✅ Created {len(nodes)} nodes and {len(relationships)} relationships for patient {patient_id}")
        return nodes, relationships
    
    def export_to_neo4j(self, nodes, relationships):
        """Export knowledge graph to Neo4j"""
        logger.info("🔄 Exporting to Neo4j...")
        
        with self.neo4j_driver.session() as session:
            # Clear existing data
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create nodes
            for node in nodes:
                query = f"""
                CREATE (n:{node['type']})
                SET n.nodeId = $nodeId,
                    n.name = $name,
                    n += $properties
                """
                session.run(query, 
                           nodeId=node['id'],
                           name=node['name'],
                           properties=node['properties'])
            
            # Create relationships
            for rel in relationships:
                query = f"""
                MATCH (source {{nodeId: $sourceId}})
                MATCH (target {{nodeId: $targetId}})
                CREATE (source)-[r:{rel['type']}]->(target)
                SET r += $properties
                """
                session.run(query,
                           sourceId=rel['source'],
                           targetId=rel['target'],
                           properties=rel.get('properties', {}))
        
        logger.info(f"✅ Exported {len(nodes)} nodes and {len(relationships)} relationships to Neo4j")
    
    def export_to_csv(self, nodes, relationships, patient_id):
        """Export knowledge graph to CSV files"""
        logger.info("💾 Exporting to CSV files...")
        
        # Export nodes
        nodes_data = []
        for node in nodes:
            nodes_data.append({
                ':ID': node['id'],
                'name': node['name'],
                ':LABEL': node['type'],
                'properties': json.dumps(node['properties'])
            })
        
        nodes_df = pd.DataFrame(nodes_data)
        nodes_file = f'atomic_kg_nodes_patient_{patient_id}.csv'
        nodes_df.to_csv(nodes_file, index=False)
        
        # Export relationships
        rels_data = []
        for rel in relationships:
            rels_data.append({
                ':START_ID': rel['source'],
                ':END_ID': rel['target'],
                ':TYPE': rel['type'],
                'properties': json.dumps(rel.get('properties', {}))
            })
        
        rels_df = pd.DataFrame(rels_data)
        rels_file = f'atomic_kg_relationships_patient_{patient_id}.csv'
        rels_df.to_csv(rels_file, index=False)
        
        logger.info(f"✅ Exported to {nodes_file} and {rels_file}")
        return nodes_file, rels_file
    
    def create_complete_kg(self):
        """Create knowledge graph for all patients"""
        logger.info("🚀 Creating Complete Atomic Facts Knowledge Graph")
        logger.info("=" * 60)
        
        if not self.connect_mysql():
            return False
        
        if not self.connect_neo4j():
            return False
        
        try:
            # Get all patients
            cursor = self.mysql_conn.cursor(dictionary=True)
            cursor.execute("SELECT patient_id, name FROM Patient")
            patients = cursor.fetchall()
            cursor.close()
            
            logger.info(f"📊 Found {len(patients)} patients")
            
            all_nodes = []
            all_relationships = []
            
            # Create KG for each patient
            for patient in patients:
                patient_id = patient['patient_id']
                patient_name = patient['name']
                
                logger.info(f"🔄 Processing patient {patient_id}: {patient_name}")
                
                nodes, relationships = self.create_kg_for_patient(patient_id)
                
                if nodes and relationships:
                    all_nodes.extend(nodes)
                    all_relationships.extend(relationships)
                    
                    # Export individual patient KG
                    self.export_to_csv(nodes, relationships, patient_id)
            
            # Export complete knowledge graph
            logger.info("📤 Exporting complete knowledge graph...")
            
            # Export to Neo4j
            self.export_to_neo4j(all_nodes, all_relationships)
            
            # Export complete CSV
            self.export_to_csv(all_nodes, all_relationships, 'complete')
            
            # Summary
            logger.info(f"""
📈 Knowledge Graph Creation Complete!
┌─────────────────────┬──────────┐
│ Metric              │ Count    │
├─────────────────────┼──────────┤
│ Total Patients      │ {len(patients):8} │
│ Total Nodes         │ {len(all_nodes):8} │
│ Total Relationships │ {len(all_relationships):8} │
└─────────────────────┴──────────┘
            """)
            
            # Node type breakdown
            node_types = {}
            for node in all_nodes:
                node_type = node['type']
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            logger.info("🏷️ Node Types:")
            for node_type, count in sorted(node_types.items()):
                logger.info(f"  {node_type}: {count}")
            
            # Relationship type breakdown
            rel_types = {}
            for rel in all_relationships:
                rel_type = rel['type']
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            logger.info("🔗 Relationship Types:")
            for rel_type, count in sorted(rel_types.items()):
                logger.info(f"  {rel_type}: {count}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating knowledge graph: {e}")
            return False
        
        finally:
            if self.mysql_conn:
                self.mysql_conn.close()
            if self.neo4j_driver:
                self.neo4j_driver.close()

def main():
    creator = AtomicFactsKGCreator()
    success = creator.create_complete_kg()
    
    if success:
        print("""
🎉 Atomic Facts Knowledge Graph Created Successfully!
🌐 View in Neo4j Browser: Your AuraDB instance
🔍 Try these queries:

1. See all patients and their medications:
   MATCH (p:Patient)-[:PRESCRIBED]->(m:Medication)-[:TREATS]->(c:MedicalCondition)
   RETURN p.name, m.name, c.name

2. Find patients with specific conditions:
   MATCH (p:Patient)-[:HAS_HISTORY]->(h:MedicalHistory)
   WHERE h.history_type = 'allergy'
   RETURN p.name, h.name

3. View complete patient graph:
   MATCH (p:Patient {name: 'John Doe'})-[*1..3]-(connected)
   RETURN p, connected

4. Find abnormal lab results:
   MATCH (p:Patient)-[:HAS_LAB_REPORT]->(lr:LabReport)-[:CONTAINS_FINDING]->(lf:LabFinding)
   WHERE lf.is_abnormal = true
   RETURN p.name, lf.test_name, lf.value, lf.abnormal_flag
        """)
    else:
        print("❌ Failed to create knowledge graph")

if __name__ == "__main__":
    main()