import json
import logging
from typing import Dict, Any, Tuple
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class OutcomeClassifier:
    """
    STEP 1: DOMAIN CLASSIFICATION
    Maps input to HARD, SOFT, or OPEN domains with confidence.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine

    def classify(self, query: str) -> Dict[str, Any]:
        system = (
            "Classify input: HARD (exact/facts), SOFT (interpretation), or OPEN (subjective).\n"
            "Output ONLY JSON: {\"domain\": \"...\", \"confidence\": 0.0-1.0}"
        )
        res = "".join(list(self.engine.generate_stream(query, system)))
        try:
            return json.loads(res[res.find("{"):res.rfind("}")+1])
        except:
            return {"domain": "SOFT", "confidence": 0.5}

class OutcomeCritic:
    """
    STEP 3: SELF-CRITIQUE LOOP
    Checks for logical errors and unsupported claims.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine

    def critique(self, answer: str, domain: str) -> Tuple[bool, str]:
        system = (
            f"Critique this {domain} answer. Check for: 1. Logic errors, 2. Unsupported claims.\n"
            "Output ONLY JSON: {\"passed\": bool, \"issues\": \"...\", \"correction_needed\": bool}"
        )
        res = "".join(list(self.engine.generate_stream(answer, system)))
        try:
            data = json.loads(res[res.find("{"):res.rfind("}")+1])
            return data.get("passed", True), data.get("issues", "")
        except:
            return True, ""
