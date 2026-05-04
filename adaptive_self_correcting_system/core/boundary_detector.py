from typing import Tuple, Optional

class BoundaryDetector:
    """
    3. OOD (OUT-OF-DISTRIBUTION) DETECTION
    6. KNOWLEDGE BOUNDARY DETECTOR
    """
    def __init__(self, ood_threshold: float = 0.8):
        self.ood_threshold = ood_threshold

    def detect_ood(self, embedding_vector: list) -> Tuple[bool, float]:
        # Mock OOD detection (Mahalanobis distance simulation)
        # 1.0 = perfect in-distribution, 0.0 = completely OOD
        ood_score = 0.95 
        return ood_score < self.ood_threshold, ood_score

    def check_knowledge_boundary(self, domain: str, intent: str) -> bool:
        # Mock knowledge coverage check
        covered_intents = {
            "finance": ["transfer", "balance"],
            "system": ["status", "reset"],
            "code": ["transform", "optimize"]
        }
        return intent in covered_intents.get(domain, [])
吐
