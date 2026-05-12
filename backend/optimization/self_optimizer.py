"""
backend/optimization/self_optimizer.py
Self-Optimization Engine (Point 14).

Monitors performance metrics (reuse_rate, latency) and 
adjusts semantic clustering thresholds and pipeline execution.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SelfOptimizer:
    """
    Self-Optimization: Auto-adjust thresholds and pipeline.
    """
    def __init__(self, target_latency_ms: float = 200.0):
        self.target_latency_ms = target_latency_ms
        self.target_avoidance = 0.98  # Point 14 target
        self.current_threshold = 0.90
        self.prediction_depth = 12
        self.cache_ttl_policy = "standard"

    def update_metrics(self, avoidance_rate: float, avg_latency: float):
        """
        Point 7: Auto-adjust thresholds, prediction depth, and cache policies.
        """
        logger.info(f"self_optimizer: Analyzing metrics (Avoidance={avoidance_rate:.2f}, Latency={avg_latency:.2f}ms)")

        # 1. REACHING 98% DOMINANCE: If avoidance is low, increase prediction depth
        if avoidance_rate < self.target_avoidance:
            self.prediction_depth = min(self.prediction_depth + 1, 25)
            # Relax threshold slightly to find more semantic matches
            self.current_threshold = max(self.current_threshold - 0.005, 0.85)
            logger.info(f"self_optimizer: INCREASING prediction depth to {self.prediction_depth} via Point 7.")

        # 2. STABILITY PROTECTION: If latency is high, reduce depth and tighten thresholds
        if avg_latency > self.target_latency_ms:
            self.prediction_depth = max(self.prediction_depth - 2, 5)
            self.current_threshold = min(self.current_threshold + 0.01, 0.95)
            self.cache_ttl_policy = "aggressive_pruning"
            logger.info("self_optimizer: TIGHTENING stability guards due to latency pressure.")
        else:
            self.cache_ttl_policy = "persistent"

    def get_threshold(self) -> float:
        return self.current_threshold

    def get_prediction_depth(self) -> int:
        return self.prediction_depth

global_self_optimizer = SelfOptimizer()
