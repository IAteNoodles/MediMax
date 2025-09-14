#!/usr/bin/env python3
"""
Check connectivity of the knowledge graph
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()
driver = GraphDatabase.driver(os.getenv('NEO4J_URI'), auth=(os.getenv('NEO4J_USERNAME'), os.getenv('NEO4J_PASSWORD')))

with driver.session() as session:
    # Check which patients we have
    result = session.run('MATCH (p:Patient) RETURN p.nodeId as id, p.name as name')
    patients = list(result)
    print('Patients in database:')
    for p in patients:
        print(f'  {p["id"]}: {p["name"]}')
    
    # Check connections for the actual patient
    if patients:
        patient_id = patients[0]['id']
        result = session.run(f'MATCH (p:Patient {{nodeId: "{patient_id}"}}) MATCH (p)-[r]->(connected) RETURN type(r) as rel, connected.name as target')
        connections = list(result)
        print(f'\n{patient_id} connections ({len(connections)} total):')
        for conn in connections:
            print(f'  -[{conn["rel"]}]-> {conn["target"]}')
    
    # Show overall graph structure
    result = session.run('MATCH (n)-[r]->(m) RETURN labels(n)[0] as start_type, type(r) as rel_type, labels(m)[0] as end_type, n.name as start_name, m.name as end_name LIMIT 15')
    connections = list(result)
    print(f'\nSample graph connections ({len(connections)} shown):')
    for conn in connections:
        print(f'  {conn["start_type"]}({conn["start_name"]}) -[{conn["rel_type"]}]-> {conn["end_type"]}({conn["end_name"]})')

driver.close()