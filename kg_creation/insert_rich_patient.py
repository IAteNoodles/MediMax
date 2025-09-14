#!/usr/bin/env python3
"""
Insert Rich Patient Data into Atomic Facts Database
==================================================

This script inserts the comprehensive Dr. Sarah Mitchell data
into our atomic facts database using the MCP server.

Author: GitHub Copilot
Date: September 14, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend_noodles.mcp_client import MCPClient
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RichPatientInserter:
    def __init__(self):
        self.client = MCPClient()
        self.patient_id = 6  # Dr. Sarah Mitchell's ID
    
    async def insert_medical_history(self):
        """Insert comprehensive medical history"""
        logger.info("📋 Inserting Medical History...")
        
        history_items = [
            ('allergy', 'Penicillin allergy', 'Severe anaphylactic reaction in 1995', 'severe', '1995-06-15'),
            ('allergy', 'Latex allergy', 'Developed after years of surgical glove use', 'moderate', '2010-03-10'),
            ('allergy', 'Shellfish allergy', 'Mild urticaria and GI symptoms', 'mild', '2005-08-20'),
            ('condition', 'Hypertension', 'Essential hypertension diagnosed during pregnancy', 'moderate', '2015-02-14'),
            ('condition', 'Type 2 Diabetes Mellitus', 'Gestational diabetes that progressed to T2DM', 'moderate', '2016-11-08'),
            ('condition', 'Hyperlipidemia', 'Familial combined hyperlipidemia', 'moderate', '2018-05-15'),
            ('condition', 'Anxiety Disorder', 'Work-related stress and pandemic burnout', 'mild', '2020-09-12'),
            ('condition', 'Chronic Kidney Disease Stage 2', 'Secondary to diabetes and hypertension', 'moderate', '2023-01-20'),
            ('condition', 'Hypothyroidism', 'Hashimoto thyroiditis', 'mild', '2021-07-03'),
            ('surgery', 'Cholecystectomy', 'Laparoscopic cholecystectomy for gallstones', 'moderate', '2019-04-15'),
            ('surgery', 'Cesarean Section', 'Emergency C-section for fetal distress', 'moderate', '2015-09-22'),
            ('family_history', 'Paternal CAD', 'Father had MI at age 52, died at 58', 'severe', '1950-01-01'),
            ('family_history', 'Maternal Diabetes', 'Mother has T2DM and diabetic nephropathy', 'moderate', '1955-01-01'),
            ('family_history', 'Sister Breast Cancer', 'BRCA2 positive, diagnosed at 38', 'severe', '1981-01-01'),
            ('lifestyle', 'Former Smoker', '10 pack-year history, quit 2010', 'moderate', '2010-01-01'),
            ('lifestyle', 'Social Drinker', '2-3 glasses wine per week', 'mild', '2024-01-01'),
        ]
        
        for history_type, item, details, severity, date in history_items:
            query = f"""
            INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
            VALUES ({self.patient_id}, '{history_type}', '{item}', '{details}', '{severity}', true, '{date}')
            """
            await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': query})
        
        logger.info(f"✅ Inserted {len(history_items)} medical history items")
    
    async def insert_medications(self):
        """Insert comprehensive medication list"""
        logger.info("💊 Inserting Medications...")
        
        medications = [
            ('Metformin XR', '1000mg', 'Twice daily', 'Type 2 Diabetes', '2016-11-08', 'Dr. Jennifer Adams', True, None),
            ('Insulin Glargine', '25 units', 'Daily at bedtime', 'Type 2 Diabetes', '2020-03-15', 'Dr. Jennifer Adams', True, None),
            ('Insulin Lispro', '1:10 ratio', 'With meals', 'Type 2 Diabetes', '2020-03-15', 'Dr. Jennifer Adams', True, None),
            ('Lisinopril', '20mg', 'Daily', 'Hypertension', '2015-02-14', 'Dr. Michael Chen', True, None),
            ('Amlodipine', '10mg', 'Daily', 'Hypertension', '2018-06-20', 'Dr. Michael Chen', True, None),
            ('Atorvastatin', '40mg', 'Daily at bedtime', 'Hyperlipidemia', '2018-05-15', 'Dr. Michael Chen', True, None),
            ('Aspirin', '81mg', 'Daily', 'Cardiovascular Protection', '2018-05-15', 'Dr. Michael Chen', True, None),
            ('Levothyroxine', '88mcg', 'Daily on empty stomach', 'Hypothyroidism', '2021-07-03', 'Dr. Lisa Park', True, None),
            ('Sertraline', '50mg', 'Daily', 'Anxiety Disorder', '2020-09-12', 'Dr. Robert Kim', True, None),
            ('Losartan', '50mg', 'Daily', 'Chronic Kidney Disease', '2023-01-20', 'Dr. Elena Rodriguez', True, None),
            ('Vitamin D3', '2000 IU', 'Daily', 'Vitamin D Deficiency', '2019-11-10', 'Dr. Jennifer Adams', True, None),
            ('Calcium Carbonate', '1200mg', 'Twice daily', 'Osteoporosis Prevention', '2022-03-08', 'Dr. Jennifer Adams', True, None),
            ('Omega-3 Fish Oil', '1000mg', 'Twice daily', 'Cardiovascular Health', '2019-06-12', 'Dr. Michael Chen', True, None),
            ('Hydrochlorothiazide', '25mg', 'Daily', 'Hypertension', '2015-02-14', 'Dr. Michael Chen', False, '2023-01-20'),
        ]
        
        for name, dosage, frequency, condition, prescribed_date, prescribed_by, is_continued, discontinued_date in medications:
            disc_date = f"'{discontinued_date}'" if discontinued_date else 'NULL'
            
            # Insert medication
            query = f"""
            INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
            VALUES ({self.patient_id}, '{name}', {str(is_continued).lower()}, '{prescribed_date}', {disc_date}, '{dosage}', '{frequency}', '{prescribed_by}')
            """
            result = await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': query})
            
            # Get the medication ID and insert purpose
            med_query = f"SELECT medication_id FROM Medication WHERE patient_id = {self.patient_id} AND medicine_name = '{name}'"
            med_result = await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': med_query})
            
            if med_result.get('results'):
                med_id = med_result['results'][0]['medication_id']
                purpose_query = f"""
                INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
                VALUES ({med_id}, '{condition}', 'Prescribed for {condition} management')
                """
                await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': purpose_query})
        
        logger.info(f"✅ Inserted {len(medications)} medications with purposes")
    
    async def insert_appointments(self):
        """Insert appointment history with symptoms"""
        logger.info("📅 Inserting Appointments...")
        
        appointments = [
            ('2024-09-10', '14:30:00', 'Dr. Jennifer Adams', 'follow_up', 'completed', [
                ('Polyuria', 'Increased urination, especially at night', 'moderate', '2 weeks'),
                ('Polydipsia', 'Excessive thirst', 'moderate', '2 weeks'),
                ('Fatigue', 'Persistent tiredness despite adequate sleep', 'moderate', '3 weeks'),
                ('Blurred Vision', 'Intermittent blurring, worse in evenings', 'mild', '1 week'),
            ]),
            ('2024-08-15', '10:00:00', 'Dr. Elena Rodriguez', 'consultation', 'completed', [
                ('Ankle Swelling', 'Bilateral pedal edema, worse at end of day', 'mild', '1 month'),
                ('Proteinuria', 'Foamy urine noticed by patient', 'moderate', '2 months'),
            ]),
            ('2024-07-22', '09:15:00', 'Dr. Michael Chen', 'routine_checkup', 'completed', [
                ('Chest Tightness', 'Occasional chest tightness with exertion', 'mild', '6 weeks'),
                ('Dyspnea on Exertion', 'Shortness of breath climbing 2 flights stairs', 'mild', '2 months'),
            ]),
            ('2024-06-28', '16:00:00', 'Dr. Robert Kim', 'follow_up', 'completed', [
                ('Anxiety', 'Work-related stress and sleep disturbances', 'moderate', '1 month'),
                ('Insomnia', 'Difficulty falling asleep, early awakening', 'moderate', '3 weeks'),
            ]),
            ('2024-05-18', '11:30:00', 'Dr. Lisa Park', 'follow_up', 'completed', [
                ('Hair Loss', 'Thinning hair despite thyroid treatment', 'mild', '3 months'),
                ('Cold Intolerance', 'Feeling cold even in warm weather', 'mild', '2 months'),
            ]),
            ('2024-10-15', '14:00:00', 'Dr. Jennifer Adams', 'follow_up', 'scheduled', []),
            ('2024-11-20', '10:30:00', 'Dr. Michael Chen', 'routine_checkup', 'scheduled', []),
        ]
        
        for date, time, doctor, appt_type, status, symptoms in appointments:
            # Insert appointment
            query = f"""
            INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
            VALUES ({self.patient_id}, '{date}', '{time}', '{status}', '{appt_type}', '{doctor}')
            """
            await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': query})
            
            # Get appointment ID and insert symptoms
            appt_query = f"""
            SELECT appointment_id FROM Appointment 
            WHERE patient_id = {self.patient_id} AND appointment_date = '{date}' AND appointment_time = '{time}'
            """
            appt_result = await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': appt_query})
            
            if appt_result.get('results'):
                appt_id = appt_result['results'][0]['appointment_id']
                
                for symptom_name, description, severity, duration in symptoms:
                    symptom_query = f"""
                    INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
                    VALUES ({appt_id}, '{symptom_name}', '{description}', '{severity}', '{duration}')
                    """
                    await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': symptom_query})
        
        logger.info(f"✅ Inserted {len(appointments)} appointments with symptoms")
    
    async def insert_lab_reports(self):
        """Insert comprehensive lab reports"""
        logger.info("🧪 Inserting Lab Reports...")
        
        lab_reports = [
            ('2024-09-08', 'Comprehensive Metabolic Panel', 'Dr. Jennifer Adams', 'Central Lab', [
                ('Glucose (fasting)', '165', 'mg/dL', '70-100', True, 'high'),
                ('HbA1c', '8.2', '%', '<7.0', True, 'high'),
                ('Creatinine', '1.3', 'mg/dL', '0.6-1.1', True, 'high'),
                ('eGFR', '58', 'mL/min/1.73m²', '>60', True, 'low'),
                ('BUN', '28', 'mg/dL', '7-20', True, 'high'),
                ('Sodium', '138', 'mEq/L', '136-145', False, None),
                ('Potassium', '4.8', 'mEq/L', '3.5-5.0', False, None),
                ('Chloride', '102', 'mEq/L', '98-107', False, None),
            ]),
            ('2024-09-08', 'Lipid Panel', 'Dr. Michael Chen', 'Central Lab', [
                ('Total Cholesterol', '195', 'mg/dL', '<200', False, None),
                ('LDL Cholesterol', '88', 'mg/dL', '<100', False, None),
                ('HDL Cholesterol', '52', 'mg/dL', '>50', False, None),
                ('Triglycerides', '275', 'mg/dL', '<150', True, 'high'),
                ('Non-HDL Cholesterol', '143', 'mg/dL', '<130', True, 'high'),
            ]),
            ('2024-08-12', 'Complete Blood Count', 'Dr. Elena Rodriguez', 'Central Lab', [
                ('Hemoglobin', '11.8', 'g/dL', '12.0-15.5', True, 'low'),
                ('Hematocrit', '35.2', '%', '36.0-46.0', True, 'low'),
                ('WBC Count', '7.2', 'K/μL', '4.5-11.0', False, None),
                ('Platelet Count', '285', 'K/μL', '150-400', False, None),
                ('MCV', '78', 'fL', '80-100', True, 'low'),
                ('MCH', '26', 'pg', '27-32', True, 'low'),
            ]),
        ]
        
        for lab_date, lab_type, doctor, facility, findings in lab_reports:
            # Insert lab report
            query = f"""
            INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
            VALUES ({self.patient_id}, '{lab_date}', '{lab_type}', '{doctor}', '{facility}')
            """
            await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': query})
            
            # Get lab report ID and insert findings
            lab_query = f"""
            SELECT lab_report_id FROM Lab_Report 
            WHERE patient_id = {self.patient_id} AND lab_date = '{lab_date}' AND lab_type = '{lab_type}'
            """
            lab_result = await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': lab_query})
            
            if lab_result.get('results'):
                lab_id = lab_result['results'][0]['lab_report_id']
                
                for test_name, value, unit, range_val, abnormal, flag in findings:
                    flag_val = f"'{flag}'" if flag else 'NULL'
                    finding_query = f"""
                    INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
                    VALUES ({lab_id}, '{test_name}', '{value}', '{unit}', '{range_val}', {str(abnormal).lower()}, {flag_val})
                    """
                    await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': finding_query})
        
        logger.info(f"✅ Inserted {len(lab_reports)} lab reports with findings")
    
    async def insert_chat_history(self):
        """Insert rich chat history"""
        logger.info("💬 Inserting Chat History...")
        
        chat_messages = [
            ("Dr. Adams, I've been having increased thirst and urination again, especially at night. My glucose readings at home have been running 180-220.", 'patient', 'session_sarah_001', '2024-09-05 14:30:00'),
            ("How long have you been experiencing these symptoms? Have you made any changes to your diet or medication routine recently?", 'doctor', 'session_sarah_001', '2024-09-05 14:32:00'),
            ("About 2-3 weeks now. I've been under a lot of stress at the hospital - we've had several difficult cases. I admit I've been eating more convenience foods and my exercise has been inconsistent.", 'patient', 'session_sarah_001', '2024-09-05 14:33:00'),
            ("I understand the demands of your profession. Let's get some labs and consider adjusting your insulin regimen. We may need to increase your basal insulin and optimize your meal coverage.", 'doctor', 'session_sarah_001', '2024-09-05 14:35:00'),
            ("Dr. Rodriguez, I've noticed my ankles swelling more lately, and my urine seems foamy. I'm concerned about my kidney function given my diabetes.", 'patient', 'session_sarah_002', '2024-08-10 09:15:00'),
            ("Those are important observations. The foamy urine could indicate protein spillage. Let's check your microalbumin levels and creatinine. How's your blood pressure control been?", 'doctor', 'session_sarah_002', '2024-08-10 09:17:00'),
            ("My home readings have been averaging 135/85, which is higher than my usual 125/80. I've been taking my medications as prescribed.", 'patient', 'session_sarah_002', '2024-08-10 09:18:00'),
            ("We may need to optimize your blood pressure management. I'm going to add an ARB to provide additional kidney protection and better BP control.", 'doctor', 'session_sarah_002', '2024-08-10 09:20:00'),
        ]
        
        for message, msg_type, session, timestamp in chat_messages:
            # Escape single quotes
            escaped_message = message.replace("'", "''")
            query = f"""
            INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
            VALUES ({self.patient_id}, '{escaped_message}', '{msg_type}', '{session}', '{timestamp}')
            """
            await self.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': query})
        
        logger.info(f"✅ Inserted {len(chat_messages)} chat messages")

async def main():
    inserter = RichPatientInserter()
    
    logger.info("🏥 Inserting Rich Patient Data: Dr. Sarah Mitchell")
    logger.info("=" * 55)
    
    # Insert all data categories
    await inserter.insert_medical_history()
    await inserter.insert_medications()
    await inserter.insert_appointments()
    await inserter.insert_lab_reports()
    await inserter.insert_chat_history()
    
    logger.info("✅ Rich patient data insertion completed!")
    
    # Verify the data
    verify_query = f"""
    SELECT 
        (SELECT COUNT(*) FROM Medical_History WHERE patient_id = {inserter.patient_id}) as history_count,
        (SELECT COUNT(*) FROM Medication WHERE patient_id = {inserter.patient_id}) as medication_count,
        (SELECT COUNT(*) FROM Appointment WHERE patient_id = {inserter.patient_id}) as appointment_count,
        (SELECT COUNT(*) FROM Lab_Report WHERE patient_id = {inserter.patient_id}) as lab_report_count,
        (SELECT COUNT(*) FROM Chat_History WHERE patient_id = {inserter.patient_id}) as chat_count
    """
    
    result = await inserter.client.call_mcp_tool('mcp_hospitaldb_ExecuteQuery_MariaDB', {'query': verify_query})
    
    if result.get('results'):
        counts = result['results'][0]
        print(f"""
🎯 Data Verification Summary:
┌─────────────────────────┬──────────┐
│ Medical History Items   │    {counts['history_count']:2}    │
│ Medications             │    {counts['medication_count']:2}    │
│ Appointments            │    {counts['appointment_count']:2}    │
│ Lab Reports             │    {counts['lab_report_count']:2}    │
│ Chat Messages           │    {counts['chat_count']:2}    │
└─────────────────────────┴──────────┘

🏥 Dr. Sarah Mitchell now has comprehensive medical data 
   ready for rich knowledge graph creation!
        """)

if __name__ == "__main__":
    asyncio.run(main())