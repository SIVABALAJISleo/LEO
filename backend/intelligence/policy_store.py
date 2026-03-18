"""
Policy Store
Maintains the dynamic thresholds for the Adaptive Intelligence Controller.
"""
import copy

class PolicyStore:
    """
    Holds routing bounds. As the LearningEngine receives feedback, 
    these bounds adjust to maximize inference avoidance safely.
    """
    def __init__(self):
        # Initial conservative bounds
        self.policy = {
            "skip_threshold": 0.75,     # High threshold to skip model entirely
            "enhance_threshold": 0.50,  # Lower threshold to push to DLSS Enhancer
            "escalate_threshold": 0.30  # Below this, always escalate to Large Model
        }

    def get(self) -> dict:
        return copy.deepcopy(self.policy)

    def update(self, updates: dict):
        """Merges new thresholds into the active policy."""
        for k, v in updates.items():
            if k in self.policy:
                # Keep bounds within sane limits
                if v > 0.95: v = 0.95
                if v < 0.10: v = 0.10
                self.policy[k] = round(v, 3)

global_policy_store = PolicyStore()
