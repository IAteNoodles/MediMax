from __future__ import annotations
import httpx
from typing import Any, Dict

class MCPClient:
    """Client to interact with MCP server exposing ML model tools via /chat endpoint.

    The MCP server wraps LangChain agent tools; we send a crafted natural language
    message that instructs it which tool to call with which parameters.
    """

    def __init__(self, base_url: str, timeout: float = 60.0):
        self.base_url = base_url.rstrip('/')
        self._client = httpx.Client(timeout=timeout)

    def _post_chat(self, message: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat"
        try:
            resp = self._client.post(url, json={"message": message})
            resp.raise_for_status()
            data = resp.json()
            raw_resp = data.get("response", "")
            import json as _json
            try:
                parsed = _json.loads(raw_resp)
                return parsed if isinstance(parsed, dict) else {"raw": raw_resp}
            except _json.JSONDecodeError:
                return {"raw": raw_resp, "error": "non_json_tool_output"}
        except httpx.HTTPError as e:
            return {"error": "http_error", "details": str(e)}

    def predict_cardio(self, **params: Any) -> Dict[str, Any]:
        """Invoke cardiovascular risk tool.

        Params expected: age, gender, height, weight, ap_hi, ap_lo, cholesterol,
        gluc, smoke, alco, active
        """
        print(f"[MCP DEBUG] Calling predict_cardio with params: {params}")
        tool_call = self._format_tool_call(
            tool_name="Predict_Cardiovascular_Risk_With_Explanation", **params
        )
        print(f"[MCP DEBUG] Making request to: {self.base_url}/chat")
        result = self._post_chat(tool_call)
        print(f"[MCP DEBUG] Got response: {result}")
        return result

    def predict_diabetes(self, **params: Any) -> Dict[str, Any]:
        tool_call = self._format_tool_call(
            tool_name="Predict_Diabetes_Risk_With_Explanation", **params
        )
        return self._post_chat(tool_call)

    def _format_tool_call(self, tool_name: str, **params: Any) -> str:
        # Natural language instruction for the MCP agent to pick the correct tool.
        lines = [
            "You are a system orchestrator. Call the tool exactly with the provided parameters.",
            f"Tool: {tool_name}",
            "Parameters:" 
        ]
        for k, v in params.items():
            lines.append(f"- {k}={v}")
        lines.append("Return ONLY the tool JSON output.")
        return "\n".join(lines)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
