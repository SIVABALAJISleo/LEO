"""
Confidence Gating Engine
Computes a weighted confidence score for any answer from the pipeline.
Only escalates to large model if confidence < 0.85.
This is the LAST gate before model escalation.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Thresholds
MODEL_ESCALATION_THRESHOLD = 0.85
ACCEPT_THRESHOLD = 0.70

# Weight distribution for confidence scoring
WEIGHTS = {
    "retrieval_similarity":   0.35,  # How similar retrieved docs are to query
    "graph_match_score":      0.30,  # Whether graph has a matching pattern
    "historical_accuracy":    0.20,  # Past accuracy for this intent/entity
    "answer_length_score":    0.10,  # Answer completeness proxy
    "source_reliability":     0.05,  # Cache/template > retrieval > model
}

# Source reliability scores
SOURCE_SCORES = {
    "CANONICAL":       1.00,
    "TEMPLATE":        0.98,
    "ANSWER_GRAPH":    0.95,
    "REASONING_MEM":   0.92,
    "SHADOW_STORE":    0.90,
    "PPE_HIT":         0.90,
    "SEMANTIC_CACHE":  0.88,
    "RETRIEVAL":       0.75,
    "ENHANCEMENT":     0.72,
    "MICRO_MODEL":     0.70,
    "FULL_CALC":       0.60,
    "FALLBACK":        0.30,
}


class ConfidenceGate:
    """
    Computes weighted confidence scores and gates model escalation.
    Rule: if score < 0.85, escalate. If score < 0.70, reject and retry.
    """

    def score(
        self,
        answer: str,
        source: str = "RETRIEVAL",
        retrieval_sim: float = 0.7,
        graph_match: float = 0.0,
        historical_acc: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Returns weighted confidence score and routing decision.
        """
        # Component scores
        answer_len = min(len(answer.split()) / 50.0, 1.0)  # Cap at 50 words = 1.0
        source_rel = SOURCE_SCORES.get(source, 0.5)

        weighted = (
            retrieval_sim * WEIGHTS["retrieval_similarity"] +
            graph_match   * WEIGHTS["graph_match_score"] +
            historical_acc * WEIGHTS["historical_accuracy"] +
            answer_len    * WEIGHTS["answer_length_score"] +
            source_rel    * WEIGHTS["source_reliability"]
        )

        decision = self._decide(weighted)

        result = {
            "score": round(weighted, 3),
            "decision": decision,
            "source": source,
            "components": {
                "retrieval_sim": retrieval_sim,
                "graph_match": graph_match,
                "historical_acc": historical_acc,
                "answer_len": round(answer_len, 2),
                "source_rel": source_rel,
            },
        }
        logger.debug(f"confidence_gate: score={weighted:.3f} decision={decision}")
        return result

    def _decide(self, score: float) -> str:
        if score >= MODEL_ESCALATION_THRESHOLD:
            return "ACCEPT"
        elif score >= ACCEPT_THRESHOLD:
            return "ACCEPT_LOW_CONFIDENCE"
        else:
            return "ESCALATE_TO_MODEL"

    def should_escalate(self, score: float) -> bool:
        return score < MODEL_ESCALATION_THRESHOLD

    def quick_score_source(self, source: str) -> float:
        """Fast path: score based only on source reliability."""
        return SOURCE_SCORES.get(source, 0.5)


global_confidence_gate = ConfidenceGate()
