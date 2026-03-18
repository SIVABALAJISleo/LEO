"""
Confidence Estimator
Assesses the semantic confidence of an answer text independently
from pipeline retrieval confidence.
"""

class ConfidenceEstimator:
    """
    Rule-based estimator to determine if the text "sounds" confident.
    """

    def estimate(self, answer: str) -> float:
        text = str(answer).strip().lower()

        if len(text) < 20:
            return 0.3

        # Low confidence markers
        uncertainty_markers = [
            "unknown", "might be", "possibly", "i guess", 
            "not sure", "unclear", "potentially", "could happen"
        ]

        # High confidence markers
        certainty_markers = [
            "is defined as", "always", "specifically", "for example",
            "must be", "will result in", "refers to", "ensures"
        ]

        score = 0.7  # Base confidence

        for marker in uncertainty_markers:
            if marker in text:
                score -= 0.15

        for marker in certainty_markers:
            if marker in text:
                score += 0.1

        if score < 0.2:
            return 0.2
        if score > 1.0:
            return 1.0

        return round(score, 3)
