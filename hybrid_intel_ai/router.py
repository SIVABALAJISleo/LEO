import json
import logging
from typing import Dict, Any, List, Tuple
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class HybridRouter:
    """
    LAYER 1 & 2: INTENT PARSER & ROUTER
    Uses a small model to extract structured intent and route requests.
    """
    def __init__(self, inference_engine: IntelInferenceEngine):
        self.engine = inference_engine

    def parse_intent(self, query: str) -> Dict[str, Any]:
        """
        Extracts structured intent from the query using the LLM.
        """
        system_prompt = (
            "Extract intent from the user query. Output ONLY valid JSON.\n"
            "Format: {\"task\": \"math|knowledge|language|complex\", \"sub_task\": \"...\", \"entities\": {}}\n"
            "If it's math, sub_task should be 'add', 'multiply', etc., and entities should contain 'args' list."
        )
        
        # We use a non-streaming call for intent parsing (needs to be fast)
        # Note: Added a non-streaming helper or just take the full result
        response_gen = self.engine.generate_stream(query, system_prompt)
        full_response = "".join(list(response_gen))
        
        try:
            # Clean response if model adds noise
            start = full_response.find("{")
            end = full_response.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(full_response[start:end])
        except Exception as e:
            logger.warning(f"Intent parsing failed: {e}. Falling back to 'language'.")
        
        return {"task": "language", "sub_task": "general", "entities": {}}

    def route(self, intent: Dict[str, Any]) -> str:
        return intent.get("task", "language")
