from medimax.util.specs_loader import ModelSpecs
from medimax.agents.router_agent import RouterAgent
from medimax.mcp.client import MCPClient
from medimax.llm.medgemma import MedGemmaClient
import os

# Enable debug
os.environ['MEDIMAX_DEBUG'] = '1'

specs = ModelSpecs('medimax/util/model_specs.yaml')
# Dummy clients to avoid network in this quick check
class DummyMCP(MCPClient):
    def __init__(self):
        pass
    def predict_cardio(self, **params):
        print('[DummyMCP] cardio invoked unexpectedly with', params)
        return {"prediction": 0}
    def predict_diabetes(self, **params):
        print('[DummyMCP] diabetes invoked unexpectedly with', params)
        return {"prediction": 0}
    def close(self):
        pass
class DummyMed:
    def generate_report(self, context, predictions):
        return {"content": "{}"}

router = RouterAgent(specs, DummyMed(), DummyMCP())

payload = {
    'patient_history': '54-year-old with mild hypertension.',
    'symptoms': 'Occasional chest pressure.',
    'query': 'Assess cardiovascular risk.',
    'age': 54,
    'gender': 2,
    'ap_hi': 145,
    'ap_lo': 95
}

res = router.route(payload)
print('Result:', res)
