"""
Early Exit Controller
Stops model computation early if confidence from a simpler/faster method is high enough.
Prevents unnecessary processing once a good-enough answer is found.
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Thresholds by mode
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
    Decides whether to exit from the pipeline early with the current answer.
    Called at each pipeline layer to check if we've found a good-enough answer.
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

    def best_result(self, results: list) -> Optional[Dict[str, Any]]:
        """
        From a list of partial results, return the one with highest confidence.
        """
        if not results:
            return None
        return max(results, key=lambda r: r.get("confidence", 0))


global_early_exit = EarlyExitController()
