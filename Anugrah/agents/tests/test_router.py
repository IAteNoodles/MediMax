import json
from medimax.util.specs_loader import ModelSpecs
from medimax.agents.router_agent import RouterAgent
from medimax.agents.main_agent import MainAgent
from medimax.llm.groq_client import GroqLLM
from medimax.mcp.client import MCPClient


class DummyMCP:
    def predict_cardio(self, **params):
        return {"prediction": 1, "probability": 0.8, "explanation": "Mock cardio"}
    def predict_diabetes(self, **params):
        return {"prediction": 0, "probability": 0.2, "explanation": "Mock diabetes"}
    def close(self):
        pass

class DummyMedGemma:
    def generate_report(self, context, predictions):
        return {"content": json.dumps({"report": "All good", "follow_up_questions": ["Any allergies?"]})}

class DummyGroq:
    def chat(self, messages, temperature=0.2, max_tokens=1024):
        # Mock LLM responses for different scenarios
        user_content = messages[-1].get('content', '') if messages else ''
        
        if 'orchestration' in user_content.lower() or 'analyze this patient' in user_content.lower():
            # Main agent decision
            return '{"action": "route_to_models", "reasoning": "Sufficient data for assessment", "next_agent": "router"}'
        elif 'routing' in user_content.lower() or 'which models' in user_content.lower():
            # Router agent decision
            return '{"decision": "invoke", "models_to_invoke": ["cardiovascular_risk"], "reasoning": "Cardiovascular parameters available"}'
        elif 'summarize' in user_content.lower():
            # Summary request
            return "Mock patient summary: 54-year-old with cardiovascular risk factors"
        else:
            return "Mock LLM response"
    
    def summarize_for_routing(self, payload):
        return "Mock summary: patient context"
    
    def routing_explanation(self, numeric, models_status):
        return "Mock explanation: routing decision"


def build_router():
    specs = ModelSpecs('medimax/util/model_specs.yaml')
    return RouterAgent(specs, DummyMedGemma(), DummyMCP(), DummyGroq())

def build_main_agent():
    return MainAgent(DummyGroq())


def test_missing_params_branch():
    """Test LLM-based router with missing parameters."""
    router = build_router()
    payload = {"age": 50}  # minimal data
    res = router.route(payload)
    
    # Should trigger fallback routing due to insufficient LLM context
    assert res.need_more_data is True or res.predictions is not None
    assert res.routing_explanation is not None


def test_complete_cardio_model():
    """Test LLM-based router with complete cardiovascular parameters."""
    router = build_router()
    payload = {
        'age': 54,
        'gender': 2,
        'height': 175,
        'weight': 80,
        'ap_hi': 140,
        'ap_lo': 90,
        'cholesterol': 2,
        'gluc': 1,
        'smoke': 0,
        'alco': 0,
        'active': 1,
        'patient_history': 'Hypertensive patient',
        'symptoms': 'Chest pain'
    }
    res = router.route(payload)
    
    # LLM should decide to invoke models or request more data
    assert res.routing_explanation is not None
    assert isinstance(res.predictions, list)


def test_main_agent_llm_orchestration():
    """Test LLM-based main agent orchestration."""
    main = build_main_agent()
    payload = {
        'patient_history': '54-year-old male with hypertension',
        'symptoms': 'Chest pain, shortness of breath',
        'query': 'Assess cardiovascular risk',
        'age': 54,
        'gender': 2
    }
    
    resp = main.handle(payload)
    
    # Main agent should make LLM-based decision
    assert resp.action in ['route_to_models', 'need_more_data', 'complete']
    assert resp.routing_explanation is not None
    assert resp.routing_summary is not None
