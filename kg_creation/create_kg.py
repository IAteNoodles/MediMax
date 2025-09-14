import csv
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any
import re
import sys

# Configure logging with better Windows compatibility
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_graph.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- KNOWLEDGE GRAPH SCHEMA BASED ON PROVIDED IMAGE ---
ENTITIES = ['Patient', 'Symptom', 'LabTest', 'Medication', 'Encounter']
RELATIONS = ['has_symptom', 'has_lab_test', 'prescribed_medication', 'has_encounter', 'contains_test', 'contains_medication', 'contains_symptom']

class DatabaseKnowledgeGraphBuilder:
    """
    Rule-based Knowledge Graph Builder that extracts structured data from MediMax database
    and creates a knowledge graph following the Patient-Symptom-LabTest-Medication-Encounter schema.
    """
    
    def __init__(self):
        """Initialize the KG builder."""
        self.nodes = []
        self.relationships = []
        self.seen_nodes = set()
        logger.info("Initialized DatabaseKnowledgeGraphBuilder")
        
        # In production, you would import and initialize MCP tools here
        # For now, we'll use sample data that mimics the database structure
    
    def add_node(self, node_id: str, name: str, label: str, properties: Dict = None) -> None:
        """Add a node to the knowledge graph if it doesn't already exist."""
        if node_id not in self.seen_nodes:
            node = {
                'id': node_id,
                'name': name,
                'label': label,
                'properties': properties or {}
            }
            self.nodes.append(node)
            self.seen_nodes.add(node_id)
            logger.debug(f"Added node: {label} - {name}")
    
    def add_relationship(self, start_id: str, relation_type: str, end_id: str, properties: Dict = None) -> None:
        """Add a relationship to the knowledge graph."""
        relationship = {
            'start_id': start_id,
            'type': relation_type,
            'end_id': end_id,
            'properties': properties or {}
        }
        self.relationships.append(relationship)
        logger.debug(f"Added relationship: {start_id} --[{relation_type}]--> {end_id}")
    
    def extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract symptoms using rule-based pattern matching."""
        if not text:
            return []
        
        # Common symptom patterns
        symptom_patterns = [
            r'\b(pain|ache|hurt|discomfort)\b',
            r'\b(fatigue|tired|exhausted|weakness)\b',
            r'\b(fever|temperature|chills)\b',
            r'\b(nausea|vomiting|dizziness)\b',
            r'\b(cough|breathing|shortness of breath)\b',
            r'\b(headache|migraine)\b',
            r'\b(swelling|inflammation)\b',
            r'\b(rash|itching|skin)\b',
            r'\b(hypertension|high blood pressure)\b',
            r'\b(diabetes|high blood sugar)\b',
            r'\b(chest pain|heart|cardiac)\b'
        ]
        
        symptoms = []
        text_lower = text.lower()
        
        for pattern in symptom_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match not in symptoms:
                    symptoms.append(match)
        
        # Additional specific symptoms extraction
        if 'mild fatigue' in text_lower:
            symptoms.append('mild fatigue')
        if 'routine checkup' in text_lower or 'checkup' in text_lower:
            symptoms.append('routine checkup')
        if 'pregnancy' in text_lower:
            symptoms.append('pregnancy monitoring')
            
        return symptoms
    
    def extract_lab_tests_from_text(self, text: str) -> List[str]:
        """Extract lab tests using rule-based pattern matching."""
        if not text:
            return []
        
        lab_test_patterns = [
            r'\b(blood test|CBC|complete blood count)\b',
            r'\b(cholesterol|lipid panel)\b',
            r'\b(glucose|blood sugar)\b',
            r'\b(X-ray|CT scan|MRI|ultrasound)\b',
            r'\b(urine test|urinalysis)\b',
            r'\b(ECG|EKG|electrocardiogram)\b',
            r'\b(hemoglobin|hematocrit)\b',
            r'\b(liver function|kidney function)\b',
            r'\b(HbA1c|hemoglobin A1c)\b'
        ]
        
        tests = []
        text_lower = text.lower()
        
        for pattern in lab_test_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match not in tests:
                    tests.append(match)
        
        # If text mentions "test" and "results", assume it's a lab test
        if 'test' in text_lower and 'results' in text_lower:
            if 'blood' in text_lower:
                tests.append('blood test')
        
        return tests
    
    def extract_medications_from_text(self, text: str) -> List[str]:
        """Extract medications using rule-based pattern matching."""
        if not text:
            return []
        
        medication_patterns = [
            r'\b(aspirin|ibuprofen|acetaminophen)\b',
            r'\b(metformin|insulin)\b',
            r'\b(lisinopril|amlodipine|losartan)\b',
            r'\b(atorvastatin|simvastatin)\b',
            r'\b(metoprolol|propranolol)\b',
            r'\b([A-Z][a-z]+(?:in|ol|ide|ine|ium))\b'  # Common drug endings
        ]
        
        medications = []
        text_lower = text.lower()
        
        for pattern in medication_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match not in medications:
                    medications.append(match)
        
        return medications

class DatabaseKnowledgeGraphBuilder:
    """
    Rule-based Knowledge Graph Builder that extracts structured data from MediMax database
    and creates a knowledge graph following the Patient-Symptom-LabTest-Medication-Encounter schema.
    """
    
    def __init__(self):
        """Initialize the KG builder with database connection via MCP."""
        self.nodes = []
        self.relationships = []
        self.seen_nodes = set()
        logger.info("� Initialized DatabaseKnowledgeGraphBuilder")
    
    def execute_db_query(self, query: str) -> List[Dict]:
        """Execute database query via MCP tools."""
        try:
            # This is a placeholder - in actual implementation, you would use MCP tools
            # For now, we'll simulate with the structure we know exists
            logger.info(f"📊 Executing query: {query}")
            return []
        except Exception as e:
            logger.error(f"❌ Database query failed: {e}")
            return []
    
    def add_node(self, node_id: str, name: str, label: str, properties: Dict = None) -> None:
        """Add a node to the knowledge graph if it doesn't already exist."""
        if node_id not in self.seen_nodes:
            node = {
                'id': node_id,
                'name': name,
                'label': label,
                'properties': properties or {}
            }
            self.nodes.append(node)
            self.seen_nodes.add(node_id)
            logger.debug(f"➕ Added node: {label} - {name}")
    
    def add_relationship(self, start_id: str, relation_type: str, end_id: str, properties: Dict = None) -> None:
        """Add a relationship to the knowledge graph."""
        relationship = {
            'start_id': start_id,
            'type': relation_type,
            'end_id': end_id,
            'properties': properties or {}
        }
        self.relationships.append(relationship)
        logger.debug(f"🔗 Added relationship: {start_id} --[{relation_type}]--> {end_id}")
    
    def extract_symptoms_from_text(self, text: str) -> List[str]:
        """Extract symptoms using rule-based pattern matching."""
        if not text:
            return []
        
        # Common symptom patterns
        symptom_patterns = [
            r'\b(pain|ache|hurt|discomfort)\b',
            r'\b(fatigue|tired|exhausted|weakness)\b',
            r'\b(fever|temperature|chills)\b',
            r'\b(nausea|vomiting|dizziness)\b',
            r'\b(cough|breathing|shortness of breath)\b',
            r'\b(headache|migraine)\b',
            r'\b(swelling|inflammation)\b',
            r'\b(rash|itching|skin)\b'
        ]
        
        symptoms = []
        text_lower = text.lower()
        
        for pattern in symptom_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match not in symptoms:
                    symptoms.append(match)
        
        # Additional specific symptoms extraction
        if 'mild fatigue' in text_lower:
            symptoms.append('mild fatigue')
        if 'checkup' in text_lower:
            symptoms.append('routine checkup')
            
        return symptoms
    
    def extract_lab_tests_from_text(self, text: str) -> List[str]:
        """Extract lab tests using rule-based pattern matching."""
        if not text:
            return []
        
        lab_test_patterns = [
            r'\b(blood test|CBC|complete blood count)\b',
            r'\b(cholesterol|lipid panel)\b',
            r'\b(glucose|blood sugar)\b',
            r'\b(X-ray|CT scan|MRI|ultrasound)\b',
            r'\b(urine test|urinalysis)\b',
            r'\b(ECG|EKG|electrocardiogram)\b'
        ]
        
        tests = []
        text_lower = text.lower()
        
        for pattern in lab_test_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match not in tests:
                    tests.append(match)
        
        return tests
    
    def extract_medications_from_text(self, text: str) -> List[str]:
        """Extract medications using rule-based pattern matching."""
        if not text:
            return []
        
        medication_patterns = [
            r'\b(aspirin|ibuprofen|acetaminophen)\b',
            r'\b(metformin|insulin)\b',
            r'\b(lisinopril|amlodipine|losartan)\b',
            r'\b(atorvastatin|simvastatin)\b',
            r'\b([A-Z][a-z]+(?:in|ol|ide|ine|ium))\b'  # Common drug endings
        ]
        
        medications = []
        text_lower = text.lower()
        
        for pattern in medication_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match not in medications:
                    medications.append(match)
        
        return medications
    
    def build_patient_knowledge_graph(self, patient_id: int) -> Tuple[List[Dict], List[Dict]]:
        """
        Build a comprehensive knowledge graph for a specific patient using rule-based extraction.
        """
        logger.info(f"🔍 Building knowledge graph for Patient ID: {patient_id}")
        
        # Reset graph for this patient
        self.nodes = []
        self.relationships = []
        self.seen_nodes = set()
        
        try:
            # Note: In actual implementation, replace these with MCP database calls
            # For demonstration, using sample data structure
            
            # 1. Get Patient Information
            patient_data = self._get_patient_data(patient_id)
            if not patient_data:
                logger.error(f"❌ Patient {patient_id} not found")
                return [], []
            
            # Add Patient node
            patient_node_id = f"patient_{patient_id}"
            self.add_node(
                patient_node_id, 
                patient_data.get('name', f'Patient {patient_id}'), 
                'Patient',
                {
                    'dob': patient_data.get('dob'),
                    'sex': patient_data.get('sex'),
                    'remarks': patient_data.get('remarks')
                }
            )
            
            # 2. Process Medical History
            history_data = self._get_patient_history(patient_id)
            if history_data:
                self._process_medical_history(patient_node_id, history_data)
            
            # 3. Process Lab Reports
            lab_reports = self._get_lab_reports(patient_id)
            for report in lab_reports:
                self._process_lab_report(patient_node_id, report)
            
            # 4. Process Prescriptions
            prescriptions = self._get_prescriptions(patient_id)
            for prescription in prescriptions:
                self._process_prescription(patient_node_id, prescription)
            
            # 5. Process Appointments (as Encounters)
            appointments = self._get_appointments(patient_id)
            for appointment in appointments:
                self._process_appointment(patient_node_id, appointment)
            
            logger.info(f"✅ Successfully built KG with {len(self.nodes)} nodes and {len(self.relationships)} relationships")
            return self.nodes, self.relationships
            
        except Exception as e:
            logger.error(f"❌ Error building knowledge graph: {e}")
            return [], []
    
    def _get_patient_data(self, patient_id: int) -> Dict:
        """Get patient basic information (placeholder for MCP call)."""
        # Placeholder - replace with actual MCP database call
        sample_patients = {
            1: {'name': 'John Doe', 'dob': '1985-03-15', 'sex': 'Male', 'remarks': 'Regular checkup patient'},
            2: {'name': 'Jane Smith', 'dob': '1992-07-22', 'sex': 'Female', 'remarks': 'Has hypertension'},
            3: {'name': 'Robert Johnson', 'dob': '1978-11-08', 'sex': 'Male', 'remarks': 'Diabetic patient'}
        }
        return sample_patients.get(patient_id, {})
    
    def _get_patient_history(self, patient_id: int) -> Dict:
        """Get patient medical history (placeholder for MCP call)."""
        # Placeholder - replace with actual MCP database call
        sample_history = {
            1: {"allergies": ["penicillin"], "surgeries": ["appendectomy"], "medications": ["aspirin"]}
        }
        return sample_history.get(patient_id, {})
    
    def _get_lab_reports(self, patient_id: int) -> List[Dict]:
        """Get patient lab reports (placeholder for MCP call)."""
        # Placeholder - replace with actual MCP database call
        sample_reports = {
            1: [{'text': 'Blood test results: CBC normal, cholesterol 180 mg/dL', 'date': '2024-09-01'}]
        }
        return sample_reports.get(patient_id, [])
    
    def _get_prescriptions(self, patient_id: int) -> List[Dict]:
        """Get patient prescriptions (placeholder for MCP call)."""
        # Placeholder - replace with actual MCP database call
        sample_prescriptions = {
            1: [{'prescription': 'Aspirin 81mg daily', 'date': '2024-09-01'}]
        }
        return sample_prescriptions.get(patient_id, [])
    
    def _get_appointments(self, patient_id: int) -> List[Dict]:
        """Get patient appointments (placeholder for MCP call)."""
        # Placeholder - replace with actual MCP database call
        sample_appointments = {
            1: [{'date': '2024-09-15', 'status': 'Scheduled', 'symptoms': 'Routine checkup, mild fatigue'}]
        }
        return sample_appointments.get(patient_id, [])
    
    def _process_medical_history(self, patient_id: str, history: Dict) -> None:
        """Process medical history data and create nodes/relationships."""
        logger.info("� Processing medical history")
        
        # Process allergies as symptoms
        if 'allergies' in history:
            for allergy in history['allergies']:
                symptom_id = f"symptom_allergy_{allergy}"
                self.add_node(symptom_id, f"Allergy to {allergy}", 'Symptom', {'type': 'allergy'})
                self.add_relationship(patient_id, 'has_symptom', symptom_id)
        
        # Process historical medications
        if 'medications' in history:
            for medication in history['medications']:
                med_id = f"medication_{medication}"
                self.add_node(med_id, medication.title(), 'Medication', {'historical': True})
                self.add_relationship(patient_id, 'prescribed_medication', med_id)
    
    def _process_lab_report(self, patient_id: str, report: Dict) -> None:
        """Process lab report and extract relevant information."""
        logger.info(f"🧪 Processing lab report from {report.get('date')}")
        
        report_text = report.get('text', '')
        report_date = report.get('date', '')
        
        # Create encounter for this lab session
        encounter_id = f"encounter_lab_{report_date}"
        self.add_node(
            encounter_id, 
            f"Lab Session {report_date}", 
            'Encounter',
            {'date': report_date, 'type': 'laboratory'}
        )
        self.add_relationship(patient_id, 'has_encounter', encounter_id)
        
        # Extract lab tests
        lab_tests = self.extract_lab_tests_from_text(report_text)
        for test in lab_tests:
            test_id = f"labtest_{test.replace(' ', '_')}"
            self.add_node(test_id, test.title(), 'LabTest')
            self.add_relationship(encounter_id, 'contains_test', test_id)
            self.add_relationship(patient_id, 'has_lab_test', test_id)
    
    def _process_prescription(self, patient_id: str, prescription: Dict) -> None:
        """Process prescription data."""
        logger.info(f"💊 Processing prescription from {prescription.get('date')}")
        
        prescription_text = prescription.get('prescription', '')
        prescription_date = prescription.get('date', '')
        
        # Extract medications
        medications = self.extract_medications_from_text(prescription_text)
        for medication in medications:
            med_id = f"medication_{medication}"
            self.add_node(
                med_id, 
                medication.title(), 
                'Medication',
                {'prescription_date': prescription_date, 'details': prescription_text}
            )
            self.add_relationship(patient_id, 'prescribed_medication', med_id)
    
    def _process_appointment(self, patient_id: str, appointment: Dict) -> None:
        """Process appointment as an encounter with symptoms."""
        logger.info(f"📅 Processing appointment on {appointment.get('date')}")
        
        appointment_date = appointment.get('date', '')
        status = appointment.get('status', '')
        symptoms_text = appointment.get('symptoms', '')
        
        # Create encounter for this appointment
        encounter_id = f"encounter_appointment_{appointment_date}"
        self.add_node(
            encounter_id,
            f"Appointment {appointment_date}",
            'Encounter',
            {'date': appointment_date, 'status': status, 'type': 'appointment'}
        )
        self.add_relationship(patient_id, 'has_encounter', encounter_id)
        
        # Extract and process symptoms
        symptoms = self.extract_symptoms_from_text(symptoms_text)
        for symptom in symptoms:
            symptom_id = f"symptom_{symptom.replace(' ', '_')}"
            self.add_node(symptom_id, symptom.title(), 'Symptom')
            self.add_relationship(patient_id, 'has_symptom', symptom_id)
            self.add_relationship(encounter_id, 'contains_symptom', symptom_id)


def save_knowledge_graph_to_csv(nodes: List[Dict], relationships: List[Dict]) -> None:
    """Save the knowledge graph to CSV files for import."""
    logger.info("� Saving knowledge graph to CSV files")
    
    try:
        # Save nodes
        with open('nodes.csv', 'w', newline='', encoding='utf-8') as f:
            if nodes:
                fieldnames = [':ID', 'name', ':LABEL'] + list(nodes[0].get('properties', {}).keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for node in nodes:
                    row = {
                        ':ID': node['id'],
                        'name': node['name'],
                        ':LABEL': node['label']
                    }
                    # Add properties as additional columns
                    row.update(node.get('properties', {}))
                    writer.writerow(row)
        
        logger.info("✅ nodes.csv created successfully")
        
        # Save relationships
        with open('relationships.csv', 'w', newline='', encoding='utf-8') as f:
            if relationships:
                fieldnames = [':START_ID', ':TYPE', ':END_ID'] + list(relationships[0].get('properties', {}).keys()) if relationships else [':START_ID', ':TYPE', ':END_ID']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for rel in relationships:
                    row = {
                        ':START_ID': rel['start_id'],
                        ':TYPE': rel['type'],
                        ':END_ID': rel['end_id']
                    }
                    # Add properties as additional columns
                    row.update(rel.get('properties', {}))
                    writer.writerow(row)
        
        logger.info("✅ relationships.csv created successfully")
        
    except Exception as e:
        logger.error(f"❌ Error saving CSV files: {e}")


def create_knowledge_graph_for_patient(patient_id: int) -> Tuple[List[Dict], List[Dict]]:
    """
    Main function to create a knowledge graph for a specific patient.
    
    Args:
        patient_id (int): The ID of the patient to create a knowledge graph for
        
    Returns:
        Tuple[List[Dict], List[Dict]]: nodes and relationships lists
    """
    logger.info(f"🚀 Starting knowledge graph creation for patient {patient_id}")
    
    try:
        # Initialize the knowledge graph builder
        kg_builder = DatabaseKnowledgeGraphBuilder()
        
        # Build the knowledge graph
        nodes, relationships = kg_builder.build_patient_knowledge_graph(patient_id)
        
        if not nodes:
            logger.warning(f"⚠️ No knowledge graph data found for patient {patient_id}")
            return [], []
        
        # Save to CSV files
        save_knowledge_graph_to_csv(nodes, relationships)
        
        # Print summary
        logger.info(f"📊 Knowledge Graph Summary:")
        logger.info(f"   - Total Nodes: {len(nodes)}")
        logger.info(f"   - Total Relationships: {len(relationships)}")
        
        # Group nodes by type
        node_types = {}
        for node in nodes:
            label = node['label']
            node_types[label] = node_types.get(label, 0) + 1
        
        for label, count in node_types.items():
            logger.info(f"   - {label} nodes: {count}")
        
        return nodes, relationships
        
    except Exception as e:
        logger.error(f"❌ Failed to create knowledge graph: {e}")
        return [], []


# --- MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    import sys
    
    # Get patient ID from command line argument or use default
    patient_id = 1
    if len(sys.argv) > 1:
        try:
            patient_id = int(sys.argv[1])
        except ValueError:
            logger.error("❌ Invalid patient ID provided. Using default patient ID: 1")
    
    logger.info(f"🎯 Creating knowledge graph for Patient ID: {patient_id}")
    
    # Create knowledge graph
    nodes, relationships = create_knowledge_graph_for_patient(patient_id)
    
    if nodes and relationships:
        logger.info("🎉 Knowledge graph creation completed successfully!")
        logger.info("📁 Files generated: nodes.csv, relationships.csv")
        logger.info("📄 Check knowledge_graph.log for detailed logs")
    else:
        logger.error("❌ Failed to create knowledge graph")
        sys.exit(1)