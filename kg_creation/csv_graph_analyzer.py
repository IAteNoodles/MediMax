#!/usr/bin/env python3
"""
CSV-based Knowledge Graph Analysis Tool
This tool provides graph analysis capabilities using CSV files without requiring Neo4j.
"""

import csv
import json
import logging
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CSVKnowledgeGraph:
    """A knowledge graph implementation using CSV files."""
    
    def __init__(self, unified_csv_file: str):
        """Initialize the knowledge graph from unified CSV."""
        self.nodes = {}
        self.relationships = []
        self.node_relationships = defaultdict(list)
        self.load_from_csv(unified_csv_file)
    
    def load_from_csv(self, csv_file: str):
        """Load the knowledge graph from unified CSV."""
        logger.info(f"Loading knowledge graph from {csv_file}")
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if row['type'] == 'NODE':
                    # Process node
                    node_id = row['id']
                    self.nodes[node_id] = {
                        'id': node_id,
                        'name': row['name'],
                        'category': row['category'],
                        'date': row['date'],
                        'status': row['status'],
                        'details': row['details'],
                        'properties': json.loads(row['properties']) if row['properties'] else {}
                    }
                    
                elif row['type'] == 'RELATIONSHIP':
                    # Process relationship
                    rel = {
                        'source_id': row['source_id'],
                        'target_id': row['target_id'],
                        'relationship_type': row['relationship_type'],
                        'date': row['date'],
                        'status': row['status'],
                        'details': row['details'],
                        'properties': json.loads(row['properties']) if row['properties'] else {}
                    }
                    self.relationships.append(rel)
                    
                    # Index relationships by nodes
                    self.node_relationships[row['source_id']].append(rel)
        
        logger.info(f"Loaded {len(self.nodes)} nodes and {len(self.relationships)} relationships")
    
    def get_node(self, node_id: str) -> Dict:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_nodes_by_category(self, category: str) -> List[Dict]:
        """Get all nodes of a specific category."""
        return [node for node in self.nodes.values() if node['category'] == category]
    
    def get_relationships_for_node(self, node_id: str) -> List[Dict]:
        """Get all relationships for a node."""
        relationships = []
        
        # Outgoing relationships
        relationships.extend(self.node_relationships.get(node_id, []))
        
        # Incoming relationships
        for rel in self.relationships:
            if rel['target_id'] == node_id:
                relationships.append(rel)
        
        return relationships
    
    def find_connected_nodes(self, node_id: str, relationship_type: str = None) -> List[Dict]:
        """Find nodes connected to a given node."""
        connected = []
        
        for rel in self.get_relationships_for_node(node_id):
            if relationship_type and rel['relationship_type'] != relationship_type:
                continue
                
            # Find the connected node
            connected_id = rel['target_id'] if rel['source_id'] == node_id else rel['source_id']
            connected_node = self.get_node(connected_id)
            if connected_node:
                connected.append({
                    'node': connected_node,
                    'relationship': rel
                })
        
        return connected
    
    def get_patient_summary(self, patient_name: str = None) -> Dict:
        """Get a comprehensive summary for a patient."""
        # Find patient node
        patients = self.get_nodes_by_category('Patient')
        
        if patient_name:
            patient = next((p for p in patients if p['name'] == patient_name), None)
            if not patient:
                return {"error": f"Patient '{patient_name}' not found"}
        else:
            patient = patients[0] if patients else None
            if not patient:
                return {"error": "No patients found"}
        
        # Get all connected information
        symptoms = self.find_connected_nodes(patient['id'], 'has_symptom')
        medications = self.find_connected_nodes(patient['id'], 'prescribed_medication')
        encounters = self.find_connected_nodes(patient['id'], 'has_encounter')
        lab_tests = self.find_connected_nodes(patient['id'], 'has_lab_test')
        
        return {
            'patient': patient,
            'symptoms': [{'name': s['node']['name'], 'details': s['node']['details']} for s in symptoms],
            'medications': [{'name': m['node']['name'], 'details': m['node']['details']} for m in medications],
            'encounters': [{'name': e['node']['name'], 'date': e['node']['date'], 'status': e['node']['status']} for e in encounters],
            'lab_tests': [{'name': l['node']['name'], 'details': l['node']['details']} for l in lab_tests]
        }
    
    def analyze_graph_statistics(self) -> Dict:
        """Analyze the knowledge graph and return statistics."""
        stats = {
            'total_nodes': len(self.nodes),
            'total_relationships': len(self.relationships),
            'node_categories': {},
            'relationship_types': {},
            'most_connected_nodes': []
        }
        
        # Count nodes by category
        for node in self.nodes.values():
            category = node['category']
            stats['node_categories'][category] = stats['node_categories'].get(category, 0) + 1
        
        # Count relationships by type
        for rel in self.relationships:
            rel_type = rel['relationship_type']
            stats['relationship_types'][rel_type] = stats['relationship_types'].get(rel_type, 0) + 1
        
        # Find most connected nodes
        connection_counts = {}
        for node_id in self.nodes.keys():
            connection_counts[node_id] = len(self.get_relationships_for_node(node_id))
        
        # Sort by connection count
        sorted_connections = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)
        for node_id, count in sorted_connections[:10]:
            node = self.get_node(node_id)
            stats['most_connected_nodes'].append({
                'name': node['name'],
                'category': node['category'],
                'connections': count
            })
        
        return stats
    
    def search_nodes(self, search_term: str) -> List[Dict]:
        """Search for nodes containing the search term."""
        results = []
        search_lower = search_term.lower()
        
        for node in self.nodes.values():
            if (search_lower in node['name'].lower() or 
                search_lower in node.get('details', '').lower()):
                results.append(node)
        
        return results
    
    def export_to_json(self, filename: str):
        """Export the knowledge graph to JSON format."""
        export_data = {
            'nodes': list(self.nodes.values()),
            'relationships': self.relationships,
            'metadata': {
                'total_nodes': len(self.nodes),
                'total_relationships': len(self.relationships),
                'categories': list(set(node['category'] for node in self.nodes.values())),
                'relationship_types': list(set(rel['relationship_type'] for rel in self.relationships))
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported knowledge graph to {filename}")

def main():
    """Main function to demonstrate the CSV knowledge graph."""
    csv_file = 'medimax_unified_knowledge_graph.csv'
    
    if not os.path.exists(csv_file):
        logger.error(f"CSV file not found: {csv_file}")
        logger.info("Please run unified_export.py first to generate the CSV file")
        return
    
    # Load the knowledge graph
    kg = CSVKnowledgeGraph(csv_file)
    
    # Display statistics
    logger.info("\n" + "="*60)
    logger.info("KNOWLEDGE GRAPH ANALYSIS")
    logger.info("="*60)
    
    stats = kg.analyze_graph_statistics()
    
    logger.info(f"Total Nodes: {stats['total_nodes']}")
    logger.info(f"Total Relationships: {stats['total_relationships']}")
    
    logger.info("\nNode Categories:")
    for category, count in stats['node_categories'].items():
        logger.info(f"  {category}: {count}")
    
    logger.info("\nRelationship Types:")
    for rel_type, count in stats['relationship_types'].items():
        logger.info(f"  {rel_type}: {count}")
    
    logger.info("\nMost Connected Nodes:")
    for node in stats['most_connected_nodes'][:5]:
        logger.info(f"  {node['name']} ({node['category']}): {node['connections']} connections")
    
    # Show patient summaries
    logger.info("\n" + "="*60)
    logger.info("PATIENT SUMMARIES")
    logger.info("="*60)
    
    patients = kg.get_nodes_by_category('Patient')
    for patient in patients:
        summary = kg.get_patient_summary(patient['name'])
        
        logger.info(f"\nPatient: {summary['patient']['name']}")
        logger.info(f"DOB: {summary['patient']['properties'].get('dob', 'N/A')}")
        logger.info(f"Sex: {summary['patient']['properties'].get('sex', 'N/A')}")
        logger.info(f"Symptoms: {len(summary['symptoms'])}")
        logger.info(f"Medications: {len(summary['medications'])}")
        logger.info(f"Encounters: {len(summary['encounters'])}")
        logger.info(f"Lab Tests: {len(summary['lab_tests'])}")
    
    # Export to JSON
    kg.export_to_json('knowledge_graph.json')
    
    # Interactive queries
    logger.info("\n" + "="*60)
    logger.info("INTERACTIVE ANALYSIS")
    logger.info("="*60)
    logger.info("Available commands:")
    logger.info("  1. Search for 'diabetes' related entries")
    logger.info("  2. Search for 'hypertension' related entries")
    logger.info("  3. Search for 'medication' related entries")
    
    # Example searches
    searches = ['diabetes', 'hypertension', 'medication']
    for search_term in searches:
        results = kg.search_nodes(search_term)
        logger.info(f"\nSearch results for '{search_term}': {len(results)} matches")
        for result in results[:3]:  # Show first 3 results
            logger.info(f"  - {result['name']} ({result['category']})")

if __name__ == "__main__":
    main()