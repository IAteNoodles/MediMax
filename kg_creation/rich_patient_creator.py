#!/usr/bin/env python3
"""
Rich Patient Data Generator for Atomic Facts Knowledge Graph
============================================================

This script creates a comprehensive patient with extensive medical data
to demonstrate the full power of our atomic facts knowledge graph system.

Features:
- Multiple medications with complex interactions
- Extensive medical history with temporal relationships
- Multiple lab reports showing progression over time
- Detailed appointment history with symptom tracking
- Rich chat history showing patient journey
- Complex medical conditions and their relationships

Author: GitHub Copilot
Date: September 14, 2025
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RichPatientCreator:
    def __init__(self):
        load_dotenv()
    
    def create_comprehensive_patient(self):
        """Create a patient with comprehensive medical data"""
        logger.info("🏥 Creating Rich Patient with Comprehensive Medical Data")
        logger.info("=" * 65)
        
        # Patient: Dr. Sarah Mitchell (a 45-year-old physician with complex medical history)
        rich_patient_data = {
            'patient_info': {
                'name': 'Dr. Sarah Mitchell',
                'dob': '1979-03-22',
                'sex': 'Female',
                'occupation': 'Cardiologist',
                'emergency_contact': 'Dr. James Mitchell (spouse)'
            },
            
            'medical_history': [
                # Allergies
                {'type': 'allergy', 'item': 'Penicillin allergy', 'details': 'Severe anaphylactic reaction in 1995', 'severity': 'severe', 'date': '1995-06-15'},
                {'type': 'allergy', 'item': 'Latex allergy', 'details': 'Developed after years of surgical glove use', 'severity': 'moderate', 'date': '2010-03-10'},
                {'type': 'allergy', 'item': 'Shellfish allergy', 'details': 'Mild urticaria and GI symptoms', 'severity': 'mild', 'date': '2005-08-20'},
                
                # Medical Conditions
                {'type': 'condition', 'item': 'Hypertension', 'details': 'Essential hypertension diagnosed during pregnancy', 'severity': 'moderate', 'date': '2015-02-14'},
                {'type': 'condition', 'item': 'Type 2 Diabetes Mellitus', 'details': 'Gestational diabetes that progressed to T2DM', 'severity': 'moderate', 'date': '2016-11-08'},
                {'type': 'condition', 'item': 'Hyperlipidemia', 'details': 'Familial combined hyperlipidemia', 'severity': 'moderate', 'date': '2018-05-15'},
                {'type': 'condition', 'item': 'Anxiety Disorder', 'details': 'Work-related stress and pandemic burnout', 'severity': 'mild', 'date': '2020-09-12'},
                {'type': 'condition', 'item': 'Chronic Kidney Disease Stage 2', 'details': 'Secondary to diabetes and hypertension', 'severity': 'moderate', 'date': '2023-01-20'},
                {'type': 'condition', 'item': 'Hypothyroidism', 'details': 'Hashimoto thyroiditis', 'severity': 'mild', 'date': '2021-07-03'},
                
                # Surgical History
                {'type': 'surgery', 'item': 'Cholecystectomy', 'details': 'Laparoscopic cholecystectomy for gallstones', 'severity': 'moderate', 'date': '2019-04-15'},
                {'type': 'surgery', 'item': 'Cesarean Section', 'details': 'Emergency C-section for fetal distress', 'severity': 'moderate', 'date': '2015-09-22'},
                
                # Family History
                {'type': 'family_history', 'item': 'Paternal CAD', 'details': 'Father had MI at age 52, died at 58', 'severity': 'severe', 'date': '1950-01-01'},
                {'type': 'family_history', 'item': 'Maternal Diabetes', 'details': 'Mother has T2DM and diabetic nephropathy', 'severity': 'moderate', 'date': '1955-01-01'},
                {'type': 'family_history', 'item': 'Sister Breast Cancer', 'details': 'BRCA2 positive, diagnosed at 38', 'severity': 'severe', 'date': '1981-01-01'},
                
                # Lifestyle
                {'type': 'lifestyle', 'item': 'Former Smoker', 'details': '10 pack-year history, quit 2010', 'severity': 'moderate', 'date': '2010-01-01'},
                {'type': 'lifestyle', 'item': 'Social Drinker', 'details': '2-3 glasses wine per week', 'severity': 'mild', 'date': '2024-01-01'},
            ],
            
            'medications': [
                # Diabetes Management
                {'name': 'Metformin XR', 'dosage': '1000mg', 'frequency': 'Twice daily', 'condition': 'Type 2 Diabetes', 'prescribed_date': '2016-11-08', 'prescribed_by': 'Dr. Jennifer Adams', 'is_continued': True},
                {'name': 'Insulin Glargine', 'dosage': '25 units', 'frequency': 'Daily at bedtime', 'condition': 'Type 2 Diabetes', 'prescribed_date': '2020-03-15', 'prescribed_by': 'Dr. Jennifer Adams', 'is_continued': True},
                {'name': 'Insulin Lispro', 'dosage': '1:10 ratio', 'frequency': 'With meals', 'condition': 'Type 2 Diabetes', 'prescribed_date': '2020-03-15', 'prescribed_by': 'Dr. Jennifer Adams', 'is_continued': True},
                
                # Cardiovascular Management
                {'name': 'Lisinopril', 'dosage': '20mg', 'frequency': 'Daily', 'condition': 'Hypertension', 'prescribed_date': '2015-02-14', 'prescribed_by': 'Dr. Michael Chen', 'is_continued': True},
                {'name': 'Amlodipine', 'dosage': '10mg', 'frequency': 'Daily', 'condition': 'Hypertension', 'prescribed_date': '2018-06-20', 'prescribed_by': 'Dr. Michael Chen', 'is_continued': True},
                {'name': 'Atorvastatin', 'dosage': '40mg', 'frequency': 'Daily at bedtime', 'condition': 'Hyperlipidemia', 'prescribed_date': '2018-05-15', 'prescribed_by': 'Dr. Michael Chen', 'is_continued': True},
                {'name': 'Aspirin', 'dosage': '81mg', 'frequency': 'Daily', 'condition': 'Cardiovascular Protection', 'prescribed_date': '2018-05-15', 'prescribed_by': 'Dr. Michael Chen', 'is_continued': True},
                
                # Thyroid Management
                {'name': 'Levothyroxine', 'dosage': '88mcg', 'frequency': 'Daily on empty stomach', 'condition': 'Hypothyroidism', 'prescribed_date': '2021-07-03', 'prescribed_by': 'Dr. Lisa Park', 'is_continued': True},
                
                # Mental Health
                {'name': 'Sertraline', 'dosage': '50mg', 'frequency': 'Daily', 'condition': 'Anxiety Disorder', 'prescribed_date': '2020-09-12', 'prescribed_by': 'Dr. Robert Kim', 'is_continued': True},
                
                # Kidney Protection
                {'name': 'Losartan', 'dosage': '50mg', 'frequency': 'Daily', 'condition': 'Chronic Kidney Disease', 'prescribed_date': '2023-01-20', 'prescribed_by': 'Dr. Elena Rodriguez', 'is_continued': True},
                
                # Supplements
                {'name': 'Vitamin D3', 'dosage': '2000 IU', 'frequency': 'Daily', 'condition': 'Vitamin D Deficiency', 'prescribed_date': '2019-11-10', 'prescribed_by': 'Dr. Jennifer Adams', 'is_continued': True},
                {'name': 'Calcium Carbonate', 'dosage': '1200mg', 'frequency': 'Twice daily', 'condition': 'Osteoporosis Prevention', 'prescribed_date': '2022-03-08', 'prescribed_by': 'Dr. Jennifer Adams', 'is_continued': True},
                {'name': 'Omega-3 Fish Oil', 'dosage': '1000mg', 'frequency': 'Twice daily', 'condition': 'Cardiovascular Health', 'prescribed_date': '2019-06-12', 'prescribed_by': 'Dr. Michael Chen', 'is_continued': True},
                
                # Recently Discontinued
                {'name': 'Hydrochlorothiazide', 'dosage': '25mg', 'frequency': 'Daily', 'condition': 'Hypertension', 'prescribed_date': '2015-02-14', 'prescribed_by': 'Dr. Michael Chen', 'is_continued': False, 'discontinued_date': '2023-01-20'},
            ],
            
            'appointments': [
                # Recent appointments with detailed symptoms
                {
                    'date': '2024-09-10', 'time': '14:30:00', 'doctor': 'Dr. Jennifer Adams', 'type': 'follow_up', 'status': 'completed',
                    'symptoms': [
                        {'name': 'Polyuria', 'description': 'Increased urination, especially at night', 'severity': 'moderate', 'duration': '2 weeks'},
                        {'name': 'Polydipsia', 'description': 'Excessive thirst', 'severity': 'moderate', 'duration': '2 weeks'},
                        {'name': 'Fatigue', 'description': 'Persistent tiredness despite adequate sleep', 'severity': 'moderate', 'duration': '3 weeks'},
                        {'name': 'Blurred Vision', 'description': 'Intermittent blurring, worse in evenings', 'severity': 'mild', 'duration': '1 week'},
                    ]
                },
                {
                    'date': '2024-08-15', 'time': '10:00:00', 'doctor': 'Dr. Elena Rodriguez', 'type': 'consultation', 'status': 'completed',
                    'symptoms': [
                        {'name': 'Ankle Swelling', 'description': 'Bilateral pedal edema, worse at end of day', 'severity': 'mild', 'duration': '1 month'},
                        {'name': 'Proteinuria', 'description': 'Foamy urine noticed by patient', 'severity': 'moderate', 'duration': '2 months'},
                    ]
                },
                {
                    'date': '2024-07-22', 'time': '09:15:00', 'doctor': 'Dr. Michael Chen', 'type': 'routine_checkup', 'status': 'completed',
                    'symptoms': [
                        {'name': 'Chest Tightness', 'description': 'Occasional chest tightness with exertion', 'severity': 'mild', 'duration': '6 weeks'},
                        {'name': 'Dyspnea on Exertion', 'description': 'Shortness of breath climbing 2 flights stairs', 'severity': 'mild', 'duration': '2 months'},
                    ]
                },
                {
                    'date': '2024-06-28', 'time': '16:00:00', 'doctor': 'Dr. Robert Kim', 'type': 'follow_up', 'status': 'completed',
                    'symptoms': [
                        {'name': 'Anxiety', 'description': 'Work-related stress and sleep disturbances', 'severity': 'moderate', 'duration': '1 month'},
                        {'name': 'Insomnia', 'description': 'Difficulty falling asleep, early awakening', 'severity': 'moderate', 'duration': '3 weeks'},
                    ]
                },
                {
                    'date': '2024-05-18', 'time': '11:30:00', 'doctor': 'Dr. Lisa Park', 'type': 'follow_up', 'status': 'completed',
                    'symptoms': [
                        {'name': 'Hair Loss', 'description': 'Thinning hair despite thyroid treatment', 'severity': 'mild', 'duration': '3 months'},
                        {'name': 'Cold Intolerance', 'description': 'Feeling cold even in warm weather', 'severity': 'mild', 'duration': '2 months'},
                    ]
                },
                # Upcoming appointments
                {
                    'date': '2024-10-15', 'time': '14:00:00', 'doctor': 'Dr. Jennifer Adams', 'type': 'follow_up', 'status': 'scheduled',
                    'symptoms': []
                },
                {
                    'date': '2024-11-20', 'time': '10:30:00', 'doctor': 'Dr. Michael Chen', 'type': 'routine_checkup', 'status': 'scheduled',
                    'symptoms': []
                },
            ],
            
            'lab_reports': [
                # Comprehensive Metabolic Panel - September 2024
                {
                    'date': '2024-09-08', 'type': 'Comprehensive Metabolic Panel', 'doctor': 'Dr. Jennifer Adams', 'facility': 'Central Lab',
                    'findings': [
                        {'test': 'Glucose (fasting)', 'value': '165', 'unit': 'mg/dL', 'range': '70-100', 'abnormal': True, 'flag': 'high'},
                        {'test': 'HbA1c', 'value': '8.2', 'unit': '%', 'range': '<7.0', 'abnormal': True, 'flag': 'high'},
                        {'test': 'Creatinine', 'value': '1.3', 'unit': 'mg/dL', 'range': '0.6-1.1', 'abnormal': True, 'flag': 'high'},
                        {'test': 'eGFR', 'value': '58', 'unit': 'mL/min/1.73m²', 'range': '>60', 'abnormal': True, 'flag': 'low'},
                        {'test': 'BUN', 'value': '28', 'unit': 'mg/dL', 'range': '7-20', 'abnormal': True, 'flag': 'high'},
                        {'test': 'Sodium', 'value': '138', 'unit': 'mEq/L', 'range': '136-145', 'abnormal': False, 'flag': None},
                        {'test': 'Potassium', 'value': '4.8', 'unit': 'mEq/L', 'range': '3.5-5.0', 'abnormal': False, 'flag': None},
                        {'test': 'Chloride', 'value': '102', 'unit': 'mEq/L', 'range': '98-107', 'abnormal': False, 'flag': None},
                    ]
                },
                
                # Lipid Panel - September 2024
                {
                    'date': '2024-09-08', 'type': 'Lipid Panel', 'doctor': 'Dr. Michael Chen', 'facility': 'Central Lab',
                    'findings': [
                        {'test': 'Total Cholesterol', 'value': '195', 'unit': 'mg/dL', 'range': '<200', 'abnormal': False, 'flag': None},
                        {'test': 'LDL Cholesterol', 'value': '88', 'unit': 'mg/dL', 'range': '<100', 'abnormal': False, 'flag': None},
                        {'test': 'HDL Cholesterol', 'value': '52', 'unit': 'mg/dL', 'range': '>50', 'abnormal': False, 'flag': None},
                        {'test': 'Triglycerides', 'value': '275', 'unit': 'mg/dL', 'range': '<150', 'abnormal': True, 'flag': 'high'},
                        {'test': 'Non-HDL Cholesterol', 'value': '143', 'unit': 'mg/dL', 'range': '<130', 'abnormal': True, 'flag': 'high'},
                    ]
                },
                
                # Complete Blood Count - August 2024
                {
                    'date': '2024-08-12', 'type': 'Complete Blood Count', 'doctor': 'Dr. Elena Rodriguez', 'facility': 'Central Lab',
                    'findings': [
                        {'test': 'Hemoglobin', 'value': '11.8', 'unit': 'g/dL', 'range': '12.0-15.5', 'abnormal': True, 'flag': 'low'},
                        {'test': 'Hematocrit', 'value': '35.2', 'unit': '%', 'range': '36.0-46.0', 'abnormal': True, 'flag': 'low'},
                        {'test': 'WBC Count', 'value': '7.2', 'unit': 'K/μL', 'range': '4.5-11.0', 'abnormal': False, 'flag': None},
                        {'test': 'Platelet Count', 'value': '285', 'unit': 'K/μL', 'range': '150-400', 'abnormal': False, 'flag': None},
                        {'test': 'MCV', 'value': '78', 'unit': 'fL', 'range': '80-100', 'abnormal': True, 'flag': 'low'},
                        {'test': 'MCH', 'value': '26', 'unit': 'pg', 'range': '27-32', 'abnormal': True, 'flag': 'low'},
                    ]
                },
                
                # Thyroid Function Tests - July 2024
                {
                    'date': '2024-07-20', 'type': 'Thyroid Function Panel', 'doctor': 'Dr. Lisa Park', 'facility': 'Endocrine Lab',
                    'findings': [
                        {'test': 'TSH', 'value': '3.8', 'unit': 'mIU/L', 'range': '0.4-4.0', 'abnormal': False, 'flag': None},
                        {'test': 'Free T4', 'value': '1.1', 'unit': 'ng/dL', 'range': '0.8-1.8', 'abnormal': False, 'flag': None},
                        {'test': 'Free T3', 'value': '2.8', 'unit': 'pg/mL', 'range': '2.3-4.2', 'abnormal': False, 'flag': None},
                        {'test': 'TPO Antibodies', 'value': '245', 'unit': 'IU/mL', 'range': '<35', 'abnormal': True, 'flag': 'high'},
                    ]
                },
                
                # Microalbumin - June 2024
                {
                    'date': '2024-06-15', 'type': 'Microalbumin (24hr)', 'doctor': 'Dr. Elena Rodriguez', 'facility': 'Nephrology Lab',
                    'findings': [
                        {'test': 'Microalbumin', 'value': '85', 'unit': 'mg/24hr', 'range': '<30', 'abnormal': True, 'flag': 'high'},
                        {'test': 'Creatinine Clearance', 'value': '62', 'unit': 'mL/min', 'range': '>90', 'abnormal': True, 'flag': 'low'},
                        {'test': 'Protein/Creatinine Ratio', 'value': '0.18', 'unit': 'mg/mg', 'range': '<0.15', 'abnormal': True, 'flag': 'high'},
                    ]
                },
                
                # Cardiac Stress Test - May 2024
                {
                    'date': '2024-05-25', 'type': 'Cardiac Stress Test with Echo', 'doctor': 'Dr. Michael Chen', 'facility': 'Cardiology Center',
                    'findings': [
                        {'test': 'Exercise Tolerance', 'value': '8.5 METS', 'unit': 'METS', 'range': '>7', 'abnormal': False, 'flag': None},
                        {'test': 'Peak Heart Rate', 'value': '158', 'unit': 'bpm', 'range': '85% max predicted', 'abnormal': False, 'flag': None},
                        {'test': 'ST Segment Changes', 'value': 'None', 'unit': '', 'range': 'None', 'abnormal': False, 'flag': None},
                        {'test': 'LVEF (Rest)', 'value': '58', 'unit': '%', 'range': '>55', 'abnormal': False, 'flag': None},
                        {'test': 'LVEF (Stress)', 'value': '55', 'unit': '%', 'range': '>55', 'abnormal': False, 'flag': None},
                    ]
                }
            ],
            
            'chat_history': [
                # Recent diabetes concerns
                {'message': 'Dr. Adams, I\'ve been having increased thirst and urination again, especially at night. My glucose readings at home have been running 180-220.', 'type': 'patient', 'session': 'session_sarah_001', 'timestamp': '2024-09-05 14:30:00'},
                {'message': 'How long have you been experiencing these symptoms? Have you made any changes to your diet or medication routine recently?', 'type': 'doctor', 'session': 'session_sarah_001', 'timestamp': '2024-09-05 14:32:00'},
                {'message': 'About 2-3 weeks now. I\'ve been under a lot of stress at the hospital - we\'ve had several difficult cases. I admit I\'ve been eating more convenience foods and my exercise has been inconsistent.', 'type': 'patient', 'session': 'session_sarah_001', 'timestamp': '2024-09-05 14:33:00'},
                {'message': 'I understand the demands of your profession. Let\'s get some labs and consider adjusting your insulin regimen. We may need to increase your basal insulin and optimize your meal coverage.', 'type': 'doctor', 'session': 'session_sarah_001', 'timestamp': '2024-09-05 14:35:00'},
                
                # Kidney function concerns
                {'message': 'Dr. Rodriguez, I\'ve noticed my ankles swelling more lately, and my urine seems foamy. I\'m concerned about my kidney function given my diabetes.', 'type': 'patient', 'session': 'session_sarah_002', 'timestamp': '2024-08-10 09:15:00'},
                {'message': 'Those are important observations. The foamy urine could indicate protein spillage. Let\'s check your microalbumin levels and creatinine. How\'s your blood pressure control been?', 'type': 'doctor', 'session': 'session_sarah_002', 'timestamp': '2024-08-10 09:17:00'},
                {'message': 'My home readings have been averaging 135/85, which is higher than my usual 125/80. I\'ve been taking my medications as prescribed.', 'type': 'patient', 'session': 'session_sarah_002', 'timestamp': '2024-08-10 09:18:00'},
                {'message': 'We may need to optimize your blood pressure management. I\'m going to add an ARB to provide additional kidney protection and better BP control.', 'type': 'doctor', 'session': 'session_sarah_002', 'timestamp': '2024-08-10 09:20:00'},
                
                # Cardiovascular concerns
                {'message': 'Dr. Chen, I\'ve been experiencing some chest tightness when I climb stairs at the hospital. It\'s not severe, but it\'s new for me.', 'type': 'patient', 'session': 'session_sarah_003', 'timestamp': '2024-07-18 15:30:00'},
                {'message': 'Given your family history and current risk factors, we should take this seriously. Let\'s schedule a stress test to evaluate your cardiac function.', 'type': 'doctor', 'session': 'session_sarah_003', 'timestamp': '2024-07-18 15:32:00'},
                {'message': 'I was hoping you\'d say that wasn\'t necessary, but I know you\'re right. My father\'s history makes me vigilant about cardiac symptoms.', 'type': 'patient', 'session': 'session_sarah_003', 'timestamp': '2024-07-18 15:33:00'},
                
                # Mental health support
                {'message': 'Dr. Kim, the pandemic really took a toll, and now with my health issues, I\'m feeling overwhelmed. My sleep is terrible and I\'m constantly worried.', 'type': 'patient', 'session': 'session_sarah_004', 'timestamp': '2024-06-25 16:45:00'},
                {'message': 'Healthcare workers have faced unprecedented challenges. It\'s completely understandable. How are the sertraline and our coping strategies working for you?', 'type': 'doctor', 'session': 'session_sarah_004', 'timestamp': '2024-06-25 16:47:00'},
                {'message': 'The medication helps with the daily anxiety, but I still wake up at 3 AM worried about my patients and my own health. The meditation app you recommended does help sometimes.', 'type': 'patient', 'session': 'session_sarah_004', 'timestamp': '2024-06-25 16:48:00'},
                
                # Thyroid management
                {'message': 'Dr. Park, despite the levothyroxine, I\'m still losing hair and feeling cold. My energy levels aren\'t what they should be.', 'type': 'patient', 'session': 'session_sarah_005', 'timestamp': '2024-05-15 11:00:00'},
                {'message': 'Your TSH levels look good, but with Hashimoto\'s, sometimes we need to optimize further. Let\'s check your T3 levels and consider if you might benefit from combination therapy.', 'type': 'doctor', 'session': 'session_sarah_005', 'timestamp': '2024-05-15 11:02:00'},
                {'message': 'I\'ve read about T4/T3 combinations. As a physician, I appreciate the complexity of thyroid management, but as a patient, I just want to feel like myself again.', 'type': 'patient', 'session': 'session_sarah_005', 'timestamp': '2024-05-15 11:03:00'},
            ]
        }
        
        return rich_patient_data
    
    def generate_sql_inserts(self, patient_data):
        """Generate SQL INSERT statements for the rich patient data"""
        logger.info("📝 Generating SQL INSERT statements...")
        
        sql_statements = []
        
        # Patient insert
        patient_info = patient_data['patient_info']
        sql_statements.append(f"""
-- Insert rich patient: {patient_info['name']}
INSERT INTO Patient (name, dob, sex) 
VALUES ('{patient_info['name']}', '{patient_info['dob']}', '{patient_info['sex']}');

SET @patient_id = LAST_INSERT_ID();
""")
        
        # Medical History inserts
        sql_statements.append("-- Medical History")
        for history in patient_data['medical_history']:
            sql_statements.append(f"""
INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, '{history['type']}', '{history['item']}', '{history['details']}', '{history['severity']}', true, '{history['date']}');
""")
        
        # Medication inserts
        sql_statements.append("\n-- Medications and Purposes")
        for i, med in enumerate(patient_data['medications'], 1):
            discontinued_date = f"'{med.get('discontinued_date')}'" if med.get('discontinued_date') else 'NULL'
            sql_statements.append(f"""
INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, '{med['name']}', {str(med['is_continued']).lower()}, '{med['prescribed_date']}', {discontinued_date}, '{med['dosage']}', '{med['frequency']}', '{med['prescribed_by']}');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), '{med['condition']}', 'Prescribed for {med['condition']} management');
""")
        
        # Appointment inserts
        sql_statements.append("\n-- Appointments and Symptoms")
        for appt in patient_data['appointments']:
            time_val = f"'{appt['time']}'" if appt.get('time') else 'NULL'
            sql_statements.append(f"""
INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '{appt['date']}', {time_val}, '{appt['status']}', '{appt['type']}', '{appt['doctor']}');

SET @appointment_id = LAST_INSERT_ID();
""")
            
            # Symptoms for this appointment
            for symptom in appt.get('symptoms', []):
                sql_statements.append(f"""
INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, '{symptom['name']}', '{symptom['description']}', '{symptom['severity']}', '{symptom['duration']}');
""")
        
        # Lab Reports and Findings
        sql_statements.append("\n-- Lab Reports and Findings")
        for lab in patient_data['lab_reports']:
            sql_statements.append(f"""
INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
VALUES (@patient_id, '{lab['date']}', '{lab['type']}', '{lab['doctor']}', '{lab['facility']}');

SET @lab_report_id = LAST_INSERT_ID();
""")
            
            # Findings for this lab report
            for finding in lab['findings']:
                abnormal_flag = f"'{finding['flag']}'" if finding['flag'] else 'NULL'
                sql_statements.append(f"""
INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, '{finding['test']}', '{finding['value']}', '{finding['unit']}', '{finding['range']}', {str(finding['abnormal']).lower()}, {abnormal_flag});
""")
        
        # Chat History
        sql_statements.append("\n-- Chat History")
        for chat in patient_data['chat_history']:
            # Escape single quotes in message text
            message_text = chat['message'].replace("'", "''")
            sql_statements.append(f"""
INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, '{message_text}', '{chat['type']}', '{chat['session']}', '{chat['timestamp']}');
""")
        
        return '\n'.join(sql_statements)

def main():
    creator = RichPatientCreator()
    
    # Create comprehensive patient data
    rich_data = creator.create_comprehensive_patient()
    
    # Generate SQL statements
    sql_code = creator.generate_sql_inserts(rich_data)
    
    # Save to file
    with open('rich_patient_data.sql', 'w', encoding='utf-8') as f:
        f.write(sql_code)
    
    logger.info("✅ Rich patient SQL generated successfully!")
    
    # Print summary
    print(f"""
🏥 Rich Patient Data Generated: {rich_data['patient_info']['name']}
═══════════════════════════════════════════════════════════════

📊 Data Summary:
┌─────────────────────────┬──────────┐
│ Medical History Items   │    {len(rich_data['medical_history']):2}    │
│ Medications             │    {len(rich_data['medications']):2}    │
│ Appointments            │    {len(rich_data['appointments']):2}    │
│ Lab Reports             │    {len(rich_data['lab_reports']):2}    │
│ Chat Messages           │    {len(rich_data['chat_history']):2}    │
└─────────────────────────┴──────────┘

📋 Medical Complexity:
• Multiple chronic conditions (Diabetes, HTN, CKD, Hypothyroidism)
• Complex medication regimen with interactions
• Progressive disease monitoring over time
• Multi-specialty care coordination
• Rich temporal relationships

💾 Next Steps:
1. Review 'rich_patient_data.sql'
2. Execute SQL in database
3. Run knowledge graph creator
4. Explore rich interconnected medical relationships

This patient demonstrates the full power of atomic facts knowledge graphs
for complex medical cases with temporal progression and multi-system involvement!
    """)

if __name__ == "__main__":
    main()