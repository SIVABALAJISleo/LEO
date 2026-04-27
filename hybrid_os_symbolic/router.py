import json
import logging
from typing import Dict, Any, Tuple
from intel_core_ai.inference import IntelInferenceEngine

logger = logging.getLogger(__name__)

class HybridRouter:
    """
    LAYER 2: ROUTER (DOMAIN SPLIT)
    LAYER 3: TRANSLATOR MODE
    """
    def __init__(self, inference: IntelInferenceEngine):
        self.inference = inference

    def route_and_translate(self, query: str, context: str) -> Dict[str, Any]:
        """
        Classifies domain and translates query into tool parameters.
        """
        system_prompt = (
            "You are a TRANSLATOR for a Hybrid AI OS.\n"
            "Classify the query into: MATH, LOGIC, CODE, FACTUAL, or CREATIVE.\n"
            "Output ONLY JSON: {\"domain\": \"...\", \"tool_input\": \"...\", \"plan\": \"...\"}\n"
            "MATH -> Output SymPy expression.\n"
            "LOGIC -> Output Z3 constraints.\n"
            "Context provided below.\n"
            f"RAM Context:\n{context}"
        )
        
        gen = self.inference.generate_stream(query, system_prompt)
        res = "".join(list(gen))
        
        try:
            start = res.find("{")
            end = res.rfind("}") + 1
            return json.loads(res[start:end])
        except:
            return {"domain": "CREATIVE", "tool_input": query, "plan": "Default fallback"}

    def translate_output(self, tool_output: str, original_query: str) -> str:
        """
        Translates raw tool data back to clear English.
        """
        prompt = f"Translate this raw data to a user-friendly answer for: {original_query}\nData: {tool_output}"
        gen = self.inference.generate_stream("", prompt)
        return "".join(list(gen)).strip()
