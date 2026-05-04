from typing import Tuple, Optional
from ..models.schemas import HyperIntent

class IntentExtractor:
    """
    1. DOMAIN GATING
    - Enforce structured intent extraction:
      {goal, domain, constraints, output_format, depth}
    """
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def extract(self, user_input: str) -> Tuple[Optional[HyperIntent], Optional[str]]:
        # In a production system, this would call a small, structured model
        # For now, we simulate extraction via keywords
        
        input_lower = user_input.lower()
        
        # Simple extraction logic
        domain = "coding" if "code" in input_lower or "python" in input_lower else "general"
        if "calculate" in input_lower or "math" in input_lower: domain = "math"
        
        # If input is too short, reject as underspecified
        if len(user_input.split()) < 4:
            return None, "Query is too brief. Please specify your goal and constraints."

        intent = HyperIntent(
            goal=user_input,
            domain=domain,
            constraints=["deterministic execution" if domain == "math" else "type safety"],
            output_format="JSON" if "json" in input_lower else "text",
            depth="deep" if "thorough" in input_lower or "complex" in input_lower else "shallow"
        )
        
        return intent, None
吐
