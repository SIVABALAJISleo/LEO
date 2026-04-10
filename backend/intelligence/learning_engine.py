"""
Learning Engine
Implements the feedback loop that adjusts Policy Store thresholds over time.
"""
from backend.intelligence.policy_store import PolicyStore

class LearningEngine:
    """
    Continuously adjusts the routing thresholds. 
    If skips are succeeding, it lowers the threshold slightly to catch more.
    If skips fail (user regenerates/downvotes), it tightens the threshold.
    """
    def update(self, feedback: dict, policy_store: PolicyStore):
        current_policy = policy_store.get()
        skip_t = current_policy.get("skip_threshold", 0.75)
        enhance_t = current_policy.get("enhance_threshold", 0.50)

        # Micro-adjustments per feedback event
        if feedback.get("success"):
            # If a bypass succeeded, become slightly more aggressive
            if not feedback.get("fallback_triggered"):
                skip_t -= 0.005
                enhance_t -= 0.002
        else:
            # If an answer failed, become noticeably more conservative
            skip_t += 0.05
            enhance_t += 0.02

        policy_store.update({
            "skip_threshold": skip_t,
            "enhance_threshold": enhance_t
        })
