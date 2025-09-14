from __future__ import annotations
from typing import Dict, Any, List
from dataclasses import dataclass, field
import json
import os

from medimax.util.specs_loader import ModelSpecs
from medimax.llm.medgemma import MedGemmaClient
from medimax.llm.groq_client import GroqLLM
from medimax.mcp.client import MCPClient
from typing import Protocol, Optional, List, Dict, Any

class GroqLike(Protocol):  # Protocol for LLM functionality
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> str: ...
    def routing_explanation(self, numeric: Dict[str, Any], models_status: Dict[str, Any]) -> str: ...


class MedGemmaClientProto(Protocol):  # existing protocol for LLM
    def generate_report(self, context: str, predictions: List[Dict[str, Any]]) -> Dict[str, Any]: ...

@dataclass
class RouterResult:
    need_more_data: bool
    missing_parameters: List[str] = field(default_factory=list)
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    report: str | None = None
    follow_up_questions: List[str] = field(default_factory=list)
    routing_explanation: str | None = None
    debug_info: List[str] = field(default_factory=list)

class MCPClientProto(Protocol):
    def predict_cardio(self, **params: Any) -> Dict[str, Any]: ...
    def predict_diabetes(self, **params: Any) -> Dict[str, Any]: ...
    def close(self) -> None: ...


class RouterAgent:
    """LLM-based routing agent using Groq llama-3.1-8b-instant for intelligent model selection."""
    
    def __init__(self, specs: ModelSpecs, medgemma: MedGemmaClientProto, mcp_client: MCPClientProto, groq: GroqLike):
        self.specs = specs
        self.medgemma = medgemma
        self.mcp = mcp_client
        self.groq = groq

    def route(self, payload: Dict[str, Any]) -> RouterResult:
        """Use LLM to make intelligent routing decisions based on clinical context."""
        
        # Extract available data
        numeric, text = self._extract(payload)
        model_specs = self._get_model_requirements()
        
        # Build context for LLM routing decision
        context = self._build_routing_context(payload, numeric, model_specs)
        
        # LLM prompt for routing decision
        system_prompt = """You are a medical AI routing agent. Analyze patient data and decide which ML models to invoke.

Available Models:
1. Cardiovascular Risk Model - requires: age, gender, height, weight, ap_hi, ap_lo, cholesterol, gluc, smoke, alco, active
2. Diabetes Risk Model - requires: age, gender, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level

Your job:
- Analyze available patient parameters vs model requirements
- Make clinical judgments about which models are appropriate
- If data is insufficient, identify the most critical missing parameters
- Consider medical urgency and clinical relevance

CRITICAL: You MUST respond with ONLY valid JSON in this exact format:
{"decision": "invoke", "models_to_invoke": ["cardiovascular_risk"], "missing_critical": [], "reasoning": "explanation here"}
OR
{"decision": "need_data", "models_to_invoke": [], "missing_critical": ["param1", "param2"], "reasoning": "explanation here"}

Do NOT include any text before or after the JSON. Do NOT use markdown formatting."""

        user_prompt = f"""Analyze this patient case and return ONLY JSON:

{context}

JSON response only:"""

        debug_log = []
        try:
            debug_log.append(f"Making LLM routing decision...")
            print(f"[RouterAgent DEBUG] Making LLM routing decision...")
            response = self.groq.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ], temperature=0.2)
            
            debug_log.append(f"LLM response: {response}")
            print(f"[RouterAgent DEBUG] LLM response: {response}")
            
            # Parse LLM routing decision
            decision = self._parse_routing_decision(response)
            debug_log.append(f"Parsed decision: {decision}")
            print(f"[RouterAgent DEBUG] Parsed decision: {decision}")
            
            if decision['decision'] == 'need_data':
                debug_log.append(f"LLM decided need_data")
                print(f"[RouterAgent DEBUG] LLM decided need_data")
                return RouterResult(
                    need_more_data=True,
                    missing_parameters=decision.get('missing_critical', []),
                    routing_explanation=decision.get('reasoning'),
                    debug_info=debug_log
                )
            
            debug_log.append(f"LLM decided to invoke models")
            print(f"[RouterAgent DEBUG] LLM decided to invoke models")
            # LLM decided to invoke models
            result = self._execute_model_invocations(decision, numeric, text, payload)
            result.debug_info = debug_log + (result.debug_info or [])
            return result
            
        except Exception as e:
            debug_log.append(f'LLM routing error: {e}')
            print(f'[RouterAgent DEBUG] LLM routing error: {e}')
            import traceback
            traceback.print_exc()
            debug_log.append(f'Exception traceback: {traceback.format_exc()}')
            if os.getenv('MEDIMAX_DEBUG') == '1':
                print(f'[RouterAgent] LLM routing error: {e}')
            # Fallback to rule-based routing
            debug_log.append(f"Falling back to rule-based routing")
            print(f"[RouterAgent DEBUG] Falling back to rule-based routing")
            result = self._fallback_routing(payload)
            result.debug_info = debug_log + (result.debug_info or [])
            return result

    def _build_routing_context(self, payload: Dict[str, Any], numeric: Dict[str, Any], model_specs: Dict) -> str:
        """Build comprehensive context for LLM routing analysis."""
        context_parts = []
        
        # Clinical narrative
        clinical_fields = ['patient_history', 'symptoms', 'medical_report', 'query']
        for field in clinical_fields:
            if payload.get(field):
                context_parts.append(f"{field.title()}: {payload[field]}")
        
        # Available numeric parameters
        if numeric:
            context_parts.append(f"Available Parameters: {numeric}")
        else:
            context_parts.append("Available Parameters: None")
        
        # Model requirements
        context_parts.append("Model Requirements:")
        for model_name, requirements in model_specs.items():
            context_parts.append(f"- {model_name}: {requirements}")
        
        return "\n\n".join(context_parts)

    def _get_model_requirements(self) -> Dict[str, List[str]]:
        """Get model requirements from specs."""
        requirements = {}
        # Access specs.models properly based on ModelSpecs structure
        if hasattr(self.specs, 'models') and isinstance(self.specs.models, dict):
            for model_name, spec in self.specs.models.items():
                requirements[model_name] = spec.get('required_parameters', [])
        else:
            # Fallback for list-based specs
            requirements = {
                'cardiovascular_risk': ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active'],
                'diabetes_risk': ['age', 'gender', 'hypertension', 'heart_disease', 'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level']
            }
        return requirements

    def _parse_routing_decision(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response with fallbacks."""
        print(f"[RouterAgent DEBUG] Parsing LLM response: {response[:500]}...")
        
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            print(f"[RouterAgent DEBUG] JSON boundaries: start={start}, end={end}")
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                print(f"[RouterAgent DEBUG] Extracted JSON: {json_str}")
                parsed = json.loads(json_str)
                print(f"[RouterAgent DEBUG] Parsed JSON successfully: {parsed}")
                return parsed
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[RouterAgent DEBUG] JSON parsing error: {e}")
            pass
        
        # Fallback parsing
        print(f"[RouterAgent DEBUG] Using fallback parsing")
        if 'need_data' in response.lower() or 'missing' in response.lower():
            fallback = {'decision': 'need_data', 'missing_critical': [], 'reasoning': response}
            print(f"[RouterAgent DEBUG] Fallback: need_data - {fallback}")
            return fallback
        else:
            fallback = {'decision': 'invoke', 'models_to_invoke': ['cardiovascular_risk'], 'reasoning': response}
            print(f"[RouterAgent DEBUG] Fallback: invoke - {fallback}")
            return fallback

    def _execute_model_invocations(self, decision: Dict[str, Any], numeric: Dict[str, Any], text: str, payload: Dict[str, Any]) -> RouterResult:
        """Execute the models that LLM decided to invoke."""
        exec_debug = []
        models_to_invoke = decision.get('models_to_invoke', [])
        predictions: List[Dict[str, Any]] = []
        
        exec_debug.append(f"Models to invoke: {models_to_invoke}")
        
        # Map model names to tools and invoke
        model_tool_map = {
            'cardiovascular_risk': 'Predict_Cardiovascular_Risk_With_Explanation',
            'diabetes_risk': 'Predict_Diabetes_Risk_With_Explanation'
        }
        
        # Also handle LLM's natural language model names
        model_name_aliases = {
            'Cardiovascular Risk Model': 'cardiovascular_risk',
            'cardiovascular risk model': 'cardiovascular_risk',
            'cardiovascular risk': 'cardiovascular_risk',
            'Diabetes Risk Model': 'diabetes_risk', 
            'diabetes risk model': 'diabetes_risk',
            'diabetes risk': 'diabetes_risk'
        }
        
        # Normalize model names from LLM response
        normalized_models = []
        for model_name in models_to_invoke:
            if model_name in model_name_aliases:
                normalized_models.append(model_name_aliases[model_name])
            elif model_name in model_tool_map:
                normalized_models.append(model_name)
            else:
                exec_debug.append(f"Unknown model name: {model_name}")
        
        exec_debug.append(f"Normalized models: {normalized_models}")
        
        for model_name in normalized_models:
            if model_name in model_tool_map:
                tool = model_tool_map[model_name]
                try:
                    # Get model requirements and filter available params
                    requirements = self._get_model_requirements()
                    required_params = requirements.get(model_name, [])
                    available_params = {k: v for k, v in numeric.items() if k in required_params}
                    
                    exec_debug.append(f"Invoking {model_name} with params: {list(available_params.keys())}")
                    if os.getenv('MEDIMAX_DEBUG') == '1':
                        print(f'[RouterAgent] Invoking {model_name} with params: {available_params}')
                    
                    print(f'[RouterAgent DEBUG] About to call _invoke_tool for {model_name}')
                    print(f'[RouterAgent DEBUG] Tool: {tool}')
                    print(f'[RouterAgent DEBUG] Available params: {available_params}')
                    
                    prediction_raw = self._invoke_tool(tool, available_params)
                    exec_debug.append(f"Raw prediction result: {prediction_raw}")
                    
                    print(f'[RouterAgent DEBUG] Raw prediction result: {prediction_raw}')
                    
                    if os.getenv('MEDIMAX_DEBUG') == '1':
                        print(f'[RouterAgent] {model_name} returned: {prediction_raw}')
                    
                    pred_entry = {
                        'model': model_name,
                        **prediction_raw
                    }
                    predictions.append(pred_entry)
                    exec_debug.append(f"Added prediction entry: {pred_entry}")
                    print(f'[RouterAgent DEBUG] Added prediction entry: {pred_entry}')
                except Exception as e:
                    exec_debug.append(f"Model invocation error for {model_name}: {e}")
                    if os.getenv('MEDIMAX_DEBUG') == '1':
                        print(f'[RouterAgent] Model invocation error for {model_name}: {e}')
                        import traceback
                        traceback.print_exc()
        
        if not predictions:
            exec_debug.append("No predictions generated - checking for missing parameters")
            # Better fallback - check if we actually have sufficient data
            model_requirements = self._get_model_requirements()
            cardio_required = model_requirements.get('cardiovascular_risk', [])
            cardio_missing = [p for p in cardio_required if p not in numeric]
            
            if not cardio_missing:
                exec_debug.append("All required data present but prediction service failed")
                # We have all required data but MCP failed - return error status
                return RouterResult(
                    need_more_data=False,
                    missing_parameters=[],
                    predictions=[],
                    routing_explanation="Model services are currently unavailable. All required data is present but prediction service failed.",
                    report="Unable to generate predictions due to service unavailability.",
                    debug_info=exec_debug
                )
            else:
                exec_debug.append(f"Missing required parameters: {cardio_missing}")
                # Actually missing required parameters
                return RouterResult(
                    need_more_data=True,
                    missing_parameters=cardio_missing,
                    routing_explanation=f"Missing required parameters: {', '.join(cardio_missing)}",
                    debug_info=exec_debug
                )
        
        exec_debug.append(f"Successfully generated {len(predictions)} predictions")
        # Generate report using MedGemma
        text_context = self._compose_text_context(text, payload.get('query'))
        try:
            exec_debug.append("Calling MedGemma for report generation")
            llm_out = self.medgemma.generate_report(text_context, predictions)
            report_content = llm_out.get('content', '')
            exec_debug.append(f"MedGemma report generated: {len(report_content)} characters")
            
            # Parse JSON from report
            follow_ups: List[str] = []
            report_text = report_content
            try:
                data = json.loads(report_content)
                report_text = data.get('report', report_content)
                follow_ups = data.get('follow_up_questions', [])
            except json.JSONDecodeError:
                pass
                
        except Exception as e:
            exec_debug.append(f"MedGemma error: {e}")
            if os.getenv('MEDIMAX_DEBUG') == '1':
                print(f'[RouterAgent] MedGemma error: {e}')
            report_text = "Report generation failed"
            follow_ups = []

        return RouterResult(
            need_more_data=False,
            predictions=predictions,
            report=report_text,
            follow_up_questions=follow_ups,
            routing_explanation=decision.get('reasoning'),
            debug_info=exec_debug
        )

    def _fallback_routing(self, payload: Dict[str, Any]) -> RouterResult:
        """Fallback to rule-based routing if LLM fails."""
        fallback_debug = ["Using fallback routing due to LLM error"]
        
        numeric, text = self._extract(payload)
        model_matches = self.specs.match_models(numeric)
        
        satisfied_models = [name for name, info in model_matches.items() if not info['missing']]
        fallback_debug.append(f"Satisfied models: {satisfied_models}")
        
        if not satisfied_models:
            # Choose model with smallest number of missing params
            candidate = min(model_matches.items(), key=lambda kv: len(kv[1]['missing']))
            missing = candidate[1]['missing']
            fallback_debug.append(f"No satisfied models, missing: {missing}")
            return RouterResult(
                need_more_data=True, 
                missing_parameters=missing,
                routing_explanation="Fallback routing: insufficient parameters",
                debug_info=fallback_debug
            )
        
        # Execute satisfied models
        predictions: List[Dict[str, Any]] = []
        for model_name in satisfied_models:
            info = model_matches[model_name]
            tool = info['tool']
            params = {k: numeric[k] for k in info['present']}
            try:
                fallback_debug.append(f"Executing fallback model: {model_name}")
                prediction_raw = self._invoke_tool(tool, params)
                pred_entry = {
                    'model': model_name,
                    **prediction_raw
                }
                predictions.append(pred_entry)
                fallback_debug.append(f"Fallback model {model_name} successful")
            except Exception as e:
                fallback_debug.append(f"Fallback model error for {model_name}: {e}")
                if os.getenv('MEDIMAX_DEBUG') == '1':
                    print(f'[RouterAgent] Fallback model error for {model_name}: {e}')

        # Generate report
        text_context = self._compose_text_context(text, payload.get('query'))
        try:
            fallback_debug.append("Calling MedGemma for fallback report")
            llm_out = self.medgemma.generate_report(text_context, predictions)
            report_content = llm_out.get('content', '')
            
            follow_ups: List[str] = []
            report_text = report_content
            try:
                data = json.loads(report_content)
                report_text = data.get('report', report_content)
                follow_ups = data.get('follow_up_questions', [])
            except json.JSONDecodeError:
                pass
                
        except Exception as e:
            fallback_debug.append(f"Fallback MedGemma error: {e}")
            if os.getenv('MEDIMAX_DEBUG') == '1':
                print(f'[RouterAgent] Fallback MedGemma error: {e}')
            report_text = "Fallback report generation failed"
            follow_ups = []

        return RouterResult(
            need_more_data=False,
            predictions=predictions,
            report=report_text,
            follow_up_questions=follow_ups,
            routing_explanation="Fallback routing completed",
            debug_info=fallback_debug
        )

    def _extract(self, payload: Dict[str, Any]):
        # Parameter name mapping from user-friendly to model names
        param_mapping = {
            'glucose': 'gluc',
            'smoking': 'smoke', 
            'alcohol': 'alco',
            'activity': 'active'
        }
        
        numeric = {}
        text_parts = []
        for k, v in payload.items():
            if k in ('query', 'patient_history', 'medical_report', 'symptoms', 'answers'):
                if isinstance(v, str):
                    text_parts.append(f"{k}: {v}")
                continue
            # Parameter candidate
            if isinstance(v, (int, float)):
                # Map parameter name if needed
                mapped_key = param_mapping.get(k, k)
                numeric[mapped_key] = v
            else:
                # Try parse
                try:
                    parsed_val = float(v)
                    mapped_key = param_mapping.get(k, k)
                    numeric[mapped_key] = parsed_val
                except (ValueError, TypeError):
                    # treat as text
                    if isinstance(v, str):
                        text_parts.append(f"{k}: {v}")
        # Add main textual fields
        for field in ['patient_history', 'medical_report', 'symptoms', 'answers']:
            if field in payload and isinstance(payload[field], str):
                # already appended above if str
                pass
        text_context = "\n".join(text_parts)
        return numeric, text_context

    def _invoke_tool(self, tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if tool == 'Predict_Cardiovascular_Risk_With_Explanation':
            return self.mcp.predict_cardio(**params)
        if tool == 'Predict_Diabetes_Risk_With_Explanation':
            return self.mcp.predict_diabetes(**params)
        if tool == 'Hello':  # simple hello tool support
            # The MCP agent might respond with greeting; mimic structure
            return self.mcp._post_chat(self.mcp._format_tool_call('Hello', **params))  # type: ignore
        return {"error": "unknown_tool", "tool": tool}

    def close(self):
        try:
            self.mcp.close()  # type: ignore[attr-defined]
        except Exception:
            pass

    def _compose_text_context(self, text: str, query: Any) -> str:
        q = f"Query: {query}" if query else ""
        return f"{q}\n{text}".strip()
