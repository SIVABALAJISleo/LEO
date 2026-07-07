"""
Failure Learning Engine
When the pipeline fails (falls through to model or returns low-confidence answer),
store the failure pattern so the system can avoid it next time.
Turn every failure into future avoidance.
"""
import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class FailureStore:
    """
    Stores failure patterns and learns from them.
    Failures are indexed by shape_key.
    After sufficient failures, triggers precomputation of canonical answer.
    """

    def __init__(self):
        self._failures: Dict[str, List[Dict]] = {}
        self._fixed: Dict[str, str] = {}  # shape_key → fixed answer

    def record_failure(
        self,
        query: str,
        shape_key: str,
        mode: str,
        confidence: float,
        reason: str = "low_confidence",
    ):
        """Record a pipeline failure for learning."""
        if shape_key not in self._failures:
            self._failures[shape_key] = []

        self._failures[shape_key].append({
            "query": query,
            "mode": mode,
            "confidence": confidence,
            "reason": reason,
            "timestamp": time.time(),
        })
        count = len(self._failures[shape_key])
        logger.warning(f"failure_recorded: shape={shape_key} count={count} reason={reason}")

        # Auto-trigger canonical registration after 3+ failures for same shape
        if count >= 3:
            self._trigger_auto_fix(shape_key)

    def _trigger_auto_fix(self, shape_key: str):
        """Signal that this shape needs a canonical answer pre-seeded."""
        if shape_key not in self._fixed:
            logger.info(f"failure_auto_fix_triggered: shape={shape_key}")
            # In production: queue this for precompute expander
            # Here: mark as "needs_canonical" for monitoring
            self._fixed[shape_key] = "PENDING_CANONICAL"

    def record_fix(self, shape_key: str, answer: str):
        """Register a fixed answer for a previously failing shape."""
        self._fixed[shape_key] = answer
        logger.info(f"failure_fixed: shape={shape_key}")

    def is_known_failure(self, shape_key: str) -> bool:
        """Check if this shape has historically failed."""
        return len(self._failures.get(shape_key, [])) > 0

    def get_shapes_needing_precompute(self) -> List[str]:
        """Returns shape_keys that have failed 3+ times and need canonical answers."""
        return [
            k for k, v in self._failures.items()
            if len(v) >= 3 and self._fixed.get(k) in (None, "PENDING_CANONICAL")
        ]

    def stats(self) -> Dict[str, Any]:
        return {
            "total_failure_shapes": len(self._failures),
            "total_fixed": sum(1 for v in self._fixed.values() if v != "PENDING_CANONICAL"),
            "pending_fixes": sum(1 for v in self._fixed.values() if v == "PENDING_CANONICAL"),
        }


global_failure_store = FailureStore()
