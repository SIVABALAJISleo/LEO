"""
Quality Estimator
Scores answer quality based on length, completeness, and clarity signals.
No model calls — pure heuristics for maximum speed.
"""
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class QualityEstimator:
    """
    Heuristic-based answer quality scoring system.
    Returns a score 0.0-1.0 and identifies specific quality issues.
    """

    def estimate(self, answer: str, query: str = "") -> Dict[str, Any]:
        """
        Scores the answer and returns actionable quality signals.
        """
        if not answer or len(answer.strip()) == 0:
            return {"score": 0.0, "issues": ["empty_answer"], "needs_enhancement": True}

        issues = []
        score = 1.0

        word_count = len(answer.split())
        char_count = len(answer.strip())

        # Issue: Too short
        if word_count < 10:
            issues.append("too_short")
            score -= 0.3

        # Issue: Too long (likely hallucinated)
        if word_count > 500:
            issues.append("too_long")
            score -= 0.1

        # Issue: No punctuation (poorly structured)
        if not re.search(r"[.!?]", answer):
            issues.append("no_punctuation")
            score -= 0.15

        # Issue: Repetitive content
        sentences = re.split(r"[.!?]", answer)
        unique = set(s.strip().lower() for s in sentences if s.strip())
        if len(unique) < len(sentences) * 0.7:
            issues.append("repetitive")
            score -= 0.2

        # Issue: Vague/generic language
        vague_terms = ["it depends", "generally", "in some cases", "can vary"]
        if sum(1 for t in vague_terms if t in answer.lower()) > 2:
            issues.append("vague")
            score -= 0.1

        score = max(0.0, min(1.0, score))
        needs_enhancement = score < 0.75 or len(issues) > 0

        return {
            "score": round(score, 2),
            "issues": issues,
            "word_count": word_count,
            "needs_enhancement": needs_enhancement,
        }


global_quality_estimator = QualityEstimator()
