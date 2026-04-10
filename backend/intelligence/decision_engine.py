"""
Decision Engine
Calculates feature scores against the active policy to decide routing logic.
"""

class DecisionEngine:
    """
    Determines if a query/context vector should SKIP_MODEL, ENHANCE, or ESCALATE.
    """
    def decide(self, features: dict, policy: dict) -> str:
        # Heavily weight quality and confidence, with a small bump if it matched a local cache
        score = (
            features.get("quality", 0) * 0.4 +
            features.get("confidence", 0) * 0.4 +
            features.get("cache_hit", 0) * 0.2
        )

        if score > policy.get("skip_threshold", 0.75):
            return "SKIP_MODEL"

        if score > policy.get("enhance_threshold", 0.50):
            return "ENHANCE"

        return "ESCALATE"
