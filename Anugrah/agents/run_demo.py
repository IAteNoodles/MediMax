from medimax.graph import build_graph, GraphState

# Demo showing two passes: first missing parameters, second complete

def main():
    graph = build_graph(
        specs_path='medimax/util/model_specs.yaml',
        mcp_url='http://10.26.5.29:8000',
        medgemma_url='http://10.26.5.99:1234'
    )

    # First payload missing many params
    payload1 = {
        'patient_history': 'Patient with history of mild hypertension.',
        'symptoms': 'Occasional chest discomfort.',
        'query': 'Assess cardiovascular risk.',
        'age': 54,
        'gender': 2,
        'height': 175,
        'weight': 88,
        'ap_hi': 145,
        'ap_lo': 95,
    }

    s1 = graph.invoke(GraphState(payload=payload1))
    print('First pass result:', s1.result)

    if s1.result.get('need_more_data'):
        # Simulate backend providing missing params
        for p in s1.result['missing_parameters']:
            # simple mock values
            payload1[p] = 1 if p in ('cholesterol', 'gluc', 'smoke', 'alco', 'active') else 0.0

    s2 = graph.invoke(GraphState(payload=payload1))
    print('Second pass result:', s2.result)

if __name__ == '__main__':
    main()
