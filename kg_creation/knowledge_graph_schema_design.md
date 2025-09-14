# Knowledge Graph Optimized Database Schema Design

## Philosophy: Atomic Facts & Graph-First Design

This schema is designed from the ground up to facilitate easy knowledge graph creation where:
- Each piece of information is an atomic fact (node)
- Relationships are explicit and meaningful
- Complex data structures are decomposed into connected atomic entities
- Every entity can be easily mapped to graph nodes and relationships

## Schema Map Overview

```
PATIENT (Central Hub)
    ├── BASIC_INFO → demographics, contact
    ├── CHAT_INTERACTIONS → individual messages
    ├── MEDICATIONS → individual medicines
    │   ├── MEDICATION_DETAILS → dosage, frequency
    │   └── MEDICAL_CONDITIONS → what it treats
    ├── REPORTS → individual report instances
    │   ├── REPORT_FINDINGS → individual key findings
    │   └── REPORT_CONTENT → full report text
    ├── MEDICAL_HISTORY → individual history items
    └── LAB_REPORTS → individual lab sessions
        └── LAB_FINDINGS → individual test results
    └── APPOINTMENTS → individual appointment instances
        └── SYMPTOMS → individual symptoms per appointment
```

## Table Structures (Knowledge Graph Optimized)

### 1. Patient (Central Node)
```sql
CREATE TABLE Patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    sex ENUM('Male', 'Female', 'Other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```
**Graph Properties**: Core identity node
**Relationships**: Connected to all other entities via patient_id

### 2. Chat_History (Atomic Messages)
```sql
CREATE TABLE Chat_History (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    message_text TEXT NOT NULL,
    message_type ENUM('patient', 'system', 'doctor') DEFAULT 'patient',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100), -- Groups related messages
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    INDEX idx_patient_session (patient_id, session_id),
    INDEX idx_timestamp (timestamp)
);
```
**Graph Properties**: Each message is a node with text content
**Relationships**: 
- PATIENT --[HAS_CHAT]--> CHAT_MESSAGE
- CHAT_MESSAGE --[PART_OF_SESSION]--> CHAT_SESSION

### 3. Medication (Individual Medicine Instances)
```sql
CREATE TABLE Medication (
    medication_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    medicine_name VARCHAR(255) NOT NULL,
    is_continued BOOLEAN DEFAULT TRUE,
    prescribed_date DATE NOT NULL,
    discontinued_date DATE NULL,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    INDEX idx_patient_active (patient_id, is_continued)
);
```

### 4. Medication_Purpose (What each medicine treats)
```sql
CREATE TABLE Medication_Purpose (
    purpose_id INT PRIMARY KEY AUTO_INCREMENT,
    medication_id INT NOT NULL,
    condition_name VARCHAR(255) NOT NULL,
    purpose_description TEXT,
    
    FOREIGN KEY (medication_id) REFERENCES Medication(medication_id),
    INDEX idx_medication (medication_id),
    INDEX idx_condition (condition_name)
);
```
**Graph Properties**: Each medicine-condition pair is atomic
**Relationships**:
- PATIENT --[PRESCRIBED]--> MEDICATION
- MEDICATION --[TREATS]--> MEDICAL_CONDITION
- MEDICATION --[IS_ACTIVE/IS_DISCONTINUED]--> STATUS

### 5. Report (Individual Report Instances)
```sql
CREATE TABLE Report (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    report_type ENUM('lab', 'imaging', 'consultation', 'diagnostic', 'other') NOT NULL,
    report_date DATE NOT NULL,
    complete_report LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    INDEX idx_patient_date (patient_id, report_date),
    INDEX idx_type (report_type)
);
```

### 6. Report_Finding (Individual Key Findings)
```sql
CREATE TABLE Report_Finding (
    finding_id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    finding_key VARCHAR(255) NOT NULL, -- e.g., "blood_pressure", "hemoglobin"
    finding_value VARCHAR(500) NOT NULL, -- e.g., "120/80", "12.5 g/dL"
    finding_unit VARCHAR(50), -- e.g., "mmHg", "g/dL"
    normal_range VARCHAR(100), -- e.g., "90-120/60-80"
    is_abnormal BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (report_id) REFERENCES Report(report_id),
    INDEX idx_report (report_id),
    INDEX idx_finding_key (finding_key),
    INDEX idx_abnormal (is_abnormal)
);
```
**Graph Properties**: Each finding is an atomic fact
**Relationships**:
- PATIENT --[HAS_REPORT]--> REPORT
- REPORT --[CONTAINS_FINDING]--> FINDING
- FINDING --[HAS_VALUE]--> VALUE
- FINDING --[IS_NORMAL/IS_ABNORMAL]--> STATUS

### 7. Medical_History (Individual History Items)
```sql
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
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    INDEX idx_patient_type (patient_id, history_type),
    INDEX idx_active (is_active)
);
```
**Graph Properties**: Each history item is atomic
**Relationships**:
- PATIENT --[HAS_HISTORY]--> HISTORY_ITEM
- HISTORY_ITEM --[OF_TYPE]--> HISTORY_TYPE
- HISTORY_ITEM --[HAS_SEVERITY]--> SEVERITY_LEVEL

### 8. Lab_Report (Individual Lab Sessions)
```sql
CREATE TABLE Lab_Report (
    lab_report_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    lab_date DATE NOT NULL,
    lab_type VARCHAR(255), -- e.g., "Blood Panel", "Urine Analysis"
    ordering_doctor VARCHAR(255),
    lab_facility VARCHAR(255),
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    INDEX idx_patient_date (patient_id, lab_date),
    INDEX idx_type (lab_type)
);
```

### 9. Lab_Finding (Individual Test Results)
```sql
CREATE TABLE Lab_Finding (
    lab_finding_id INT PRIMARY KEY AUTO_INCREMENT,
    lab_report_id INT NOT NULL,
    test_name VARCHAR(255) NOT NULL, -- e.g., "Hemoglobin", "Glucose"
    test_value VARCHAR(255) NOT NULL, -- e.g., "12.5", "95"
    test_unit VARCHAR(50), -- e.g., "g/dL", "mg/dL"
    reference_range VARCHAR(100), -- e.g., "12.0-15.5"
    is_abnormal BOOLEAN DEFAULT FALSE,
    abnormal_flag ENUM('high', 'low', 'critical') NULL,
    
    FOREIGN KEY (lab_report_id) REFERENCES Lab_Report(lab_report_id),
    INDEX idx_lab_report (lab_report_id),
    INDEX idx_test_name (test_name),
    INDEX idx_abnormal (is_abnormal)
);
```
**Graph Properties**: Each lab test result is atomic
**Relationships**:
- PATIENT --[HAS_LAB_REPORT]--> LAB_REPORT
- LAB_REPORT --[CONTAINS_TEST]--> LAB_TEST
- LAB_TEST --[HAS_RESULT]--> TEST_RESULT
- TEST_RESULT --[IS_NORMAL/IS_ABNORMAL]--> STATUS

### 10. Appointment (Individual Appointment Instances)
```sql
CREATE TABLE Appointment (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME,
    status ENUM('scheduled', 'confirmed', 'completed', 'cancelled', 'no_show') DEFAULT 'scheduled',
    appointment_type ENUM('consultation', 'follow_up', 'emergency', 'routine_checkup') DEFAULT 'consultation',
    doctor_name VARCHAR(255),
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id),
    INDEX idx_patient_date (patient_id, appointment_date),
    INDEX idx_status (status)
);
```

### 11. Appointment_Symptom (Individual Symptoms per Appointment)
```sql
CREATE TABLE Appointment_Symptom (
    symptom_id INT PRIMARY KEY AUTO_INCREMENT,
    appointment_id INT NOT NULL,
    symptom_name VARCHAR(255) NOT NULL, -- e.g., "headache", "fever"
    symptom_description TEXT,
    severity ENUM('mild', 'moderate', 'severe') DEFAULT 'mild',
    duration VARCHAR(100), -- e.g., "2 days", "1 week"
    onset_type ENUM('sudden', 'gradual') DEFAULT 'gradual',
    
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id),
    INDEX idx_appointment (appointment_id),
    INDEX idx_symptom_name (symptom_name)
);
```
**Graph Properties**: Each symptom is atomic with properties
**Relationships**:
- PATIENT --[HAS_APPOINTMENT]--> APPOINTMENT
- APPOINTMENT --[REPORTED_SYMPTOM]--> SYMPTOM
- SYMPTOM --[HAS_SEVERITY]--> SEVERITY_LEVEL
- SYMPTOM --[HAS_DURATION]--> TIME_PERIOD

## Knowledge Graph Mapping Strategy

### Node Types:
1. **Patient** - Central hub node
2. **ChatMessage** - Individual chat messages
3. **Medication** - Individual medicines
4. **MedicalCondition** - Conditions treated by medications
5. **Report** - Individual reports
6. **Finding** - Individual findings from reports
7. **HistoryItem** - Individual medical history items
8. **LabReport** - Individual lab sessions
9. **LabTest** - Individual lab test results
10. **Appointment** - Individual appointments
11. **Symptom** - Individual symptoms

### Relationship Types:
- `HAS_CHAT`, `PRESCRIBED`, `HAS_REPORT`, `HAS_HISTORY`, `HAS_LAB_REPORT`, `HAS_APPOINTMENT`
- `TREATS`, `CONTAINS_FINDING`, `CONTAINS_TEST`, `REPORTED_SYMPTOM`
- `IS_ACTIVE`, `IS_ABNORMAL`, `HAS_SEVERITY`, `HAS_VALUE`
- `PART_OF_SESSION`, `OF_TYPE`, `OCCURRED_ON`

### Advantages for Knowledge Graph:
1. **Atomic Facts**: Each record represents one fact
2. **Easy Relationships**: Direct foreign keys map to graph edges
3. **Semantic Clarity**: Relationship names are meaningful
4. **Temporal Data**: Dates allow time-based graph queries
5. **Flexible Queries**: Can trace complex medical relationships
6. **Scalable**: New entity types can be added without schema changes

This design ensures that every piece of medical information becomes a node in the knowledge graph, connected through meaningful relationships, making complex medical queries and AI analysis much more effective.