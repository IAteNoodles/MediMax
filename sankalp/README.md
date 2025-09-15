# Cache-augmented generation (Med-Gemma)

Build a KV cache for a static prefix in one forward pass, then reuse it for multiple follow-up queries via incremental decoding.

## Install

Create a virtualenv and install dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r sankalp/requirements.txt
```

Notes:
- Install a PyTorch build matching your platform (CPU/CUDA/MPS). See https://pytorch.org/get-started/locally/
- You need access to the Med-Gemma model on Hugging Face (default: `google/medgemma-4b-it`). Accept the license and log in if required. If gated, set an HF token via `export HF_TOKEN=...` or pass `--hf-token`.

## Quickstart

Run the demo CLI which caches the prefix once and answers multiple queries:

```
python -m sankalp.run_cag --model google/medgemma-4b-it \
  --prefix "Patient ID: P123\nSymptoms: Dyspnea, cough\nLabs: CRP = 38.2 mg/L\nRelevant Knowledge: Dyspnea with high CRP often indicates pneumonia.\n" \
  --queries "What is the likely diagnosis?" "List two initial treatments." \
  --max-new 96
```

Or import and use programmatically:

```python
from sankalp.cag import CacheAugmentedGenerator

cag = CacheAugmentedGenerator(model_name="google/medgemma-4b-it")

prefix = (
    "Patient ID: P123\n"
    "Symptoms: Dyspnea, cough\n"
    "Labs: CRP = 38.2 mg/L\n"
    "Relevant Knowledge: Dyspnea with high CRP often indicates pneumonia.\n"
)

cag.build_prefix_cache(prefix)
print(cag.generate("What is the likely diagnosis?", max_new_tokens=64))
print(cag.generate("List two initial treatments.", max_new_tokens=64))
```

## Tips
- On Apple Silicon (MPS), FP16 is typically fast; on CPU, BF16/FP32 may be used.
- If you hit EOS immediately and get an empty string, try higher `max_new_tokens`, non-zero temperature, or ensure your prompt/query formatting is correct.
- Use `clear_cache()` if you need to switch to a new prefix.