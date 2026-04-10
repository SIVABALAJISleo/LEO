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
    def __init__(self, target_latency_ms: float = 50.0):
        self.target_latency_ms = target_latency_ms
        self.reuse_rate = 0.0
        self.avg_latency = 0.0
        self.base_semantic_threshold = 0.85
        self.current_semantic_threshold = 0.85

    def update_metrics(self, reuse_rate: float, avg_latency: float):
        """Update metrics and adjust system parameters."""
        self.reuse_rate = reuse_rate
        self.avg_latency = avg_latency
        
        # 1. Latency Optimization: If latency > target, tighten thresholds
        if avg_latency > self.target_latency_ms:
            # Increase threshold to favor faster direct matches
            self.current_semantic_threshold = min(self.current_semantic_threshold + 0.01, 0.95)
            logger.info("self_optimizer: TIGHTENING threshold due to latency pressure.")
        
        # 2. Reuse Optimization: If reuse is low, lower threshold slightly (within reason)
        elif self.reuse_rate < 0.7:
             # Lower threshold slightly to increase hit-rate (but never below 0.82)
             self.current_semantic_threshold = max(self.current_semantic_threshold - 0.005, 0.82)
             logger.info("self_optimizer: LOWERING threshold to increase reuse_rate.")

    def get_threshold(self) -> float:
        """Returns the currently optimized semantic threshold."""
        return self.current_semantic_threshold

global_self_optimizer = SelfOptimizer()
