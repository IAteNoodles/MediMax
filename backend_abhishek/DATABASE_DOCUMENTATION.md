# MediMax Database Documentation

## Table of Contents
1. [Database Overview](#database-overview)
2. [Connection Management](#connection-management)
3. [Schema Design](#schema-design)
4. [Table Specifications](#table-specifications)
5. [Relationship Mappings](#relationship-mappings)
6. [Enum Values & Constraints](#enum-values--constraints)
7. [Data Validation](#data-validation)
8. [Performance Considerations](#performance-considerations)
9. [Backup & Recovery](#backup--recovery)

---

## Database Overview

The MediMax system uses **MariaDB/MySQL** as its primary database management system, designed to handle comprehensive healthcare data with strict validation, referential integrity, and optimized performance for medical record management.

### Database Configuration
```python
# Environment Variables (.env file)
DB_HOST=your_database_host          # Database server hostname/IP
DB_PORT=3306                        # Database port (default MySQL/MariaDB)
DB_NAME=medimax                     # Database name
DB_USER=your_username               # Database username
DB_PASSWORD=your_password           # Database password
```

### Key Features
- **ACID Compliance**: Full transaction support for data integrity
- **Referential Integrity**: Foreign key constraints ensure data consistency
- **Enum Validation**: Strict enumeration values for standardized data
- **Timestamp Tracking**: Automatic creation and update timestamps
- **Indexing Strategy**: Optimized indexes for common query patterns
- **Unicode Support**: Full UTF-8 support for international patient names

---

## Connection Management

### Connection Function Implementation
```python
def get_db_connection():
    """
    Establishes and returns a database connection with proper error handling.
    
    Returns:
        pymysql.Connection: Database connection object with cursor factory
        
    Raises:
        HTTPException: 500 status with connection error details
    """
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',                    # Full Unicode support
            cursorclass=pymysql.cursors.DictCursor,  # Return results as dictionaries
            autocommit=False,                     # Manual transaction control
            connect_timeout=10,                   # 10-second connection timeout
            read_timeout=30,                      # 30-second read timeout
            write_timeout=30                      # 30-second write timeout
        )
        return connection
    except pymysql.Error as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Database connection failed: {str(e)}"
        )
```

### Connection Lifecycle Management
```python
# Proper connection handling pattern
def example_endpoint(db=Depends(get_db_connection)):
    try:
        cursor = db.cursor()
        
        # Perform database operations
        cursor.execute("SELECT * FROM Patient WHERE patient_id = %s", (patient_id,))
        result = cursor.fetchone()
        
        # Commit changes for write operations
        db.commit()
        cursor.close()
        
        return result
        
    except Exception as e:
        # Rollback on error
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Always close connection
        if db:
            db.close()
```

### Connection Pool Configuration
```python
# For production environments, consider connection pooling
import pymysql.pooling

connection_pool = pymysql.pooling.Pool(
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    max_connections=20,        # Maximum pool size
    min_connections=5,         # Minimum pool size
    blocking=True,             # Block when pool is exhausted
    reset_session=True         # Reset session variables on return
)
```

---

## Schema Design

### Design Principles
1. **Normalization**: Database follows 3NF to minimize redundancy
2. **Patient-Centric**: All medical data links to the Patient table
3. **Extensibility**: Schema supports future medical data types
4. **Audit Trail**: Timestamp fields track data creation/modification
5. **Data Integrity**: Foreign keys and constraints ensure consistency

### Entity Relationship Diagram
```
Patient (1) ──────────────┐
│                         │
├─── (1:N) Medical_History │
├─── (1:N) Medication     │
├─── (1:N) Appointment    │
├─── (1:N) Lab_Report     │
└─── (1:N) Report         │
                          │
Appointment (1) ──────────┼─── (1:N) Appointment_Symptom
                          │
Lab_Report (1) ───────────┼─── (1:N) Lab_Finding
                          │
Medication (1) ───────────└─── (1:N) Medication_Purpose
```

---

## Table Specifications

### Patient Table
**Purpose**: Core patient demographic and identification information

```sql
CREATE TABLE Patient (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    sex ENUM('Male', 'Female', 'Other') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_patient_name (name),
    INDEX idx_patient_dob (dob),
    INDEX idx_patient_sex (sex)
);
```

**Field Specifications**:
- `patient_id`: **INT AUTO_INCREMENT PRIMARY KEY** - Unique patient identifier
- `name`: **VARCHAR(255) NOT NULL** - Full legal name of patient
- `dob`: **DATE** - Date of birth (YYYY-MM-DD format)
- `sex`: **ENUM('Male', 'Female', 'Other') NOT NULL** - Gender identification
- `created_at`: **TIMESTAMP DEFAULT CURRENT_TIMESTAMP** - Record creation time
- `updated_at`: **TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP** - Last modification time

**Validation Rules**:
- Name must be non-empty string, max 255 characters
- DOB must be valid date, can be NULL
- Sex must be one of the three enum values
- Automatic timestamp management

### Medical_History Table
**Purpose**: Patient medical history including conditions, allergies, surgeries, and family history

```sql
CREATE TABLE Medical_History (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    history_type ENUM('allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other') NOT NULL,
    history_item VARCHAR(255) NOT NULL,
    history_details TEXT,
    history_date DATE,
    severity ENUM('mild', 'moderate', 'severe', 'critical') DEFAULT 'mild',
    is_active TINYINT(1) DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_history_patient (patient_id),
    INDEX idx_history_type (history_type),
    INDEX idx_history_active (is_active),
    INDEX idx_history_date (history_date)
);
```

**Field Specifications**:
- `history_id`: **INT AUTO_INCREMENT PRIMARY KEY** - Unique history record identifier
- `patient_id`: **INT NOT NULL** - Foreign key to Patient table
- `history_type`: **ENUM** - Type of medical history (see enum values below)
- `history_item`: **VARCHAR(255) NOT NULL** - Name/title of the medical history item
- `history_details`: **TEXT** - Detailed description (optional)
- `history_date`: **DATE** - When the medical event occurred
- `severity`: **ENUM** - Severity level (mild, moderate, severe, critical)
- `is_active`: **TINYINT(1) DEFAULT 1** - Whether condition is currently active
- `updated_at`: **TIMESTAMP** - Last modification timestamp

**Enum Values**:
- `history_type`: 'allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other'
- `severity`: 'mild', 'moderate', 'severe', 'critical'

### Appointment Table
**Purpose**: Scheduled patient appointments with healthcare providers

```sql
CREATE TABLE Appointment (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME,
    status ENUM('Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show') DEFAULT 'Scheduled',
    appointment_type ENUM('consultation', 'follow_up', 'emergency', 'routine_checkup') DEFAULT 'routine_checkup',
    doctor_name VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_appointment_patient (patient_id),
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_appointment_status (status),
    INDEX idx_appointment_type (appointment_type),
    INDEX idx_appointment_doctor (doctor_name)
);
```

**Field Specifications**:
- `appointment_id`: **INT AUTO_INCREMENT PRIMARY KEY** - Unique appointment identifier
- `patient_id`: **INT NOT NULL** - Foreign key to Patient table
- `appointment_date`: **DATE NOT NULL** - Date of appointment
- `appointment_time`: **TIME** - Time of appointment (optional)
- `status`: **ENUM** - Current appointment status
- `appointment_type`: **ENUM** - Type of appointment
- `doctor_name`: **VARCHAR(255)** - Name of attending physician
- `notes`: **TEXT** - Additional appointment notes
- `created_at`: **TIMESTAMP** - Record creation timestamp
- `updated_at`: **TIMESTAMP** - Last modification timestamp

### Appointment_Symptom Table
**Purpose**: Symptoms reported during specific appointments

```sql
CREATE TABLE Appointment_Symptom (
    symptom_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    symptom_name VARCHAR(255) NOT NULL,
    symptom_description TEXT,
    severity ENUM('mild', 'moderate', 'severe', 'critical') DEFAULT 'mild',
    duration VARCHAR(100),
    onset_type ENUM('sudden', 'gradual', 'chronic', 'intermittent') DEFAULT 'gradual',
    
    FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE,
    INDEX idx_symptom_appointment (appointment_id),
    INDEX idx_symptom_name (symptom_name),
    INDEX idx_symptom_severity (severity)
);
```

### Medication Table
**Purpose**: Current and historical patient medications

```sql
CREATE TABLE Medication (
    medication_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    medicine_name VARCHAR(255) NOT NULL,
    is_continued TINYINT(1) DEFAULT 1,
    prescribed_date DATE NOT NULL,
    discontinued_date DATE,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    prescribed_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_medication_patient (patient_id),
    INDEX idx_medication_name (medicine_name),
    INDEX idx_medication_continued (is_continued),
    INDEX idx_medication_prescribed_date (prescribed_date)
);
```

### Medication_Purpose Table
**Purpose**: Link medications to specific conditions or purposes

```sql
CREATE TABLE Medication_Purpose (
    purpose_id INT AUTO_INCREMENT PRIMARY KEY,
    medication_id INT NOT NULL,
    condition_name VARCHAR(255),
    purpose_description TEXT,
    
    FOREIGN KEY (medication_id) REFERENCES Medication(medication_id) ON DELETE CASCADE,
    INDEX idx_purpose_medication (medication_id),
    INDEX idx_purpose_condition (condition_name)
);
```

### Lab_Report Table
**Purpose**: Laboratory test reports and orders

```sql
CREATE TABLE Lab_Report (
    lab_report_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    lab_date DATE NOT NULL,
    lab_type VARCHAR(255) NOT NULL,
    ordering_doctor VARCHAR(255),
    lab_facility VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_lab_patient (patient_id),
    INDEX idx_lab_date (lab_date),
    INDEX idx_lab_type (lab_type),
    INDEX idx_lab_doctor (ordering_doctor)
);
```

### Lab_Finding Table
**Purpose**: Individual test results within lab reports

```sql
CREATE TABLE Lab_Finding (
    lab_finding_id INT AUTO_INCREMENT PRIMARY KEY,
    lab_report_id INT NOT NULL,
    test_name VARCHAR(255) NOT NULL,
    test_value VARCHAR(255) NOT NULL,
    test_unit VARCHAR(50),
    reference_range VARCHAR(100),
    is_abnormal TINYINT(1) DEFAULT 0,
    abnormal_flag ENUM('high', 'low', 'critical_high', 'critical_low'),
    
    FOREIGN KEY (lab_report_id) REFERENCES Lab_Report(lab_report_id) ON DELETE CASCADE,
    INDEX idx_finding_report (lab_report_id),
    INDEX idx_finding_test (test_name),
    INDEX idx_finding_abnormal (is_abnormal)
);
```

### Report Table
**Purpose**: General medical reports (radiology, pathology, etc.)

```sql
CREATE TABLE Report (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    report_type VARCHAR(100) NOT NULL,
    report_date DATE NOT NULL,
    complete_report TEXT,
    report_summary TEXT,
    doctor_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES Patient(patient_id) ON DELETE CASCADE,
    INDEX idx_report_patient (patient_id),
    INDEX idx_report_type (report_type),
    INDEX idx_report_date (report_date)
);
```

---

## Relationship Mappings

### Foreign Key Relationships
```sql
-- All medical data tied to patients
Medical_History.patient_id → Patient.patient_id
Appointment.patient_id → Patient.patient_id
Medication.patient_id → Patient.patient_id
Lab_Report.patient_id → Patient.patient_id
Report.patient_id → Patient.patient_id

-- Symptoms tied to appointments
Appointment_Symptom.appointment_id → Appointment.appointment_id

-- Lab findings tied to reports
Lab_Finding.lab_report_id → Lab_Report.lab_report_id

-- Medication purposes tied to medications
Medication_Purpose.medication_id → Medication.medication_id
```

### Cascade Behavior
- **ON DELETE CASCADE**: When a patient is deleted, all related records are automatically removed
- **ON UPDATE CASCADE**: Foreign key values update automatically when primary keys change

### Data Integrity Constraints
```sql
-- Ensure appointment dates are not in the past (for new appointments)
ALTER TABLE Appointment ADD CONSTRAINT chk_future_date 
CHECK (appointment_date >= CURDATE() OR status IN ('Completed', 'Cancelled', 'No_Show'));

-- Ensure discontinued medications have discontinued dates
ALTER TABLE Medication ADD CONSTRAINT chk_discontinued_date 
CHECK (is_continued = 1 OR discontinued_date IS NOT NULL);

-- Ensure abnormal labs have abnormal flags
ALTER TABLE Lab_Finding ADD CONSTRAINT chk_abnormal_flag 
CHECK (is_abnormal = 0 OR abnormal_flag IS NOT NULL);
```

---

## Enum Values & Constraints

### API-to-Database Enum Mappings

#### History Type Mapping
```python
HISTORY_TYPE_MAPPING = {
    # API Input → Database Value
    'chronic_condition': 'condition',    # Legacy mapping
    'allergy': 'allergy',
    'surgery': 'surgery', 
    'family_history': 'family_history',
    'condition': 'condition',
    'lifestyle': 'lifestyle',
    'other': 'other'
}

# Database ENUM Values
DATABASE_HISTORY_TYPES = ['allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other']
```

#### Appointment Type Mapping
```python
APPOINTMENT_TYPE_MAPPING = {
    # API Input → Database Value
    'Regular': 'routine_checkup',
    'Emergency': 'emergency',
    'Follow_up': 'follow_up', 
    'Consultation': 'consultation',
    'Surgery': 'consultation'    # Surgery mapped to consultation
}

# Database ENUM Values
DATABASE_APPOINTMENT_TYPES = ['consultation', 'follow_up', 'emergency', 'routine_checkup']
```

#### Severity Levels
```python
# Consistent across all tables
SEVERITY_LEVELS = ['mild', 'moderate', 'severe', 'critical']

# Usage in Medical_History, Appointment_Symptom tables
```

#### Appointment Status Values
```python
# No mapping needed - direct usage
APPOINTMENT_STATUSES = ['Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show']
```

#### Symptom Onset Types
```python
# Direct usage in Appointment_Symptom table
ONSET_TYPES = ['sudden', 'gradual', 'chronic', 'intermittent']
```

#### Lab Finding Flags
```python
# Abnormal lab result indicators
ABNORMAL_FLAGS = ['high', 'low', 'critical_high', 'critical_low']
```

### Validation Functions
```python
def validate_history_type(input_type):
    """Convert API input to database-compatible history type."""
    mapping = {
        'chronic_condition': 'condition',
        'allergy': 'allergy',
        'surgery': 'surgery',
        'family_history': 'family_history', 
        'condition': 'condition',
        'lifestyle': 'lifestyle',
        'other': 'other'
    }
    
    mapped_type = mapping.get(input_type, input_type.lower())
    valid_types = ['allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other']
    
    if mapped_type not in valid_types:
        raise ValueError(f"Invalid history type. Must be one of: {valid_types}")
    
    return mapped_type

def validate_appointment_type(input_type):
    """Convert API input to database-compatible appointment type."""
    mapping = {
        'Regular': 'routine_checkup',
        'Emergency': 'emergency',
        'Follow_up': 'follow_up',
        'Consultation': 'consultation', 
        'Surgery': 'consultation'
    }
    
    mapped_type = mapping.get(input_type, input_type.lower())
    valid_types = ['consultation', 'follow_up', 'emergency', 'routine_checkup']
    
    if mapped_type not in valid_types:
        raise ValueError(f"Invalid appointment type. Must be one of: {valid_types}")
    
    return mapped_type
```

---

## Data Validation

### Input Validation Rules

#### Patient Data
```python
def validate_patient_data(data):
    """Comprehensive patient data validation."""
    
    # Name validation
    if not data.get('name') or len(data['name'].strip()) == 0:
        raise ValueError("Patient name is required and cannot be empty")
    
    if len(data['name']) > 255:
        raise ValueError("Patient name cannot exceed 255 characters")
    
    # Date of birth validation
    if data.get('dob'):
        try:
            dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
            if dob > date.today():
                raise ValueError("Date of birth cannot be in the future")
            if dob < date(1900, 1, 1):
                raise ValueError("Date of birth cannot be before 1900")
        except ValueError as e:
            raise ValueError(f"Invalid date format for DOB. Use YYYY-MM-DD: {str(e)}")
    
    # Sex validation
    valid_sexes = ['Male', 'Female', 'Other']
    if data.get('sex') not in valid_sexes:
        raise ValueError(f"Sex must be one of: {valid_sexes}")
    
    return True
```

#### Medical History Validation
```python
def validate_medical_history(data):
    """Validate medical history data."""
    
    # Required fields
    if not data.get('history_item'):
        raise ValueError("History item is required")
    
    # History type validation with mapping
    if data.get('history_type'):
        data['history_type'] = validate_history_type(data['history_type'])
    
    # Severity validation
    valid_severities = ['mild', 'moderate', 'severe', 'critical']
    if data.get('severity') and data['severity'].lower() not in valid_severities:
        raise ValueError(f"Severity must be one of: {valid_severities}")
    
    # Date validation
    if data.get('history_date'):
        try:
            history_date = datetime.strptime(data['history_date'], '%Y-%m-%d').date()
            if history_date > date.today():
                raise ValueError("History date cannot be in the future")
        except ValueError as e:
            raise ValueError(f"Invalid date format for history_date. Use YYYY-MM-DD: {str(e)}")
    
    return True
```

#### Appointment Validation
```python
def validate_appointment_data(data):
    """Validate appointment data."""
    
    # Required appointment date
    if not data.get('appointment_date'):
        raise ValueError("Appointment date is required")
    
    try:
        apt_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        # Allow past dates for historical appointments
    except ValueError:
        raise ValueError("Invalid date format for appointment_date. Use YYYY-MM-DD")
    
    # Time validation
    if data.get('appointment_time'):
        try:
            datetime.strptime(data['appointment_time'], '%H:%M:%S')
        except ValueError:
            raise ValueError("Invalid time format for appointment_time. Use HH:MM:SS")
    
    # Status validation
    valid_statuses = ['Scheduled', 'Confirmed', 'Pending', 'Completed', 'Cancelled', 'No_Show']
    if data.get('status') and data['status'] not in valid_statuses:
        raise ValueError(f"Status must be one of: {valid_statuses}")
    
    # Type validation with mapping
    if data.get('appointment_type'):
        data['appointment_type'] = validate_appointment_type(data['appointment_type'])
    
    return True
```

### Database-Level Constraints
```sql
-- Add database constraints for additional validation
ALTER TABLE Patient ADD CONSTRAINT chk_patient_name_length 
CHECK (CHAR_LENGTH(name) > 0 AND CHAR_LENGTH(name) <= 255);

ALTER TABLE Medical_History ADD CONSTRAINT chk_history_item_not_empty 
CHECK (CHAR_LENGTH(history_item) > 0);

ALTER TABLE Appointment ADD CONSTRAINT chk_appointment_date_not_null 
CHECK (appointment_date IS NOT NULL);

ALTER TABLE Medication ADD CONSTRAINT chk_medication_name_not_empty 
CHECK (CHAR_LENGTH(medicine_name) > 0);

ALTER TABLE Lab_Finding ADD CONSTRAINT chk_test_value_not_empty 
CHECK (CHAR_LENGTH(test_value) > 0);
```

---

## Performance Considerations

### Indexing Strategy
```sql
-- Primary key indexes (automatic)
-- Patient table
CREATE INDEX idx_patient_name ON Patient(name);
CREATE INDEX idx_patient_dob ON Patient(dob);

-- Medical History table
CREATE INDEX idx_history_patient_type ON Medical_History(patient_id, history_type);
CREATE INDEX idx_history_active_date ON Medical_History(is_active, history_date);

-- Appointment table  
CREATE INDEX idx_appointment_patient_date ON Appointment(patient_id, appointment_date);
CREATE INDEX idx_appointment_doctor_date ON Appointment(doctor_name, appointment_date);

-- Medication table
CREATE INDEX idx_medication_patient_continued ON Medication(patient_id, is_continued);

-- Lab Report table
CREATE INDEX idx_lab_patient_date ON Lab_Report(patient_id, lab_date);
```

### Query Optimization

#### Efficient Patient Search
```sql
-- Optimized patient search with proper indexing
SELECT patient_id, name, dob, sex 
FROM Patient 
WHERE name LIKE CONCAT('%', ?, '%')
AND sex = ?
ORDER BY created_at DESC 
LIMIT ? OFFSET ?;

-- Use covering index for common searches
CREATE INDEX idx_patient_search_covering ON Patient(name, sex, created_at, patient_id);
```

#### Efficient Medical Record Retrieval
```sql
-- Optimized complete patient profile query
SELECT 
    p.patient_id, p.name, p.dob, p.sex,
    mh.history_type, mh.history_item, mh.is_active,
    m.medicine_name, m.is_continued,
    a.appointment_date, a.status
FROM Patient p
LEFT JOIN Medical_History mh ON p.patient_id = mh.patient_id AND mh.is_active = 1
LEFT JOIN Medication m ON p.patient_id = m.patient_id AND m.is_continued = 1  
LEFT JOIN Appointment a ON p.patient_id = a.patient_id
WHERE p.patient_id = ?
ORDER BY a.appointment_date DESC;
```

### Connection Pooling
```python
# Production connection pool configuration
import pymysql.pooling

class DatabasePool:
    def __init__(self):
        self.pool = pymysql.pooling.Pool(
            host=DB_HOST,
            port=int(DB_PORT),
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            max_connections=50,        # Adjust based on load
            min_connections=10,
            blocking=True,
            reset_session=True
        )
    
    def get_connection(self):
        return self.pool.get_connection()

# Usage in FastAPI dependency
database_pool = DatabasePool()

def get_pooled_db_connection():
    return database_pool.get_connection()
```

### Query Caching
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def get_patient_basic_info(patient_id):
    """Cache frequently accessed patient basic information."""
    # Implementation with caching
    pass

# Redis caching for complex queries
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_complete_patient_profile_cached(patient_id):
    cache_key = f"patient_profile:{patient_id}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    # Fetch from database
    result = get_complete_patient_profile_from_db(patient_id)
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(result, default=str))
    
    return result
```

---

## Backup & Recovery

### Automated Backup Strategy
```bash
#!/bin/bash
# Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/path/to/backups"
DB_NAME="medimax"

# Create backup
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --hex-blob \
    $DB_NAME | gzip > $BACKUP_DIR/medimax_backup_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "medimax_backup_*.sql.gz" -mtime +30 -delete

# Log backup completion
echo "$(date): Backup completed - medimax_backup_$DATE.sql.gz" >> $BACKUP_DIR/backup.log
```

### Point-in-Time Recovery
```bash
# Enable binary logging in MySQL/MariaDB configuration
# /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
log-bin=mysql-bin
binlog_format=ROW
expire_logs_days=7
sync_binlog=1
```

### Disaster Recovery Procedures
```bash
# 1. Restore from backup
gunzip < medimax_backup_20240914_120000.sql.gz | mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME

# 2. Apply binary logs for point-in-time recovery
mysqlbinlog --start-datetime="2024-09-14 12:00:00" \
           --stop-datetime="2024-09-14 15:30:00" \
           mysql-bin.000001 | mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME

# 3. Verify data integrity
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "
    SELECT 
        (SELECT COUNT(*) FROM Patient) as patient_count,
        (SELECT COUNT(*) FROM Medical_History) as history_count,
        (SELECT COUNT(*) FROM Appointment) as appointment_count;
"
```

### Data Integrity Checks
```sql
-- Regular integrity check queries
-- Check for orphaned records
SELECT 'Orphaned Medical History' as issue, COUNT(*) as count
FROM Medical_History mh
LEFT JOIN Patient p ON mh.patient_id = p.patient_id  
WHERE p.patient_id IS NULL

UNION ALL

SELECT 'Orphaned Appointments' as issue, COUNT(*) as count
FROM Appointment a
LEFT JOIN Patient p ON a.patient_id = p.patient_id
WHERE p.patient_id IS NULL

UNION ALL

SELECT 'Orphaned Symptoms' as issue, COUNT(*) as count  
FROM Appointment_Symptom s
LEFT JOIN Appointment a ON s.appointment_id = a.appointment_id
WHERE a.appointment_id IS NULL;

-- Check for invalid enum values (should return 0 rows)
SELECT * FROM Medical_History 
WHERE history_type NOT IN ('allergy', 'surgery', 'family_history', 'condition', 'lifestyle', 'other');

SELECT * FROM Appointment
WHERE appointment_type NOT IN ('consultation', 'follow_up', 'emergency', 'routine_checkup');
```

---

This comprehensive database documentation provides complete guidance for understanding, implementing, and maintaining the MediMax database system with proper performance, security, and reliability considerations.