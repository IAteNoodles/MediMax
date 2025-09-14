#!/usr/bin/env python3
"""
Rich Patient Knowledge Graph Creator
===================================

Creates a comprehensive knowledge graph for Dr. Sarah Mitchell 
showcasing the full power of atomic facts in medical knowledge representation.

Features:
- Multiple medication pathways and interactions
- Disease progression over time
- Multi-specialty care coordination
- Complex symptom-condition relationships
- Temporal relationships in lab values
- Rich chat history analysis

Author: GitHub Copilot
Date: September 14, 2025
"""

from neo4j import GraphDatabase
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RichKnowledgeGraphCreator:
    def __init__(self):
        # Neo4j AuraDB connection
        self.uri = "neo4j+s://98d1982d.databases.neo4j.io"
        self.username = "neo4j"
        self.password = "SY0_UpYCANtZx3Pu5wF_nD0JO4WDuvIWAkdL2mj5S44"
        self.driver = None
        
    def connect(self):
        """Connect to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            logger.info("✅ Connected to Neo4j AuraDB")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            return False
    
    def clear_patient_data(self, patient_name):
        """Clear existing data for the patient"""
        with self.driver.session() as session:
            # Delete all relationships and nodes for this patient
            session.run("""
                MATCH (p:Patient {name: $patient_name})-[*0..3]-(n)
                DETACH DELETE n
            """, patient_name=patient_name)
            logger.info(f"🧹 Cleared existing data for {patient_name}")
    
    def create_patient_node(self):
        """Create the central patient node"""
        with self.driver.session() as session:
            session.run("""
                CREATE (p:Patient {
                    name: 'Dr. Sarah Mitchell',
                    dob: '1979-03-22',
                    sex: 'Female',
                    age: 45,
                    occupation: 'Cardiologist',
                    complexity_score: 'High',
                    risk_level: 'Moderate-High',
                    node_type: 'Patient'
                })
            """)
            logger.info("👤 Created patient node: Dr. Sarah Mitchell")
    
    def create_medical_conditions(self):
        """Create nodes for major medical conditions"""
        with self.driver.session() as session:
            conditions = [
                ('Type 2 Diabetes Mellitus', 'Endocrine', 'moderate', '2016-11-08', 'Progressive from gestational diabetes'),
                ('Hypertension', 'Cardiovascular', 'moderate', '2015-02-14', 'Essential hypertension, pregnancy-related onset'),
                ('Hyperlipidemia', 'Cardiovascular', 'moderate', '2018-05-15', 'Familial combined hyperlipidemia'),
                ('Chronic Kidney Disease Stage 2', 'Renal', 'moderate', '2023-01-20', 'Secondary to diabetes and hypertension'),
                ('Hypothyroidism', 'Endocrine', 'mild', '2021-07-03', 'Hashimoto thyroiditis with autoimmune component'),
                ('Anxiety Disorder', 'Mental Health', 'mild', '2020-09-12', 'Work-related stress and pandemic burnout'),
            ]
            
            for name, system, severity, date, details in conditions:
                session.run("""
                    MATCH (p:Patient {name: 'Dr. Sarah Mitchell'})
                    CREATE (c:MedicalCondition {
                        name: $name,
                        system: $system,
                        severity: $severity,
                        diagnosis_date: $date,
                        details: $details,
                        node_type: 'Medical Condition'
                    })
                    CREATE (p)-[:HAS_CONDITION {
                        since: $date,
                        status: 'active',
                        severity: $severity
                    }]->(c)
                """, name=name, system=system, severity=severity, date=date, details=details)
            
            logger.info(f"🏥 Created {len(conditions)} medical condition nodes")
    
    def create_medications(self):
        """Create medication nodes with complex relationships"""
        with self.driver.session() as session:
            medications = [
                ('Metformin XR', 'Antidiabetic', '1000mg BID', 'Type 2 Diabetes', '2016-11-08', 'Dr. Jennifer Adams'),
                ('Insulin Glargine', 'Insulin', '25 units qHS', 'Type 2 Diabetes', '2020-03-15', 'Dr. Jennifer Adams'),
                ('Lisinopril', 'ACE Inhibitor', '20mg daily', 'Hypertension', '2015-02-14', 'Dr. Michael Chen'),
                ('Amlodipine', 'CCB', '10mg daily', 'Hypertension', '2018-06-20', 'Dr. Michael Chen'),
                ('Atorvastatin', 'Statin', '40mg qHS', 'Hyperlipidemia', '2018-05-15', 'Dr. Michael Chen'),
                ('Levothyroxine', 'Thyroid Hormone', '88mcg daily', 'Hypothyroidism', '2021-07-03', 'Dr. Lisa Park'),
                ('Sertraline', 'SSRI', '50mg daily', 'Anxiety Disorder', '2020-09-12', 'Dr. Robert Kim'),
                ('Losartan', 'ARB', '50mg daily', 'Chronic Kidney Disease', '2023-01-20', 'Dr. Elena Rodriguez'),
                ('Aspirin', 'Antiplatelet', '81mg daily', 'Cardiovascular Protection', '2018-05-15', 'Dr. Michael Chen'),
                ('Vitamin D3', 'Supplement', '2000 IU daily', 'Bone Health', '2019-11-10', 'Dr. Jennifer Adams'),
            ]
            
            for name, category, dosage, indication, date, doctor in medications:
                session.run("""
                    MATCH (p:Patient {name: 'Dr. Sarah Mitchell'})
                    CREATE (m:Medication {
                        name: $name,
                        category: $category,
                        dosage: $dosage,
                        indication: $indication,
                        prescribed_date: $date,
                        prescribed_by: $doctor,
                        status: 'active',
                        node_type: 'Medication'
                    })
                    CREATE (p)-[:PRESCRIBED {
                        date: $date,
                        prescriber: $doctor,
                        indication: $indication,
                        status: 'active'
                    }]->(m)
                """, name=name, category=category, dosage=dosage, indication=indication, date=date, doctor=doctor)
            
            # Create medication-condition relationships
            med_condition_pairs = [
                ('Metformin XR', 'Type 2 Diabetes Mellitus'),
                ('Insulin Glargine', 'Type 2 Diabetes Mellitus'),
                ('Lisinopril', 'Hypertension'),
                ('Amlodipine', 'Hypertension'),
                ('Atorvastatin', 'Hyperlipidemia'),
                ('Levothyroxine', 'Hypothyroidism'),
                ('Sertraline', 'Anxiety Disorder'),
                ('Losartan', 'Chronic Kidney Disease Stage 2'),
            ]
            
            for med_name, condition_name in med_condition_pairs:
                session.run("""
                    MATCH (m:Medication {name: $med_name})
                    MATCH (c:MedicalCondition {name: $condition_name})
                    CREATE (m)-[:TREATS {
                        mechanism: 'direct therapeutic effect',
                        efficacy: 'established'
                    }]->(c)
                """, med_name=med_name, condition_name=condition_name)
            
            logger.info(f"💊 Created {len(medications)} medication nodes with therapeutic relationships")
    
    def create_lab_findings(self):
        """Create lab test nodes showing disease progression"""
        with self.driver.session() as session:
            lab_tests = [
                # Diabetes monitoring
                ('HbA1c', '8.2%', 'high', '2024-09-08', 'Comprehensive Metabolic Panel', 'Poor glycemic control'),
                ('Glucose (fasting)', '165 mg/dL', 'high', '2024-09-08', 'Comprehensive Metabolic Panel', 'Hyperglycemia'),
                
                # Kidney function
                ('Creatinine', '1.3 mg/dL', 'high', '2024-09-08', 'Comprehensive Metabolic Panel', 'Mild kidney impairment'),
                ('eGFR', '58 mL/min/1.73m²', 'low', '2024-09-08', 'Comprehensive Metabolic Panel', 'Stage 2 CKD confirmed'),
                ('BUN', '28 mg/dL', 'high', '2024-09-08', 'Comprehensive Metabolic Panel', 'Kidney function decline'),
                
                # Lipid management
                ('Triglycerides', '275 mg/dL', 'high', '2024-09-08', 'Lipid Panel', 'Diabetic dyslipidemia'),
                ('LDL Cholesterol', '88 mg/dL', 'normal', '2024-09-08', 'Lipid Panel', 'Good statin response'),
                
                # Anemia workup
                ('Hemoglobin', '11.8 g/dL', 'low', '2024-08-12', 'Complete Blood Count', 'Mild anemia'),
                ('Hematocrit', '35.2%', 'low', '2024-08-12', 'Complete Blood Count', 'Consistent with anemia'),
                
                # Thyroid monitoring
                ('TSH', '3.8 mIU/L', 'normal', '2024-07-20', 'Thyroid Function Panel', 'Adequate replacement'),
                ('TPO Antibodies', '245 IU/mL', 'high', '2024-07-20', 'Thyroid Function Panel', 'Hashimoto confirmed'),
            ]
            
            for test_name, value, flag, date, panel, interpretation in lab_tests:
                session.run("""
                    MATCH (p:Patient {name: 'Dr. Sarah Mitchell'})
                    CREATE (l:LabFinding {
                        test_name: $test_name,
                        value: $value,
                        flag: $flag,
                        date: $date,
                        panel: $panel,
                        interpretation: $interpretation,
                        node_type: 'Lab Finding'
                    })
                    CREATE (p)-[:HAS_LAB_RESULT {
                        date: $date,
                        panel: $panel,
                        abnormal: $abnormal
                    }]->(l)
                """, test_name=test_name, value=value, flag=flag, date=date, 
                     panel=panel, interpretation=interpretation, 
                     abnormal=(flag != 'normal'))
            
            logger.info(f"🧪 Created {len(lab_tests)} lab finding nodes")
    
    def create_appointments_and_symptoms(self):
        """Create appointment nodes with associated symptoms"""
        with self.driver.session() as session:
            appointments = [
                ('2024-09-10', 'Dr. Jennifer Adams', 'Endocrinology Follow-up', 'completed', [
                    ('Polyuria', 'Increased urination, especially at night', 'moderate'),
                    ('Polydipsia', 'Excessive thirst', 'moderate'),
                    ('Fatigue', 'Persistent tiredness despite adequate sleep', 'moderate'),
                ]),
                ('2024-08-15', 'Dr. Elena Rodriguez', 'Nephrology Consultation', 'completed', [
                    ('Ankle Swelling', 'Bilateral pedal edema, worse at end of day', 'mild'),
                    ('Proteinuria', 'Foamy urine noticed by patient', 'moderate'),
                ]),
                ('2024-07-22', 'Dr. Michael Chen', 'Cardiology Follow-up', 'completed', [
                    ('Chest Tightness', 'Occasional chest tightness with exertion', 'mild'),
                    ('Dyspnea on Exertion', 'Shortness of breath climbing stairs', 'mild'),
                ]),
                ('2024-06-28', 'Dr. Robert Kim', 'Psychiatry Follow-up', 'completed', [
                    ('Anxiety', 'Work-related stress and sleep disturbances', 'moderate'),
                    ('Insomnia', 'Difficulty falling asleep, early awakening', 'moderate'),
                ]),
            ]
            
            for date, doctor, visit_type, status, symptoms in appointments:
                # Create appointment node
                session.run("""
                    MATCH (p:Patient {name: 'Dr. Sarah Mitchell'})
                    CREATE (a:Appointment {
                        date: $date,
                        doctor: $doctor,
                        visit_type: $visit_type,
                        status: $status,
                        node_type: 'Appointment'
                    })
                    CREATE (p)-[:HAS_APPOINTMENT {
                        date: $date,
                        status: $status
                    }]->(a)
                """, date=date, doctor=doctor, visit_type=visit_type, status=status)
                
                # Create symptom nodes and relationships
                for symptom_name, description, severity in symptoms:
                    session.run("""
                        MATCH (a:Appointment {date: $date, doctor: $doctor})
                        CREATE (s:Symptom {
                            name: $symptom_name,
                            description: $description,
                            severity: $severity,
                            reported_date: $date,
                            node_type: 'Symptom'
                        })
                        CREATE (a)-[:REPORTED_SYMPTOM {
                            severity: $severity,
                            date: $date
                        }]->(s)
                    """, date=date, doctor=doctor, symptom_name=symptom_name, 
                         description=description, severity=severity)
            
            logger.info(f"📅 Created {len(appointments)} appointment nodes with associated symptoms")
    
    def create_care_team(self):
        """Create care team nodes and relationships"""
        with self.driver.session() as session:
            doctors = [
                ('Dr. Jennifer Adams', 'Endocrinologist', 'Primary diabetes care'),
                ('Dr. Michael Chen', 'Cardiologist', 'Cardiovascular risk management'),
                ('Dr. Elena Rodriguez', 'Nephrologist', 'Kidney disease monitoring'),
                ('Dr. Lisa Park', 'Endocrinologist', 'Thyroid management'),
                ('Dr. Robert Kim', 'Psychiatrist', 'Mental health support'),
            ]
            
            for name, specialty, role in doctors:
                session.run("""
                    MATCH (p:Patient {name: 'Dr. Sarah Mitchell'})
                    CREATE (d:Doctor {
                        name: $name,
                        specialty: $specialty,
                        role: $role,
                        node_type: 'Healthcare Provider'
                    })
                    CREATE (p)-[:UNDER_CARE_OF {
                        specialty: $specialty,
                        role: $role
                    }]->(d)
                """, name=name, specialty=specialty, role=role)
            
            logger.info(f"👨‍⚕️ Created {len(doctors)} care team member nodes")
    
    def create_medical_history(self):
        """Create medical history nodes"""
        with self.driver.session() as session:
            history_items = [
                ('Penicillin allergy', 'allergy', 'severe', 'Anaphylactic reaction in 1995'),
                ('Latex allergy', 'allergy', 'moderate', 'Occupational exposure'),
                ('Cesarean Section', 'surgery', 'moderate', 'Emergency procedure 2015'),
                ('Cholecystectomy', 'surgery', 'moderate', 'Laparoscopic 2019'),
                ('Former Smoker', 'lifestyle', 'moderate', '10 pack-year history, quit 2010'),
                ('Family History CAD', 'family_history', 'severe', 'Father died of MI at 58'),
                ('Family History Diabetes', 'family_history', 'moderate', 'Mother has T2DM'),
            ]
            
            for item, history_type, severity, details in history_items:
                session.run("""
                    MATCH (p:Patient {name: 'Dr. Sarah Mitchell'})
                    CREATE (h:MedicalHistory {
                        item: $item,
                        type: $history_type,
                        severity: $severity,
                        details: $details,
                        node_type: 'Medical History'
                    })
                    CREATE (p)-[:HAS_HISTORY {
                        type: $history_type,
                        severity: $severity
                    }]->(h)
                """, item=item, history_type=history_type, severity=severity, details=details)
            
            logger.info(f"📋 Created {len(history_items)} medical history nodes")
    
    def create_disease_relationships(self):
        """Create complex relationships between diseases"""
        with self.driver.session() as session:
            # Diabetes -> Kidney Disease progression
            session.run("""
                MATCH (dm:MedicalCondition {name: 'Type 2 Diabetes Mellitus'})
                MATCH (ckd:MedicalCondition {name: 'Chronic Kidney Disease Stage 2'})
                CREATE (dm)-[:CAUSES {
                    mechanism: 'diabetic nephropathy',
                    progression_time: '7 years',
                    evidence: 'microalbuminuria and eGFR decline'
                }]->(ckd)
            """)
            
            # Hypertension -> Kidney Disease
            session.run("""
                MATCH (htn:MedicalCondition {name: 'Hypertension'})
                MATCH (ckd:MedicalCondition {name: 'Chronic Kidney Disease Stage 2'})
                CREATE (htn)-[:CONTRIBUTES_TO {
                    mechanism: 'hypertensive nephrosclerosis',
                    synergy: 'with diabetes'
                }]->(ckd)
            """)
            
            # Diabetes -> Hyperlipidemia
            session.run("""
                MATCH (dm:MedicalCondition {name: 'Type 2 Diabetes Mellitus'})
                MATCH (lipid:MedicalCondition {name: 'Hyperlipidemia'})
                CREATE (dm)-[:ASSOCIATED_WITH {
                    mechanism: 'insulin resistance and metabolic syndrome',
                    pattern: 'diabetic dyslipidemia'
                }]->(lipid)
            """)
            
            logger.info("🔗 Created complex disease progression relationships")
    
    def create_medication_interactions(self):
        """Create medication interaction relationships"""
        with self.driver.session() as session:
            # ACE inhibitor + ARB for kidney protection
            session.run("""
                MATCH (ace:Medication {name: 'Lisinopril'})
                MATCH (arb:Medication {name: 'Losartan'})
                CREATE (ace)-[:SYNERGISTIC_WITH {
                    purpose: 'dual RAAS blockade',
                    target: 'renal protection',
                    monitoring: 'serum potassium and creatinine'
                }]->(arb)
            """)
            
            # Metformin + Insulin combination
            session.run("""
                MATCH (met:Medication {name: 'Metformin XR'})
                MATCH (ins:Medication {name: 'Insulin Glargine'})
                CREATE (met)-[:COMPLEMENTS {
                    mechanism: 'insulin sensitization + exogenous insulin',
                    benefit: 'improved glycemic control with lower insulin doses'
                }]->(ins)
            """)
            
            logger.info("💊 Created medication interaction relationships")
    
    def create_chat_insights(self):
        """Create nodes for key chat insights"""
        with self.driver.session() as session:
            insights = [
                ('Stress Management Challenge', 'Behavioral', 'Work stress affecting diabetes control'),
                ('Medication Adherence', 'Behavioral', 'Good compliance reported by patient'),
                ('Symptom Awareness', 'Clinical', 'Patient recognizes diabetic symptoms'),
                ('Quality of Life Impact', 'Psychosocial', 'Multiple conditions affecting daily life'),
            ]
            
            for insight, category, description in insights:
                session.run("""
                    MATCH (p:Patient {name: 'Dr. Sarah Mitchell'})
                    CREATE (i:ClinicalInsight {
                        insight: $insight,
                        category: $category,
                        description: $description,
                        node_type: 'Clinical Insight'
                    })
                    CREATE (p)-[:HAS_INSIGHT {
                        category: $category
                    }]->(i)
                """, insight=insight, category=category, description=description)
            
            logger.info(f"💭 Created {len(insights)} clinical insight nodes")
    
    def get_graph_statistics(self):
        """Get comprehensive graph statistics"""
        with self.driver.session() as session:
            # Count nodes by type
            node_stats = session.run("""
                MATCH (n)
                WHERE n.node_type IS NOT NULL
                RETURN n.node_type as node_type, count(n) as count
                ORDER BY count DESC
            """)
            
            # Count relationships by type
            rel_stats = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
            """)
            
            # Get total counts
            total_nodes = session.run("MATCH (n) RETURN count(n) as total").single()['total']
            total_rels = session.run("MATCH ()-[r]->() RETURN count(r) as total").single()['total']
            
            return {
                'total_nodes': total_nodes,
                'total_relationships': total_rels,
                'node_types': list(node_stats),
                'relationship_types': list(rel_stats)
            }
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            logger.info("🔒 Database connection closed")

def main():
    creator = RichKnowledgeGraphCreator()
    
    if not creator.connect():
        return
    
    try:
        logger.info("🏥 Creating Rich Knowledge Graph for Dr. Sarah Mitchell")
        logger.info("=" * 65)
        
        # Clear existing data
        creator.clear_patient_data("Dr. Sarah Mitchell")
        
        # Create all nodes and relationships
        creator.create_patient_node()
        creator.create_medical_conditions()
        creator.create_medications()
        creator.create_lab_findings()
        creator.create_appointments_and_symptoms()
        creator.create_care_team()
        creator.create_medical_history()
        creator.create_disease_relationships()
        creator.create_medication_interactions()
        creator.create_chat_insights()
        
        # Get statistics
        stats = creator.get_graph_statistics()
        
        logger.info("✅ Rich knowledge graph creation completed!")
        
        # Print comprehensive statistics
        print(f"""
🎯 Rich Knowledge Graph Statistics for Dr. Sarah Mitchell
═══════════════════════════════════════════════════════════════

📊 Overall Graph Metrics:
┌─────────────────────────┬──────────┐
│ Total Nodes             │   {stats['total_nodes']:3}    │
│ Total Relationships     │   {stats['total_relationships']:3}    │
└─────────────────────────┴──────────┘

🏷️  Node Distribution:""")
        
        for node_type in stats['node_types']:
            print(f"│ {node_type['node_type']:<22} │   {node_type['count']:3}    │")
        
        print(f"""└─────────────────────────┴──────────┘

🔗 Relationship Distribution:""")
        
        for rel_type in stats['relationship_types']:
            print(f"│ {rel_type['relationship_type']:<22} │   {rel_type['count']:3}    │")
        
        print(f"""└─────────────────────────┴──────────┘

🏥 Medical Complexity Highlights:
• Multiple chronic conditions with interconnected pathways
• Disease progression relationships (Diabetes → CKD)
• Complex medication regimens with drug interactions
• Multi-specialty care coordination across 5 providers
• Temporal progression visible through lab values
• Rich symptom-condition-treatment relationships
• Clinical insights from patient communications

🎭 This graph demonstrates the full power of atomic facts
   for representing complex medical scenarios with rich
   interconnectedness and temporal relationships!

📊 The knowledge graph is now ready for:
   • Complex medical queries and analytics
   • Care pathway optimization
   • Drug interaction analysis
   • Disease progression monitoring
   • Care coordination insights
        """)
        
    except Exception as e:
        logger.error(f"❌ Error creating knowledge graph: {e}")
    finally:
        creator.close()

if __name__ == "__main__":
    main()