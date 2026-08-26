import logging
from typing import Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class IntelQuerySchema(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    session_id: str
    metadata: Dict[str, Any] = {}

class IntelLogicEngine:
    """
    LAYER 1: INPUT CONTROL
    LAYER 6: LOGIC OFFLOADING
    - Rejects invalid inputs.
    - Resolves deterministic queries before LLM.
    """
    def __init__(self):
        # Deterministic rule map (example)
        self.rules = {
            "system status": "All Intel CPU cores nominal. iGPU (Iris Xe) acceleration active.",
            "uptime": "System has been operational for 142 hours.",
            "who are you": "I am an Intel-optimized local AI system (Phi-3 based)."
        }

    def validate(self, raw_input: Dict[str, Any]) -> Tuple[bool, Any]:
        try:
            validated = IntelQuerySchema(**raw_input)
            return True, validated
        except Exception:
            return False, {"error": "Invalid Input", "details": "Input schema validation failed."}

    def check_rules(self, query: str) -> Optional[str]:
        q = query.lower().strip()
        for key, value in self.rules.items():
            if key in q:
                return value
        return None
