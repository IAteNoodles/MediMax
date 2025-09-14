-- MediMax Knowledge Graph Cypher Queries
-- Use these queries in Neo4j Browser or Neo4j Desktop

-- 1. Overview: Count all nodes by type
MATCH (n) 
RETURN labels(n)[0] as NodeType, count(n) as Count 
ORDER BY Count DESC;

-- 2. Overview: Count all relationships by type
MATCH ()-[r]->() 
RETURN type(r) as RelationshipType, count(r) as Count 
ORDER BY Count DESC;

-- 3. Find all patients and their basic info
MATCH (p:Patient) 
RETURN p.name, p.dob, p.sex, p.remarks 
ORDER BY p.name;

-- 4. Find all symptoms for a specific patient
MATCH (p:Patient)-[:has_symptom]->(s:Symptom) 
WHERE p.name = "John Doe"
RETURN p.name, s.name, s.type;

-- 5. Find all medications prescribed to patients
MATCH (p:Patient)-[:prescribed_medication]->(m:Medication) 
RETURN p.name, m.name, m.details, m.prescription_date 
ORDER BY p.name, m.prescription_date;

-- 6. Find patients with diabetes
MATCH (p:Patient)-[:has_symptom]->(s:Symptom) 
WHERE toLower(s.name) CONTAINS "diabetes"
RETURN p.name, s.name;

-- 7. Find patients with allergies
MATCH (p:Patient)-[:has_symptom]->(s:Symptom) 
WHERE s.type = "allergy"
RETURN p.name, s.name;

-- 8. Find all lab tests and their encounters
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)-[:contains_test]->(l:LabTest)
RETURN p.name, e.date, e.type, l.name
ORDER BY p.name, e.date;

-- 9. Find patients and their appointment history
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)
WHERE e.type = "appointment"
RETURN p.name, e.date, e.status, e.type
ORDER BY p.name, e.date;

-- 10. Find complex paths: Patient -> Symptoms -> Medications
MATCH path = (p:Patient)-[:has_symptom]->(s:Symptom), (p)-[:prescribed_medication]->(m:Medication)
RETURN p.name, s.name, m.name
ORDER BY p.name;

-- 11. Find patients with multiple conditions
MATCH (p:Patient)-[:has_symptom]->(s:Symptom)
WHERE s.type = "condition"
WITH p, count(s) as condition_count
WHERE condition_count > 1
MATCH (p)-[:has_symptom]->(s:Symptom)
WHERE s.type = "condition"
RETURN p.name, collect(s.name) as conditions, condition_count
ORDER BY condition_count DESC;

-- 12. Find medication interactions (patients taking multiple medications)
MATCH (p:Patient)-[:prescribed_medication]->(m:Medication)
WITH p, collect(m.name) as medications, count(m) as med_count
WHERE med_count > 1
RETURN p.name, medications, med_count
ORDER BY med_count DESC;

-- 13. Find recent lab tests (last 6 months)
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)-[:contains_test]->(l:LabTest)
WHERE e.type = "laboratory" AND e.date >= "2024-03-01"
RETURN p.name, e.date, l.name, l.details
ORDER BY e.date DESC;

-- 14. Find patients by age (approximate, using DOB)
MATCH (p:Patient)
WHERE p.dob IS NOT NULL
WITH p, duration.between(date(p.dob), date()).years as age
RETURN p.name, p.dob, age
ORDER BY age DESC;

-- 15. Network analysis: Find highly connected patients
MATCH (p:Patient)-[r]-()
WITH p, count(r) as connection_count
RETURN p.name, connection_count
ORDER BY connection_count DESC
LIMIT 10;

-- 16. Find diagnostic patterns: Symptoms -> Lab Tests
MATCH (p:Patient)-[:has_symptom]->(s:Symptom), (p)-[:has_lab_test]->(l:LabTest)
RETURN s.name as Symptom, collect(DISTINCT l.name) as LabTests
ORDER BY Symptom;

-- 17. Find treatment patterns: Symptoms -> Medications
MATCH (p:Patient)-[:has_symptom]->(s:Symptom), (p)-[:prescribed_medication]->(m:Medication)
RETURN s.name as Symptom, collect(DISTINCT m.name) as Medications
ORDER BY Symptom;

-- 18. Timeline view: Patient's medical history
MATCH (p:Patient)-[:has_encounter]->(e:Encounter)
WHERE p.name = "John Doe" AND e.date IS NOT NULL
OPTIONAL MATCH (e)-[:contains_test]->(l:LabTest)
OPTIONAL MATCH (e)-[:contains_symptom]->(s:Symptom)
RETURN e.date, e.type, e.status, collect(DISTINCT l.name) as lab_tests, collect(DISTINCT s.name) as symptoms
ORDER BY e.date;

-- 19. Find potential risk factors (patients with multiple risk symptoms)
MATCH (p:Patient)-[:has_symptom]->(s:Symptom)
WHERE s.name IN ["Hypertension", "Diabetes Type 2", "Coronary Artery Disease", "High Cholesterol"]
WITH p, collect(s.name) as risk_factors, count(s) as risk_count
WHERE risk_count >= 2
RETURN p.name, risk_factors, risk_count
ORDER BY risk_count DESC;

-- 20. Export data for analysis
MATCH (p:Patient)-[r]->(n)
RETURN p.name as Patient, type(r) as Relationship, labels(n)[0] as TargetType, n.name as TargetName
ORDER BY Patient, Relationship;
