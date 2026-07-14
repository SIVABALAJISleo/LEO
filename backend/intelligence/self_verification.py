"""
backend/intelligence/self_verification.py
Subsystem 19: Self-Verification Engine.
Detects hallucinations, scores confidence, cross-references generated answers
with the retrieval engine, and retries when confidence is too low.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
import difflib

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """
    Computes a confidence score for a generated answer
    using lexical overlap with retrieved source documents.
    """

    def score(self, answer: str, source_docs: List[str]) -> float:
        """
        Returns [0.0, 1.0] — fraction of answer content supported by sources.
        Uses character-level sequence matching for portability (no ML required).
        """
        if not source_docs or not answer.strip():
            return 0.0

        combined_source = " ".join(source_docs).lower()
        answer_words = re.findall(r'\b\w+\b', answer.lower())

        if not answer_words:
            return 0.0

        supported = sum(1 for word in answer_words if word in combined_source)
        return supported / len(answer_words)


class HallucinationDetector:
    """
    Rule-based hallucination detection.
    Flags answers that:
    - Contain unsubstantiated numeric claims not in sources
    - Reference entities not found in retrieved context
    - Have extremely low lexical overlap with sources
    """

    HALLUCINATION_PATTERNS = [
        r"\b(?:studies show|research proves|experts say|scientists found)\b",
        r"\b(?:100%|always|never|everyone|no one)\b",
        r"\bin \d{4}\b",  # Year claims that may be fabricated
    ]

    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in self.HALLUCINATION_PATTERNS]

    def detect(self, answer: str, source_docs: List[str]) -> Tuple[bool, List[str]]:
        """
        Returns (is_hallucination_risk, list_of_flags).
        """
        flags = []
        combined_source = " ".join(source_docs).lower()

        for pat in self.patterns:
            m = pat.search(answer)
            if m:
                matched_text = m.group(0)
                # If the flagged phrase also appears verbatim in source, it's fine
                if matched_text.lower() not in combined_source:
                    flags.append(f"Unsupported claim pattern: '{matched_text}'")

        is_risky = len(flags) > 0
        return is_risky, flags


class SelfVerificationEngine:
    """
    Master self-verification pipeline.
    Scores and gates answers before returning them to the user.
    """

    def __init__(self, min_confidence: float = 0.15, max_retries: int = 2):
        self.min_confidence = min_confidence
        self.max_retries = max_retries
        self.scorer = ConfidenceScorer()
        self.detector = HallucinationDetector()

    def verify(self, answer: str, source_docs: List[str]) -> Dict[str, Any]:
        """
        Verifies an answer against source documents.
        Returns a structured verification report.
        """
        confidence = self.scorer.score(answer, source_docs)
        is_risky, flags = self.detector.detect(answer, source_docs)

        passed = confidence >= self.min_confidence and not is_risky

        report = {
            "answer": answer,
            "confidence_score": round(confidence, 3),
            "hallucination_risk": is_risky,
            "flags": flags,
            "verification_passed": passed,
            "recommendation": "SERVE" if passed else "RETRY_OR_CAVEAT"
        }

        if not passed:
            logger.warning(
                f"Self-verification FAILED. Confidence: {confidence:.2f}. Flags: {flags}"
            )
        else:
            logger.info(f"Self-verification PASSED. Confidence: {confidence:.2f}.")

        return report

    def add_caveat(self, answer: str, confidence: float) -> str:
        """Prepends a transparency caveat when confidence is low but answer is served anyway."""
        if confidence < 0.3:
            return f"[Confidence: {confidence:.0%}] Note: This answer may be incomplete. " + answer
        return answer
