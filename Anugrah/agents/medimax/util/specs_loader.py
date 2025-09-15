from __future__ import annotations
from typing import List, Dict, Any
import yaml
from pathlib import Path

class ModelSpecs:
    def __init__(self, path: str):
        self.path = Path(path)
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        with self.path.open('r') as f:
            return yaml.safe_load(f)

    @property
    def models(self) -> List[Dict[str, Any]]:
        return self._data.get('models', [])

    def required_params(self, model_name: str) -> List[str]:
        for m in self.models:
            if m['name'] == model_name:
                return list(m.get('parameters', []))
        return []

    def match_models(self, provided: dict) -> Dict[str, Dict[str, Any]]:
        """Return satisfaction info per model.
        { model_name: {"missing": [...], "present": [...], "tool": str} }
        """
        result = {}
        for m in self.models:
            params = m.get('parameters', [])
            missing = [p for p in params if p not in provided]
            present = [p for p in params if p in provided]
            result[m['name']] = {
                'missing': missing,
                'present': present,
                'tool': m.get('tool')
            }
        return result
