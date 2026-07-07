"""
Quality Scorer Module
Evaluates raw answers based on length, structure, and clarity markers.
Returns a score from 0.0 to 1.0 representing intrinsic quality.
"""

class QualityScorer:
    """
    Scores textual quality independent of generation source confidence.
    Used to decide if an answer is 'good enough' to enhance instead of escalate.
    """

    def score(self, answer: str) -> float:
        if not answer or not str(answer).strip():
            return 0.0

        text = str(answer).strip()
        words = text.split()
        length = len(words)

        # Baseline length score (optimal between 20 and 100 words for short factual AI SaaS)
        length_score = min(length / 50.0, 1.0)
        
        # Clarity multiplier
        clarity_multiplier = 0.5
        if "." in text:
            clarity_multiplier += 0.2
        if "\n" in text or "•" in text or "-" in text:
            clarity_multiplier += 0.2
        if text[0].isupper() and text[-1] in ".!?":
            clarity_multiplier += 0.1

        clarity_multiplier = min(clarity_multiplier, 1.0)

        # Penalties for obvious failures
        if "i don't know" in text.lower() or "i am sorry" in text.lower():
            return 0.1
        if "error" in text.lower()[:20]:
            return 0.0

        final_score = min(length_score * clarity_multiplier, 1.0)
        return round(final_score, 3)
