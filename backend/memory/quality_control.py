"""
backend/memory/quality_control.py
Knowledge Quality Control (Point 9).

Validates, scores, and manages the lifecycle of knowledge fragments.
Promotes high-value data and decays low-value data.
"""
import time
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class QualityControl:
    """
    Manages knowledge lifecycle: scoring, promotion, and decay.
    """
    def __init__(self, decay_rate: float = 0.05, promotion_threshold: float = 0.9):
        self.decay_rate = decay_rate
        self.promotion_threshold = promotion_threshold
        # In-memory store for scores (In production, persist to DB)
        self.scores: Dict[str, Dict[str, Any]] = {}

    def score_knowledge(self, knowledge_id: str, success: bool = True):
        """Points 9: Score knowledge based on usage and success."""
        if knowledge_id not in self.scores:
            self.scores[knowledge_id] = {
                "usage_count": 0,
                "success_rate": 1.0,
                "last_used": time.time(),
                "base_score": 0.5,
                "promoted": False
            }
        
        entry = self.scores[knowledge_id]
        entry["usage_count"] += 1
        entry["last_used"] = time.time()
        
        # Calculate success moving average
        alpha = 0.1
        current_success = 1.0 if success else 0.0
        entry["success_rate"] = (1 - alpha) * entry["success_rate"] + alpha * current_success
        
        # Final Score calculation
        score = (entry["success_rate"] * 0.6) + (min(entry["usage_count"] / 10, 1.0) * 0.4)
        
        if score >= self.promotion_threshold and not entry["promoted"]:
            self.promote(knowledge_id)
            entry["promoted"] = True
            
        return score

    def promote(self, knowledge_id: str):
        """Point 9: Promote high-value data to persistent/priority store."""
        logger.info(f"quality_control: PROMOTING knowledge_id='{knowledge_id}' due to high value.")
        # Logic to move to canonical store or set priority flag

    def run_decay(self):
        """Point 9: Decay low-value data periodically."""
        now = time.time()
        to_delete = []
        for kid, entry in self.scores.items():
            # Decay based on recency (time since last used)
            idle_time = now - entry["last_used"]
            if idle_time > 86400 * 7: # 1 week idle
                entry["base_score"] -= self.decay_rate
                
            if entry["base_score"] <= 0 and entry["usage_count"] < 3:
                to_delete.append(kid)
                
        for kid in to_delete:
            logger.info(f"quality_control: DECAYING knowledge_id='{kid}' - removing low-value data.")
            del self.scores[kid]

global_quality_control = QualityControl()
