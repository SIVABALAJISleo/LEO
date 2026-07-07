"""
backend/inference/early_exit.py
Layer 3 — Skip Sequential Token Steps: Early Exit Controller.

Decides whether to terminate transformer forward pass early at an intermediate
layer once intermediate output distribution confidence exceeds a threshold.
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Thresholds by execution block / mode
CONFIDENCE_THRESHOLDS = {
    "ANSWER_GRAPH":       0.90,
    "PREDICTIVE_STORE":   0.88,
    "SHADOW_STORE":       0.85,
    "SEMANTIC_CACHE":     0.90,
    "TEMPLATE":           0.95,
    "ENHANCEMENT":        0.80,
    "MICRO_MODEL":        0.82,
}


class EarlyExitController:
    """
    Decides whether to exit from the pipeline early with the current answer,
    or terminate a model's forward pass at an intermediate transformer layer.
    """

    def should_exit(self, result: Optional[Dict[str, Any]], mode: str) -> bool:
        """
        Returns True if the result confidence is above the exit threshold for this mode.
        """
        if not result:
            return False

        confidence = result.get("confidence", 0.0)
        threshold = CONFIDENCE_THRESHOLDS.get(mode, 0.85)

        if confidence >= threshold:
            logger.info(f"early_exit: mode={mode} confidence={confidence:.2f} threshold={threshold}")
            return True

        return False

    def should_exit_layer(self, layer_idx: int, total_layers: int, confidence: float, threshold: float = 0.80) -> bool:
        """
        CALM-style early exit for intermediate layers.
        If confidence at layer_idx exceeds the threshold, exit forward pass early.
        """
        # Ensure we do at least 25% of the model layers for basic representation stability
        min_layers = max(1, total_layers // 4)
        if layer_idx < min_layers:
            return False
            
        if confidence >= threshold:
            logger.info(f"layer_early_exit: layer={layer_idx}/{total_layers} confidence={confidence:.4f} threshold={threshold} -> EXITING EARLY")
            return True
            
        return False

    def best_result(self, results: list) -> Optional[Dict[str, Any]]:
        """
        From a list of partial results, return the one with highest confidence.
        """
        if not results:
            return None
        return max(results, key=lambda r: r.get("confidence", 0))


global_early_exit = EarlyExitController()
