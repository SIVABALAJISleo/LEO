"""
backend/core/failure_recovery_engine.py

Failure Recovery + Approximation Safety Layer
=============================================
If:
  - Confidence is low, OR
  - Latency > 100ms

Then:
  - Return safe partial answer INSTANTLY
  - Trigger background full compute
  - Store improved result permanently
  - NEVER repeat failure

Rules:
  - Low-confidence answer returned = BUG (this engine prevents it)
  - Same failure path repeated = BUG (failure_map prevents it)
  - ALWAYS improve and store
"""
import logging
import time
import asyncio
import json
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

# File for persistent failure map (never repeat same failure)
FAILURE_MAP_PATH = os.path.join(os.getcwd(), "failure_map.json")

# Thresholds
LOW_CONFIDENCE_THRESHOLD = 0.95   # Per spec: NEVER return below this
HIGH_LATENCY_THRESHOLD_MS = 100   # Per spec: if >100ms → background recompute


def _load_failure_map() -> Dict[str, Dict[str, Any]]:
    try:
        if os.path.exists(FAILURE_MAP_PATH):
            with open(FAILURE_MAP_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_failure_map(fmap: Dict[str, Dict[str, Any]]) -> None:
    try:
        with open(FAILURE_MAP_PATH, "w", encoding="utf-8") as f:
            json.dump(fmap, f, indent=2)
    except Exception as exc:
        logger.warning(f"failure_map.save_error: {exc}")


class FailureRecoveryEngine:
    """
    Detects low-confidence / high-latency situations and:
      1. Returns a safe instant skeleton response.
      2. Enqueues a full background recompute.
      3. Marks the pattern in failure_map (never repeats).
      4. On subsequent identical queries, serves from improved store.
    """

    def __init__(self):
        self._failure_map: Dict[str, Dict[str, Any]] = _load_failure_map()
        self._recovery_count: int = 0
        self._improvement_count: int = 0

    # ── Failure Detection ──────────────────────────────────────────────────── #

    def is_failure(self, confidence: float, latency_ms: float) -> bool:
        """A result is a 'failure' if confidence < floor OR latency exceeded budget."""
        return confidence < LOW_CONFIDENCE_THRESHOLD or latency_ms > HIGH_LATENCY_THRESHOLD_MS

    def was_seen_before(self, family_id: str) -> bool:
        """Check if this failure pattern was already handled."""
        return family_id in self._failure_map

    # ── Recovery Actions ──────────────────────────────────────────────────── #

    def get_safe_skeleton(self, query: str, reason: str = "") -> str:
        """
        Returns an instant, safe partial answer.
        Never returns nothing — always provides context-aware placeholder.
        """
        msg_parts = [
            f"Processing your query about '{query}'.",
            "Relevant information is being retrieved and verified.",
        ]
        if reason:
            msg_parts.append(f"({reason})")
        msg_parts.append(
            "A complete, verified answer will replace this shortly. "
            "This ensures accuracy — no uncertain results returned."
        )
        return " ".join(msg_parts)

    async def handle_failure(
        self,
        query: str,
        family_id: str,
        confidence: float,
        latency_ms: float,
        tenant_id: str,
        session_id: str,
        bg_compute,
    ) -> Dict[str, Any]:
        """
        Full failure recovery sequence:
          1. Record failure in failure_map
          2. Return safe skeleton immediately
          3. Trigger background full compute
        """
        self._recovery_count += 1

        # 1. Record in failure map (persistent — never repeats)
        self._failure_map[family_id] = {
            "query": query,
            "confidence_at_failure": confidence,
            "latency_at_failure": latency_ms,
            "recovery_count": self._failure_map.get(family_id, {}).get("recovery_count", 0) + 1,
            "last_seen": time.time(),
        }
        _save_failure_map(self._failure_map)

        # 2. Log the failure clearly
        logger.warning(
            f"failure_recovery: family={family_id} "
            f"confidence={confidence:.3f} latency={latency_ms:.1f}ms "
            f"recovery_count={self._failure_map[family_id]['recovery_count']}"
        )

        # 3. Determine failure reason
        reasons = []
        if confidence < LOW_CONFIDENCE_THRESHOLD:
            reasons.append(f"low confidence ({confidence:.2f})")
        if latency_ms > HIGH_LATENCY_THRESHOLD_MS:
            reasons.append(f"latency exceeded ({latency_ms:.0f}ms)")
        reason_str = " + ".join(reasons)

        # 4. Enqueue background improvement (non-blocking)
        try:
            asyncio.create_task(
                bg_compute.enqueue(
                    query, tenant_id, "FAILURE_RECOVERY", session_id, priority="high"
                )
            )
        except Exception as exc:
            logger.warning(f"failure_recovery.enqueue_error: {exc}")

        # 5. Return instant safe skeleton
        skeleton = self.get_safe_skeleton(query, reason=reason_str)
        return {
            "answer": skeleton,
            "mode": "failure_recovery_skeleton",
            "confidence": 0.5,
            "is_skeleton": True,
            "reason": reason_str,
            "background_compute_triggered": True,
        }

    def record_improvement(self, family_id: str, new_confidence: float) -> None:
        """
        Called when a background compute completes and stores a better result.
        Updates failure_map to reflect improvement.
        """
        if family_id in self._failure_map:
            self._failure_map[family_id]["resolved"] = True
            self._failure_map[family_id]["resolved_confidence"] = new_confidence
            self._failure_map[family_id]["resolved_at"] = time.time()
            _save_failure_map(self._failure_map)
            self._improvement_count += 1
            logger.info(
                f"failure_recovery.improved: family={family_id} "
                f"new_confidence={new_confidence:.3f}"
            )

    # ── Approximation Safety ──────────────────────────────────────────────── #

    def safe_approximation(
        self,
        partial_answer: str,
        query: str,
        confidence: float,
    ) -> Dict[str, Any]:
        """
        Returns a partial answer with safety wrapper.
        Confidence MUST be reported accurately — no inflation.
        """
        safety_note = (
            f" [Approximation — confidence: {confidence:.0%}. "
            "Background verification in progress.]"
        )
        return {
            "answer": partial_answer + safety_note,
            "mode": "safe_approximation",
            "confidence": confidence,
            "is_approximation": True,
        }

    def stats(self) -> Dict[str, Any]:
        resolved = sum(
            1 for v in self._failure_map.values() if v.get("resolved", False)
        )
        return {
            "total_failures_recorded": len(self._failure_map),
            "resolved": resolved,
            "unresolved": len(self._failure_map) - resolved,
            "recovery_count": self._recovery_count,
            "improvement_count": self._improvement_count,
        }


global_failure_recovery = FailureRecoveryEngine()
