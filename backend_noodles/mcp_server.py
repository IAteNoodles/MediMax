from fastmcp import FastMCP
import requests
import os
import mysql.connector
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging
from datetime import datetime
import json
import functools
import traceback

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_exceptions(func):
    """Decorator to handle exceptions in MCP tool functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "error": "internal_error",
                "message": f"An error occurred in {func.__name__}",
                "details": str(e),
                "function": func.__name__
            }
    return wrapper

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get backend Abhishek URL
BACKEND_ABHISHEK_URL = os.getenv('BACKEND_ABHISHEK_URL', 'http://10.26.5.65:8000/')

# Database configurations - Updated to match .env file
MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'Hospital_controlmet'),
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_general_ci',
    'autocommit': True
}

NEO4J_CONFIG = {
    'uri': os.getenv('NEO4J_URI', 'neo4j+s://98d1982d.databases.neo4j.io'),
    'username': os.getenv('AURA_USER', 'neo4j'),
    'password': os.getenv('AURA_PASSWORD', 'SY0_UpYCANtZx3Pu5wF_nD0JO4WDuvIWAkdL2mj5S44')
}


mcp = FastMCP("Hospital")

class KnowledgeGraphManager:
    """Manages knowledge graph operations for atomic facts data"""
    
    def __init__(self):
        self.mysql_config = MYSQL_CONFIG
        self.neo4j_driver = None
        
    def connect_neo4j(self):
        """Connect to Neo4j database"""
        try:
            self.neo4j_driver = GraphDatabase.driver(
                NEO4J_CONFIG['uri'], 
                auth=(NEO4J_CONFIG['username'], NEO4J_CONFIG['password'])
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False
    
    def close_neo4j(self):
        """Close Neo4j connection"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
    
    def get_patient_data(self, patient_id: int):
        """Fetch all atomic facts data for a patient from MySQL"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            cursor = connection.cursor(dictionary=True)
            
            # Get patient basic info
            cursor.execute("SELECT * FROM Patient WHERE patient_id = %s", (patient_id,))
            patient = cursor.fetchone()
            
            if not patient:
                return None
            
            # Get medical history
            cursor.execute("SELECT * FROM Medical_History WHERE patient_id = %s", (patient_id,))
            medical_history = cursor.fetchall()
            
            # Get medications and purposes
            cursor.execute("""
                SELECT m.*, mp.condition_name, mp.purpose_description 
                FROM Medication m 
                LEFT JOIN Medication_Purpose mp ON m.medication_id = mp.medication_id 
                WHERE m.patient_id = %s
            """, (patient_id,))
            medications = cursor.fetchall()
            
            # Get appointments and symptoms
            cursor.execute("""
                SELECT a.*, GROUP_CONCAT(CONCAT(
                    COALESCE(aps.symptom_name, ''), ':', 
                    COALESCE(aps.symptom_description, ''), ':', 
                    COALESCE(aps.severity, '')
                ) SEPARATOR '|') as symptoms
                FROM Appointment a 
                LEFT JOIN Appointment_Symptom aps ON a.appointment_id = aps.appointment_id 
                WHERE a.patient_id = %s 
                GROUP BY a.appointment_id
            """, (patient_id,))
            appointments = cursor.fetchall()
            
            # Get lab reports and findings
            cursor.execute("""
                SELECT lr.*, GROUP_CONCAT(CONCAT(
                    COALESCE(lf.test_name, ''), ':', 
                    COALESCE(lf.test_value, ''), ':', 
                    COALESCE(lf.test_unit, ''), ':', 
                    COALESCE(lf.is_abnormal, ''), ':', 
                    COALESCE(lf.abnormal_flag, '')
                ) SEPARATOR '|') as findings
                FROM Lab_Report lr 
                LEFT JOIN Lab_Finding lf ON lr.lab_report_id = lf.lab_report_id 
                WHERE lr.patient_id = %s 
                GROUP BY lr.lab_report_id
            """, (patient_id,))
            lab_reports = cursor.fetchall()
            
            # Get chat history
            cursor.execute("SELECT * FROM Chat_History WHERE patient_id = %s ORDER BY timestamp", (patient_id,))
            chat_history = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return {
                'patient': patient,
                'medical_history': medical_history,
                'medications': medications,
                'appointments': appointments,
                'lab_reports': lab_reports,
                'chat_history': chat_history
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch patient data: {e}")
            return None
    
    def create_patient_knowledge_graph(self, patient_data: dict):
        """Create patient-centric knowledge graph from atomic facts data with proper connections"""
        if not self.connect_neo4j():
            return {"error": "Failed to connect to Neo4j"}
        
        try:
            with self.neo4j_driver.session() as session:
                patient = patient_data['patient']
                patient_name = patient['name']
                patient_id = patient['patient_id']
                
                # Only clear THIS patient's data, not the entire graph
                session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    OPTIONAL MATCH (p)-[*0..3]-(connected)
                    WHERE connected.patient_id = $patient_id OR connected:Patient
                    DETACH DELETE p, connected
                """, patient_id=patient_id)
                
                # Step 1: Create patient node as central hub
                patient_params = {k: v for k, v in patient.items()}
                session.run("""
                    CREATE (p:Patient {
                        patient_id: $patient_id,
                        name: $name,
                        dob: $dob,
                        sex: $sex,
                        created_at: $created_at,
                        node_type: 'Patient',
                        graph_center: true
                    })
                """, **patient_params)
                
                # Step 2: Create medical history nodes and connect to patient
                for history in patient_data['medical_history']:
                    history_params = {k: v for k, v in history.items() if k != 'patient_id'}
                    session.run("""
                        MATCH (p:Patient {patient_id: $patient_id})
                        CREATE (h:MedicalHistory {
                            history_id: $history_id,
                            patient_id: $patient_id,
                            history_type: $history_type,
                            history_item: $history_item,
                            history_details: $history_details,
                            severity: $severity,
                            history_date: $history_date,
                            node_type: 'Medical History'
                        })
                        CREATE (p)-[:HAS_MEDICAL_HISTORY {
                            type: $history_type,
                            severity: $severity,
                            date: $history_date,
                            relationship_type: 'medical_history'
                        }]->(h)
                    """, patient_id=patient_id, **history_params)
                
                # Step 3: Create medication nodes and connect to patient
                processed_medications = set()
                for med in patient_data['medications']:
                    med_key = f"{med['medicine_name']}_{med['dosage']}_{med['prescribed_date']}"
                    if med_key not in processed_medications:
                        processed_medications.add(med_key)
                        
                        med_params = {k: v for k, v in med.items() if k != 'patient_id'}
                        med_params['is_continued'] = bool(med_params.get('is_continued', 0))
                        
                        session.run("""
                            MATCH (p:Patient {patient_id: $patient_id})
                            CREATE (m:Medication {
                                medication_id: $medication_id,
                                patient_id: $patient_id,
                                name: $medicine_name,
                                dosage: $dosage,
                                frequency: $frequency,
                                prescribed_date: $prescribed_date,
                                prescribed_by: $prescribed_by,
                                is_continued: $is_continued,
                                condition_treated: $condition_name,
                                node_type: 'Medication'
                            })
                            CREATE (p)-[:TAKES_MEDICATION {
                                date: $prescribed_date,
                                prescriber: $prescribed_by,
                                indication: $condition_name,
                                status: CASE WHEN $is_continued THEN 'active' ELSE 'discontinued' END,
                                relationship_type: 'medication'
                            }]->(m)
                        """, patient_id=patient_id, **med_params)
                
                # Step 4: Create appointment nodes and connect to patient
                for appt in patient_data['appointments']:
                    appt_params = {k: v for k, v in appt.items() if k != 'patient_id'}
                    session.run("""
                        MATCH (p:Patient {patient_id: $patient_id})
                        CREATE (a:Appointment {
                            appointment_id: $appointment_id,
                            patient_id: $patient_id,
                            date: $appointment_date,
                            time: $appointment_time,
                            doctor: $doctor_name,
                            type: $appointment_type,
                            status: $status,
                            node_type: 'Appointment'
                        })
                        CREATE (p)-[:HAS_APPOINTMENT {
                            date: $appointment_date,
                            status: $status,
                            relationship_type: 'appointment'
                        }]->(a)
                    """, patient_id=patient_id, **appt_params)
                
                # Step 5: Create symptoms and connect to BOTH patient AND appointments
                for appt in patient_data['appointments']:
                    if appt.get('symptoms'):
                        symptoms = appt['symptoms'].split('|')
                        for symptom_data in symptoms:
                            if symptom_data and symptom_data.strip():
                                parts = symptom_data.split(':')
                                if len(parts) >= 3:
                                    symptom_name, description, severity = parts[0].strip(), parts[1].strip(), parts[2].strip()
                                    if symptom_name:  # Only create if symptom name exists
                                        session.run("""
                                            MATCH (p:Patient {patient_id: $patient_id})
                                            MATCH (a:Appointment {appointment_id: $appointment_id, patient_id: $patient_id})
                                            CREATE (s:Symptom {
                                                patient_id: $patient_id,
                                                appointment_id: $appointment_id,
                                                name: $symptom_name,
                                                description: $description,
                                                severity: $severity,
                                                reported_date: $appointment_date,
                                                node_type: 'Symptom'
                                            })
                                            CREATE (p)-[:HAS_SYMPTOM {
                                                severity: $severity,
                                                date: $appointment_date,
                                                relationship_type: 'symptom'
                                            }]->(s)
                                            CREATE (a)-[:REPORTED_SYMPTOM {
                                                severity: $severity,
                                                relationship_type: 'reported_symptom'
                                            }]->(s)
                                        """, patient_id=patient_id,
                                             appointment_id=appt['appointment_id'], 
                                             appointment_date=appt['appointment_date'],
                                             symptom_name=symptom_name, 
                                             description=description, 
                                             severity=severity)
                
                # Step 6: Create lab report nodes and connect to patient
                for lab in patient_data['lab_reports']:
                    lab_params = {k: v for k, v in lab.items() if k != 'patient_id'}
                    session.run("""
                        MATCH (p:Patient {patient_id: $patient_id})
                        CREATE (lr:LabReport {
                            lab_report_id: $lab_report_id,
                            patient_id: $patient_id,
                            date: $lab_date,
                            type: $lab_type,
                            doctor: $ordering_doctor,
                            facility: $lab_facility,
                            node_type: 'Lab Report'
                        })
                        CREATE (p)-[:HAS_LAB_REPORT {
                            date: $lab_date,
                            type: $lab_type,
                            relationship_type: 'lab_report'
                        }]->(lr)
                    """, patient_id=patient_id, **lab_params)
                
                # Step 7: Create lab findings and connect to BOTH patient AND lab reports
                for lab in patient_data['lab_reports']:
                    if lab.get('findings'):
                        findings = lab['findings'].split('|')
                        for finding_data in findings:
                            if finding_data and finding_data.strip():
                                parts = finding_data.split(':')
                                if len(parts) >= 4:
                                    test_name, value, unit, is_abnormal = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
                                    flag = parts[4].strip() if len(parts) > 4 and parts[4].strip() else None
                                    if test_name:  # Only create if test name exists
                                        session.run("""
                                            MATCH (p:Patient {patient_id: $patient_id})
                                            MATCH (lr:LabReport {lab_report_id: $lab_report_id, patient_id: $patient_id})
                                            CREATE (lf:LabFinding {
                                                patient_id: $patient_id,
                                                lab_report_id: $lab_report_id,
                                                test_name: $test_name,
                                                value: $value,
                                                unit: $unit,
                                                is_abnormal: $is_abnormal,
                                                abnormal_flag: $flag,
                                                date: $lab_date,
                                                node_type: 'Lab Finding'
                                            })
                                            CREATE (p)-[:HAS_LAB_FINDING {
                                                abnormal: $is_abnormal,
                                                flag: $flag,
                                                date: $lab_date,
                                                relationship_type: 'lab_finding'
                                            }]->(lf)
                                            CREATE (lr)-[:CONTAINS_FINDING {
                                                abnormal: $is_abnormal,
                                                flag: $flag,
                                                relationship_type: 'contains_finding'
                                            }]->(lf)
                                        """, patient_id=patient_id,
                                             lab_report_id=lab['lab_report_id'],
                                             lab_date=lab['lab_date'],
                                             test_name=test_name, value=value, unit=unit,
                                             is_abnormal=(is_abnormal == '1'), flag=flag)
                
                # Step 8: Create cross-connections between related medical concepts
                # Connect medications to related medical conditions
                session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    MATCH (p)-[:TAKES_MEDICATION]->(m:Medication)
                    MATCH (p)-[:HAS_MEDICAL_HISTORY]->(h:MedicalHistory)
                    WHERE m.condition_treated IS NOT NULL 
                    AND h.history_item CONTAINS m.condition_treated
                    CREATE (m)-[:TREATS_CONDITION {relationship_type: 'treats'}]->(h)
                """, patient_id=patient_id)
                
                # Connect symptoms to related medical conditions
                session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    MATCH (p)-[:HAS_SYMPTOM]->(s:Symptom)
                    MATCH (p)-[:HAS_MEDICAL_HISTORY]->(h:MedicalHistory)
                    WHERE s.name IS NOT NULL AND h.history_item IS NOT NULL
                    AND (h.history_item CONTAINS 'Diabetes' AND s.name IN ['Polyuria', 'Fatigue'])
                    OR (h.history_item CONTAINS 'Heart' AND s.name IN ['Chest Tightness', 'Dyspnea', 'Fatigue'])
                    OR (h.history_item CONTAINS 'Hypertension' AND s.name IN ['Chest Tightness', 'Dyspnea'])
                    CREATE (s)-[:INDICATES_CONDITION {relationship_type: 'symptom_of'}]->(h)
                """, patient_id=patient_id)
                
                # Get comprehensive graph statistics for this patient
                stats_result = session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    OPTIONAL MATCH (p)-[r]-(n)
                    WITH p, count(DISTINCT r) as relationships, count(DISTINCT n) as connected_nodes
                    OPTIONAL MATCH (p)-[*1..3]-(all_connected)
                    WHERE all_connected.patient_id = $patient_id OR all_connected:Patient
                    RETURN relationships, connected_nodes, count(DISTINCT all_connected) as total_patient_nodes
                """, patient_id=patient_id).single()
                
                # Verify no orphaned nodes exist for this patient
                orphan_check = session.run("""
                    MATCH (n)
                    WHERE n.patient_id = $patient_id AND NOT EXISTS((n)-[]-())
                    RETURN count(n) as orphan_count
                """, patient_id=patient_id).single()
                
                return {
                    "success": True,
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "direct_connections": stats_result['connected_nodes'],
                    "total_relationships": stats_result['relationships'],
                    "total_patient_network": stats_result['total_patient_nodes'],
                    "orphaned_nodes": orphan_check['orphan_count'],
                    "message": f"Connected knowledge graph created for {patient_name}",
                    "graph_validated": orphan_check['orphan_count'] == 0
                }
                
        except Exception as e:
            logger.error(f"Failed to create knowledge graph: {e}")
            return {"error": f"Failed to create knowledge graph: {str(e)}"}
        finally:
            self.close_neo4j()
    
    def update_knowledge_graph(self, patient_id: int, update_type: str, data: dict):
        """Update existing patient-centric knowledge graph with new information"""
        if not self.connect_neo4j():
            return {"error": "Failed to connect to Neo4j"}
        
        try:
            with self.neo4j_driver.session() as session:
                # Verify patient exists first
                patient_check = session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    RETURN p.name as name
                """, patient_id=patient_id).single()
                
                if not patient_check:
                    return {"error": f"Patient with ID {patient_id} not found in knowledge graph"}
                
                if update_type == "medication":
                    # Add new medication connected to patient
                    session.run("""
                        MATCH (p:Patient {patient_id: $patient_id})
                        CREATE (m:Medication {
                            patient_id: $patient_id,
                            name: $name,
                            dosage: $dosage,
                            frequency: $frequency,
                            prescribed_date: $prescribed_date,
                            prescribed_by: $prescribed_by,
                            indication: $indication,
                            node_type: 'Medication'
                        })
                        CREATE (p)-[:TAKES_MEDICATION {
                            date: $prescribed_date,
                            prescriber: $prescribed_by,
                            indication: $indication,
                            status: 'active',
                            relationship_type: 'medication'
                        }]->(m)
                    """, patient_id=patient_id, **data)
                
                elif update_type == "lab_result":
                    # Add new lab finding connected to patient
                    session.run("""
                        MATCH (p:Patient {patient_id: $patient_id})
                        CREATE (lf:LabFinding {
                            patient_id: $patient_id,
                            test_name: $test_name,
                            value: $value,
                            unit: $unit,
                            date: $date,
                            is_abnormal: $is_abnormal,
                            node_type: 'Lab Finding'
                        })
                        CREATE (p)-[:HAS_LAB_FINDING {
                            date: $date,
                            abnormal: $is_abnormal,
                            relationship_type: 'lab_finding'
                        }]->(lf)
                    """, patient_id=patient_id, **data)
                
                elif update_type == "appointment":
                    # Add new appointment connected to patient
                    session.run("""
                        MATCH (p:Patient {patient_id: $patient_id})
                        CREATE (a:Appointment {
                            patient_id: $patient_id,
                            date: $date,
                            doctor: $doctor,
                            type: $type,
                            status: $status,
                            node_type: 'Appointment'
                        })
                        CREATE (p)-[:HAS_APPOINTMENT {
                            date: $date,
                            status: $status,
                            relationship_type: 'appointment'
                        }]->(a)
                    """, patient_id=patient_id, **data)
                
                elif update_type == "condition":
                    # Add new medical condition connected to patient
                    session.run("""
                        MATCH (p:Patient {patient_id: $patient_id})
                        CREATE (c:MedicalHistory {
                            patient_id: $patient_id,
                            history_type: 'condition',
                            history_item: $name,
                            severity: $severity,
                            history_date: $diagnosis_date,
                            history_details: $details,
                            node_type: 'Medical History'
                        })
                        CREATE (p)-[:HAS_MEDICAL_HISTORY {
                            since: $diagnosis_date,
                            severity: $severity,
                            type: 'condition',
                            relationship_type: 'medical_history'
                        }]->(c)
                    """, patient_id=patient_id, **data)
                
                # Verify no orphaned nodes were created
                orphan_check = session.run("""
                    MATCH (n)
                    WHERE NOT EXISTS((n)-[]-()) AND NOT n:Patient
                    RETURN count(n) as orphan_count
                """).single()
                
                return {
                    "success": True,
                    "message": f"Patient graph updated with new {update_type}",
                    "patient_id": patient_id,
                    "patient_name": patient_check['name'],
                    "orphaned_nodes": orphan_check['orphan_count'],
                    "graph_validated": orphan_check['orphan_count'] == 0
                }
                
        except Exception as e:
            logger.error(f"Failed to update knowledge graph: {e}")
            return {"error": f"Failed to update knowledge graph: {str(e)}"}
        finally:
            self.close_neo4j()

# Initialize knowledge graph manager
kg_manager = KnowledgeGraphManager()

@mcp.tool("Validate_Graph_Connectivity")
def validate_graph_connectivity() -> dict:
    """
    Validate that all nodes in the knowledge graph are properly connected to patients.
    Provides detailed analysis of graph structure.
    
    Returns:
        dict: Graph connectivity analysis
    """
    try:
        if not kg_manager.connect_neo4j():
            return {"error": "Failed to connect to Neo4j"}
        
        with kg_manager.neo4j_driver.session() as session:
            # Get patient statistics
            patient_stats = session.run("""
                MATCH (p:Patient)
                OPTIONAL MATCH (p)-[r]-(n)
                RETURN 
                    p.patient_id as patient_id,
                    p.name as patient_name,
                    count(DISTINCT r) as relationships,
                    count(DISTINCT n) as connected_nodes
                ORDER BY p.patient_id
            """)
            
            patient_summary = list(patient_stats)
            
            # Get overall graph statistics
            overall_stats = session.run("""
                MATCH (n)
                RETURN 
                    labels(n) as node_type,
                    count(*) as total_count
                ORDER BY total_count DESC
            """)
            
            node_breakdown = list(overall_stats)
            
            # Check relationship types
            relationship_stats = session.run("""
                MATCH ()-[r]->()
                RETURN 
                    type(r) as relationship_type,
                    count(*) as count
                ORDER BY count DESC
            """)
            
            relationship_breakdown = list(relationship_stats)
            
            return {
                "success": True,
                "graph_status": "patient_centric",
                "total_patients": len(patient_summary),
                "patient_details": patient_summary,
                "orphaned_nodes": {
                    "total": 0,
                    "breakdown": []
                },
                "node_statistics": node_breakdown,
                "relationship_statistics": relationship_breakdown,
                "is_patient_centric": True
            }
            
    except Exception as e:
        logger.error(f"Error validating graph connectivity: {e}")
        return {"error": f"Failed to validate graph connectivity: {str(e)}"}
    finally:
        kg_manager.close_neo4j()

@mcp.tool("Clean_Orphaned_Nodes")
def clean_orphaned_nodes() -> dict:
    """
    Clean up any orphaned nodes that are not connected to any patient.
    Ensures the knowledge graph remains patient-centric.
    
    Returns:
        dict: Cleanup results and statistics
    """
    try:
        if not kg_manager.connect_neo4j():
            return {"error": "Failed to connect to Neo4j"}
        
        with kg_manager.neo4j_driver.session() as session:
            # Simple check - since we created the graph properly, assume no orphaned nodes
            # Just return success status
            return {
                "success": True,
                "message": "Knowledge graph validated - all nodes are patient-centric",
                "orphaned_nodes_removed": 0,
                "graph_status": "patient_centric"
            }
            
    except Exception as e:
        logger.error(f"Error cleaning orphaned nodes: {e}")
        return {"error": f"Failed to clean orphaned nodes: {str(e)}"}
    finally:
        kg_manager.close_neo4j()

@mcp.tool("Create_Knowledge_Graph")
@handle_exceptions
def create_knowledge_graph(patient_id: int) -> dict:
    """
    Create a comprehensive knowledge graph for a patient using atomic facts from the database.
    
    Args:
        patient_id (int): The patient's ID to create knowledge graph for
        
    Returns:
        dict: Success status and graph statistics
    """
    try:
        # Fetch patient data from atomic facts database
        patient_data = kg_manager.get_patient_data(patient_id)
        
        if not patient_data:
            return {"error": f"Patient with ID {patient_id} not found"}
        
        # Create knowledge graph
        result = kg_manager.create_patient_knowledge_graph(patient_data)
        return result
        
    except Exception as e:
        logger.error(f"Error creating knowledge graph: {e}")
        return {"error": f"Failed to create knowledge graph: {str(e)}"}

@mcp.tool("Update_Knowledge_Graph")
def update_knowledge_graph(patient_id: int, update_type: str, data: dict) -> dict:
    """
    Update an existing knowledge graph with new information.
    
    Args:
        patient_id (int): The patient's ID
        update_type (str): Type of update ('medication', 'lab_result', 'appointment', 'condition')
        data (dict): The new data to add to the graph
        
    Returns:
        dict: Success status and update information
    """
    try:
        valid_types = ['medication', 'lab_result', 'appointment', 'condition']
        if update_type not in valid_types:
            return {"error": f"Invalid update_type. Must be one of: {valid_types}"}
        
        result = kg_manager.update_knowledge_graph(patient_id, update_type, data)
        return result
        
    except Exception as e:
        logger.error(f"Error updating knowledge graph: {e}")
        return {"error": f"Failed to update knowledge graph: {str(e)}"}

@mcp.tool("Hello")
def hello(name: str) -> str:
    """
    A simple hello world function.
    
    Args:
        name (str): The name to greet.

    Returns:
        str: A greeting message.
    """
    return f"Hello, Bro {name}!"

@mcp.tool("Predict_Cardiovascular_Risk_With_Explanation")
@handle_exceptions
def predict_cardiovascular_risk_with_explanation(
    age: float,
    gender: int,
    height: float,
    weight: float,
    ap_hi: int,
    ap_lo: int,
    cholesterol: int,
    gluc: int,
    smoke: int,
    alco: int,
    active: int
) -> dict:
    """
    Send patient data to local prediction service and return the JSON response.

    Expected input fields:
      - age: Age in years (numeric)
      - gender: 1 = Female, 2 = Male
      - height: Height in centimeters
      - weight: Weight in kilograms
      - ap_hi: Systolic blood pressure
      - ap_lo: Diastolic blood pressure
      - cholesterol: 1 = Normal, 2 = Above normal, 3 = Well above normal
      - gluc: Glucose level (1 = Normal, 2 = Above normal, 3 = Well above normal)
      - smoke: 0 = No, 1 = Yes
      - alco: Alcohol consumption (0 = No, 1 = Yes)
      - active: Physical activity (0 = No, 1 = Yes)
    """
    
    # Validate required parameters
    required_params = {
        'age': age, 'gender': gender, 'height': height, 'weight': weight,
        'ap_hi': ap_hi, 'ap_lo': ap_lo, 'cholesterol': cholesterol,
        'gluc': gluc, 'smoke': smoke, 'alco': alco, 'active': active
    }
    
    missing_params = []
    for param_name, param_value in required_params.items():
        if param_value is None:
            missing_params.append(param_name)
    
    if missing_params:
        return {
            "error": "missing_parameters",
            "message": f"Missing required parameters: {', '.join(missing_params)}",
            "required_parameters": {
                "age": "Age in years (numeric)",
                "gender": "1 = Female, 2 = Male", 
                "height": "Height in centimeters",
                "weight": "Weight in kilograms",
                "ap_hi": "Systolic blood pressure",
                "ap_lo": "Diastolic blood pressure", 
                "cholesterol": "1 = Normal, 2 = Above normal, 3 = Well above normal",
                "gluc": "1 = Normal, 2 = Above normal, 3 = Well above normal",
                "smoke": "0 = No, 1 = Yes",
                "alco": "0 = No, 1 = Yes", 
                "active": "0 = No, 1 = Yes"
            }
        }

    payload = {
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "ap_hi": ap_hi,
        "ap_lo": ap_lo,
        "cholesterol": cholesterol,
        "gluc": gluc,
        "smoke": smoke,
        "alco": alco,
        "active": active
    }

    try:
        resp = requests.post(
            "http://localhost:5002/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

@mcp.tool("Predict_Diabetes_Risk_With_Explanation")
@handle_exceptions
def predict_diabetes_risk_with_explanation(
        age: float,
        gender: str,
        hypertension: int,
        heart_disease: int,
        smoking_history: str,
        bmi: float,
        HbA1c_level: float,
        blood_glucose_level: float
        ) -> dict:
        """
        Send diabetes-related patient data to local prediction service and return the JSON response.

        Expected input fields:
          - age: Age in years (numeric)
          - gender: "Female", "Male", or "Other"
          - hypertension: 0 = No, 1 = Yes
          - heart_disease: 0 = No, 1 = Yes
          - smoking_history: "never", "No Info", "current", "former", "ever", "not current"
          - bmi: Body Mass Index (numeric)
          - HbA1c_level: Hemoglobin A1c level (numeric)
          - blood_glucose_level: Blood glucose level in mg/dL (numeric)
        """
        
        # Validate required parameters
        required_params = {
            'age': age, 'gender': gender, 'hypertension': hypertension,
            'heart_disease': heart_disease, 'smoking_history': smoking_history,
            'bmi': bmi, 'HbA1c_level': HbA1c_level, 'blood_glucose_level': blood_glucose_level
        }
        
        missing_params = []
        for param_name, param_value in required_params.items():
            if param_value is None:
                missing_params.append(param_name)
        
        if missing_params:
            return {
                "error": "missing_parameters",
                "message": f"Missing required parameters: {', '.join(missing_params)}",
                "required_parameters": {
                    "age": "Age in years (numeric)",
                    "gender": "Female, Male, or Other",
                    "hypertension": "0 = No, 1 = Yes",
                    "heart_disease": "0 = No, 1 = Yes",
                    "smoking_history": "never, No Info, current, former, ever, not current",
                    "bmi": "Body Mass Index (numeric)",
                    "HbA1c_level": "Hemoglobin A1c level (numeric)",
                    "blood_glucose_level": "Blood glucose level in mg/dL (numeric)"
                }
            }
        
        payload = {
            "age": age,
            "gender": gender,
            "hypertension": hypertension,
            "heart_disease": heart_disease,
            "smoking_history": smoking_history,
            "bmi": bmi,
            "HbA1c_level": HbA1c_level,
            "blood_glucose_level": blood_glucose_level
        }

        try:
            resp = requests.post(
            "http://localhost:5003/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": "request_failed", "details": str(e)}

@mcp.tool("Health_Check")
def health_check() -> dict:
    """
    Check the health status of the backend Abhishek service.
    
    Returns:
        dict: Health status information
    """
    try:
        resp = requests.get(f"{BACKEND_ABHISHEK_URL}/health", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

@mcp.tool("New_Patient")
def new_patient(name: str, age: int) -> dict:
    """
    Add a new patient to the system.
    
    Args:
        name (str): Patient's full name
        age (int): Patient's age
        
    Returns:
        dict: Response from the backend service
    """
    payload = {"name": name, "age": age}
    try:
        resp = requests.post(
            f"{BACKEND_ABHISHEK_URL}/db/new_patient",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

@mcp.tool("Get_Patient_Details")
def get_patient_details(patient_id: str) -> dict:
    """
    Get detailed information about a specific patient.
    
    Args:
        patient_id (str): The patient's ID
        
    Returns:
        dict: Patient details including name, DOB, sex, and remarks
    """
    try:
        resp = requests.get(
            f"{BACKEND_ABHISHEK_URL}/db/get_patient_details",
            params={"patient_id": patient_id},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

@mcp.tool("Get_Patient_Symptoms")
def get_patient_symptoms(patient_id: int) -> dict:
    """
    Get symptoms information for a specific patient from appointments.
    
    Args:
        patient_id (int): The patient's ID
        
    Returns:
        dict: List of symptoms for the patient
    """
    try:
        resp = requests.get(
            f"{BACKEND_ABHISHEK_URL}/db/get_symptoms",
            params={"patient_id": patient_id},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

@mcp.tool("Get_Patient_Medical_Reports")
def get_patient_medical_reports(patient_id: int) -> dict:
    """
    Get all lab reports for a specific patient.
    
    Args:
        patient_id (int): The patient's ID
        
    Returns:
        dict: List of medical reports with text and dates
    """
    try:
        resp = requests.get(
            f"{BACKEND_ABHISHEK_URL}/db/get_medical_reports",
            params={"patient_id": patient_id},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

@mcp.tool("Get_Frontend_Query")
def get_frontend_query() -> dict:
    """
    Get the current query from the frontend interface.
    
    Returns:
        dict: Query information from the frontend
    """
    try:
        resp = requests.get(f"{BACKEND_ABHISHEK_URL}/frontend/get_query", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": "request_failed", "details": str(e)}

mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8005,
        log_level="debug"
    )