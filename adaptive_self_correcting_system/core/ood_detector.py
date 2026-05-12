from typing import Tuple

class OODDetector:
    """
    3. OOD (UNKNOWN DETECTOR)
    - Embedding distance (Cosine similarity simulation)
    """
    def __init__(self, ood_threshold: float = 0.75):
        self.ood_threshold = ood_threshold

    def check_ood(self, embedding: list) -> Tuple[bool, float]:
        # Mock OOD check
        # 1.0 = known pattern, 0.0 = completely unknown
        score = 0.9 # High score = in-distribution
        return score < self.ood_threshold, score

