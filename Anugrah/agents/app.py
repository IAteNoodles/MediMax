import json
import streamlit as st
from typing import Dict, Any

from medimax.graph import build_graph, GraphState
from medimax.util.specs_loader import ModelSpecs
from medimax.mcp.client import MCPClient
from medimax.llm.medgemma import MedGemmaClient
from medimax.agents.router_agent import RouterAgent

# Enable debug mode
import os
os.environ['MEDIMAX_DEBUG'] = '1'

st.set_page_config(page_title="MediMax Orchestrator Demo", layout="wide")

st.title("🩺 MediMax Multi-Model Orchestration Demo")

st.markdown("""
This Streamlit app lets you interact with the orchestration layer without a backend.
1. Enter patient textual data and numeric parameters.
2. Submit to see if required parameters are missing or receive model predictions & report.
3. Provide additional parameters iteratively until complete.
""")

with st.sidebar:
    st.header("Configuration")
    mcp_url = st.text_input("MCP Server Base URL", value="http://10.26.5.29:8000")
    medgemma_url = st.text_input("MedGemma Base URL", value="http://10.26.5.29:11434")
    use_groq = st.toggle("Use Groq LLM Agents (required)", value=True, help="LLM-based agents require Groq API")
    mock_mode = st.toggle("Mock LLM / MCP (offline)", value=False)
    
    if not use_groq:
        st.error("⚠️ LLM-based agents require Groq API. Toggle must be enabled.")
    
    run_button_label = "Run Inference" if not st.session_state.get('need_more_data') else "Provide Missing & Re-run"

# Session state containers
if 'payload' not in st.session_state:
    st.session_state.payload = {}
if 'need_more_data' not in st.session_state:
    st.session_state.need_more_data = False
if 'missing' not in st.session_state:
    st.session_state.missing = []
if 'history' not in st.session_state:
    st.session_state.history = []

st.subheader("Patient Context")
col1, col2 = st.columns(2)
with col1:
    patient_history = st.text_area("Patient History", height=120)
    symptoms = st.text_area("Symptoms", height=120)
with col2:
    medical_report = st.text_area("Medical Report (optional)", height=120)
    query = st.text_input("Query", value="Assess cardiovascular and diabetes risk")

st.subheader("Numeric / Categorical Parameters")
param_cols = st.columns(4)
fields = [
    ('age', 'int/float'), ('gender', '1=F 2=M'), ('height', 'cm'), ('weight', 'kg'),
    ('ap_hi', 'systolic'), ('ap_lo', 'diastolic'), ('cholesterol', '1-3'), ('gluc', '1-3'),
    ('smoke', '0/1'), ('alco', '0/1'), ('active', '0/1'),
    ('hypertension','0/1'), ('heart_disease','0/1'), ('smoking_history','str'), ('bmi','float'),
    ('HbA1c_level','float'), ('blood_glucose_level','float')
]
values: Dict[str, Any] = {}
for i, (fname, help_text) in enumerate(fields):
    with param_cols[i % 4]:
        val = st.text_input(fname, help=help_text)
        if val.strip():
            # Attempt numeric parse
            try:
                if '.' in val:
                    values[fname] = float(val)
                else:
                    values[fname] = int(val)
            except ValueError:
                values[fname] = val

if st.button(run_button_label, type='primary'):
    # Build payload
    payload = {
        'patient_history': patient_history,
        'symptoms': symptoms,
        'medical_report': medical_report,
        'query': query,
        **values
    }
    st.session_state.payload = payload

    # Build components (mock or real)
    if mock_mode:
        # Simple mock result for demo
        class SimpleResult:
            def __init__(self):
                self.need_more_data = len([k for k, v in payload.items() if isinstance(v, (int, float))]) < 5
                self.missing_parameters = ['age', 'gender', 'bp'] if self.need_more_data else []
                self.predictions = [] if self.need_more_data else [{"model": "mock", "prediction": 1}]
                self.report = None if self.need_more_data else "Mock LLM-generated report"
                self.follow_up_questions = [] if self.need_more_data else ["Mock follow-up?"]
                self.routing_explanation = "Mock LLM routing decision"
                self.routing_summary = "Mock patient summary"
                self.status = 'need_more_data' if self.need_more_data else 'complete'
                self.action = self.status
        
        res = SimpleResult()
    else:
        # Check if we should use mock mode due to service unavailability
        use_mock_services = st.sidebar.checkbox("Use Mock Services (when real services are down)", value=False)
        
        # Use real graph
        try:
            if use_mock_services:
                # Simple mock result for full demo
                result = {
                    'status': 'complete',
                    'action': 'complete',
                    'missing_parameters': [],
                    'report': "## Medical Assessment Report (MOCK)\n\nBased on cardiovascular risk analysis:\n- **Risk Level**: High (78% probability)\n- **Key Factors**: Age (55), hypertension, elevated cholesterol (200)\n- **Symptoms**: Headache, fatigue, chest tightness\n\n**Recommendations**:\n1. Continue blood pressure management\n2. Consider cholesterol therapy\n3. Lifestyle modifications\n4. Regular monitoring",
                    'predictions': [{'model': 'cardiovascular_risk', 'prediction': 1, 'probability': 0.78, 'explanation': 'High cardiovascular risk'}],
                    'follow_up_questions': ['Have you experienced chest pain during physical activity?', 'Are you currently on any heart medications?'],
                    'routing_explanation': 'Successfully routed to cardiovascular risk model with complete data (MOCK MODE)',
                    'routing_summary': 'High-risk cardiovascular patient with multiple risk factors'
                }
                st.info("🔧 Using mock services for demonstration. This shows how the system works with complete data and working services.")
            else:
                graph = build_graph(
                    specs_path='medimax/util/model_specs.yaml',
                    mcp_url=mcp_url,
                    medgemma_url=medgemma_url,
                    use_groq=use_groq  # Now always required for LLM agents
                )
                
                # Execute graph with simpler error handling
                state_obj = graph.invoke(GraphState(payload=payload))
                # state_obj is the final GraphState, access result directly
                result = state_obj['result'] if isinstance(state_obj, dict) else state_obj.result
            
            if not result:
                # Fallback if result is empty
                result = {
                    'status': 'error',
                    'routing_explanation': 'Graph execution returned empty result',
                    'need_more_data': True,
                    'missing_parameters': ['Unable to process - check logs']
                }
            
            if not result:
                # Fallback if result is empty
                result = {
                    'status': 'error',
                    'routing_explanation': 'Graph execution returned empty result',
                    'need_more_data': True,
                    'missing_parameters': ['Unable to process - check logs']
                }
        except Exception as e:
            st.error(f"Graph execution failed: {e}")
            result = {
                'status': 'error',
                'routing_explanation': f'Error: {str(e)}',
                'need_more_data': True,
                'missing_parameters': ['System error occurred']
            }
        from dataclasses import dataclass
        @dataclass
        class TempResult:
            need_more_data: bool
            missing_parameters: list[str]
            predictions: list[dict]
            report: str | None
            follow_up_questions: list[str]
            routing_explanation: str | None
            routing_summary: str | None
            status: str | None
            action: str | None
            debug_info: list[str]
        res = TempResult(
            need_more_data=result.get('status') == 'need_more_data',
            missing_parameters=result.get('missing_parameters', []) or [],
            predictions=result.get('predictions', []) or [],
            report=result.get('report'),
            follow_up_questions=result.get('follow_up_questions', []) or [],
            routing_explanation=result.get('routing_explanation'),
            routing_summary=result.get('routing_summary'),
            status=result.get('status'),
            action=result.get('action'),
            debug_info=result.get('debug_info', []) or []
        )

    # Handle both old and new response formats
    need_more = res.need_more_data
    if hasattr(res, 'status') and getattr(res, 'status', None) == 'need_more_data':
        need_more = True
    
    st.session_state.need_more_data = need_more
    st.session_state.missing = res.missing_parameters if need_more else []
    # Append history
    st.session_state.history.append({
        'input': payload,
        'need_more_data': need_more,
        'missing': res.missing_parameters if need_more else [],
        'predictions': getattr(res, 'predictions', []),
        'report': getattr(res, 'report', None),
        'follow_up_questions': getattr(res, 'follow_up_questions', []),
        'routing_explanation': getattr(res, 'routing_explanation', None),
        'routing_summary': getattr(res, 'routing_summary', None),
        'status': getattr(res, 'status', None),
        'action': getattr(res, 'action', None),
        'debug_info': getattr(res, 'debug_info', [])
    })

# Display results
st.subheader("Result")
if st.session_state.need_more_data:
    missing_list = st.session_state.missing or []
    st.warning("Additional parameters required: " + ", ".join(missing_list))
else:
    if st.session_state.history:
        latest = st.session_state.history[-1]
        
        # Show debug information first
        debug_info = latest.get('debug_info', [])
        if debug_info:
            st.markdown("### 🐛 Debug Information")
            for i, debug_msg in enumerate(debug_info):
                st.text(f"{i+1}. {debug_msg}")
        
        preds = latest.get('predictions', [])
        if preds:
            st.markdown("### Model Predictions")
            for p in preds:
                st.json(p)
        if latest.get('routing_summary'):
            st.markdown("### Routing Summary (Groq)")
            st.info(latest['routing_summary'])
        if latest.get('routing_explanation'):
            st.markdown("### Routing Explanation (Groq)")
            st.code(latest['routing_explanation'])
        if latest.get('report'):
            st.markdown("### Report")
            st.write(latest['report'])
        if latest.get('follow_up_questions'):
            st.markdown("### Follow-up Questions")
            for q in latest['follow_up_questions']:
                st.write("- " + q)

st.subheader("Interaction History")
for i, entry in enumerate(st.session_state.history):
    with st.expander(f"Attempt {i+1}"):
        st.json(entry)

st.caption("Prototype demo - not for clinical use.")
