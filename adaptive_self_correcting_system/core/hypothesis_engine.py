import math
from typing import List, Tuple

class HypothesisEngine:
    """
    8. MULTI-HYPOTHESIS ENGINE
    - hypotheses = generate_multiple_answers(query)
    - entropy threshold for ambiguity
    """
    def __init__(self, entropy_threshold: float = 0.5):
        self.entropy_threshold = entropy_threshold

    def calculate_entropy(self, probabilities: List[float]) -> float:
        if not probabilities: return 0.0
        return -sum(p * math.log2(p) for p in probabilities if p > 0)

    def check_ambiguity(self, hypothesis_scores: List[float]) -> bool:
        # Normalize scores to probabilities
        total = sum(hypothesis_scores)
        if total == 0: return True
        probs = [s / total for s in hypothesis_scores]
        
        entropy = self.calculate_entropy(probs)
        return entropy > self.entropy_threshold
吐
