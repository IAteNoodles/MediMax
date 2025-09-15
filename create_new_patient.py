import mariadb
import os
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
import random

# Load environment variables
load_dotenv()

# Database configuration
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3305))

def get_db_connection():
    """Establish database connection"""
    return mariadb.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT
    )

def execute_query(query, params=None):
    """Execute a database query"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if query.strip().upper().startswith('INSERT'):
            conn.commit()
            return cursor.lastrowid  # Return the last inserted ID
        elif query.strip().upper().startswith(('UPDATE', 'DELETE')):
            conn.commit()
            return cursor.rowcount
        else:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]

    except mariadb.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def create_new_patient():
    """Create new patient with comprehensive medical data"""
    print("Creating new patient with diabetes/cardiovascular risk factors...")

    # Insert patient
    patient_query = """
    INSERT INTO Patient (name, dob, sex, created_at, updated_at)
    VALUES (?, ?, ?, NOW(), NOW())
    """
    patient_id = execute_query(patient_query, ("John Anderson", date(1980, 9, 15), "Male"))
    print(f"Created Patient with ID: {patient_id}")

    # Insert medical history (2 entries)
    history_entries = [
        ("chronic_condition", "Hypertension", "Diagnosed with essential hypertension", date(2023, 1, 10), "Moderate", 1),
        ("lifestyle", "Smoking History", "Former smoker, quit 3 years ago", date(2022, 3, 20), "Mild", 0)
    ]

    for history in history_entries:
        history_query = """
        INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, history_date, severity, is_active, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
        """
        execute_query(history_query, (patient_id, *history))

    # Insert appointments (2 entries)
    appointments = [
        (date(2024, 3, 15), "09:00:00", "Completed", "Annual_checkup", "Dr. Martinez", "Comprehensive health assessment"),
        (date(2024, 9, 10), "11:30:00", "Completed", "Follow_up", "Dr. Martinez", "Diabetes and hypertension monitoring")
    ]

    appointment_ids = []
    for appt in appointments:
        appt_query = """
        INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        appt_id = execute_query(appt_query, (patient_id, *appt))
        appointment_ids.append(appt_id)

    # Insert symptoms for appointments (2 entries per appointment)
    symptoms_data = [
        (appointment_ids[0], "Fatigue", "General tiredness and low energy", "Moderate", "3 weeks", "Gradual"),
        (appointment_ids[0], "Headache", "Occasional headaches, possibly related to blood pressure", "Mild", "1 week", "Intermittent"),
        (appointment_ids[1], "Increased thirst", "Frequent need to drink water", "Moderate", "2 weeks", "Gradual"),
        (appointment_ids[1], "Frequent urination", "Needing to urinate more often than usual", "Mild", "1 week", "Chronic")
    ]

    for symptom in symptoms_data:
        symptom_query = """
        INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration, onset_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        execute_query(symptom_query, symptom)

    # Insert medications (2 entries)
    medications = [
        ("Lisinopril", 1, date(2023, 1, 15), None, "10mg", "Once daily", "Dr. Martinez"),
        ("Metformin", 1, date(2023, 6, 20), None, "500mg", "Twice daily", "Dr. Martinez")
    ]

    medication_ids = []
    for med in medications:
        med_query = """
        INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        med_id = execute_query(med_query, (patient_id, *med))
        medication_ids.append(med_id)

    # Insert medication purposes (2 entries)
    purposes = [
        (medication_ids[0], "Hypertension", "Blood pressure control"),
        (medication_ids[1], "Diabetes Risk", "Blood glucose management and prevention")
    ]

    for purpose in purposes:
        purpose_query = """
        INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
        VALUES (?, ?, ?)
        """
        execute_query(purpose_query, purpose)

    # Insert lab reports (2 entries with multiple findings each)
    lab_reports = [
        (date(2024, 3, 10), "Comprehensive Metabolic Panel", "Dr. Martinez", "City Lab"),
        (date(2024, 9, 5), "Diabetes & Lipid Panel", "Dr. Martinez", "City Lab")
    ]

    lab_report_ids = []
    for lab in lab_reports:
        lab_query = """
        INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
        VALUES (?, ?, ?, ?, ?)
        """
        lab_id = execute_query(lab_query, (patient_id, *lab))
        lab_report_ids.append(lab_id)

    # Insert lab findings for first report (2 entries)
    lab_findings_1 = [
        (lab_report_ids[0], "Glucose", "140", "mg/dL", "70-100", "High", "Fasting glucose elevated"),
        (lab_report_ids[0], "HbA1c", "6.2", "%", "4.0-5.6", "High", "Prediabetic range")
    ]

    for finding in lab_findings_1:
        finding_query = """
        INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, unit, reference_range, result_status, clinical_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(finding_query, finding)

    # Insert lab findings for second report (2 entries)
    lab_findings_2 = [
        (lab_report_ids[1], "Total Cholesterol", "220", "mg/dL", "<200", "High", "Borderline high"),
        (lab_report_ids[1], "HDL Cholesterol", "35", "mg/dL", ">40", "Low", "Below optimal range")
    ]

    for finding in lab_findings_2:
        finding_query = """
        INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, unit, reference_range, result_status, clinical_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(finding_query, finding)

    print(f"Successfully created comprehensive patient record for John Anderson (ID: {patient_id})")
    return patient_id

if __name__ == "__main__":
    create_new_patient()