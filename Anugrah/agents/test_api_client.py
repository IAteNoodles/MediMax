"""
Example client demonstrating how to interact with the MediMax Multi-Agent API.
This shows how your backend server can integrate with the orchestration system.
"""

import requests
import json
from typing import Dict, Any

class MediMaxAPIClient:
    """Client for interacting with MediMax Multi-Agent API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy and agents are initialized."""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
        
    def assess_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send patient data for multi-agent assessment."""
        response = requests.post(f"{self.base_url}/assess", json=patient_data)
        response.raise_for_status()
        return response.json()
        
    def assess_cardiovascular_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized cardiovascular risk assessment."""
        response = requests.post(f"{self.base_url}/assess/cardiovascular", json=patient_data)
        response.raise_for_status()
        return response.json()
        
    def assess_diabetes_risk(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized diabetes risk assessment."""
        response = requests.post(f"{self.base_url}/assess/diabetes", json=patient_data)
        response.raise_for_status()
        return response.json()
        
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available models and their requirements."""
        response = requests.get(f"{self.base_url}/models")
        response.raise_for_status()
        return response.json()

def demo_api_usage():
    """Demonstrate API usage with sample patient data."""
    
    print("🧪 MediMax Multi-Agent API Demo")
    print("=" * 50)
    
    # Initialize client
    client = MediMaxAPIClient()
    
    # 1. Health check
    print("\\n1. Checking API health...")
    try:
        health = client.health_check()
        print(f"✅ API Status: {health['status']}")
        print(f"   Agents Initialized: {health['agents_initialized']}")
        print(f"   Services: {health['services']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # 2. Get available models
    print("\\n2. Getting available models...")
    try:
        models_info = client.get_available_models()
        print("Available models:")
        for model_name, info in models_info['available_models'].items():
            print(f"   {model_name}:")
            print(f"     Description: {info['description']}")
            print(f"     Required params: {len(info['required_parameters'])} parameters")
    except Exception as e:
        print(f"❌ Models info failed: {e}")
    
    # 3. Sample patient data
    patient_data = {
        "patient_history": "55-year-old male with hypertension",
        "symptoms": "Headache, fatigue, chest tightness",
        "medical_report": "",
        "query": "Assess cardiovascular risk",
        "age": 55,
        "gender": 1,
        "height": 175,
        "weight": 80,
        "ap_hi": 140,
        "ap_lo": 90,
        "cholesterol": 200,
        "gluc": 100,
        "smoke": 0,
        "alco": 0,
        "active": 1
    }
    
    print("\\n3. Patient Assessment...")
    print(f"Patient: {patient_data['patient_history']}")
    print(f"Symptoms: {patient_data['symptoms']}")
    print(f"Query: {patient_data['query']}")
    
    try:
        # General assessment
        result = client.assess_patient(patient_data)
        
        print(f"\\n📊 Assessment Results:")
        print(f"   Status: {result['status']}")
        print(f"   Need more data: {result['need_more_data']}")
        
        if result['need_more_data']:
            print(f"   Missing parameters: {', '.join(result['missing_parameters'])}")
        else:
            print(f"   Number of predictions: {len(result['predictions'])}")
            
            # Show predictions
            for pred in result['predictions']:
                print(f"\\n   🔬 Model: {pred['model']}")
                if pred.get('prediction'):
                    print(f"      Prediction: {pred['prediction']}")
                if pred.get('probability'):
                    print(f"      Probability: {pred['probability']:.2%}")
                if pred.get('raw'):
                    print(f"      Assessment: {pred['raw'][:100]}...")
                    
            # Show report
            if result.get('report'):
                print(f"\\n📋 Generated Report:")
                report_preview = result['report'][:300]
                print(f"   {report_preview}...")
                
            # Show debug info if available
            if result.get('debug_info'):
                print(f"\\n🐛 Debug Information ({len(result['debug_info'])} steps):")
                for i, debug_msg in enumerate(result['debug_info'][:5], 1):
                    print(f"   {i}. {debug_msg}")
                if len(result['debug_info']) > 5:
                    print(f"   ... and {len(result['debug_info']) - 5} more steps")
                    
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
    
    print("\\n" + "=" * 50)
    print("✅ API Demo completed!")

def demo_missing_parameters():
    """Demonstrate iterative parameter collection."""
    
    print("\\n🔄 Iterative Parameter Collection Demo")
    print("=" * 50)
    
    client = MediMaxAPIClient()
    
    # Start with minimal data
    patient_data = {
        "patient_history": "Middle-aged patient with chest pain",
        "symptoms": "Chest pain, shortness of breath",
        "query": "Assess cardiovascular risk",
        "age": 50,
        "gender": 1
    }
    
    print("Starting with minimal patient data...")
    print(f"Available parameters: {list(patient_data.keys())}")
    
    try:
        result = client.assess_patient(patient_data)
        
        if result['need_more_data']:
            print(f"\\n⚠️ More data needed!")
            print(f"Missing parameters: {', '.join(result['missing_parameters'])}")
            print("\\nIn a real backend, you would:")
            print("1. Store the partial assessment state")
            print("2. Request additional parameters from user/database")
            print("3. Call the API again with complete data")
            
        else:
            print("✅ Assessment completed with minimal data")
            
    except Exception as e:
        print(f"❌ Iterative demo failed: {e}")

if __name__ == "__main__":
    # Run the demo
    demo_api_usage()
    demo_missing_parameters()
    
    print("\\n🔗 Integration Guide:")
    print("1. Install requests: pip install requests")
    print("2. Use MediMaxAPIClient class in your backend")
    print("3. Handle responses and missing parameter scenarios") 
    print("4. API Documentation available at: http://localhost:8000/docs")
