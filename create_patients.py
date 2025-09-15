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

def create_patient_1():
    """Create Patient 1 with diabetes-related data"""
    print("Creating Patient 1 (Diabetes focus)...")

    # Insert patient
    patient_query = """
    INSERT INTO Patient (name, dob, sex, created_at, updated_at)
    VALUES (?, ?, ?, NOW(), NOW())
    """
    patient_id = execute_query(patient_query, ("John Smith", date(1979, 5, 15), "Male"))
    print(f"Created Patient 1 with ID: {patient_id}")

    # Insert medical history (2 entries)
    history_entries = [
        ("chronic_condition", "Type 2 Diabetes", "Diagnosed with Type 2 Diabetes Mellitus", date(2023, 3, 10), "Moderate", 1),
        ("lifestyle", "Smoking History", "Former smoker, quit 2 years ago", date(2022, 6, 15), "Mild", 0)
    ]

    for history in history_entries:
        history_query = """
        INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, history_date, severity, is_active, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
        """
        execute_query(history_query, (patient_id, *history))

    # Insert appointments (2 entries)
    appointments = [
        (date(2024, 1, 15), "10:00:00", "Completed", "Follow_up", "Dr. Johnson", "Regular diabetes checkup"),
        (date(2024, 6, 20), "14:30:00", "Completed", "Consultation", "Dr. Johnson", "Diabetes management review")
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
        (appointment_ids[0], "Fatigue", "Persistent tiredness throughout the day", "Moderate", "2 weeks", "Gradual"),
        (appointment_ids[0], "Increased thirst", "Frequent need to drink water", "Mild", "1 week", "Gradual"),
        (appointment_ids[1], "Frequent urination", "Needing to urinate more often", "Moderate", "3 weeks", "Chronic"),
        (appointment_ids[1], "Blurred vision", "Difficulty seeing clearly at times", "Mild", "1 week", "Intermittent")
    ]

    for symptom in symptoms_data:
        symptom_query = """
        INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration, onset_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        execute_query(symptom_query, symptom)

    # Insert medications (2 entries)
    medications = [
        ("Metformin", 1, date(2023, 3, 15), None, "500mg", "Twice daily", "Dr. Johnson"),
        ("Lisinopril", 1, date(2023, 3, 15), None, "10mg", "Once daily", "Dr. Johnson")
    ]

    medication_ids = []
    for med in medications:
        med_query = """
        INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        med_id = execute_query(med_query, (patient_id, *med))
        medication_ids.append(med_id)

    # Insert medication purposes
    purposes = [
        (medication_ids[0], "Type 2 Diabetes", "Blood glucose control"),
        (medication_ids[1], "Hypertension", "Blood pressure management")
    ]

    for purpose in purposes:
        purpose_query = """
        INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
        VALUES (?, ?, ?)
        """
        execute_query(purpose_query, purpose)

    # Insert lab reports (2 entries with multiple findings each)
    lab_reports = [
        (date(2024, 1, 10), "Diabetes Panel", "Dr. Johnson", "City Lab"),
        (date(2024, 6, 15), "Comprehensive Metabolic Panel", "Dr. Johnson", "City Lab")
    ]

    lab_report_ids = []
    for lab in lab_reports:
        lab_query = """
        INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
        VALUES (?, ?, ?, ?, ?)
        """
        lab_id = execute_query(lab_query, (patient_id, *lab))
        lab_report_ids.append(lab_id)

    # Insert lab findings (multiple per report)
    findings_data = [
        # First lab report
        (lab_report_ids[0], "HbA1c", "6.2", "%", "4.0-5.6", 1, "High"),
        (lab_report_ids[0], "Blood Glucose", "140", "mg/dL", "70-99", 1, "High"),
        (lab_report_ids[0], "BMI", "28.5", "kg/m²", "18.5-24.9", 1, "High"),

        # Second lab report
        (lab_report_ids[1], "HbA1c", "6.0", "%", "4.0-5.6", 1, "High"),
        (lab_report_ids[1], "Blood Glucose", "135", "mg/dL", "70-99", 1, "High"),
        (lab_report_ids[1], "Cholesterol", "220", "mg/dL", "<200", 1, "High")
    ]

    for finding in findings_data:
        finding_query = """
        INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(finding_query, finding)

    return patient_id

def create_patient_2():
    """Create Patient 2 with cardiovascular-related data"""
    print("Creating Patient 2 (Cardiovascular focus)...")

    # Insert patient
    patient_query = """
    INSERT INTO Patient (name, dob, sex, created_at, updated_at)
    VALUES (?, ?, ?, NOW(), NOW())
    """
    patient_id = execute_query(patient_query, ("Sarah Johnson", date(1974, 8, 22), "Female"))
    print(f"Created Patient 2 with ID: {patient_id}")

    # Insert medical history (2 entries)
    history_entries = [
        ("chronic_condition", "Hypertension", "Essential hypertension diagnosed 5 years ago", date(2019, 11, 5), "Moderate", 1),
        ("lifestyle", "Smoking", "Current smoker, 1 pack per day", date(2020, 1, 1), "Moderate", 1)
    ]

    for history in history_entries:
        history_query = """
        INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, history_date, severity, is_active, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
        """
        execute_query(history_query, (patient_id, *history))

    # Insert appointments (2 entries)
    appointments = [
        (date(2024, 2, 10), "09:00:00", "Completed", "Regular", "Dr. Williams", "Cardiovascular checkup"),
        (date(2024, 7, 5), "11:15:00", "Completed", "Follow_up", "Dr. Williams", "Hypertension management")
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
        (appointment_ids[0], "Headache", "Occasional headaches, possibly related to blood pressure", "Mild", "2 days", "Intermittent"),
        (appointment_ids[0], "Dizziness", "Lightheadedness when standing up quickly", "Mild", "1 week", "Intermittent"),
        (appointment_ids[1], "Chest discomfort", "Mild chest tightness after exertion", "Moderate", "3 days", "Intermittent"),
        (appointment_ids[1], "Shortness of breath", "Difficulty breathing during physical activity", "Moderate", "1 week", "Gradual")
    ]

    for symptom in symptoms_data:
        symptom_query = """
        INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration, onset_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        execute_query(symptom_query, symptom)

    # Insert medications (2 entries)
    medications = [
        ("Amlodipine", 1, date(2019, 11, 10), None, "5mg", "Once daily", "Dr. Williams"),
        ("Atorvastatin", 1, date(2023, 1, 15), None, "20mg", "Once daily", "Dr. Williams")
    ]

    medication_ids = []
    for med in medications:
        med_query = """
        INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        med_id = execute_query(med_query, (patient_id, *med))
        medication_ids.append(med_id)

    # Insert medication purposes
    purposes = [
        (medication_ids[0], "Hypertension", "Blood pressure control"),
        (medication_ids[1], "Hypercholesterolemia", "Cholesterol management")
    ]

    for purpose in purposes:
        purpose_query = """
        INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
        VALUES (?, ?, ?)
        """
        execute_query(purpose_query, purpose)

    # Insert lab reports (2 entries with multiple findings each)
    lab_reports = [
        (date(2024, 2, 5), "Cardiovascular Risk Panel", "Dr. Williams", "Metro Lab"),
        (date(2024, 7, 1), "Lipid Profile", "Dr. Williams", "Metro Lab")
    ]

    lab_report_ids = []
    for lab in lab_reports:
        lab_query = """
        INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
        VALUES (?, ?, ?, ?, ?)
        """
        lab_id = execute_query(lab_query, (patient_id, *lab))
        lab_report_ids.append(lab_id)

    # Insert lab findings (multiple per report)
    findings_data = [
        # First lab report
        (lab_report_ids[0], "Systolic BP", "140", "mmHg", "<120", 1, "High"),
        (lab_report_ids[0], "Diastolic BP", "90", "mmHg", "<80", 1, "High"),
        (lab_report_ids[0], "Cholesterol", "240", "mg/dL", "<200", 1, "High"),
        (lab_report_ids[0], "Glucose", "95", "mg/dL", "70-99", 0, None),

        # Second lab report
        (lab_report_ids[1], "Systolic BP", "135", "mmHg", "<120", 1, "High"),
        (lab_report_ids[1], "Diastolic BP", "85", "mmHg", "<80", 1, "High"),
        (lab_report_ids[1], "HDL Cholesterol", "45", "mg/dL", ">40", 1, "High"),
        (lab_report_ids[1], "Triglycerides", "180", "mg/dL", "<150", 1, "High")
    ]

    for finding in findings_data:
        finding_query = """
        INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(finding_query, finding)

    return patient_id

def main():
    """Main function to create both patients"""
    print("Starting patient data creation...")
    print("=" * 50)

    try:
        # Create Patient 1 (Diabetes focus)
        patient_1_id = create_patient_1()
        print(f"✅ Patient 1 created successfully with ID: {patient_1_id}")
        print()

        # Create Patient 2 (Cardiovascular focus)
        patient_2_id = create_patient_2()
        print(f"✅ Patient 2 created successfully with ID: {patient_2_id}")
        print()

        print("=" * 50)
        print("🎉 All patients created successfully!")
        print(f"Patient 1 (Diabetes): ID {patient_1_id}")
        print(f"Patient 2 (Cardiovascular): ID {patient_2_id}")
        print()
        print("Each patient has:")
        print("- 2 medical history entries")
        print("- 2 appointments with 2 symptoms each (4 total symptoms)")
        print("- 2 medications with purposes")
        print("- 2 lab reports with multiple findings each")

    except Exception as e:
        print(f"❌ Error creating patients: {e}")

if __name__ == "__main__":
    main()