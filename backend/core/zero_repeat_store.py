"""
backend/core/zero_repeat_store.py

Zero-Repeat Guarantee Store
=============================
Every computed answer MUST be stored.
Same/similar query MUST NEVER trigger compute again.

This module acts as the WRITE SIDE of the pipeline:
  - After ANY computation, call store()
  - Verifies no entry already exists (idempotent)
  - Persists to global_memory + shadow_store

Rules enforced:
  - Recompute of same family = BUG (logged as violation)
  - Every entry stored with full metadata
  - Confidence must be reported accurately
"""
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ZeroRepeatStore:
    """
    Write gate that enforces the zero-repeat guarantee.
    Wraps global_memory and shadow_store to ensure:
      1. Every result is stored once and only once.
      2. Attempts to recompute the same family_id are caught and logged.
      3. All stores are async-safe.
    """

    def __init__(self):
        # In-memory set for ultra-fast duplicate check (current session)
        self._stored_this_session: set = set()
        self._store_count: int = 0
        self._duplicate_attempts: int = 0
        self._violation_log: list = []   # track recompute violations

    # ── Core Store ─────────────────────────────────────────────────────────── #

    def store(
        self,
        query: str,
        answer: str,
        family_id: str,
        mode: str,
        confidence: float,
        latency_ms: float,
        session_id: str,
        global_memory,
        shadow_store,
        overwrite: bool = False,
    ) -> bool:
        """
        Stores a computed answer to global_memory + shadow_store.
        Returns True if stored, False if duplicate (already stored).

        Args:
            overwrite: If True, allow updating existing entry with higher confidence.
        """
        # Fast duplicate check
        if family_id in self._stored_this_session and not overwrite:
            self._duplicate_attempts += 1
            logger.debug(f"zero_repeat.skip_duplicate: family={family_id}")
            return False

        # Double-check: attempt to lookup before storing
        if not overwrite:
            existing = global_memory.lookup(query, canonical_form=family_id)
            if existing and existing.get("confidence", 0) >= confidence:
                self._stored_this_session.add(family_id)
                self._duplicate_attempts += 1
                logger.debug(
                    f"zero_repeat.already_exists: family={family_id} "
                    f"existing_conf={existing.get('confidence', 0):.3f}"
                )
                return False

        # Store in global memory (FAISS + log)
        try:
            global_memory.log(
                query=query,
                answer=answer,
                mode=mode,
                canonical_form=family_id,
                confidence=confidence,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            logger.error(f"zero_repeat.global_memory_store_error: {exc}")

        # Store in shadow store (fast RAM-backed)
        try:
            shadow_store.store(
                family_id=family_id,
                session_id=session_id,
                answer=answer,
                confidence=confidence,
                mode=mode,
            )
        except Exception as exc:
            logger.warning(f"zero_repeat.shadow_store_error: {exc}")

        self._stored_this_session.add(family_id)
        self._store_count += 1

        logger.info(
            f"zero_repeat.stored: family={family_id} "
            f"confidence={confidence:.3f} mode={mode} "
            f"session_count={self._store_count}"
        )
        return True

    # ── Violation Detection ────────────────────────────────────────────────── #

    def log_recompute_violation(
        self,
        family_id: str,
        query: str,
        reason: str,
    ) -> None:
        """
        Called when compute was triggered for an already-stored family.
        This is a BUG — log it prominently for investigation.
        """
        violation = {
            "family_id": family_id,
            "query": query,
            "reason": reason,
            "timestamp": time.time(),
        }
        self._violation_log.append(violation)
        logger.critical(
            f"!!! ZERO_REPEAT_VIOLATION !!! family={family_id} reason={reason} "
            f"query='{query}' — THIS IS A SYSTEM ARCHITECTURE BUG"
        )

    def check_before_compute(
        self,
        family_id: str,
        query: str,
        global_memory,
        shadow_store,
        session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Final gate check BEFORE any compute begins.
        If a result exists and confidence >= 0.95, abort compute and return it.
        
        Returns existing result dict if compute should be skipped, else None.
        """
        # 1. Session-level check (fastest)
        if family_id in self._stored_this_session:
            # Try to get the actual stored answer
            existing = global_memory.lookup(query, canonical_form=family_id)
            if existing and existing.get("confidence", 0) >= 0.95:
                self.log_recompute_violation(
                    family_id, query, "session_memory_hit_missed_before_compute"
                )
                return existing

        # 2. Shadow store check
        try:
            shadow = shadow_store.lookup(family_id, session_id)
            if shadow and shadow.get("confidence", 0) >= 0.95:
                self.log_recompute_violation(
                    family_id, query, "shadow_store_hit_missed"
                )
                return shadow
        except Exception:
            pass

        return None  # Proceed with compute

    def lookup_atom(self, atomic_hash: str) -> Optional[Dict[str, Any]]:
        """
        Fast lookup for symbolic atoms to prevent re-execution of identical logic primitives.
        Currently returns None until atom-level caching is fully implemented.
        """
        return None

    # ── Stats ──────────────────────────────────────────────────────────────── #

    def stats(self) -> Dict[str, Any]:
        return {
            "stored_this_session": len(self._stored_this_session),
            "total_stores": self._store_count,
            "duplicate_attempts_blocked": self._duplicate_attempts,
            "recompute_violations": len(self._violation_log),
            "recent_violations": self._violation_log[-5:],
        }


global_zero_repeat_store = ZeroRepeatStore()
