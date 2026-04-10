"""
Enhancement Router Module
The CRITICAL LOGIC layer that determines if a weak answer is "good enough"
to be enhanced instead of being escalated to an expensive LLM.
"""
from typing import Tuple, List, Optional
from backend.enhancement.enhancer import AnswerEnhancer
from backend.enhancement.quality_scorer import QualityScorer
from backend.enhancement.confidence_estimator import ConfidenceEstimator

class EnhancementRouter:
    """
    Evaluates raw answer quality and routes it to the enhancer if it meets DLSS thresholds.
    """

    def __init__(self):
        self.enhancer = AnswerEnhancer()
        self.scorer = QualityScorer()
        self.confidence = ConfidenceEstimator()

    def process(self, answer: str, query: str, context_docs: Optional[List[str]] = None, intent: str = "general") -> Tuple[Optional[str], str]:
        """
        Returns (Enhanced_Answer, Status_Code).
        If quality < 0.5 or confidence < 0.6, returns (None, "escalate").
        """
        if not answer or not str(answer).strip():
            return None, "escalate"

        quality = self.scorer.score(answer)
        confidence = self.confidence.estimate(answer)

        # DLSS LOGIC: Acceptable raw proxy -> upscale it instead of recomputing
        if quality > 0.5 and confidence > 0.6:
            enhanced = self.enhancer.enhance(answer, query, context_docs, intent)
            return enhanced, "enhanced"

        return None, "escalate"
