from __future__ import annotations
from typing import Dict, Any, Protocol, List
from dataclasses import dataclass
import json
from medimax.llm.groq_client import GroqLLM

class GroqLike(Protocol):
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> str: ...
    def summarize_for_routing(self, payload: Dict[str, Any]) -> str: ...
    def routing_explanation(self, numeric: Dict[str, Any], models_status: Dict[str, Any]) -> str: ...

@dataclass
class MainAgentResponse:
    status: str  # 'need_more_data' | 'complete' | 'route_to_models'
    action: str  # 'collect_params' | 'route' | 'complete'
    missing_parameters: list[str] | None = None
    report: str | None = None
    predictions: list[dict] | None = None
    follow_up_questions: list[str] | None = None
    routing_explanation: str | None = None
    routing_summary: str | None = None
    next_agent: str | None = None  # 'router' | None
    enhanced_payload: Dict[str, Any] | None = None  # Structured data extracted from text

class MainAgent:
    """LLM-based main orchestration agent using Groq llama-3.1-8b-instant."""
    
    def __init__(self, groq: GroqLike):
        self.groq = groq

    def handle(self, payload: Dict[str, Any]) -> MainAgentResponse:
        """Use LLM to analyze payload and make orchestration decisions."""
        
        # First, extract structured data from free-form text if needed
        if 'patient_text' in payload:
            payload = self._extract_structured_data(payload)
            # Store the enhanced payload for use by subsequent agents
            self._enhanced_payload = payload
        
        # Build context for LLM decision making
        context = self._build_context(payload)
        
        # LLM prompt for orchestration decision
        system_prompt = f"""You are the Main Agent in a medical AI orchestration system. Your job is to analyze patient data and decide the next action.

Available actions:
1. "route_to_models" - if you have sufficient data for risk assessment, route to model execution
2. "need_more_data" - if critical parameters are missing, request more information
3. "complete" - if this is a follow-up with complete results

For routing decisions, consider these medical models:
- Cardiovascular Risk: needs age, gender, height, weight, blood pressure (ap_hi, ap_lo), cholesterol, glucose, smoking, alcohol, activity
- Diabetes Risk: needs age, gender, hypertension status, heart disease, smoking history, BMI, HbA1c, blood glucose

IMPORTANT: Respond ONLY with valid JSON in this exact format:
{{"action": "route_to_models|need_more_data|complete", "reasoning": "brief explanation", "next_agent": "router", "missing_if_any": ["param1", "param2"]}}"""

        user_prompt = f"""Analyze this patient data and decide the next action:

{context}

Respond with JSON only. If data is sufficient for cardiovascular or diabetes risk assessment, use "route_to_models"."""

        try:
            response = self.groq.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], temperature=0.2)
            
            # Parse LLM decision
            decision = self._parse_llm_decision(response)
            
            response_obj = MainAgentResponse(
                status=decision['action'],
                action=decision['action'], 
                next_agent=decision.get('next_agent'),
                missing_parameters=decision.get('missing_if_any'),
                routing_explanation=decision.get('reasoning'),
                routing_summary=self._summarize_context(payload)
            )
            
            # Store enhanced payload for access by other components
            response_obj.enhanced_payload = payload if hasattr(self, '_enhanced_payload') else None
            
            return response_obj
            
        except Exception as e:
            # Fallback to simple logic if LLM fails
            return self._fallback_decision(payload)

    def _extract_structured_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured medical data from free-form patient text using LLM."""
        patient_text = payload.get('patient_text', '')
        query = payload.get('query', 'Assess medical risk')
        additional_notes = payload.get('additional_notes', '')
        
        # Combine all text sources
        full_text = f"Query: {query}\n\nPatient Information: {patient_text}"
        if additional_notes:
            full_text += f"\n\nAdditional Notes: {additional_notes}"
        
        # LLM prompt for data extraction
        extraction_prompt = """You are a medical data extraction expert. Extract relevant medical information from the patient text and return it as JSON.

Extract these parameters when mentioned (use null if not found):

Cardiovascular Risk Parameters:
- age: patient age in years (integer)
- gender: 0 for female, 1 for male (integer) 
- height: height in cm (float)
- weight: weight in kg (float)
- ap_hi: systolic blood pressure (integer)
- ap_lo: diastolic blood pressure (integer)  
- cholesterol: cholesterol level (float)
- gluc: glucose/blood sugar level (float)
- smoke: smoking status - 0 for no, 1 for yes (integer)
- alco: alcohol consumption - 0 for no, 1 for yes (integer)
- active: physical activity - 0 for no, 1 for yes (integer)

Diabetes Risk Parameters:
- hypertension: hypertension status - 0 for no, 1 for yes (integer)
- heart_disease: heart disease status - 0 for no, 1 for yes (integer)
- smoking_history: smoking history as text (string)
- bmi: body mass index (float)
- HbA1c_level: HbA1c level (float)
- blood_glucose_level: blood glucose level (float)

Clinical Text:
- patient_history: relevant medical history (string)
- symptoms: current symptoms (string)
- medical_report: additional medical findings (string)

IMPORTANT: Return ONLY valid JSON in this format:
{"age": 45, "gender": 1, "height": 175.0, "weight": 80.0, "patient_history": "...", "symptoms": "...", ...}

Use null for any parameter not mentioned in the text."""

        try:
            # Get structured data from LLM
            response = self.groq.chat([
                {"role": "system", "content": extraction_prompt},
                {"role": "user", "content": f"Extract medical data from this text:\n\n{full_text}"}
            ], temperature=0.1, max_tokens=1024)
            
            # Parse the extracted data
            structured_data = self._parse_extracted_data(response)
            
            # Add original query and preserve any existing structured fields
            structured_data['query'] = query
            for key, value in payload.items():
                if key not in ['patient_text', 'additional_notes'] and key not in structured_data:
                    structured_data[key] = value
            
            print(f"[MainAgent DEBUG] Extracted structured data: {structured_data}")
            return structured_data
            
        except Exception as e:
            print(f"[MainAgent ERROR] Data extraction failed: {e}")
            # Fallback - return original payload with minimal structure
            return {
                'query': query,
                'patient_history': patient_text,
                'symptoms': '',
                'medical_report': additional_notes
            }

    def _parse_extracted_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM-extracted data with fallback handling."""
        try:
            # Clean the response
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Find JSON boundaries
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = cleaned[start:end]
                parsed = json.loads(json_str)
                
                # Convert null values and ensure proper types
                for key, value in parsed.items():
                    if value == "null" or value == "None":
                        parsed[key] = None
                
                print(f"[MainAgent DEBUG] Successfully parsed extracted data")
                return parsed
                
        except Exception as e:
            print(f"[MainAgent ERROR] JSON parsing failed for extraction: {e}")
            print(f"[MainAgent DEBUG] Raw extraction response: {response}")
        
        # Return empty structure if parsing fails
        return {}

    def _build_context(self, payload: Dict[str, Any]) -> str:
        """Build readable context for LLM analysis."""
        context_parts = []
        
        # Clinical context
        for field in ['patient_history', 'symptoms', 'medical_report', 'query']:
            if payload.get(field):
                context_parts.append(f"{field.title()}: {payload[field]}")
        
        # Numeric parameters
        numeric_params = {}
        for key, value in payload.items():
            if isinstance(value, (int, float)) and key not in ['query']:
                numeric_params[key] = value
        
        if numeric_params:
            context_parts.append(f"Numeric Parameters: {numeric_params}")
        
        return "\n\n".join(context_parts)

    def _parse_llm_decision(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response with fallbacks."""
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]  # Remove ```json
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]  # Remove ```
            cleaned = cleaned.strip()
            
            # Try to find JSON in response
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = cleaned[start:end]
                parsed = json.loads(json_str)
                
                # Ensure missing_if_any is a list
                if 'missing_if_any' in parsed and parsed['missing_if_any'] is None:
                    parsed['missing_if_any'] = []
                    
                return parsed
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parsing error: {e}")
            print(f"Response: {response}")
        
        # Fallback parsing based on keywords
        if 'route_to_models' in response.lower() or 'route' in response.lower():
            return {'action': 'route_to_models', 'next_agent': 'router', 'reasoning': response, 'missing_if_any': []}
        elif 'need_more_data' in response.lower() or 'missing' in response.lower():
            return {'action': 'need_more_data', 'next_agent': None, 'reasoning': response, 'missing_if_any': []}
        else:
            return {'action': 'need_more_data', 'reasoning': 'Could not parse LLM decision', 'missing_if_any': []}

    def _summarize_context(self, payload: Dict[str, Any]) -> str:
        """Generate concise summary of patient context."""
        try:
            context = self._build_context(payload)
            summary_prompt = f"Summarize this patient context in ≤50 words focusing on key risk factors:\n\n{context}"
            
            return self.groq.chat([
                {"role": "system", "content": "You provide concise medical summaries."},
                {"role": "user", "content": summary_prompt}
            ], temperature=0.1, max_tokens=100)
        except:
            return "Patient context summary unavailable"

    def _fallback_decision(self, payload: Dict[str, Any]) -> MainAgentResponse:
        """Simple fallback logic if LLM fails."""
        # Count numeric parameters
        numeric_count = sum(1 for v in payload.values() if isinstance(v, (int, float)))
        
        if numeric_count >= 8:  # Sufficient for some model
            return MainAgentResponse(
                status='route_to_models',
                action='route_to_models',
                next_agent='router',
                routing_explanation="Fallback: sufficient parameters detected"
            )
        else:
            return MainAgentResponse(
                status='need_more_data', 
                action='need_more_data',
                missing_parameters=['age', 'gender', 'height', 'weight'],
                routing_explanation="Fallback: insufficient parameters"
            )
