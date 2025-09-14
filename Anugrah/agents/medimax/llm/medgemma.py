from __future__ import annotations
import httpx
from typing import Dict, List, Any

class MedGemmaClient:
    """Client for MedGemma LLM via Ollama API endpoints."""

    def __init__(self, base_url: str, model: str = "alibayram/medgemma:4b", timeout: float = 60.0):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self._client = httpx.Client(timeout=timeout)

    def generate_report(self, context: str, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate medical report using Ollama API /api/generate endpoint."""
        
        print(f"[MEDGEMMA DEBUG] Generating report with {len(predictions)} predictions")
        print(f"[MEDGEMMA DEBUG] Making request to: {self.base_url}/api/generate")
        
        # Build comprehensive prompt for medical report
        prompt = self._build_medical_prompt(context, predictions)
        
        try:
            response = self._client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 1000
                    }
                }
            )
            response.raise_for_status()
            
            data = response.json()
            report_content = data.get("response", "")
            
            print(f"[MEDGEMMA DEBUG] Got response length: {len(report_content)} chars")
            
            return {
                "content": report_content,
                "raw": data
            }
            
        except Exception as e:
            print(f"[MEDGEMMA DEBUG] Error: {e}")
            return {
                "content": f"Error generating medical report: {str(e)}",
                "error": True
            }

    def _build_medical_prompt(self, context: str, predictions: List[Dict[str, Any]]) -> str:
        """Build a comprehensive medical report prompt for MedGemma."""
        
        prompt_parts = [
            "You are a medical AI assistant. Generate a comprehensive medical assessment report based on the following information:",
            "",
            "## Patient Context:",
            context,
            "",
            "## Model Predictions:"
        ]
        
        if predictions:
            for pred in predictions:
                model_name = pred.get('model', 'Unknown')
                prediction = pred.get('prediction', 'N/A')
                probability = pred.get('probability', 'N/A')
                explanation = pred.get('explanation', 'No explanation provided')
                
                prompt_parts.extend([
                    f"### {model_name.replace('_', ' ').title()}:",
                    f"- Prediction: {prediction}",
                    f"- Probability: {probability}",
                    f"- Explanation: {explanation}",
                    ""
                ])
        else:
            prompt_parts.append("No model predictions available.")
            
        prompt_parts.extend([
            "",
            "## Instructions:",
            "Generate a structured medical report that includes:",
            "1. **Patient Summary**: Brief overview of the case",
            "2. **Risk Assessment**: Analysis based on the model predictions", 
            "3. **Clinical Findings**: Key medical factors identified",
            "4. **Recommendations**: Specific medical advice and next steps",
            "5. **Follow-up**: Suggested monitoring or additional tests",
            "",
            "Keep the report professional, concise, and medically accurate. Use proper medical terminology.",
            "Format the response in clear sections with headers."
        ])
        
        return "\n".join(prompt_parts)

    def _build_user_content(self, context: str, predictions: List[Dict[str, Any]]) -> str:
        pred_lines = []
        for p in predictions:
            model = p.get("model")
            pred = p.get("prediction")
            prob = p.get("probability")
            expl = p.get("explanation")
            pred_lines.append(f"Model={model} prediction={pred} prob={prob} explanation={expl}")
        pred_block = "\n".join(pred_lines) if pred_lines else "(no predictions)"
        return f"Patient Context:\n{context}\n\nPredictions:\n{pred_block}\n\nReturn JSON with keys: report, follow_up_questions"

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
