"""
Export medication reasons for a given patient from Neo4j and MariaDB.

Usage:
  python scripts\export_medication_reasons.py --patient 7

This script looks for environment variables (AURA_USER, AURA_PASSWORD, DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
and will bail with a helpful message if they're not present. It writes two files to the repository root:
  - patient_<id>_medication_reasons.json
  - patient_<id>_medication_reasons.csv

The Neo4j portion queries TAKES_MEDICATION relationships and any TREATS_CONDITION edges from Medication nodes.
The MariaDB portion (if DB creds present) queries the Medication and Medication_Purpose tables for the patient.

The script is intentionally conservative: it won't attempt network connections unless required env vars exist.
"""

import os
import json
import csv
import argparse
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; env vars may be set outside
    pass

NEO4J_URI = os.getenv('NEO4J_URI') or "neo4j+s://98d1982d.databases.neo4j.io"
AURA_USER = os.getenv('AURA_USER')
AURA_PASSWORD = os.getenv('AURA_PASSWORD')

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3306))


def query_neo4j(patient_id: str):
    """Query Neo4j for medications and reasons (relationship.indication and TREATS_CONDITION)."""
    try:
        from neo4j import GraphDatabase
    except Exception as e:
        return {"error": f"neo4j python driver not installed: {e}"}

    if not all([AURA_USER, AURA_PASSWORD, NEO4J_URI]):
        return {"error": "Neo4j credentials (AURA_USER, AURA_PASSWORD or NEO4J_URI) not configured in environment."}

    cypher = f"""
    MATCH (p:Patient {{patient_id: '{patient_id}'}})-[r:TAKES_MEDICATION]->(m:Medication)
    OPTIONAL MATCH (m)-[t:TREATS_CONDITION]->(cond)
    RETURN m.medicine_name AS medication_name,
           labels(m) AS med_labels,
           properties(m) AS medication_properties,
           type(r) AS patient_med_relation,
           properties(r) AS relationship_properties,
           collect(DISTINCT {{treat_rel: type(t), condition_props: properties(cond), condition_labels: labels(cond)}}) AS treats
    ORDER BY medication_name
    """

    driver = GraphDatabase.driver(NEO4J_URI, auth=(AURA_USER, AURA_PASSWORD))
    with driver.session() as session:
        result = session.run(cypher)
        rows = [record.data() for record in result]
    driver.close()
    return {"results": rows}


def query_mariadb(patient_id: int):
    """Query MariaDB for Medication and Medication_Purpose records for the patient."""
    try:
        import mariadb
    except Exception as e:
        return {"error": f"mariadb driver not installed: {e}"}

    if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
        return {"error": "MariaDB credentials (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME) not configured in environment."}

    conn = None
    try:
        conn = mariadb.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT)
        cur = conn.cursor(dictionary=True)
        sql = ("SELECT m.medication_id, m.medicine_name, m.is_continued, m.prescribed_date, m.discontinued_date, "
               "m.dosage, m.frequency, m.prescribed_by, mp.purpose_description "
               "FROM Medication m LEFT JOIN Medication_Purpose mp ON m.medication_id = mp.medication_id "
               "WHERE m.patient_id = %s ORDER BY m.prescribed_date DESC")
        cur.execute(sql, (patient_id,))
        rows = cur.fetchall()
        return {"results": rows}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if conn:
            conn.close()


def save_outputs(patient_id: str, neo4j_data, mariadb_data=None):
    out_json = Path(f"patient_{patient_id}_medication_reasons.json")
    out_csv = Path(f"patient_{patient_id}_medication_reasons.csv")

    combined = {
        "patient_id": patient_id,
        "neo4j": neo4j_data,
        "mariadb": mariadb_data,
    }

    with out_json.open('w', encoding='utf8') as f:
        # Use default=str to safely serialize dates and other non-serializable objects
        json.dump(combined, f, indent=2, ensure_ascii=False, default=str)

    # Flatten Neo4j results to CSV rows if available
    csv_rows = []
    if isinstance(neo4j_data, dict) and neo4j_data.get('results'):
        for r in neo4j_data['results']:
            med = r.get('medication_name') or (r.get('medication_properties') or {}).get('medicine_name')
            rel_props = r.get('relationship_properties') or {}
            indications = rel_props.get('indication') or rel_props.get('relationship_type') or ''
            treats = r.get('treats') or []
            treat_names = []
            for t in treats:
                cond = t.get('condition_props') or {}
                name = cond.get('name') or cond.get('condition_name') or None
                if name:
                    treat_names.append(name)
            csv_rows.append({
                'medication': med,
                'indication': indications,
                'treats_conditions': ';'.join(treat_names) if treat_names else '',
                'relationship_properties': json.dumps(rel_props, ensure_ascii=False),
            })

    # If MariaDB results exist, include them as additional rows
    if isinstance(mariadb_data, dict) and mariadb_data.get('results'):
        for m in mariadb_data['results']:
            csv_rows.append({
                'medication': m.get('medicine_name'),
                'indication': m.get('purpose_description') or '',
                'treats_conditions': '',
                'relationship_properties': json.dumps(m, default=str, ensure_ascii=False),
            })

    # write CSV
    if csv_rows:
        keys = ['medication', 'indication', 'treats_conditions', 'relationship_properties']
        with out_csv.open('w', encoding='utf8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for row in csv_rows:
                writer.writerow(row)

    return str(out_json), str(out_csv) if csv_rows else (str(out_json), None)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--patient', '-p', required=True, help='Patient id (string or int)')
    args = parser.parse_args()
    patient_id = args.patient

    print(f"Exporting medication reasons for patient {patient_id}")

    neo4j_res = query_neo4j(str(patient_id))
    if neo4j_res.get('error'):
        print(f"Neo4j query skipped/failed: {neo4j_res['error']}")
    else:
        print(f"Neo4j rows: {len(neo4j_res.get('results', []))}")

    mariadb_res = None
    # attempt MariaDB query if patient id is an integer and DB creds present
    try:
        int_pid = int(patient_id)
        mariadb_res = query_mariadb(int_pid)
        if mariadb_res.get('error'):
            print(f"MariaDB query skipped/failed: {mariadb_res['error']}")
        else:
            print(f"MariaDB rows: {len(mariadb_res.get('results', []))}")
    except ValueError:
        print("Skipping MariaDB query because patient id is not an integer")

    out_json, out_csv = save_outputs(patient_id, neo4j_res, mariadb_res)
    print(f"Wrote JSON output to: {out_json}")
    if out_csv:
        print(f"Wrote CSV output to: {out_csv}")


if __name__ == '__main__':
    main()
