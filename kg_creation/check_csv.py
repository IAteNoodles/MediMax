#!/usr/bin/env python3
"""
Check unified CSV content
"""

import pandas as pd

df = pd.read_csv('medimax_unified_knowledge_graph.csv')
print('Total records:', len(df))
print('\nNode types:')
print(df['node_type'].value_counts())
print('\nPatients:')
patient_nodes = df[df['node_type'] == 'node']
patients = patient_nodes[patient_nodes['entity_type'] == 'Patient']
print(patients[['id', 'name']].to_string(index=False))