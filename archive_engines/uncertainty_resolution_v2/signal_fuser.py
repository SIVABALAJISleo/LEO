import numpy as np
from typing import Dict, Any, List

class SignalFuser:
    """
    Probabilistic Signal Fuser
    Merges multi-modal intent vectors (LLM drafts, rule-based heuristics, 
    RAG similarity) into a unified probability distribution.
    """
    def __init__(self, confidence_threshold: float = 0.85):
        self.confidence_threshold = confidence_threshold
        
    def fuse_signals(self, signals: List[Dict[str, float]]) -> Dict[str, Any]:
        """
        Fuses signals using Bayesian updates and weighted averaging.
        """
        if not signals:
            return {"action": "UNKNOWN", "confidence": 0.0, "requires_clarification": True}
            
        merged = {}
        for sig in signals:
            for action, prob in sig.items():
                if action not in merged:
                    merged[action] = []
                merged[action].append(prob)
                
        # Calculate posterior probabilities (simplified mean for deterministic output)
        posteriors = {act: float(np.mean(probs)) for act, probs in merged.items()}
        
        best_action = max(posteriors.items(), key=lambda x: x[1])
        
        return {
            "action": best_action[0],
            "confidence": best_action[1],
            "requires_clarification": best_action[1] < self.confidence_threshold,
            "distribution": posteriors
        }
