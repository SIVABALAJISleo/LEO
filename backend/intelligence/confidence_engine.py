"""
Adaptive Confidence Calibration Engine (ACCE)
Computes a unified confidence score from multi-source signals.
"""

class ConfidenceEngine:
    def compute_score(self, source_weight: float, answer_quality: float, structure_score: float) -> float:
        """
        Weights: source(50%), quality(30%), structure(20%)
        """
        score = (source_weight * 0.5) + (answer_quality * 0.3) + (structure_score * 0.2)
        return float(round(score, 3))

    def should_escalate(self, confidence: float, threshold: float = 0.7) -> bool:
        """
        Decides if the current confidence is too low to bypass the model ladder.
        """
        return confidence < threshold

global_acce = ConfidenceEngine()
