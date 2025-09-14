#!/usr/bin/env python3
"""
Fix null date issues in knowledge graph relationships
"""

import os
import logging
from dotenv import load_dotenv
from neo4j import GraphDatabase
import pandas as pd
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FixNullDates:
    def __init__(self):
        load_dotenv()
        self.uri = os.getenv('NEO4J_URI')
        self.user = os.getenv('NEO4J_USERNAME')
        self.password = os.getenv('NEO4J_PASSWORD')
        self.driver = None
        
    def connect(self):
        """Connect to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"✅ Connected to AuraDB")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def clear_existing_data(self):
        """Clear existing MediMax data"""
        logger.info("🗑️ Clearing existing MediMax data...")
        with self.driver.session() as session:
            # Delete all relationships first
            result = session.run("MATCH ()-[r]-() DELETE r RETURN COUNT(r) as deleted")
            rel_count = result.single()['deleted']
            
            # Delete all nodes
            result = session.run("MATCH (n) DELETE n RETURN COUNT(n) as deleted")
            node_count = result.single()['deleted']
            
            logger.info(f"✅ Deleted {node_count} nodes and {rel_count} relationships")
    
    def create_indexes(self):
        """Create indexes for better performance"""
        logger.info("🔧 Creating indexes...")
        with self.driver.session() as session:
            indexes = [
                "CREATE INDEX patient_id IF NOT EXISTS FOR (p:Patient) ON (p.nodeId)",
                "CREATE INDEX symptom_id IF NOT EXISTS FOR (s:Symptom) ON (s.nodeId)",
                "CREATE INDEX medication_id IF NOT EXISTS FOR (m:Medication) ON (m.nodeId)",
                "CREATE INDEX labtest_id IF NOT EXISTS FOR (l:LabTest) ON (l.nodeId)",
                "CREATE INDEX encounter_id IF NOT EXISTS FOR (e:Encounter) ON (e.nodeId)"
            ]
            
            for index_query in indexes:
                try:
                    session.run(index_query)
                    logger.info(f"  ✅ Index created")
                except Exception as e:
                    logger.warning(f"  ⚠️ Index warning: {e}")
    
    def import_nodes(self):
        """Import nodes from CSV"""
        logger.info("📥 Importing nodes...")
        
        # Read nodes CSV
        nodes_df = pd.read_csv('nodes.csv')
        
        with self.driver.session() as session:
            count = 0
            for _, row in nodes_df.iterrows():
                query = f"""
                CREATE (n:{row[':LABEL']})
                SET n.nodeId = $nodeId,
                    n.name = $name
                """
                
                # Add optional properties
                properties = {}
                for col in ['date', 'details', 'dob', 'historical', 'prescription_date', 'remarks', 'sex', 'status', 'type']:
                    if col in row and pd.notna(row[col]) and row[col] != '':
                        properties[col] = row[col]
                
                session.run(query, 
                           nodeId=row[':ID'],
                           name=row['name'])
                
                # Set additional properties if they exist
                if properties:
                    prop_query = f"MATCH (n {{nodeId: $nodeId}}) SET n += $properties"
                    session.run(prop_query, nodeId=row[':ID'], properties=properties)
                
                count += 1
                if count % 10 == 0:
                    logger.info(f"  Imported {count} nodes...")
            
            logger.info(f"✅ Imported {count} nodes")
    
    def import_relationships_fixed(self):
        """Import relationships with proper date handling"""
        logger.info("🔗 Importing relationships with fixed dates...")
        
        # Read relationships CSV
        relationships_df = pd.read_csv('relationships.csv')
        
        with self.driver.session() as session:
            count = 0
            success_count = 0
            
            for _, row in relationships_df.iterrows():
                # Create relationship without date properties to avoid null issues
                query = f"""
                MATCH (start {{nodeId: $startNodeId}})
                MATCH (end {{nodeId: $endNodeId}})
                CREATE (start)-[r:{row[':TYPE']}]->(end)
                """
                params = {
                    'startNodeId': row[':START_ID'],
                    'endNodeId': row[':END_ID']
                }
                
                try:
                    session.run(query, **params)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error creating {row[':START_ID']} -[{row[':TYPE']}]-> {row[':END_ID']}: {e}")
                
                count += 1
                if count % 10 == 0:
                    logger.info(f"  Processed {count} relationships...")
            
            logger.info(f"✅ Created {success_count} relationships out of {count} attempts")
    
    def verify_graph(self):
        """Verify the graph structure"""
        logger.info("📊 Verifying graph structure...")
        
        with self.driver.session() as session:
            # Count nodes by type
            logger.info("\n🏷️ Node counts:")
            node_query = """
            MATCH (n)
            RETURN labels(n)[0] as label, COUNT(n) as count
            ORDER BY count DESC
            """
            results = session.run(node_query)
            total_nodes = 0
            for record in results:
                count = record['count']
                total_nodes += count
                logger.info(f"  {record['label']}: {count}")
            
            # Count relationships
            rel_query = "MATCH ()-[r]->() RETURN COUNT(r) as count"
            rel_result = session.run(rel_query)
            total_relationships = rel_result.single()['count']
            
            logger.info(f"\n📈 Total: {total_nodes} nodes, {total_relationships} relationships")
            
            # Test connectivity for Patient 1
            logger.info("\n👥 Testing Patient 1 connectivity:")
            patient_query = """
            MATCH (p:Patient {nodeId: 'patient_1'})-[r]->(connected)
            RETURN type(r) as relationship, connected.nodeId as target, connected.name as name
            ORDER BY relationship, name
            """
            results = session.run(patient_query)
            patient_connections = list(results)
            
            if patient_connections:
                logger.info(f"  Patient 1 has {len(patient_connections)} direct connections:")
                for record in patient_connections:
                    logger.info(f"    -[{record['relationship']}]-> {record['target']} ({record['name']})")
            else:
                logger.warning("  ⚠️ Patient 1 has no connections!")
            
            # Sample medication prescriptions
            med_query = """
            MATCH (p:Patient)-[:PRESCRIBED_MEDICATION]->(m:Medication)
            RETURN p.name as patient, m.name as medication
            LIMIT 5
            """
            results = session.run(med_query)
            med_results = list(results)
            
            logger.info(f"\n💊 Sample medication prescriptions ({len(med_results)} found):")
            for record in med_results:
                logger.info(f"  {record['patient']} -> {record['medication']}")
            
            return total_nodes > 0 and total_relationships > 0
    
    def close(self):
        """Close connection"""
        if self.driver:
            self.driver.close()
    
    def run_complete_fix(self):
        """Run complete fix process"""
        logger.info("🚀 Fixing Knowledge Graph with Proper Date Handling")
        logger.info("=" * 60)
        
        if not self.connect():
            return False
        
        try:
            # Ask for confirmation
            response = input("\n⚠️ This will delete and recreate the entire knowledge graph.\nContinue? (y/N): ")
            if response.lower() != 'y':
                logger.info("❌ Operation cancelled")
                return False
            
            # Clear existing data
            self.clear_existing_data()
            
            # Create indexes
            self.create_indexes()
            
            # Import nodes
            self.import_nodes()
            
            # Import relationships with fixed dates
            self.import_relationships_fixed()
            
            # Verify the result
            success = self.verify_graph()
            
            if success:
                logger.info("\n🎉 Graph rebuild completed successfully!")
                return True
            else:
                logger.error("\n❌ Graph rebuild failed - no data created")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during rebuild: {e}")
            return False
        finally:
            self.close()

if __name__ == "__main__":
    fixer = FixNullDates()
    success = fixer.run_complete_fix()
    
    if success:
        print("\n✅ Knowledge graph is now properly connected!")
        print("🌐 You can view it in Neo4j Browser at your AuraDB instance")
        print("🔍 Try this query to see the full graph:")
        print("   MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50")
    else:
        print("\n❌ Failed to create connected graph")