
-- Insert rich patient: Dr. Sarah Mitchell
INSERT INTO Patient (name, dob, sex) 
VALUES ('Dr. Sarah Mitchell', '1979-03-22', 'Female');

SET @patient_id = LAST_INSERT_ID();

-- Medical History

INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'allergy', 'Penicillin allergy', 'Severe anaphylactic reaction in 1995', 'severe', true, '1995-06-15');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'allergy', 'Latex allergy', 'Developed after years of surgical glove use', 'moderate', true, '2010-03-10');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'allergy', 'Shellfish allergy', 'Mild urticaria and GI symptoms', 'mild', true, '2005-08-20');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'condition', 'Hypertension', 'Essential hypertension diagnosed during pregnancy', 'moderate', true, '2015-02-14');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'condition', 'Type 2 Diabetes Mellitus', 'Gestational diabetes that progressed to T2DM', 'moderate', true, '2016-11-08');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'condition', 'Hyperlipidemia', 'Familial combined hyperlipidemia', 'moderate', true, '2018-05-15');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'condition', 'Anxiety Disorder', 'Work-related stress and pandemic burnout', 'mild', true, '2020-09-12');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'condition', 'Chronic Kidney Disease Stage 2', 'Secondary to diabetes and hypertension', 'moderate', true, '2023-01-20');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'condition', 'Hypothyroidism', 'Hashimoto thyroiditis', 'mild', true, '2021-07-03');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'surgery', 'Cholecystectomy', 'Laparoscopic cholecystectomy for gallstones', 'moderate', true, '2019-04-15');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'surgery', 'Cesarean Section', 'Emergency C-section for fetal distress', 'moderate', true, '2015-09-22');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'family_history', 'Paternal CAD', 'Father had MI at age 52, died at 58', 'severe', true, '1950-01-01');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'family_history', 'Maternal Diabetes', 'Mother has T2DM and diabetic nephropathy', 'moderate', true, '1955-01-01');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'family_history', 'Sister Breast Cancer', 'BRCA2 positive, diagnosed at 38', 'severe', true, '1981-01-01');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'lifestyle', 'Former Smoker', '10 pack-year history, quit 2010', 'moderate', true, '2010-01-01');


INSERT INTO Medical_History (patient_id, history_type, history_item, history_details, severity, is_active, history_date)
VALUES (@patient_id, 'lifestyle', 'Social Drinker', '2-3 glasses wine per week', 'mild', true, '2024-01-01');


-- Medications and Purposes

INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Metformin XR', true, '2016-11-08', NULL, '1000mg', 'Twice daily', 'Dr. Jennifer Adams');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Type 2 Diabetes', 'Prescribed for Type 2 Diabetes management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Insulin Glargine', true, '2020-03-15', NULL, '25 units', 'Daily at bedtime', 'Dr. Jennifer Adams');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Type 2 Diabetes', 'Prescribed for Type 2 Diabetes management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Insulin Lispro', true, '2020-03-15', NULL, '1:10 ratio', 'With meals', 'Dr. Jennifer Adams');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Type 2 Diabetes', 'Prescribed for Type 2 Diabetes management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Lisinopril', true, '2015-02-14', NULL, '20mg', 'Daily', 'Dr. Michael Chen');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Hypertension', 'Prescribed for Hypertension management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Amlodipine', true, '2018-06-20', NULL, '10mg', 'Daily', 'Dr. Michael Chen');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Hypertension', 'Prescribed for Hypertension management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Atorvastatin', true, '2018-05-15', NULL, '40mg', 'Daily at bedtime', 'Dr. Michael Chen');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Hyperlipidemia', 'Prescribed for Hyperlipidemia management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Aspirin', true, '2018-05-15', NULL, '81mg', 'Daily', 'Dr. Michael Chen');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Cardiovascular Protection', 'Prescribed for Cardiovascular Protection management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Levothyroxine', true, '2021-07-03', NULL, '88mcg', 'Daily on empty stomach', 'Dr. Lisa Park');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Hypothyroidism', 'Prescribed for Hypothyroidism management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Sertraline', true, '2020-09-12', NULL, '50mg', 'Daily', 'Dr. Robert Kim');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Anxiety Disorder', 'Prescribed for Anxiety Disorder management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Losartan', true, '2023-01-20', NULL, '50mg', 'Daily', 'Dr. Elena Rodriguez');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Chronic Kidney Disease', 'Prescribed for Chronic Kidney Disease management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Vitamin D3', true, '2019-11-10', NULL, '2000 IU', 'Daily', 'Dr. Jennifer Adams');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Vitamin D Deficiency', 'Prescribed for Vitamin D Deficiency management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Calcium Carbonate', true, '2022-03-08', NULL, '1200mg', 'Twice daily', 'Dr. Jennifer Adams');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Osteoporosis Prevention', 'Prescribed for Osteoporosis Prevention management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Omega-3 Fish Oil', true, '2019-06-12', NULL, '1000mg', 'Twice daily', 'Dr. Michael Chen');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Cardiovascular Health', 'Prescribed for Cardiovascular Health management');


INSERT INTO Medication (patient_id, medicine_name, is_continued, prescribed_date, discontinued_date, dosage, frequency, prescribed_by)
VALUES (@patient_id, 'Hydrochlorothiazide', false, '2015-02-14', '2023-01-20', '25mg', 'Daily', 'Dr. Michael Chen');

INSERT INTO Medication_Purpose (medication_id, condition_name, purpose_description)
VALUES (LAST_INSERT_ID(), 'Hypertension', 'Prescribed for Hypertension management');


-- Appointments and Symptoms

INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '2024-09-10', '14:30:00', 'completed', 'follow_up', 'Dr. Jennifer Adams');

SET @appointment_id = LAST_INSERT_ID();


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Polyuria', 'Increased urination, especially at night', 'moderate', '2 weeks');


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Polydipsia', 'Excessive thirst', 'moderate', '2 weeks');


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Fatigue', 'Persistent tiredness despite adequate sleep', 'moderate', '3 weeks');


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Blurred Vision', 'Intermittent blurring, worse in evenings', 'mild', '1 week');


INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '2024-08-15', '10:00:00', 'completed', 'consultation', 'Dr. Elena Rodriguez');

SET @appointment_id = LAST_INSERT_ID();


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Ankle Swelling', 'Bilateral pedal edema, worse at end of day', 'mild', '1 month');


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Proteinuria', 'Foamy urine noticed by patient', 'moderate', '2 months');


INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '2024-07-22', '09:15:00', 'completed', 'routine_checkup', 'Dr. Michael Chen');

SET @appointment_id = LAST_INSERT_ID();


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Chest Tightness', 'Occasional chest tightness with exertion', 'mild', '6 weeks');


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Dyspnea on Exertion', 'Shortness of breath climbing 2 flights stairs', 'mild', '2 months');


INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '2024-06-28', '16:00:00', 'completed', 'follow_up', 'Dr. Robert Kim');

SET @appointment_id = LAST_INSERT_ID();


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Anxiety', 'Work-related stress and sleep disturbances', 'moderate', '1 month');


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Insomnia', 'Difficulty falling asleep, early awakening', 'moderate', '3 weeks');


INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '2024-05-18', '11:30:00', 'completed', 'follow_up', 'Dr. Lisa Park');

SET @appointment_id = LAST_INSERT_ID();


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Hair Loss', 'Thinning hair despite thyroid treatment', 'mild', '3 months');


INSERT INTO Appointment_Symptom (appointment_id, symptom_name, symptom_description, severity, duration)
VALUES (@appointment_id, 'Cold Intolerance', 'Feeling cold even in warm weather', 'mild', '2 months');


INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '2024-10-15', '14:00:00', 'scheduled', 'follow_up', 'Dr. Jennifer Adams');

SET @appointment_id = LAST_INSERT_ID();


INSERT INTO Appointment (patient_id, appointment_date, appointment_time, status, appointment_type, doctor_name)
VALUES (@patient_id, '2024-11-20', '10:30:00', 'scheduled', 'routine_checkup', 'Dr. Michael Chen');

SET @appointment_id = LAST_INSERT_ID();


-- Lab Reports and Findings

INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
VALUES (@patient_id, '2024-09-08', 'Comprehensive Metabolic Panel', 'Dr. Jennifer Adams', 'Central Lab');

SET @lab_report_id = LAST_INSERT_ID();


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Glucose (fasting)', '165', 'mg/dL', '70-100', true, 'high');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'HbA1c', '8.2', '%', '<7.0', true, 'high');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Creatinine', '1.3', 'mg/dL', '0.6-1.1', true, 'high');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'eGFR', '58', 'mL/min/1.73m²', '>60', true, 'low');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'BUN', '28', 'mg/dL', '7-20', true, 'high');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Sodium', '138', 'mEq/L', '136-145', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Potassium', '4.8', 'mEq/L', '3.5-5.0', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Chloride', '102', 'mEq/L', '98-107', false, NULL);


INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
VALUES (@patient_id, '2024-09-08', 'Lipid Panel', 'Dr. Michael Chen', 'Central Lab');

SET @lab_report_id = LAST_INSERT_ID();


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Total Cholesterol', '195', 'mg/dL', '<200', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'LDL Cholesterol', '88', 'mg/dL', '<100', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'HDL Cholesterol', '52', 'mg/dL', '>50', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Triglycerides', '275', 'mg/dL', '<150', true, 'high');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Non-HDL Cholesterol', '143', 'mg/dL', '<130', true, 'high');


INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
VALUES (@patient_id, '2024-08-12', 'Complete Blood Count', 'Dr. Elena Rodriguez', 'Central Lab');

SET @lab_report_id = LAST_INSERT_ID();


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Hemoglobin', '11.8', 'g/dL', '12.0-15.5', true, 'low');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Hematocrit', '35.2', '%', '36.0-46.0', true, 'low');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'WBC Count', '7.2', 'K/μL', '4.5-11.0', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Platelet Count', '285', 'K/μL', '150-400', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'MCV', '78', 'fL', '80-100', true, 'low');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'MCH', '26', 'pg', '27-32', true, 'low');


INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
VALUES (@patient_id, '2024-07-20', 'Thyroid Function Panel', 'Dr. Lisa Park', 'Endocrine Lab');

SET @lab_report_id = LAST_INSERT_ID();


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'TSH', '3.8', 'mIU/L', '0.4-4.0', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Free T4', '1.1', 'ng/dL', '0.8-1.8', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Free T3', '2.8', 'pg/mL', '2.3-4.2', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'TPO Antibodies', '245', 'IU/mL', '<35', true, 'high');


INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
VALUES (@patient_id, '2024-06-15', 'Microalbumin (24hr)', 'Dr. Elena Rodriguez', 'Nephrology Lab');

SET @lab_report_id = LAST_INSERT_ID();


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Microalbumin', '85', 'mg/24hr', '<30', true, 'high');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Creatinine Clearance', '62', 'mL/min', '>90', true, 'low');


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Protein/Creatinine Ratio', '0.18', 'mg/mg', '<0.15', true, 'high');


INSERT INTO Lab_Report (patient_id, lab_date, lab_type, ordering_doctor, lab_facility)
VALUES (@patient_id, '2024-05-25', 'Cardiac Stress Test with Echo', 'Dr. Michael Chen', 'Cardiology Center');

SET @lab_report_id = LAST_INSERT_ID();


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Exercise Tolerance', '8.5 METS', 'METS', '>7', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'Peak Heart Rate', '158', 'bpm', '85% max predicted', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'ST Segment Changes', 'None', '', 'None', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'LVEF (Rest)', '58', '%', '>55', false, NULL);


INSERT INTO Lab_Finding (lab_report_id, test_name, test_value, test_unit, reference_range, is_abnormal, abnormal_flag)
VALUES (@lab_report_id, 'LVEF (Stress)', '55', '%', '>55', false, NULL);


-- Chat History

INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Dr. Adams, I''ve been having increased thirst and urination again, especially at night. My glucose readings at home have been running 180-220.', 'patient', 'session_sarah_001', '2024-09-05 14:30:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'How long have you been experiencing these symptoms? Have you made any changes to your diet or medication routine recently?', 'doctor', 'session_sarah_001', '2024-09-05 14:32:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'About 2-3 weeks now. I''ve been under a lot of stress at the hospital - we''ve had several difficult cases. I admit I''ve been eating more convenience foods and my exercise has been inconsistent.', 'patient', 'session_sarah_001', '2024-09-05 14:33:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'I understand the demands of your profession. Let''s get some labs and consider adjusting your insulin regimen. We may need to increase your basal insulin and optimize your meal coverage.', 'doctor', 'session_sarah_001', '2024-09-05 14:35:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Dr. Rodriguez, I''ve noticed my ankles swelling more lately, and my urine seems foamy. I''m concerned about my kidney function given my diabetes.', 'patient', 'session_sarah_002', '2024-08-10 09:15:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Those are important observations. The foamy urine could indicate protein spillage. Let''s check your microalbumin levels and creatinine. How''s your blood pressure control been?', 'doctor', 'session_sarah_002', '2024-08-10 09:17:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'My home readings have been averaging 135/85, which is higher than my usual 125/80. I''ve been taking my medications as prescribed.', 'patient', 'session_sarah_002', '2024-08-10 09:18:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'We may need to optimize your blood pressure management. I''m going to add an ARB to provide additional kidney protection and better BP control.', 'doctor', 'session_sarah_002', '2024-08-10 09:20:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Dr. Chen, I''ve been experiencing some chest tightness when I climb stairs at the hospital. It''s not severe, but it''s new for me.', 'patient', 'session_sarah_003', '2024-07-18 15:30:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Given your family history and current risk factors, we should take this seriously. Let''s schedule a stress test to evaluate your cardiac function.', 'doctor', 'session_sarah_003', '2024-07-18 15:32:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'I was hoping you''d say that wasn''t necessary, but I know you''re right. My father''s history makes me vigilant about cardiac symptoms.', 'patient', 'session_sarah_003', '2024-07-18 15:33:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Dr. Kim, the pandemic really took a toll, and now with my health issues, I''m feeling overwhelmed. My sleep is terrible and I''m constantly worried.', 'patient', 'session_sarah_004', '2024-06-25 16:45:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Healthcare workers have faced unprecedented challenges. It''s completely understandable. How are the sertraline and our coping strategies working for you?', 'doctor', 'session_sarah_004', '2024-06-25 16:47:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'The medication helps with the daily anxiety, but I still wake up at 3 AM worried about my patients and my own health. The meditation app you recommended does help sometimes.', 'patient', 'session_sarah_004', '2024-06-25 16:48:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Dr. Park, despite the levothyroxine, I''m still losing hair and feeling cold. My energy levels aren''t what they should be.', 'patient', 'session_sarah_005', '2024-05-15 11:00:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'Your TSH levels look good, but with Hashimoto''s, sometimes we need to optimize further. Let''s check your T3 levels and consider if you might benefit from combination therapy.', 'doctor', 'session_sarah_005', '2024-05-15 11:02:00');


INSERT INTO Chat_History (patient_id, message_text, message_type, session_id, timestamp)
VALUES (@patient_id, 'I''ve read about T4/T3 combinations. As a physician, I appreciate the complexity of thyroid management, but as a patient, I just want to feel like myself again.', 'patient', 'session_sarah_005', '2024-05-15 11:03:00');
