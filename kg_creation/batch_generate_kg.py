#!/usr/bin/env python3
"""
Batch Knowledge Graph Generator for MediMax
Generates knowledge graphs for all patients in the database.
"""

import os
import sys
import logging
from typing import Dict, List
from create_kg_production import create_knowledge_graph_for_patient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_kg_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_all_patient_knowledge_graphs():
    """Generate knowledge graphs for all patients in the database."""
    logger.info("Starting batch knowledge graph generation for all patients")
    
    # Patient IDs to process (in production, get this from database)
    # In production: result = mcp_hospitaldb_ExecuteQuery_MariaDB("SELECT Patient_ID FROM Patient")
    patient_ids = [1, 2, 3, 4, 5]  # Sample patient IDs
    
    results = {
        'successful': [],
        'failed': [],
        'total_nodes': 0,
        'total_relationships': 0
    }
    
    for patient_id in patient_ids:
        try:
            logger.info(f"Processing Patient ID: {patient_id}")
            
            # Create output directory for this patient
            output_dir = f"patient_{patient_id}_kg"
            os.makedirs(output_dir, exist_ok=True)
            
            # Change to patient directory
            original_dir = os.getcwd()
            os.chdir(output_dir)
            
            try:
                # Generate knowledge graph
                nodes, relationships = create_knowledge_graph_for_patient(patient_id)
                
                if nodes and relationships:
                    results['successful'].append(patient_id)
                    results['total_nodes'] += len(nodes)
                    results['total_relationships'] += len(relationships)
                    
                    logger.info(f"Patient {patient_id}: {len(nodes)} nodes, {len(relationships)} relationships")
                else:
                    results['failed'].append(patient_id)
                    logger.warning(f"Patient {patient_id}: No data generated")
                    
            finally:
                # Return to original directory
                os.chdir(original_dir)
                
        except Exception as e:
            logger.error(f"Failed to process Patient {patient_id}: {e}")
            results['failed'].append(patient_id)
    
    # Print summary
    logger.info("\nBatch Generation Summary:")
    logger.info(f"Successfully processed: {len(results['successful'])} patients")
    logger.info(f"Failed: {len(results['failed'])} patients")
    logger.info(f"Total nodes created: {results['total_nodes']}")
    logger.info(f"Total relationships created: {results['total_relationships']}")
    
    if results['successful']:
        logger.info(f"Successful patients: {results['successful']}")
    
    if results['failed']:
        logger.warning(f"Failed patients: {results['failed']}")
    
    return results

def generate_combined_knowledge_graph():
    """Generate a single combined knowledge graph for all patients."""
    logger.info("Generating combined knowledge graph for all patients")
    
    patient_ids = [1, 2, 3, 4, 5]  # Sample patient IDs
    all_nodes = []
    all_relationships = []
    
    for patient_id in patient_ids:
        try:
            logger.info(f"Adding Patient {patient_id} to combined graph")
            nodes, relationships = create_knowledge_graph_for_patient(patient_id)
            
            # Add to combined lists
            all_nodes.extend(nodes)
            all_relationships.extend(relationships)
            
        except Exception as e:
            logger.error(f"Failed to add Patient {patient_id} to combined graph: {e}")
    
    # Save combined graph
    if all_nodes and all_relationships:
        # Import the save function
        from create_kg_production import save_knowledge_graph_to_csv
        
        # Create combined directory
        combined_dir = "combined_kg"
        os.makedirs(combined_dir, exist_ok=True)
        
        # Change to combined directory
        original_dir = os.getcwd()
        os.chdir(combined_dir)
        
        try:
            save_knowledge_graph_to_csv(all_nodes, all_relationships)
            logger.info(f"Combined knowledge graph saved with {len(all_nodes)} nodes and {len(all_relationships)} relationships")
        finally:
            os.chdir(original_dir)
    
    return all_nodes, all_relationships

def main():
    """Main execution function."""
    print("MediMax Batch Knowledge Graph Generator")
    print("=====================================")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--combined":
            print("Generating combined knowledge graph...")
            generate_combined_knowledge_graph()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python batch_generate_kg.py              # Generate individual KGs for all patients")
            print("  python batch_generate_kg.py --combined   # Generate single combined KG")
            print("  python batch_generate_kg.py --help       # Show this help")
            return
        else:
            print(f"Unknown option: {sys.argv[1]}")
            return
    else:
        print("Generating individual knowledge graphs...")
        generate_all_patient_knowledge_graphs()
    
    print("\nBatch generation completed!")
    print("Check the generated directories and batch_kg_generation.log for details.")

if __name__ == "__main__":
    main()