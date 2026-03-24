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
MODEL_ESCALATION_THRESHOLD = 0.80
ACCEPT_THRESHOLD = 0.75

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
    Dynamically adjusts weights based on source reliability and intent.
    """
    def __init__(self):
        self.weights = WEIGHTS.copy()
        self.source_scores = SOURCE_SCORES.copy()

    def score(
        self,
        answer: str,
        source: str = "RETRIEVAL",
        intent: str = "default",
        retrieval_sim: float = 0.7,
        graph_match: float = 0.0,
        historical_acc: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Returns weighted confidence score and routing decision.
        Adjusts scoring logic based on intent (e.g., 'fact' vs 'opinion').
        """
        # 1. Answer Completeness Proxy
        words = answer.split()
        answer_len = min(len(words) / 30.0, 1.0) if intent != "definition" else min(len(words) / 15.0, 1.0)
        
        # 2. Source Reliability
        source_rel = self.source_scores.get(source, 0.5)
        
        # 3. Dynamic Weight Adjustment (Focus more on retrieval for facts)
        current_weights = self.weights.copy()
        if intent in ["definition", "instruction"]:
            current_weights["retrieval_similarity"] += 0.1
            current_weights["graph_match_score"] -= 0.1

        weighted = (
            retrieval_sim * current_weights["retrieval_similarity"] +
            graph_match   * current_weights["graph_match_score"] +
            historical_acc * current_weights["historical_accuracy"] +
            answer_len    * current_weights["answer_length_score"] +
            source_rel    * current_weights["source_reliability"]
        )

        decision = self._decide(weighted)

        result = {
            "score": float(f"{weighted:.3f}"),
            "decision": decision,
            "source": source,
            "components": {
                "retrieval_sim": retrieval_sim,
                "graph_match": graph_match,
                "historical_acc": historical_acc,
                "answer_len": float(f"{answer_len:.2f}"),
                "source_rel": source_rel,
            },
        }
        logger.debug(f"confidence_gate: score={weighted:.3f} decision={decision} intent={intent}")
        return result

    def _decide(self, score: float) -> str:
        if score >= MODEL_ESCALATION_THRESHOLD:
            return "ACCEPT"
        elif score >= ACCEPT_THRESHOLD:
            return "ACCEPT_LOW_CONFIDENCE"
        else:
            return "ESCALATE_TO_MODEL"

    def should_escalate(self, score: float) -> bool:
        """Rule: if score < 0.80, escalate to larger tier."""
        return score < MODEL_ESCALATION_THRESHOLD

    def update_source_score(self, source: str, accuracy_feedback: float):
        """Phase 12 Preview: Adjusts source reliability based on user feedback."""
        if source in self.source_scores:
            # Moving average update
            self.source_scores[source] = (self.source_scores[source] * 0.9) + (accuracy_feedback * 0.1)
            logger.info(f"source_reliability_updated: source={source} new_score={self.source_scores[source]:.3f}")


global_confidence_gate = ConfidenceGate()
