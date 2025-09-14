# MediMax Knowledge Graph Creation System

This system creates rule-based knowledge graphs from patient data stored in the MediMax database. The knowledge graphs follow a structured schema based on healthcare entities and relationships, suitable for import into Neo4j or other graph databases.

## System Overview

The knowledge graph builder extracts structured data from the MediMax relational database and transforms it into a graph representation with the following entity types:

### Node Types (Entities)
- **Patient**: Central entity representing individual patients
- **Symptom**: Medical conditions, symptoms, and allergies
- **LabTest**: Laboratory tests and diagnostic procedures
- **Medication**: Prescribed medications and treatments
- **Encounter**: Medical encounters (appointments, lab sessions)

### Relationship Types
- **has_symptom**: Patient → Symptom
- **has_lab_test**: Patient → LabTest
- **prescribed_medication**: Patient → Medication
- **has_encounter**: Patient → Encounter
- **contains_test**: Encounter → LabTest
- **contains_medication**: Encounter → Medication
- **contains_symptom**: Encounter → Symptom

## Files Description

### Core Implementation Files

1. **`create_kg_production.py`** - Production-ready version with comprehensive logging and error handling
2. **`create_kg_with_mcp.py`** - Version demonstrating MCP integration structure
3. **`create_kg.py`** - Original implementation (legacy)

### Generated Output Files

1. **`nodes.csv`** - Neo4j-compatible CSV file containing all nodes with properties
2. **`relationships.csv`** - Neo4j-compatible CSV file containing all relationships
3. **`knowledge_graph.log`** - Detailed execution logs

## Usage

### Command Line Usage

```bash
# Create knowledge graph for a specific patient
python create_kg_production.py <patient_id>

# Examples:
python create_kg_production.py 1    # John Doe (regular checkup patient)
python create_kg_production.py 2    # Jane Smith (hypertension)
python create_kg_production.py 3    # Robert Johnson (diabetes)
python create_kg_production.py 4    # Emily Davis (pregnancy monitoring)
python create_kg_production.py 5    # Michael Wilson (cardiac history)
```

### Programmatic Usage

```python
from create_kg_production import create_knowledge_graph_for_patient

# Create knowledge graph for patient
patient_id = 1
nodes, relationships = create_knowledge_graph_for_patient(patient_id)

print(f"Created {len(nodes)} nodes and {len(relationships)} relationships")
```

## Rule-Based Extraction

The system uses pattern matching and medical terminology recognition to extract entities:

### Symptom Extraction Patterns
- Pain-related: `pain|ache|hurt|discomfort`
- Fatigue-related: `fatigue|tired|exhausted|weakness`
- Cardiovascular: `hypertension|high blood pressure|chest pain|cardiac`
- Metabolic: `diabetes|high blood sugar`
- General symptoms: `fever|nausea|dizziness|cough|headache`

### Lab Test Extraction Patterns
- Blood tests: `blood test|CBC|complete blood count`
- Metabolic: `glucose|cholesterol|HbA1c`
- Function tests: `liver function|kidney function`
- Imaging: `X-ray|CT scan|MRI|ultrasound`

### Medication Extraction Patterns
- Common medications: `aspirin|metformin|insulin|lisinopril`
- Drug name patterns: Words ending in `in|ol|ide|ine|ium`

## Sample Knowledge Graph Structure

For a diabetic patient (Robert Johnson, ID: 3):

### Nodes Created:
- **Patient**: Robert Johnson
- **Symptoms**: Allergy to sulfa drugs, Diabetes Type 2, Pain, Diabetes
- **Medications**: Metformin, Insulin
- **Lab Tests**: Glucose, Kidney Function
- **Encounters**: Lab sessions and appointments

### Relationships Created:
- `patient_3 --[has_symptom]--> symptom_allergy_sulfa_drugs`
- `patient_3 --[has_symptom]--> symptom_diabetes_type_2`
- `patient_3 --[prescribed_medication]--> medication_metformin`
- `patient_3 --[prescribed_medication]--> medication_insulin`
- `patient_3 --[has_encounter]--> encounter_lab_2024_08_20`
- `encounter_lab_2024_08_20 --[contains_test]--> labtest_glucose`

## Neo4j Import

The generated CSV files are formatted for Neo4j bulk import:

### Using Neo4j Admin Import
```bash
neo4j-admin import \
  --nodes=nodes.csv \
  --relationships=relationships.csv \
  --delimiter=","
```

### Using LOAD CSV (for existing database)
```cypher
// Load nodes
LOAD CSV WITH HEADERS FROM "file:///nodes.csv" AS row
CALL apoc.create.node([row.`:LABEL`], row) YIELD node
RETURN count(node);

// Load relationships
LOAD CSV WITH HEADERS FROM "file:///relationships.csv" AS row
MATCH (start {id: row.`:START_ID`})
MATCH (end {id: row.`:END_ID`})
CALL apoc.create.relationship(start, row.`:TYPE`, {}, end) YIELD rel
RETURN count(rel);
```

## Database Integration

### Current Implementation
The system currently uses sample data that mirrors the MediMax database structure for demonstration purposes.

### Production Integration
To integrate with the actual MediMax database using MCP tools, replace the sample data methods with MCP calls:

```python
def _get_patient_from_db(self, patient_id: int) -> Dict:
    """Get patient data from database via MCP."""
    result = mcp_hospitaldb_ExecuteQuery_MariaDB(
        f"SELECT * FROM Patient WHERE Patient_ID = {patient_id}"
    )
    return result['results'][0] if result['results'] else None

def _get_patient_history_from_db(self, patient_id: int) -> Dict:
    """Get patient history from database via MCP."""
    result = mcp_hospitaldb_ExecuteQuery_MariaDB(
        f"SELECT History FROM History WHERE Patient_ID = {patient_id}"
    )
    if result['results']:
        history_json = result['results'][0]['History']
        return json.loads(history_json)
    return {}
```

## Logging and Monitoring

The system provides comprehensive logging at multiple levels:

- **INFO**: High-level progress and summary information
- **DEBUG**: Detailed node and relationship creation
- **ERROR**: Error conditions and failures

Log files are saved to `knowledge_graph.log` with UTF-8 encoding.

## Error Handling

The system includes robust error handling for:
- Missing patient data
- Invalid patient IDs
- Database connection issues
- CSV file creation errors
- Pattern matching failures

## Performance Considerations

- **Memory Usage**: The system loads all patient data into memory before processing
- **Scalability**: Designed for individual patient processing; batch processing would require modifications
- **Processing Time**: Depends on the amount of data per patient (typically < 1 second per patient)

## Extension Points

### Adding New Entity Types
1. Add new entity to `ENTITIES` list
2. Create extraction patterns
3. Add processing methods
4. Update CSV generation

### Adding New Relationship Types
1. Add relationship to `RELATIONS` list
2. Implement relationship creation logic
3. Update documentation

### Custom Extraction Rules
Modify the pattern matching functions to add domain-specific extraction rules for your healthcare data.

## Requirements

- Python 3.7+
- CSV module (built-in)
- JSON module (built-in)
- Regular expressions (re module)
- Logging module (built-in)

For MCP integration:
- MCP hospital database tools
- Database connection credentials

## Troubleshooting

### Common Issues

1. **Unicode Errors in Logging**: Windows PowerShell may have issues with emoji characters in logs
   - Solution: Use file logging or disable emoji characters

2. **CSV Field Errors**: "dict contains fields not in fieldnames"
   - Solution: The production version handles dynamic fields correctly

3. **Empty Knowledge Graphs**: No data extracted for patient
   - Check patient ID validity
   - Verify database connectivity
   - Review extraction patterns

### Debug Mode
Enable debug logging by modifying the logging level:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

To contribute to the knowledge graph system:

1. Follow the existing code structure
2. Add comprehensive logging
3. Include error handling
4. Update this documentation
5. Test with sample data before production use

## License

This system is part of the MediMax healthcare management platform.