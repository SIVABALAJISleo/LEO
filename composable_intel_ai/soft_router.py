import json
import logging
from typing import Dict, Any, List, Tuple
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class SoftRouter:
    """
    LAYER 3: INTENT PARSER + SOFT ROUTER
    Extracts multi-label task types and assigns weights for LoRA blending.
    """
    def __init__(self, inference_engine: IntelInferenceEngine):
        self.engine = inference_engine
        self.available_adapters = ["coding", "math", "creative", "logic"]

    def extract_weights(self, query: str) -> Dict[str, float]:
        """
        Extracts weights for each adapter based on query signals.
        Example Output: {"coding": 0.6, "creative": 0.4}
        """
        system_prompt = (
            f"Analyze the user query and assign weights (0.0 to 1.0) to the following domains: {self.available_adapters}.\n"
            "Output ONLY valid JSON. Weights must sum to approximately 1.0.\n"
            "Example: {\"coding\": 0.7, \"logic\": 0.3}"
        )
        
        # We use a non-streaming call for the router
        response_gen = self.engine.generate_stream(query, system_prompt)
        full_response = "".join(list(response_gen))
        
        try:
            start = full_response.find("{")
            end = full_response.rfind("}") + 1
            if start != -1 and end != -1:
                weights = json.loads(full_response[start:end])
                # Filter only available and non-zero
                return {k: v for k, v in weights.items() if k in self.available_adapters and v > 0.1}
        except Exception as e:
            logger.warning(f"Soft routing failed: {e}. Defaulting to base model.")
            
        return {} # Base model only
