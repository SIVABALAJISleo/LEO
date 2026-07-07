from typing import Tuple, List, Optional
from ..models.schemas import LeoV4Spec, LeoContract

class SpecConstructor:
    """
    2. SPEC CONSTRUCTION
    - Convert input → {goal, inputs, constraints, expected_output}
    - 3. CONTRACT ENFORCEMENT (HOARE STYLE)
    """
    def __init__(self, allowed_domains: List[str] = ["code", "math", "structured data"]):
        self.allowed_domains = allowed_domains

    async def construct(self, user_input: str) -> Tuple[Optional[LeoV4Spec], List[str]]:
        # 1. DOMAIN LOCK
        input_lower = user_input.lower()
        domain_detected = False
        if any(d in input_lower for d in self.allowed_domains):
            domain_detected = True
        
        if not domain_detected:
            return None, ["Task is outside of the defined verifiable domains."]

        # 2. SPEC CONSTRUCTION logic
        clarifications = []
        if "input" not in input_lower: clarifications.append("Missing explicit input parameters.")
        if "expect" not in input_lower: clarifications.append("Missing expected outcome specification.")
        
        if clarifications:
            return None, clarifications[:2]

        # 3. CONTRACT ENFORCEMENT
        # Define mock Pre/Post conditions based on the input
        contract = LeoContract(
            preconditions=["Input types must be valid", "Input must not be null"],
            postconditions=["Result must match expected type", "Constraints must be satisfied"]
        )

        spec = LeoV4Spec(
            goal=user_input,
            inputs={},
            constraints=["logical consistency"],
            expected_output="parsed_output",
            contract=contract
        )
        
        return spec, []
