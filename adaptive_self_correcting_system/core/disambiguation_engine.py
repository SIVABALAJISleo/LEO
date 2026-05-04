from typing import Tuple, Optional

class DisambiguationEngine:
    """
    2. SOCRATIC DISAMBIGUATION LAYER (MANDATORY)
    - generate binary clarification question
    - NEVER assume intent
    """
    def __init__(self):
        pass

    def check_ambiguity(self, user_input: str) -> Tuple[bool, Optional[str]]:
        # Mock ambiguity detection
        lower_input = user_input.lower()
        
        # Example: Ambiguous command "run test" (which test?)
        if lower_input == "run test":
            return True, "Do you mean 'unit tests' or 'integration tests'?"
            
        if "delete" in lower_input and "all" not in lower_input:
            return True, "Do you mean 'delete local cache' or 'delete cloud storage'?"
            
        return False, None

