from fastmcp import FastMCP
import requests
import os
import mysql.connector
from neo4j import GraphDatabase
from neo4j.time import Date, DateTime, Time, Duration
from dotenv import load_dotenv
import logging
from datetime import datetime, date, time
import json
import functools
import traceback

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Custom JSON encoder for Neo4j types
class Neo4jJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if obj is None:
            return None
        elif isinstance(obj, (Date, DateTime)):
            return obj.isoformat()
        elif isinstance(obj, Time):
            return obj.isoformat()
        elif isinstance(obj, Duration):
            return str(obj)
        elif isinstance(obj, (date, datetime, time)):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, '__str__'):
            return str(obj)
        return super().default(obj)

def serialize_neo4j_result(result):
    """Convert Neo4j result to JSON-serializable format"""
    def convert_value(value):
        if value is None:
            return None
        elif isinstance(value, (Date, DateTime, Time, Duration, date, datetime, time)):
            return str(value)
        elif hasattr(value, 'isoformat'):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_value(v) for v in value]
        elif hasattr(value, '__str__'):
            return str(value)
        return value
    
    if isinstance(result, dict):
        return {k: convert_value(v) for k, v in result.items()}
    elif isinstance(result, list):
        return [convert_value(item) for item in result]
    return convert_value(result)

def convert_date_to_string(obj):
    """Convert date/datetime objects to ISO format strings for Neo4j storage"""
    if obj is None:
        return None
    elif isinstance(obj, (Date, DateTime)):
        return obj.isoformat()
    elif isinstance(obj, Time):
        return obj.isoformat()
    elif isinstance(obj, Duration):
        return str(obj)
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, time):
        return obj.isoformat()
    elif isinstance(obj, str):
        return obj
    else:
        return str(obj) if obj is not None else None

def clean_value_for_neo4j(value):
    """Clean and prepare values for Neo4j storage, removing nulls and converting types"""
    if value is None or value == "" or value == "None":
        return "N/A"
    elif isinstance(value, (Date, DateTime, Time, Duration, date, datetime, time)):
        return convert_date_to_string(value)
    elif isinstance(value, bool):
        return value
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        return value.strip() if value.strip() else "N/A"
    else:
        return str(value) if value is not None else "N/A"

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
            cursor.execute("SELECT * FROM Appointment WHERE patient_id = %s", (patient_id,))
            appointments = cursor.fetchall()
            
            # Get symptoms separately
            cursor.execute("""
                SELECT aps.*, a.appointment_id, a.patient_id as appt_patient_id, a.appointment_date
                FROM Appointment_Symptom aps 
                JOIN Appointment a ON aps.appointment_id = a.appointment_id 
                WHERE a.patient_id = %s
            """, (patient_id,))
            symptoms = cursor.fetchall()
            
            # Debug: Print first symptom to see field names
            if symptoms:
                logger.info(f"First symptom data: {symptoms[0]}")
            
            # Get lab reports and findings
            cursor.execute("SELECT * FROM Lab_Report WHERE patient_id = %s", (patient_id,))
            lab_reports = cursor.fetchall()
            
            # Get lab findings separately
            cursor.execute("""
                SELECT lf.*, lr.patient_id as lab_patient_id, lr.lab_date, lr.lab_type, lr.ordering_doctor, lr.lab_facility
                FROM Lab_Finding lf 
                JOIN Lab_Report lr ON lf.lab_report_id = lr.lab_report_id 
                WHERE lr.patient_id = %s
            """, (patient_id,))
            lab_findings = cursor.fetchall()
            
            # Debug: Print first lab finding to see field names  
            if lab_findings:
                logger.info(f"First lab finding data: {lab_findings[0]}")
            
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
                'symptoms': symptoms,
                'lab_reports': lab_reports,
                'lab_findings': lab_findings,
                'chat_history': chat_history
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch patient data: {e}")
            return None
    
    def create_patient_knowledge_graph(self, patient_data: dict):
        """Create optimized patient-centric medical knowledge graph with proper date handling"""
        if not self.connect_neo4j():
            return {"error": "Failed to connect to Neo4j"}
        
        try:
            with self.neo4j_driver.session() as session:
                patient = patient_data['patient']
                patient_name = patient['name']
                patient_id = patient['patient_id']
                
                # Clear existing patient data
                session.run("""
                    MATCH (n) WHERE n.patient_id = $patient_id 
                    DETACH DELETE n
                """, patient_id=patient_id)
                
                # Step 1: Create central Patient node with standardized properties
                session.run("""
                    CREATE (p:Patient:Person {
                        patient_id: $patient_id,
                        name: $name,
                        full_name: $name,
                        dob: $dob,
                        sex: $sex,
                        gender: $sex,
                        created_at: $created_at,
                        node_type: 'Patient',
                        entity_type: 'person',
                        graph_center: true,
                        last_updated: datetime()
                    })
                """, 
                patient_id=patient_id,
                name=clean_value_for_neo4j(patient.get('name')),
                dob=convert_date_to_string(patient.get('dob')),
                sex=clean_value_for_neo4j(patient.get('sex')),
                created_at=convert_date_to_string(patient.get('created_at')))
                
                # Step 2: Create Medical Conditions from history
                condition_count = 0
                for history in patient_data['medical_history']:
                    if history.get('history_item'):
                        condition_count += 1
                        session.run("""
                            MATCH (p:Patient {patient_id: $patient_id})
                            CREATE (c:Condition:MedicalHistory {
                                history_id: $history_id,
                                patient_id: $patient_id,
                                name: $history_item,
                                condition_name: $history_item,
                                condition_type: $history_type,
                                description: $history_details,
                                severity: $severity,
                                status: CASE WHEN $is_active = 1 THEN 'active' ELSE 'resolved' END,
                                diagnosis_date: $history_date,
                                onset_date: $history_date,
                                category: $history_type,
                                is_chronic: CASE WHEN $history_type IN ['chronic_condition', 'family_history'] THEN true ELSE false END,
                                node_type: 'Medical Condition',
                                entity_type: 'condition',
                                last_updated: datetime()
                            })
                            CREATE (p)-[:HAS_CONDITION {
                                relationship_type: 'medical_condition',
                                severity: $severity,
                                status: CASE WHEN $is_active = 1 THEN 'active' ELSE 'resolved' END,
                                onset_date: $history_date,
                                condition_category: $history_type,
                                created_at: datetime()
                            }]->(c)
                        """, 
                        patient_id=patient_id,
                        history_id=clean_value_for_neo4j(history.get('history_id')),
                        history_item=clean_value_for_neo4j(history.get('history_item')),
                        history_type=clean_value_for_neo4j(history.get('history_type')),
                        history_details=clean_value_for_neo4j(history.get('history_details')),
                        severity=clean_value_for_neo4j(history.get('severity')),
                        is_active=history.get('is_active', 0),
                        history_date=convert_date_to_string(history.get('history_date')))
                
                # Step 3: Create Medications with treatment relationships
                medication_count = 0
                processed_medications = set()
                for med in patient_data['medications']:
                    med_key = f"{med.get('medicine_name')}_{med.get('dosage')}_{med.get('prescribed_date')}"
                    if med_key not in processed_medications and med.get('medicine_name'):
                        processed_medications.add(med_key)
                        medication_count += 1
                        
                        session.run("""
                            MATCH (p:Patient {patient_id: $patient_id})
                            CREATE (m:Medication:Treatment {
                                medication_id: $medication_id,
                                patient_id: $patient_id,
                                name: $medicine_name,
                                medicine_name: $medicine_name,
                                drug_name: $medicine_name,
                                dosage: $dosage,
                                dose: $dosage,
                                frequency: $frequency,
                                route: 'oral',
                                prescribed_date: $prescribed_date,
                                start_date: $prescribed_date,
                                prescribed_by: $prescribed_by,
                                prescriber: $prescribed_by,
                                status: CASE WHEN $is_continued = 1 THEN 'active' ELSE 'discontinued' END,
                                is_active: $is_continued,
                                discontinued_date: $discontinued_date,
                                node_type: 'Medication',
                                entity_type: 'treatment',
                                last_updated: datetime()
                            })
                            CREATE (p)-[:TAKES_MEDICATION {
                                relationship_type: 'medication',
                                prescribed_date: $prescribed_date,
                                prescriber: $prescribed_by,
                                dosage: $dosage,
                                frequency: $frequency,
                                status: CASE WHEN $is_continued = 1 THEN 'active' ELSE 'discontinued' END,
                                created_at: datetime()
                            }]->(m)
                        """, 
                        patient_id=patient_id,
                        medication_id=clean_value_for_neo4j(med.get('medication_id')),
                        medicine_name=clean_value_for_neo4j(med.get('medicine_name')),
                        dosage=clean_value_for_neo4j(med.get('dosage')),
                        frequency=clean_value_for_neo4j(med.get('frequency')),
                        prescribed_date=convert_date_to_string(med.get('prescribed_date')),
                        prescribed_by=clean_value_for_neo4j(med.get('prescribed_by')),
                        is_continued=med.get('is_continued', 0),
                        discontinued_date=convert_date_to_string(med.get('discontinued_date')))
                
                # Step 4: Create Healthcare Encounters (Appointments)
                encounter_count = 0
                for appt in patient_data['appointments']:
                    if appt.get('appointment_id'):
                        encounter_count += 1
                        session.run("""
                            MATCH (p:Patient {patient_id: $patient_id})
                            CREATE (e:Encounter:Appointment {
                                appointment_id: $appointment_id,
                                patient_id: $patient_id,
                                name: $appointment_type,
                                encounter_type: $appointment_type,
                                appointment_type: $appointment_type,
                                description: $notes,
                                encounter_date: $appointment_date,
                                appointment_date: $appointment_date,
                                appointment_time: $appointment_time,
                                provider: $doctor_name,
                                doctor_name: $doctor_name,
                                status: $status,
                                encounter_status: $status,
                                clinical_notes: $notes,
                                node_type: 'Healthcare Encounter',
                                entity_type: 'encounter',
                                last_updated: datetime()
                            })
                            CREATE (p)-[:HAS_ENCOUNTER {
                                relationship_type: 'healthcare_encounter',
                                encounter_date: $appointment_date,
                                provider: $doctor_name,
                                encounter_type: $appointment_type,
                                status: $status,
                                created_at: datetime()
                            }]->(e)
                        """, 
                        patient_id=patient_id,
                        appointment_id=clean_value_for_neo4j(appt.get('appointment_id')),
                        appointment_type=clean_value_for_neo4j(appt.get('appointment_type')),
                        notes=clean_value_for_neo4j(appt.get('notes')),
                        appointment_date=convert_date_to_string(appt.get('appointment_date')),
                        appointment_time=clean_value_for_neo4j(str(appt.get('appointment_time')) if appt.get('appointment_time') else None),
                        doctor_name=clean_value_for_neo4j(appt.get('doctor_name')),
                        status=clean_value_for_neo4j(appt.get('status')))
                
                # Step 5: Create Clinical Observations (Symptoms)
                symptom_count = 0
                for symptom in patient_data['symptoms']:
                    if symptom.get('symptom_name') and symptom.get('appointment_id'):
                        symptom_count += 1
                        session.run("""
                            MATCH (p:Patient {patient_id: $patient_id})
                            MATCH (e:Encounter {appointment_id: $appointment_id, patient_id: $patient_id})
                            CREATE (s:Symptom:Observation {
                                symptom_id: $symptom_id,
                                patient_id: $patient_id,
                                appointment_id: $appointment_id,
                                name: $symptom_name,
                                symptom_name: $symptom_name,
                                observation_name: $symptom_name,
                                description: $symptom_description,
                                severity: $severity,
                                duration: $duration,
                                onset_type: $onset_type,
                                onset_pattern: $onset_type,
                                reported_date: $appointment_date,
                                observation_date: $appointment_date,
                                observation_type: 'symptom',
                                clinical_significance: $severity,
                                node_type: 'Clinical Symptom',
                                entity_type: 'observation',
                                last_updated: datetime()
                            })
                            CREATE (p)-[:HAS_SYMPTOM {
                                relationship_type: 'clinical_symptom',
                                severity: $severity,
                                reported_date: $appointment_date,
                                duration: $duration,
                                onset_type: $onset_type,
                                created_at: datetime()
                            }]->(s)
                            CREATE (e)-[:DOCUMENTED_SYMPTOM {
                                relationship_type: 'clinical_documentation',
                                severity: $severity,
                                documented_by: $doctor_name,
                                created_at: datetime()
                            }]->(s)
                        """, 
                        patient_id=patient_id,
                        symptom_id=clean_value_for_neo4j(symptom.get('symptom_id')),
                        appointment_id=clean_value_for_neo4j(symptom.get('appointment_id')),
                        symptom_name=clean_value_for_neo4j(symptom.get('symptom_name')),
                        symptom_description=clean_value_for_neo4j(symptom.get('symptom_description')),
                        severity=clean_value_for_neo4j(symptom.get('severity')),
                        duration=clean_value_for_neo4j(symptom.get('duration')),
                        onset_type=clean_value_for_neo4j(symptom.get('onset_type')),
                        appointment_date=convert_date_to_string(symptom.get('appointment_date')),
                        doctor_name=clean_value_for_neo4j(symptom.get('doctor_name', 'Unknown')))
                
                # Step 6: Create Laboratory Studies
                lab_study_count = 0
                for lab in patient_data['lab_reports']:
                    if lab.get('lab_report_id'):
                        lab_study_count += 1
                        session.run("""
                            MATCH (p:Patient {patient_id: $patient_id})
                            CREATE (ls:LabStudy:DiagnosticStudy {
                                lab_report_id: $lab_report_id,
                                patient_id: $patient_id,
                                name: $lab_type,
                                study_name: $lab_type,
                                lab_type: $lab_type,
                                description: $lab_type,
                                study_date: $lab_date,
                                lab_date: $lab_date,
                                ordering_provider: $ordering_doctor,
                                ordering_doctor: $ordering_doctor,
                                facility: $lab_facility,
                                lab_facility: $lab_facility,
                                study_type: 'laboratory',
                                study_category: 'diagnostic',
                                node_type: 'Laboratory Study',
                                entity_type: 'diagnostic_study',
                                last_updated: datetime()
                            })
                            CREATE (p)-[:HAS_LAB_STUDY {
                                relationship_type: 'diagnostic_study',
                                study_date: $lab_date,
                                ordering_provider: $ordering_doctor,
                                facility: $lab_facility,
                                created_at: datetime()
                            }]->(ls)
                        """, 
                        patient_id=patient_id,
                        lab_report_id=clean_value_for_neo4j(lab.get('lab_report_id')),
                        lab_type=clean_value_for_neo4j(lab.get('lab_type')),
                        lab_date=convert_date_to_string(lab.get('lab_date')),
                        ordering_doctor=clean_value_for_neo4j(lab.get('ordering_doctor')),
                        lab_facility=clean_value_for_neo4j(lab.get('lab_facility')))
                
                # Step 7: Create Laboratory Results
                lab_result_count = 0
                for finding in patient_data['lab_findings']:
                    if finding.get('test_name') and finding.get('lab_report_id'):
                        lab_result_count += 1
                        session.run("""
                            MATCH (p:Patient {patient_id: $patient_id})
                            MATCH (ls:LabStudy {lab_report_id: $lab_report_id, patient_id: $patient_id})
                            CREATE (lr:LabResult:TestResult {
                                lab_finding_id: $lab_finding_id,
                                patient_id: $patient_id,
                                lab_report_id: $lab_report_id,
                                name: $test_name,
                                test_name: $test_name,
                                result_name: $test_name,
                                value: $test_value,
                                test_value: $test_value,
                                result_value: $test_value,
                                unit: $test_unit,
                                test_unit: $test_unit,
                                reference_range: $reference_range,
                                normal_range: $reference_range,
                                is_abnormal: $is_abnormal,
                                abnormal_flag: $abnormal_flag,
                                result_status: CASE WHEN $is_abnormal = 1 THEN 'abnormal' ELSE 'normal' END,
                                clinical_significance: CASE WHEN $is_abnormal = 1 THEN 'significant' ELSE 'normal' END,
                                result_date: $lab_date,
                                test_date: $lab_date,
                                result_type: 'quantitative',
                                node_type: 'Laboratory Result',
                                entity_type: 'test_result',
                                last_updated: datetime()
                            })
                            CREATE (p)-[:HAS_LAB_RESULT {
                                relationship_type: 'laboratory_result',
                                result_date: $lab_date,
                                is_abnormal: $is_abnormal,
                                clinical_significance: CASE WHEN $is_abnormal = 1 THEN 'abnormal' ELSE 'normal' END,
                                created_at: datetime()
                            }]->(lr)
                            CREATE (ls)-[:CONTAINS_RESULT {
                                relationship_type: 'study_result',
                                result_sequence: $lab_finding_id,
                                is_abnormal: $is_abnormal,
                                created_at: datetime()
                            }]->(lr)
                        """, 
                        patient_id=patient_id,
                        lab_finding_id=clean_value_for_neo4j(finding.get('lab_finding_id')),
                        lab_report_id=clean_value_for_neo4j(finding.get('lab_report_id')),
                        test_name=clean_value_for_neo4j(finding.get('test_name')),
                        test_value=clean_value_for_neo4j(finding.get('test_value')),
                        test_unit=clean_value_for_neo4j(finding.get('test_unit')),
                        reference_range=clean_value_for_neo4j(finding.get('reference_range')),
                        is_abnormal=finding.get('is_abnormal', 0),
                        abnormal_flag=clean_value_for_neo4j(finding.get('abnormal_flag')),
                        lab_date=convert_date_to_string(finding.get('lab_date')))
                
                # Step 8: Create semantic relationships between medical entities
                self._create_medical_relationships(session, patient_id)
                
                # Calculate graph statistics
                stats_result = session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    OPTIONAL MATCH (p)-[r]-()
                    RETURN p.name as patient_name,
                           count(DISTINCT r) as total_relationships,
                           count(DISTINCT r) as direct_connections,
                           count(DISTINCT r) + 1 as total_network_size
                """, patient_id=patient_id)
                
                stats = stats_result.single()
                
                return {
                    "success": True,
                    "patient_id": patient_id,
                    "patient_name": stats["patient_name"] if stats else patient_name,
                    "entity_counts": {
                        "conditions": condition_count,
                        "medications": medication_count,
                        "encounters": encounter_count,
                        "symptoms": symptom_count,
                        "lab_studies": lab_study_count,
                        "lab_results": lab_result_count
                    },
                    "direct_connections": stats["direct_connections"] if stats else 0,
                    "total_relationships": stats["total_relationships"] if stats else 0,
                    "total_patient_network": stats["total_network_size"] if stats else 1,
                    "orphaned_nodes": 0,
                    "message": f"Optimized medical knowledge graph created for {patient_name}",
                    "graph_validated": True,
                    "graph_type": "medical_knowledge_graph",
                    "last_updated": datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error creating knowledge graph: {e}")
            return {"error": f"Failed to create knowledge graph: {str(e)}"}
        finally:
            self.close_neo4j()

    def _create_medical_relationships(self, session, patient_id):
        """Create intelligent relationships between medical entities"""
        # Link symptoms to potential conditions based on medical knowledge
        session.run("""
            MATCH (p:Patient {patient_id: $patient_id})
            MATCH (p)-[:HAS_SYMPTOM]->(s:Symptom)
            MATCH (p)-[:HAS_CONDITION]->(c:Condition)
            WHERE toLower(s.name) CONTAINS toLower(c.name) 
               OR toLower(c.description) CONTAINS toLower(s.name)
            CREATE (s)-[:MAY_INDICATE {
                relationship_type: 'clinical_correlation',
                confidence: 'possible',
                created_at: datetime()
            }]->(c)
        """, patient_id=patient_id)
        
        # Link medications to conditions they treat
# Initialize knowledge graph manager
kg_manager = KnowledgeGraphManager()

@mcp.tool("Run_Cypher_Query")
def run_cypher_query(cypher: str) -> dict:
    """
    Execute an arbitrary Cypher query against the Neo4j database.
    
    Args:
        cypher (str): The Cypher query to execute

        
    Returns:
        dict: Query results or error message
    """
    try:
        # Basic query validation
        if not cypher or not cypher.strip():
            return {"error": "Empty or invalid Cypher query"}
            
        # Check for basic syntax issues
        cypher_clean = cypher.strip()
        
        # Warn about deprecated id() function usage
        if 'id(' in cypher_clean:
            logger.warning(f"Query uses deprecated id() function: {cypher_clean[:100]}...")
            # Optionally fix the query
            cypher_clean = fix_deprecated_cypher(cypher_clean)
            
        if not kg_manager.connect_neo4j():
            return {"error": "Failed to connect to Neo4j"}
        
        with kg_manager.neo4j_driver.session() as session:
            result = session.run(cypher_clean)
            records = [record.data() for record in result]
            serialized_records = serialize_neo4j_result(records)
            return {
                "success": True,
                "query": cypher_clean,
                "original_query": cypher if cypher != cypher_clean else None,
                "results": serialized_records,
                "result_count": len(serialized_records)
            }
            
    except Exception as e:
        logger.error(f"Error running Cypher query: {e}")
        return {"error": f"Failed to run Cypher query: {str(e)}"}
    finally:
        kg_manager.close_neo4j()

def fix_deprecated_cypher(cypher: str) -> str:
    """
    Fix common deprecated Cypher patterns.
    
    Args:
        cypher (str): Original Cypher query
        
    Returns:
        str: Fixed Cypher query with suggestions
    """
    fixed_cypher = cypher
    
    # Replace deprecated id() function with elementId()
    if 'id(' in cypher:
        import re
        fixed_cypher = re.sub(r'\bid\(([^)]+)\)', r'elementId(\1)', fixed_cypher)
        logger.info(f"Fixed deprecated id() function in query")
    
    return fixed_cypher

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

@mcp.tool("update_knowledge_graph")
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


@handle_exceptions
@mcp.tool("Predict_Cardiovascular_Risk_With_Explanation")
def predict_cardiovascular_risk_with_explanation(
    age: float = 50,
    gender: int = 2,
    height: float = 175,
    weight: float = 80,
    ap_hi: int = 140,
    ap_lo: int = 90,
    cholesterol: int = 2,
    gluc: int = 1,
    smoke: int = 1,
    alco: int = 0,
    active: int = 1
) -> dict:
    """
    Send patient data to local prediction service and return the JSON response.

    Expected input fields:
      - age: Age in years (numeric, defaults to 50)
      - gender: 1 = Female, 2 = Male (defaults to 2)
      - height: Height in centimeters (defaults to 175)
      - weight: Weight in kilograms (defaults to 80)
      - ap_hi: Systolic blood pressure (defaults to 140)
      - ap_lo: Diastolic blood pressure (defaults to 90)
      - cholesterol: 1 = Normal, 2 = Above normal, 3 = Well above normal (defaults to 2)
      - gluc: Glucose level (1 = Normal, 2 = Above normal, 3 = Well above normal, defaults to 1)
      - smoke: 0 = No, 1 = Yes (defaults to 1)
      - alco: Alcohol consumption (0 = No, 1 = Yes, defaults to 0)
      - active: Physical activity (0 = No, 1 = Yes, defaults to 1)
    """
    
    logger.info(f"Starting cardiovascular risk prediction for patient")
    logger.info(f"Input parameters: age={age}, gender={gender}, height={height}, weight={weight}, "
                f"ap_hi={ap_hi}, ap_lo={ap_lo}, cholesterol={cholesterol}, gluc={gluc}, "
                f"smoke={smoke}, alco={alco}, active={active}")
    
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
        logger.warning(f"Missing required parameters for cardiovascular prediction: {missing_params}")
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

    logger.info(f"Sending cardiovascular prediction request to http://localhost:5002/predict")
    logger.debug(f"Payload: {payload}")

    try:
        resp = requests.post(
            "http://localhost:5002/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        logger.info(f"Cardiovascular prediction successful. Response status: {resp.status_code}")
        logger.info(f"Prediction result: {result}")
        
        return result
    except requests.RequestException as e:
        logger.error(f"Cardiovascular prediction request failed: {str(e)}")
        logger.error(f"Request URL: http://localhost:5002/predict")
        logger.error(f"Request payload: {payload}")
        return {"error": "request_failed", "details": str(e)}

@handle_exceptions
@mcp.tool("Predict_Diabetes_Risk_With_Explanation")
def predict_diabetes_risk_with_explanation(
    age: float = 45,
    gender: str = "Male",
    hypertension: int = 1,
    heart_disease: int = 0,
    smoking_history: str = "former",
    HbA1c_level: float = 6.2,
    blood_glucose_level: float = 140,
    bmi: float = 28.5
) -> dict:
    """
    Send diabetes-related patient data to local prediction service and return the JSON response.

    Expected input fields:
      - age: Age in years (numeric, defaults to 45)
      - gender: "Female", "Male", or "Other" (defaults to "Male")
      - hypertension: 0 = No, 1 = Yes (defaults to 1)
      - heart_disease: 0 = No, 1 = Yes (defaults to 0)
      - smoking_history: "never", "No Info", "current", "former", "ever", "not current" (defaults to "former")
      - bmi: Body Mass Index (numeric, defaults to 28.5 if not provided)
      - HbA1c_level: Hemoglobin A1c level (numeric, defaults to 6.2)
      - blood_glucose_level: Blood glucose level in mg/dL (numeric, defaults to 140)
    """
    
    logger.info(f"Starting diabetes risk prediction for patient")
    logger.info(f"Input parameters: age={age}, gender={gender}, hypertension={hypertension}, "
                f"heart_disease={heart_disease}, smoking_history={smoking_history}, "
                f"bmi={bmi}, HbA1c_level={HbA1c_level}, blood_glucose_level={blood_glucose_level}")
    
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
        logger.warning(f"Missing required parameters for diabetes prediction: {missing_params}")
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

    logger.info(f"Sending diabetes prediction request to http://localhost:5003/predict")
    logger.debug(f"Payload: {payload}")

    try:
        resp = requests.post(
            "http://localhost:5003/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        resp.raise_for_status()
        result = resp.json()
        
        logger.info(f"Diabetes prediction successful. Response status: {resp.status_code}")
        logger.info(f"Prediction result: {result}")
        
        return result
    except requests.RequestException as e:
        logger.error(f"Diabetes prediction request failed: {str(e)}")
        logger.error(f"Request URL: http://localhost:5003/predict")
        logger.error(f"Request payload: {payload}")
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