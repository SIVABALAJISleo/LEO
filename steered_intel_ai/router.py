import json
import logging
from typing import Dict, Any, List
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class SteeredRouter:
    """
    LAYER 3: INTENT PARSER + SOFT ROUTER
    Extracts domains, weights, and tool/retrieval requirements.
    """
    def __init__(self, inference_engine: IntelInferenceEngine):
        self.engine = inference_engine
        self.domains = ["math", "coding", "philosophy", "formal", "creative", "concise"]

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Multi-label parsing of the query.
        """
        system_prompt = (
            "Analyze the query. Output ONLY valid JSON.\n"
            "Format: {\"weights\": {\"domain\": weight}, \"need_tools\": bool, \"need_retrieval\": bool}\n"
            f"Available domains: {self.domains}\n"
            "Example: {\"weights\": {\"coding\": 0.8, \"concise\": 0.2}, \"need_tools\": true, \"need_retrieval\": false}"
        )
        
        # Non-streaming call for routing
        response_gen = self.engine.generate_stream(query, system_prompt)
        full_response = "".join(list(response_gen))
        
        try:
            start = full_response.find("{")
            end = full_response.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(full_response[start:end])
        except Exception as e:
            logger.warning(f"Steered routing failed: {e}. Defaulting to generic.")
            
        return {"weights": {}, "need_tools": False, "need_retrieval": False}
