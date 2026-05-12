import json
import logging
from typing import Dict, Any, List, Tuple
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class BoundaryIntentHandler:
    """
    STEP 2: INTENT CONTRACT
    STEP 3: PROBABILITY SPLIT
    Restates intent, lists assumptions, and handles multi-interpretation.
    """
    def __init__(self, engine: IntelInferenceEngine):
        self.engine = engine

    def contract(self, query: str) -> Dict[str, Any]:
        system = (
            "Analyze intent. Output ONLY JSON: \n"
            "{\"interpretation\": \"...\", \"assumptions\": [\"...\"], \"ambiguity_score\": 0.0-1.0}"
        )
        res = "".join(list(self.engine.generate_stream(query, system)))
        try:
            return json.loads(res[res.find("{"):res.rfind("}")+1])
        except:
            return {"interpretation": query, "assumptions": [], "ambiguity_score": 0.0}

    def split_probability(self, query: str) -> List[Dict[str, Any]]:
        system = (
            "Identify top 2 interpretations. Output ONLY JSON list: \n"
            "[{\"interpretation\": \"...\", \"probability\": 0.0-1.0, \"brief_solution\": \"...\"}]"
        )
        res = "".join(list(self.engine.generate_stream(query, system)))
        try:
            return json.loads(res[res.find("["):res.rfind("]")+1])
        except:
            return []
