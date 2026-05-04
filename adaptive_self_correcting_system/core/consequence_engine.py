from ..models.schemas import ConsequenceLevel, Reversibility
from typing import Tuple

class ConsequenceEngine:
    """
    1) IRREVERSIBILITY GATE
    2) CONSEQUENCE STRATIFICATION
    """
    def __init__(self):
        pass

    def classify(self, user_input: str) -> Tuple[ConsequenceLevel, Reversibility]:
        # Mock classification logic
        # Default to high risk if unknown
        level = ConsequenceLevel.MINOR
        reversibility = Reversibility.REVERSIBLE
        
        lower_input = user_input.lower()
        if any(w in lower_input for w in ["delete", "format", "permanent", "send", "money"]):
            level = ConsequenceLevel.CRITICAL
            reversibility = Reversibility.IRREVERSIBLE
            
        return level, reversibility
吐
