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

    def record_feedback(self, source: str, was_correct: bool):
        """Update source score using exponential moving average."""
        import json, os
        weights_path = "/tmp/confidence_weights.json"
        try:
            if os.path.exists(weights_path):
                with open(weights_path) as f:
                    data = json.load(f)
            else:
                data = {"source_scores": SOURCE_SCORES.copy(), "count": 0}

            current = data["source_scores"].get(source, 0.7)
            alpha = 0.1  # conservative learning rate
            updated = (1 - alpha) * current + alpha * (1.0 if was_correct else 0.0)
            data["source_scores"][source] = round(updated, 4)
            data["count"] = data.get("count", 0) + 1

            with open(weights_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Could not update weights: {e}")

    def score(self, answer, source="FULL_CALC", retrieval_similarity=0.5,
              graph_match_score=0.0, historical_accuracy=0.5):
        import json, os
        weights_path = "/tmp/confidence_weights.json"
        source_scores = SOURCE_SCORES.copy()
        try:
            if os.path.exists(weights_path):
                with open(weights_path) as f:
                    data = json.load(f)
                    source_scores.update(data.get("source_scores", {}))
        except Exception:
            pass  # use defaults

        answer_length_score = min(len(answer.split()) / 50.0, 1.0) if answer else 0.0
        source_reliability = source_scores.get(source, 0.5)

        raw = (
            WEIGHTS["retrieval_similarity"] * retrieval_similarity +
            WEIGHTS["graph_match_score"]    * graph_match_score +
            WEIGHTS["historical_accuracy"]  * historical_accuracy +
            WEIGHTS["answer_length_score"]  * answer_length_score +
            WEIGHTS["source_reliability"]   * source_reliability
        )
        return max(0.0, min(1.0, raw))

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
