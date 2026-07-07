from typing import List, Tuple
from ..models.schemas import Interpretation

class AmbiguityResolver:
    """
    2. AMBIGUITY RESOLUTION
    - Generate 2–3 interpretations
    - Rank by probability using context + history
    - If confidence < 0.75 → ask minimal clarification
    """
    def __init__(self):
        pass

    async def resolve(self, user_input: str) -> Tuple[List[Interpretation], float]:
        # Mock logic to generate interpretations
        interpretations = [
            Interpretation(
                text=f"Interpret input as a direct request for: {user_input}",
                probability=0.85,
                context="Direct semantic mapping"
            ),
            Interpretation(
                text=f"Interpret input as a request for background info on: {user_input}",
                probability=0.10,
                context="Exploratory mapping"
            )
        ]
        
        # Primary confidence is the max probability
        confidence = max(i.probability for i in interpretations)
        return interpretations, confidence
