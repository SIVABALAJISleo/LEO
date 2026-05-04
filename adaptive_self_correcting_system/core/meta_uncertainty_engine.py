from typing import List

class MetaUncertaintyEngine:
    """
    8) META-UNCERTAINTY CHECK
    - compute ensemble disagreement (on confidence, not just output)
    - high disagreement => uncertainty unreliable => abstain
    """
    def __init__(self, threshold: float = 0.2):
        self.threshold = threshold

    def check_meta_uncertainty(self, agent_confidences: List[float]) -> bool:
        if not agent_confidences: return False
        
        # Calculate variance/disagreement of confidence scores
        mean_conf = sum(agent_confidences) / len(agent_confidences)
        variance = sum((c - mean_conf) ** 2 for c in agent_confidences) / len(agent_confidences)
        
        # High variance means the agents are uncertain about their own uncertainty
        return variance > self.threshold
吐
