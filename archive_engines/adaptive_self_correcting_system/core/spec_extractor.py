from typing import Tuple, Optional
from ..models.schemas import SystemSpec

class SpecExtractor:
    """
    1. INPUT + SPEC
    - Extract {intent, constraints}
    - Build strict spec {inputs, outputs, invariants}
    - If unclear → ask 1 question
    """
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    async def extract(self, user_input: str) -> Tuple[SystemSpec, Optional[str]]:
        # In a real scenario, this would call the Proposer/LLM to parse the input
        # For now, we simulate a basic extraction or return a question if it's too vague
        
        if len(user_input.split()) < 3:
            return None, "Could you provide more details about the function's requirements and constraints?"

        # Placeholder logic: Simulate LLM-based extraction
        # This would usually be a prompt like: "Extract the spec from this input: {user_input}"
        spec = SystemSpec(
            intent=user_input,
            constraints=["Must be type-hinted", "Must handle edge cases"],
            inputs={"input_data": "Any"},
            outputs={"result": "Any"},
            invariants=["Output must match expected format"]
        )
        
        return spec, None
