import json
import logging
from typing import Dict, Any
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class HighAccuracyRouter:
    """
    STEP 1: ROUTER
    Classifies input: HARD, FACTUAL, or OPEN.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine

    def classify(self, query: str) -> Dict[str, Any]:
        system = (
            "Classify input: HARD (math/logic/code), FACTUAL (facts/explanation), or OPEN (subjective).\n"
            "Output ONLY JSON: {\"domain\": \"...\", \"confidence\": 0.0-1.0}"
        )
        res = "".join(list(self.engine.generate_stream(query, system)))
        try:
            return json.loads(res[res.find("{"):res.rfind("}")+1])
        except:
            return {"domain": "FACTUAL", "confidence": 0.5}

class IntentLock:
    """
    STEP 2: INTENT LOCK
    Restates intent and lists assumptions.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine

    def lock(self, query: str) -> Dict[str, Any]:
        system = (
            "Restate intent and list assumptions. Output ONLY JSON: \n"
            "{\"interpretation\": \"...\", \"assumptions\": [\"...\"], \"unclear\": bool}"
        )
        res = "".join(list(self.engine.generate_stream(query, system)))
        try:
            return json.loads(res[res.find("{"):res.rfind("}")+1])
        except:
            return {"interpretation": query, "assumptions": [], "unclear": False}
