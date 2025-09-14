from __future__ import annotations
import os
from typing import List, Dict, Any, cast
from groq import Groq  # type: ignore

DEFAULT_MODEL = "llama-3.1-8b-instant"

class GroqLLM:
    def __init__(self, model: str = DEFAULT_MODEL, api_key: str | None = None):
        key = api_key or os.getenv('GROQ_API_KEY')
        if not key:
            raise RuntimeError("GROQ_API_KEY not set in environment or provided explicitly")
        self.client = Groq(api_key=key)
        self.model = model

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 1024) -> str:
        # Groq python client expects list of dicts with 'role' and 'content'
        msg_list = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in messages]
        resp = self.client.chat.completions.create(  # type: ignore[arg-type]
            model=self.model,
            messages=msg_list,  # type: ignore[arg-type]
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )
        choice = resp.choices[0]
        return getattr(choice.message, 'content', '')  # type: ignore

    def summarize_for_routing(self, payload: Dict[str, Any]) -> str:
        text_parts = []
        for field in ['patient_history', 'medical_report', 'symptoms', 'query']:
            if field in payload and payload[field]:
                text_parts.append(f"{field}: {payload[field]}")
        content = "\n".join(text_parts)
        prompt = (
            "Summarize the following patient context in <=60 words focusing on risk factors and explicit numeric values.\n" + content
        )
        return self.chat([
            {"role": "system", "content": "You are a concise medical triage summarizer."},
            {"role": "user", "content": prompt}
        ], temperature=0.1, max_tokens=180)

    def routing_explanation(self, numeric: Dict[str, Any], models_status: Dict[str, Any]) -> str:
        prompt = (
            "Given numeric parameters and model requirements, explain which models are satisfied and which parameters are missing. "
            "Return a concise explanation.\nNumeric:\n" + str(numeric) + "\nStatus:\n" + str(models_status)
        )
        return self.chat([
            {"role": "system", "content": "You explain model routing decisions."},
            {"role": "user", "content": prompt}
        ], temperature=0.0, max_tokens=220)
