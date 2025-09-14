-- ============================================================================
-- MediMax Knowledge Graph Optimized Database Schema
-- ============================================================================
-- 
-- This script recreates the MediMax database with a knowledge graph-first
-- approach where every piece of information is an atomic fact that can be
-- easily mapped to graph nodes and relationships.
--
-- Author: GitHub Copilot
-- Date: September 14, 2025
-- ============================================================================

-- First, let's backup existing data (optional - uncomment if needed)
-- CREATE TABLE Patient_backup AS SELECT * FROM Patient;
-- CREATE TABLE Chat_History_backup AS SELECT * FROM Chat_History;
-- CREATE TABLE Prescription_backup AS SELECT * FROM Prescription;
-- CREATE TABLE History_backup AS SELECT * FROM History;
-- CREATE TABLE Lab_Reports_backup AS SELECT * FROM Lab_Reports;
-- CREATE TABLE Appointment_backup AS SELECT * FROM Appointment;

-- Drop existing tables (in reverse dependency order)
DROP TABLE IF EXISTS Appointment;
DROP TABLE IF EXISTS Lab_Reports;
DROP TABLE IF EXISTS History;
DROP TABLE IF EXISTS Prescription;
DROP TABLE IF EXISTS Chat_History;
DROP TABLE IF EXISTS Patient;

-- ============================================================================
-- 1. PATIENT TABLE (Central Hub Node)
-- ============================================================================
CREATE TABLE Patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    sex ENUM('Male', 'Female', 'Other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_name (name),
    INDEX idx_dob (dob)
) ENGINE=InnoDB COMMENT='Central patient node - hub for all medical information';

-- ============================================================================
-- 2. CHAT HISTORY (Atomic Messages)
-- ============================================================================
CREATE TABLE Chat_History (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    message_text TEXT NOT NULL,
    message_type ENUM('patient', 'system', 'doctor') DEFAULT 'patient',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100), -- Groups related messages
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_session (patient_id, session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_message_type (message_type)
) ENGINE=InnoDB COMMENT='Individual chat messages as atomic nodes';

-- ============================================================================
-- 3. MEDICATION (Individual Medicine Instances)
-- ============================================================================
CREATE TABLE Medication (
    medication_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    medicine_name VARCHAR(255) NOT NULL,
    is_continued BOOLEAN DEFAULT TRUE,
    prescribed_date DATE NOT NULL,
    discontinued_date DATE NULL,
    dosage VARCHAR(255),
    frequency VARCHAR(255),
    prescribed_by VARCHAR(255),
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_active (patient_id, is_continued),
    INDEX idx_medicine_name (medicine_name),
    INDEX idx_prescribed_date (prescribed_date)
) ENGINE=InnoDB COMMENT='Individual medication instances as atomic nodes';

-- ============================================================================
-- 4. MEDICATION PURPOSE (What each medicine treats)
-- ============================================================================
CREATE TABLE Medication_Purpose (
    purpose_id INT PRIMARY KEY AUTO_INCREMENT,
    medication_id INT NOT NULL,
    condition_name VARCHAR(255) NOT NULL,
    purpose_description TEXT,
    
    FOREIGN KEY (medication_id) REFERENCES Medication(medication_id) ON DELETE CASCADE,
    INDEX idx_medication (medication_id),
    INDEX idx_condition (condition_name),
    UNIQUE KEY unique_medication_condition (medication_id, condition_name)
) ENGINE=InnoDB COMMENT='Medication-condition relationships as atomic facts';

-- ============================================================================
-- 5. REPORT (Individual Report Instances)
-- ============================================================================
CREATE TABLE Report (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    report_type ENUM('lab', 'imaging', 'consultation', 'diagnostic', 'other') NOT NULL,
    report_date DATE NOT NULL,
    complete_report LONGTEXT,
    report_summary TEXT,
    doctor_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, report_date),
    INDEX idx_type (report_type),
    INDEX idx_doctor (doctor_name)
) ENGINE=InnoDB COMMENT='Individual medical reports as atomic nodes';

-- ============================================================================
-- 6. REPORT FINDING (Individual Key Findings)
-- ============================================================================
CREATE TABLE Report_Finding (
    finding_id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    finding_key VARCHAR(255) NOT NULL, -- e.g., "blood_pressure", "hemoglobin"
    finding_value VARCHAR(500) NOT NULL, -- e.g., "120/80", "12.5 g/dL"
    finding_unit VARCHAR(50), -- e.g., "mmHg", "g/dL"
    normal_range VARCHAR(100), -- e.g., "90-120/60-80"
    is_abnormal BOOLEAN DEFAULT FALSE,
    abnormal_severity ENUM('mild', 'moderate', 'severe', 'critical') NULL,
    
    FOREIGN KEY (report_id) REFERENCES Report(report_id) ON DELETE CASCADE,
    INDEX idx_report (report_id),
    INDEX idx_finding_key (finding_key),
    INDEX idx_abnormal (is_abnormal),
    INDEX idx_severity (abnormal_severity)
) ENGINE=InnoDB COMMENT='Individual report findings as atomic facts';

-- ============================================================================
-- 7. MEDICAL HISTORY (Individual History Items)
-- ============================================================================
CREATE TABLE Medical_History (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    history_type ENUM('allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other') NOT NULL,
    history_item VARCHAR(500) NOT NULL, -- e.g., "Penicillin allergy", "Appendectomy 2020"
    history_details TEXT,
    history_date DATE, -- When the condition/event occurred
    severity ENUM('mild', 'moderate', 'severe') NULL,
    is_active BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_type (patient_id, history_type),
    INDEX idx_active (is_active),
    INDEX idx_history_item (history_item),
    INDEX idx_history_date (history_date)
) ENGINE=InnoDB COMMENT='Individual medical history items as atomic nodes';

-- ============================================================================
-- 8. LAB REPORT (Individual Lab Sessions)
-- ============================================================================
CREATE TABLE Lab_Report (
    lab_report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    lab_date DATE NOT NULL,
    lab_type VARCHAR(255), -- e.g., "Blood Panel", "Urine Analysis"
    ordering_doctor VARCHAR(255),
    lab_facility VARCHAR(255),
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, lab_date),
    INDEX idx_type (lab_type),
    INDEX idx_doctor (ordering_doctor)
) ENGINE=InnoDB COMMENT='Individual lab sessions as atomic nodes';

-- ============================================================================
-- 9. LAB FINDING (Individual Test Results)
-- ============================================================================
CREATE TABLE Lab_Finding (
    lab_finding_id INT PRIMARY KEY AUTO_INCREMENT,
    lab_report_id INT NOT NULL,
    test_name VARCHAR(255) NOT NULL, -- e.g., "Hemoglobin", "Glucose"
    test_value VARCHAR(255) NOT NULL, -- e.g., "12.5", "95"
    test_unit VARCHAR(50), -- e.g., "g/dL", "mg/dL"
    reference_range VARCHAR(100), -- e.g., "12.0-15.5"
    is_abnormal BOOLEAN DEFAULT FALSE,
    abnormal_flag ENUM('high', 'low', 'critical') NULL,
    
    FOREIGN KEY (lab_report_id) REFERENCES Lab_Report(lab_report_id) ON DELETE CASCADE,
    INDEX idx_lab_report (lab_report_id),
    INDEX idx_test_name (test_name),
    INDEX idx_abnormal (is_abnormal),
    INDEX idx_test_value (test_value)
) ENGINE=InnoDB COMMENT='Individual lab test results as atomic facts';

-- ============================================================================
-- 10. APPOINTMENT (Individual Appointment Instances)
-- ============================================================================
CREATE TABLE Appointment (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME,
    status ENUM('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    appointment_type ENUM('consultation', 'follow_up', 'emergency', 'routine_checkup') DEFAULT 'consultation',
    doctor_name VARCHAR(255),
    notes TEXT,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_patient_date (patient_id, appointment_date),
    INDEX idx_status (status),
    INDEX idx_type (appointment_type),
    INDEX idx_doctor (doctor_name)
) ENGINE=InnoDB COMMENT='Individual appointments as atomic nodes';

-- ============================================================================
-- 11. APPOINTMENT SYMPTOM (Individual Symptoms per Appointment)
-- ============================================================================
CREATE TABLE Appointment_Symptom (
    symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT NOT NULL,
    symptom_name VARCHAR(255) NOT NULL, -- e.g., "headache", "fever"
    symptom_description TEXT,
    severity ENUM('mild', 'moderate', 'severe') DEFAULT 'mild',
    duration VARCHAR(100), -- e.g., "2 days", "1 week"
    onset_type ENUM('sudden', 'gradual') DEFAULT 'gradual',
    
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    INDEX idx_appointment (appointment_id),
    INDEX idx_symptom_name (symptom_name),
    INDEX idx_severity (severity)
) ENGINE=InnoDB COMMENT='Individual symptoms per appointment as atomic nodes';

-- ============================================================================
-- SAMPLE DATA INSERTION (Knowledge Graph Friendly)
-- ============================================================================

-- Insert sample patients
INSERT INTO Patient (name, dob, sex) VALUES 
('John Doe', '1985-03-15', 'Male'),
('Jane Smith', '1990-07-22', 'Female'),
('Robert Johnson', '1978-11-05', 'Male'),
('Emily Davis', '1992-02-14', 'Female'),
('Michael Wilson', '1980-05-12', 'Male');

-- Insert sample medications with atomic facts
INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, dosage, frequency, prescribed_by) VALUES
(1, 'Aspirin', true, '2024-01-15', '81mg', 'Daily', 'Dr. Smith'),
(1, 'Multivitamin', true, '2024-01-15', '1 tablet', 'Daily', 'Dr. Smith'),
(2, 'Lisinopril', true, '2024-02-01', '10mg', 'Daily', 'Dr. Johnson'),
(2, 'Metformin', true, '2024-02-01', '500mg', 'Twice daily', 'Dr. Johnson'),
(3, 'Metformin', true, '2024-01-20', '1000mg', 'Twice daily', 'Dr. Wilson'),
(3, 'Insulin', true, '2024-01-20', '20 units', 'Before meals', 'Dr. Wilson'),
(5, 'Metoprolol', true, '2024-03-01', '50mg', 'Twice daily', 'Dr. Brown'),
(5, 'Atorvastatin', true, '2024-03-01', '20mg', 'Daily', 'Dr. Brown');

-- Insert medication purposes (what each medicine treats)
INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description) VALUES
(1, 'Cardiovascular Protection', 'Low-dose aspirin for heart disease prevention'),
(2, 'Nutritional Support', 'Daily vitamin supplementation'),
(3, 'Hypertension', 'Blood pressure control'),
(4, 'Type 2 Diabetes', 'Blood glucose control'),
(5, 'Type 2 Diabetes', 'Blood glucose control'),
(6, 'Type 2 Diabetes', 'Insulin therapy for glucose management'),
(7, 'Hypertension', 'Beta-blocker for blood pressure control'),
(8, 'High Cholesterol', 'Statin therapy for cholesterol management');

-- Insert medical history as atomic facts
INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active) VALUES
(1, 'allergy', 'Penicillin allergy', 'Mild skin rash reaction', 'mild', true),
(2, 'condition', 'Hypertension', 'Diagnosed 2023, well controlled', 'moderate', true),
(3, 'allergy', 'Sulfa drug allergy', 'Severe allergic reaction', 'severe', true),
(3, 'condition', 'Type 2 Diabetes', 'Diagnosed 2022', 'moderate', true),
(4, 'condition', 'Pregnancy', 'Currently pregnant, second trimester', 'mild', true),
(5, 'allergy', 'Aspirin allergy', 'GI intolerance', 'mild', true),
(5, 'condition', 'Coronary Artery Disease', 'Stable CAD, managed with medications', 'moderate', true);

-- Insert appointments
INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name) VALUES
(1, '2024-09-15', '10:00:00', 'completed', 'routine_checkup', 'Dr. Smith'),
(1, '2024-08-01', '14:30:00', 'completed', 'consultation', 'Dr. Smith'),
(2, '2024-09-20', '09:15:00', 'scheduled', 'follow_up', 'Dr. Johnson'),
(2, '2024-08-15', '11:00:00', 'completed', 'consultation', 'Dr. Johnson'),
(3, '2024-09-25', '15:30:00', 'confirmed', 'follow_up', 'Dr. Wilson'),
(3, '2024-08-20', '10:45:00', 'completed', 'consultation', 'Dr. Wilson'),
(4, '2024-09-30', '13:00:00', 'scheduled', 'routine_checkup', 'Dr. Martinez'),
(4, '2024-08-25', '16:15:00', 'completed', 'consultation', 'Dr. Martinez'),
(5, '2024-10-01', '08:30:00', 'confirmed', 'follow_up', 'Dr. Brown'),
(5, '2024-08-30', '12:00:00', 'completed', 'consultation', 'Dr. Brown');

-- Insert symptoms as atomic facts
INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration) VALUES
(1, 'Fatigue', 'Mild fatigue, general tiredness', 'mild', '1 week'),
(1, 'Routine Checkup', 'Annual physical examination', 'mild', 'N/A'),
(3, 'Dizziness', 'Occasional dizziness episodes', 'moderate', '3 days'),
(3, 'High Blood Pressure', 'Elevated BP readings at home', 'moderate', '1 week'),
(4, 'Hypertension', 'Blood pressure monitoring', 'moderate', 'Ongoing'),
(5, 'Pain', 'General discomfort', 'moderate', '2 days'),
(5, 'Diabetes', 'Blood sugar management', 'moderate', 'Ongoing'),
(7, 'Nausea', 'Morning sickness symptoms', 'mild', '2 weeks'),
(8, 'Pregnancy Monitoring', 'Routine prenatal checkup', 'mild', 'N/A'),
(9, 'Chest Pain', 'Mild chest discomfort', 'moderate', '1 day'),
(9, 'Cardiac', 'Cardiac evaluation', 'moderate', 'Ongoing'),
(10, 'Shortness of Breath', 'Mild dyspnea on exertion', 'mild', '3 days');

-- Insert lab reports
INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility) VALUES
(1, '2024-09-01', 'Comprehensive Metabolic Panel', 'Dr. Smith', 'City Lab'),
(1, '2024-08-15', 'Lipid Panel', 'Dr. Smith', 'City Lab'),
(2, '2024-08-15', 'Basic Metabolic Panel', 'Dr. Johnson', 'Regional Lab'),
(2, '2024-08-10', 'HbA1c', 'Dr. Johnson', 'Regional Lab'),
(3, '2024-08-20', 'Glucose Tolerance Test', 'Dr. Wilson', 'Diabetes Center'),
(3, '2024-08-05', 'Kidney Function Panel', 'Dr. Wilson', 'Regional Lab'),
(4, '2024-08-25', 'Prenatal Panel', 'Dr. Martinez', 'Women\'s Health Lab'),
(4, '2024-08-15', 'Ultrasound', 'Dr. Martinez', 'Imaging Center'),
(5, '2024-08-30', 'Cardiac Enzymes', 'Dr. Brown', 'Cardiac Lab'),
(5, '2024-08-20', 'Lipid Panel', 'Dr. Brown', 'City Lab');

-- Insert lab findings as atomic facts
INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag) VALUES
-- Patient 1 lab results
(1, 'Glucose', '95', 'mg/dL', '70-100', false, NULL),
(1, 'Creatinine', '1.0', 'mg/dL', '0.7-1.3', false, NULL),
(1, 'Sodium', '140', 'mEq/L', '136-145', false, NULL),
(2, 'Total Cholesterol', '180', 'mg/dL', '<200', false, NULL),
(2, 'HDL', '45', 'mg/dL', '>40', false, NULL),
(2, 'LDL', '120', 'mg/dL', '<100', true, 'high'),
-- Patient 2 lab results
(3, 'Glucose', '180', 'mg/dL', '70-100', true, 'high'),
(3, 'Potassium', '4.2', 'mEq/L', '3.5-5.0', false, NULL),
(4, 'HbA1c', '8.2', '%', '<7.0', true, 'high'),
-- Patient 3 lab results
(5, 'Glucose (2hr)', '220', 'mg/dL', '<140', true, 'high'),
(5, 'Glucose (fasting)', '160', 'mg/dL', '70-100', true, 'high'),
(6, 'Creatinine', '1.8', 'mg/dL', '0.7-1.3', true, 'high'),
(6, 'BUN', '35', 'mg/dL', '7-20', true, 'high'),
-- Patient 4 lab results
(7, 'Hemoglobin', '11.5', 'g/dL', '12.0-15.5', true, 'low'),
(7, 'Iron', '60', 'μg/dL', '60-170', false, NULL),
-- Patient 5 lab results
(9, 'Troponin I', '0.02', 'ng/mL', '<0.04', false, NULL),
(9, 'CK-MB', '3.2', 'ng/mL', '<6.3', false, NULL),
(10, 'Total Cholesterol', '240', 'mg/dL', '<200', true, 'high'),
(10, 'LDL', '160', 'mg/dL', '<100', true, 'high');

-- Insert chat history
INSERT INTO Chat_History (patient_id, message_text, message_type, session_id) VALUES
(1, 'Hello, I have been feeling tired lately', 'patient', 'session_1_001'),
(1, 'When did this fatigue start?', 'doctor', 'session_1_001'),
(1, 'About a week ago', 'patient', 'session_1_001'),
(2, 'My blood pressure readings have been high at home', 'patient', 'session_2_001'),
(2, 'What are the typical readings you are getting?', 'doctor', 'session_2_001'),
(2, 'Usually around 150/90', 'patient', 'session_2_001'),
(3, 'I need help managing my diabetes', 'patient', 'session_3_001'),
(3, 'How has your blood sugar control been?', 'doctor', 'session_3_001'),
(4, 'I am experiencing morning sickness', 'patient', 'session_4_001'),
(5, 'I had some chest discomfort yesterday', 'patient', 'session_5_001');

-- ============================================================================
-- CREATE VIEWS FOR KNOWLEDGE GRAPH EXPORT
-- ============================================================================

-- View for all nodes in the knowledge graph
CREATE VIEW kg_nodes AS
SELECT 
    CONCAT('patient_', patient_id) as node_id,
    name as node_name,
    'Patient' as node_type,
    JSON_OBJECT(
        'dob', dob,
        'sex', sex,
        'created_at', created_at
    ) as properties
FROM Patient

UNION ALL

SELECT 
    CONCAT('medication_', medication_id) as node_id,
    medicine_name as node_name,
    'Medication' as node_type,
    JSON_OBJECT(
        'dosage', dosage,
        'frequency', frequency,
        'is_continued', is_continued,
        'prescribed_date', prescribed_date,
        'prescribed_by', prescribed_by
    ) as properties
FROM Medication

UNION ALL

SELECT 
    CONCAT('condition_', purpose_id) as node_id,
    condition_name as node_name,
    'MedicalCondition' as node_type,
    JSON_OBJECT(
        'description', purpose_description
    ) as properties
FROM Medication_Purpose

UNION ALL

SELECT 
    CONCAT('history_', history_id) as node_id,
    history_item as node_name,
    'MedicalHistory' as node_type,
    JSON_OBJECT(
        'history_type', history_type,
        'details', history_details,
        'date', history_date,
        'severity', severity,
        'is_active', is_active
    ) as properties
FROM Medical_History

UNION ALL

SELECT 
    CONCAT('appointment_', appointment_id) as node_id,
    CONCAT('Appointment on ', appointment_date) as node_name,
    'Appointment' as node_type,
    JSON_OBJECT(
        'date', appointment_date,
        'time', appointment_time,
        'status', status,
        'type', appointment_type,
        'doctor', doctor_name
    ) as properties
FROM Appointment

UNION ALL

SELECT 
    CONCAT('symptom_', symptom_id) as node_id,
    symptom_name as node_name,
    'Symptom' as node_type,
    JSON_OBJECT(
        'description', symptom_description,
        'severity', severity,
        'duration', duration,
        'onset_type', onset_type
    ) as properties
FROM Appointment_Symptom

UNION ALL

SELECT 
    CONCAT('lab_report_', lab_report_id) as node_id,
    CONCAT(lab_type, ' on ', lab_date) as node_name,
    'LabReport' as node_type,
    JSON_OBJECT(
        'date', lab_date,
        'type', lab_type,
        'doctor', ordering_doctor,
        'facility', lab_facility
    ) as properties
FROM Lab_Report

UNION ALL

SELECT 
    CONCAT('lab_finding_', lab_finding_id) as node_id,
    CONCAT(test_name, ': ', test_value, ' ', COALESCE(test_unit, '')) as node_name,
    'LabFinding' as node_type,
    JSON_OBJECT(
        'test_name', test_name,
        'value', test_value,
        'unit', test_unit,
        'reference_range', reference_range,
        'is_abnormal', is_abnormal,
        'abnormal_flag', abnormal_flag
    ) as properties
FROM Lab_Finding

UNION ALL

SELECT 
    CONCAT('chat_', chat_id) as node_id,
    LEFT(message_text, 50) as node_name,
    'ChatMessage' as node_type,
    JSON_OBJECT(
        'message_text', message_text,
        'message_type', message_type,
        'timestamp', timestamp,
        'session_id', session_id
    ) as properties
FROM Chat_History;

-- View for all relationships in the knowledge graph
CREATE VIEW kg_relationships AS
-- Patient -> Medication relationships
SELECT 
    CONCAT('patient_', m.patient_id) as source_node,
    CONCAT('medication_', m.medication_id) as target_node,
    'PRESCRIBED' as relationship_type,
    m.prescribed_date as relationship_date,
    JSON_OBJECT('prescribed_by', m.prescribed_by) as properties
FROM Medication m

UNION ALL

-- Medication -> MedicalCondition relationships
SELECT 
    CONCAT('medication_', mp.medication_id) as source_node,
    CONCAT('condition_', mp.purpose_id) as target_node,
    'TREATS' as relationship_type,
    NULL as relationship_date,
    JSON_OBJECT('description', mp.purpose_description) as properties
FROM Medication_Purpose mp

UNION ALL

-- Patient -> MedicalHistory relationships
SELECT 
    CONCAT('patient_', mh.patient_id) as source_node,
    CONCAT('history_', mh.history_id) as target_node,
    'HAS_HISTORY' as relationship_type,
    mh.history_date as relationship_date,
    JSON_OBJECT('is_active', mh.is_active) as properties
FROM Medical_History mh

UNION ALL

-- Patient -> Appointment relationships
SELECT 
    CONCAT('patient_', a.patient_id) as source_node,
    CONCAT('appointment_', a.appointment_id) as target_node,
    'HAS_APPOINTMENT' as relationship_type,
    a.appointment_date as relationship_date,
    JSON_OBJECT('status', a.status, 'type', a.appointment_type) as properties
FROM Appointment a

UNION ALL

-- Appointment -> Symptom relationships
SELECT 
    CONCAT('appointment_', s.appointment_id) as source_node,
    CONCAT('symptom_', s.symptom_id) as target_node,
    'REPORTED_SYMPTOM' as relationship_type,
    NULL as relationship_date,
    JSON_OBJECT('severity', s.severity, 'duration', s.duration) as properties
FROM Appointment_Symptom s

UNION ALL

-- Patient -> LabReport relationships
SELECT 
    CONCAT('patient_', lr.patient_id) as source_node,
    CONCAT('lab_report_', lr.lab_report_id) as target_node,
    'HAS_LAB_REPORT' as relationship_type,
    lr.lab_date as relationship_date,
    JSON_OBJECT('doctor', lr.ordering_doctor, 'facility', lr.lab_facility) as properties
FROM Lab_Report lr

UNION ALL

-- LabReport -> LabFinding relationships
SELECT 
    CONCAT('lab_report_', lf.lab_report_id) as source_node,
    CONCAT('lab_finding_', lf.lab_finding_id) as target_node,
    'CONTAINS_FINDING' as relationship_type,
    NULL as relationship_date,
    JSON_OBJECT('is_abnormal', lf.is_abnormal, 'abnormal_flag', lf.abnormal_flag) as properties
FROM Lab_Finding lf

UNION ALL

-- Patient -> ChatMessage relationships
SELECT 
    CONCAT('patient_', ch.patient_id) as source_node,
    CONCAT('chat_', ch.chat_id) as target_node,
    'HAS_CHAT' as relationship_type,
    DATE(ch.timestamp) as relationship_date,
    JSON_OBJECT('message_type', ch.message_type, 'session_id', ch.session_id) as properties
FROM Chat_History ch;

-- ============================================================================
-- KNOWLEDGE GRAPH EXPORT PROCEDURES
-- ============================================================================

DELIMITER //

CREATE PROCEDURE ExportKnowledgeGraphNodes()
BEGIN
    SELECT 
        node_id,
        node_name,
        node_type,
        properties
    FROM kg_nodes
    ORDER BY node_type, node_name;
END //

CREATE PROCEDURE ExportKnowledgeGraphRelationships()
BEGIN
    SELECT 
        source_node,
        target_node,
        relationship_type,
        relationship_date,
        properties
    FROM kg_relationships
    ORDER BY relationship_type, relationship_date;
END //

CREATE PROCEDURE GetPatientKnowledgeGraph(IN patient_id_param INT)
BEGIN
    -- Get all nodes connected to a specific patient
    SELECT DISTINCT n.*
    FROM kg_nodes n
    WHERE n.node_id = CONCAT('patient_', patient_id_param)
    
    UNION
    
    SELECT DISTINCT n.*
    FROM kg_nodes n
    JOIN kg_relationships r ON (n.node_id = r.target_node OR n.node_id = r.source_node)
    WHERE r.source_node = CONCAT('patient_', patient_id_param)
       OR r.target_node = CONCAT('patient_', patient_id_param);
       
    -- Get all relationships for this patient
    SELECT *
    FROM kg_relationships
    WHERE source_node = CONCAT('patient_', patient_id_param)
       OR target_node = CONCAT('patient_', patient_id_param);
END //

DELIMITER ;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Show table statistics
SELECT 
    TABLE_NAME,
    TABLE_ROWS as 'Estimated Rows'
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Show knowledge graph summary
SELECT 
    'Total Nodes' as metric,
    COUNT(*) as count
FROM kg_nodes

UNION ALL

SELECT 
    'Total Relationships' as metric,
    COUNT(*) as count
FROM kg_relationships

UNION ALL

SELECT 
    CONCAT('Nodes by Type: ', node_type) as metric,
    COUNT(*) as count
FROM kg_nodes
GROUP BY node_type

UNION ALL

SELECT 
    CONCAT('Relationships by Type: ', relationship_type) as metric,
    COUNT(*) as count
FROM kg_relationships
GROUP BY relationship_type;

-- ============================================================================
-- END OF SCHEMA CREATION
-- ============================================================================

COMMIT;

SELECT '✅ Knowledge Graph Optimized Schema Created Successfully!' as Status;