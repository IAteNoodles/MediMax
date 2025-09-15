# LangChain Cypher Query Generator

A Python implementation that converts natural language queries into runnable Neo4j Cypher queries using LangChain and Large Language Models (LLMs).

## Features

- **Clean Output**: Automatically removes markdown formatting and extracts only the executable Cypher query
- **Schema-Aware**: Incorporates Neo4j database schema information for better query generation
- **Syntax Validation**: Basic validation to ensure generated queries are syntactically correct
- **Multiple Usage Patterns**: Simple functions, class-based interface, and interactive mode
- **Error Handling**: Robust error handling and informative error messages

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables by copying `.env.example` to `.env`:
```bash
cp .env.example .env
```

3. Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Quick Start

### Simple Usage

```python
from cypher import generate_cypher_from_text

# Generate a Cypher query from natural language
query = generate_cypher_from_text("Find all users named John")
print(query)
# Output: MATCH (n:User) WHERE n.name = 'John' RETURN n
```

### Advanced Usage with Schema

```python
from cypher import CypherQueryGenerator

# Initialize the generator
generator = CypherQueryGenerator()

# Set your database schema for better results
schema = """
Node Labels: Person, Movie, Director
Relationship Types: ACTED_IN, DIRECTED
Property Keys: name, title, year, born
"""
generator.set_schema_info(schema)

# Generate queries
query = generator.generate_cypher_query("Show me actors who worked with Tom Hanks")
print(query)
# Output: MATCH (tom:Person {name: 'Tom Hanks'})-[:ACTED_IN]->(movie)<-[:ACTED_IN]-(actor:Person) RETURN DISTINCT actor.name
```

### Auto-Schema Detection

```python
from cypher import CypherQueryGenerator

generator = CypherQueryGenerator()

# Automatically get schema from your Neo4j database
schema = generator.get_neo4j_schema(
    uri="bolt://localhost:7687",
    username="neo4j", 
    password="your_password"
)
generator.set_schema_info(schema)

# Now generate queries with full schema context
query = generator.generate_cypher_query("Find all relationships")
```

## Key Components

### CypherQueryGenerator Class

The main class that handles query generation:

- `__init__(openai_api_key, model_name, temperature)`: Initialize with LLM settings
- `set_schema_info(schema_info)`: Set database schema information
- `get_neo4j_schema(uri, username, password)`: Auto-retrieve schema from Neo4j
- `generate_cypher_query(user_query, context)`: Generate Cypher from natural language
- `validate_cypher_syntax(cypher_query)`: Basic syntax validation

### CypherOutputParser Class

Cleans LLM output to extract pure Cypher queries:

- Removes markdown code blocks (```cypher, ```)
- Eliminates explanatory text and prefixes
- Extracts only the executable query parts
- Handles multi-line queries properly

## Output Cleaning

The system automatically cleans LLM output to ensure you get only runnable Cypher queries:

**Input from LLM:**
```
Here's the Cypher query you requested:

```cypher
MATCH (n:Person) WHERE n.name = 'John' RETURN n
```

This query will find all Person nodes with the name 'John'.
```

**Cleaned Output:**
```
MATCH (n:Person) WHERE n.name = 'John' RETURN n
```

## Examples

### Medical Database Queries

```python
generator = CypherQueryGenerator()

medical_schema = """
Node Labels: Patient, Doctor, Disease, Treatment, Hospital
Relationship Types: DIAGNOSED_WITH, TREATED_BY, WORKS_AT
Property Keys: name, age, specialization, date, severity
"""
generator.set_schema_info(medical_schema)

queries = [
    "Find all patients diagnosed with diabetes",
    "Show doctors who specialize in cardiology", 
    "Get treatments for high blood pressure"
]

for q in queries:
    cypher = generator.generate_cypher_query(q)
    print(f"Query: {q}")
    print(f"Cypher: {cypher}")
    print()
```

### Interactive Mode

Run the example file for an interactive session:

```bash
python example_usage.py
```

This will start an interactive mode where you can type natural language queries and see the generated Cypher output in real-time.

## Configuration Options

### LLM Models

You can use different OpenAI models:

```python
# Use GPT-4 for better accuracy
generator = CypherQueryGenerator(model_name="gpt-4")

# Use GPT-3.5-turbo for faster/cheaper generation  
generator = CypherQueryGenerator(model_name="gpt-3.5-turbo")
```

### Temperature Settings

Control the randomness of query generation:

```python
# More deterministic (recommended for production)
generator = CypherQueryGenerator(temperature=0.0)

# More creative (useful for exploration)
generator = CypherQueryGenerator(temperature=0.7)
```

## Best Practices

1. **Provide Schema Information**: Always set schema info for better query accuracy
2. **Use Low Temperature**: Set temperature to 0.0-0.2 for consistent results
3. **Validate Queries**: Use the built-in syntax validation before execution
4. **Handle Errors**: Wrap query generation in try-catch blocks
5. **Test Queries**: Always test generated queries on sample data first

## Error Handling

The system includes comprehensive error handling:

```python
try:
    query = generator.generate_cypher_query("Find all users")
    if generator.validate_cypher_syntax(query):
        print(f"Valid query: {query}")
    else:
        print("Generated query has syntax issues")
except Exception as e:
    print(f"Error generating query: {e}")
```

## Limitations

- Requires OpenAI API key (cost implications for heavy usage)
- Generated queries should always be tested before production use
- Complex queries may require human review
- Schema information significantly improves accuracy

## Contributing

Feel free to submit issues and pull requests to improve the functionality.

## License

This project is open source. Please check the license file for details.