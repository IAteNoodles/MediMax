# MediMax Multi-Agent Orchestration (LLM-Based)

This system implements **LLM-based medical agents** using LangGraph orchestration. Both MainAgent and RouterAgent use Groq's **llama-3.1-8b-instant** model for intelligent decision-making rather than hardcoded rules.

## Architecture

### LLM-Based Agents

- **MainAgent**: Uses Groq LLM to analyze patient data and make orchestration decisions
- **RouterAgent**: Uses Groq LLM for intelligent clinical routing and model selection
- **LangGraph Flow**: Proper agent-to-agent communication via state transitions

### External Components

- **Groq API**: Powers both agents with llama-3.1-8b-instant
- **MCP Endpoint**: Disease-specific ML models via `/chat` natural language interface
- **MedGemma**: Medical report generation via OpenAI-compatible API
- **Model Specs**: YAML-defined parameter requirements

## Agent Intelligence

### MainAgent LLM Decisions

```yaml
Input: Patient data + clinical context
LLM Analysis: "Given this 55-year-old with hypertension..."
Decision: route_to_models | need_more_data | complete
Output: Action + reasoning + summary
```

### RouterAgent LLM Decisions

```yaml
Input: Patient context + available parameters + model requirements  
LLM Analysis: "Cardiovascular model needs BP data, diabetes model needs HbA1c..."
Decision: invoke models | request critical data
Output: Model invocations + clinical reasoning
```

## Quick Start

**Requirements**: Python 3.11+, Groq API key

```bash
# Setup
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Test LLM agents
python test_orchestration.py

# Interactive UI  
streamlit run app.py
```

## LLM Agent Flow

1. **MainAgent** receives patient payload
2. **LLM analyzes** clinical context and data completeness
3. **Decision**: route to models OR request more data
4. If routing → **RouterAgent** takes over
5. **RouterAgent LLM** evaluates model requirements vs available data
6. **Invokes appropriate models** via MCP + generates report via MedGemma
7. Returns structured response with **LLM explanations**

## State Schema (LLM Response)

```json
{
  "status": "need_more_data|complete|route_to_models",
  "action": "need_more_data|route_to_models|complete",
  "missing_parameters": ["age", "bp_systolic", "cholesterol"],
  "predictions": [{"model": "cardiovascular_risk", "prediction": 1, "probability": 0.85}],
  "report": "LLM-generated medical assessment...",
  "follow_up_questions": ["Recent cardiovascular events?"],
  "routing_explanation": "LLM reasoning: Patient has sufficient cardiovascular parameters...",
  "routing_summary": "55M with hypertension, chest symptoms, requires risk assessment"
}
```

## Running Demo

Install dependencies (Python 3.11+ recommended):

```bash
pip install -r requirements.txt
```

Run demo (will attempt real HTTP calls to provided IPs; ensure connectivity or mock):

```bash
python run_demo.py
```

If endpoints are unreachable you can monkeypatch `RouterAgent._invoke_tool` for offline testing.

### Streamlit UI

Interactive testing interface:

```bash
streamlit run app.py
```

Features:

- **LLM Agent Toggle**: Required (Groq API needed)
- **Mock Mode**: Offline testing without external APIs
- **Real-time LLM Explanations**: See agent reasoning
- **Iterative Parameter Collection**: Add missing data step-by-step

Environment setup:

```bash
GROQ_API_KEY=gsk_your_key_here
```

## Integration Notes

- For production integrate `build_graph` into a FastAPI or other web service endpoint. Provide payload JSON -> run graph -> return `state.result`.
- Add authentication / retry/backoff & richer error handling for network failures (currently minimal).
- Enhance LLM prompt to enforce strict JSON using function calling or JSON schema if supported.

## Future Enhancements

- Caching model predictions.
- Partial model ranking & requesting only missing subset across multiple models.
- Add validation & type coercion per parameter.
- Stream LLM responses when supported.
- Robust JSON extraction (function calling / schema enforced).
- Additional model families & dynamic tool discovery.

## Disclaimer

This is a prototype. Not for clinical use without proper validation & regulatory compliance.
