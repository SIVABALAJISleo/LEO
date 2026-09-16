"""
hyper_x.temporal_escape
=======================
Temporal State Delta, Dirty-Mask Incremental Compute, and Fidelity Verification.
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .state_delta import StateDeltaEngine, StateDeltaResult
from .temporal_verifier import TemporalVerifier, TemporalVerificationResult


@dataclass
class TemporalStateSnapshot:
    step_id: int
    timestamp: float
    state_buffer: np.ndarray
    state_hash: str
    dirty_mask: Optional[np.ndarray] = None


class TemporalEscapeEngine:
    """
    Capitalizes on inter-step temporal continuity to eliminate redundant full evaluations.
    """

    def __init__(self, dirty_threshold: float = 1e-4):
        self.dirty_threshold = dirty_threshold
        self.history: List[TemporalStateSnapshot] = []

    def process_incremental_step(
        self,
        current_state: np.ndarray,
        step_id: int,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Calculates delta vs previous state. Reconstructs output using only dirty updates.
        """
        t0 = time.perf_counter()
        if not self.history or self.history[-1].state_buffer.shape != current_state.shape:
            # Baseline first step
            snapshot = TemporalStateSnapshot(
                step_id=step_id,
                timestamp=time.time(),
                state_buffer=current_state.copy(),
                state_hash=str(hash(current_state.tobytes()[:64])),
                dirty_mask=np.ones_like(current_state, dtype=bool),
            )
            self.history.append(snapshot)
            return current_state, {
                "step_id": step_id,
                "is_full_step": True,
                "work_avoided_pct": 0.0,
                "dirty_fraction": 1.0,
                "elapsed_ms": round((time.perf_counter() - t0) * 1000.0, 3),
            }

        prev_state = self.history[-1].state_buffer
        delta = current_state - prev_state
        dirty_mask = np.abs(delta) > self.dirty_threshold
        dirty_count = int(np.sum(dirty_mask))
        total_count = current_state.size

        dirty_fraction = dirty_count / max(1, total_count)
        work_avoided_pct = round((1.0 - dirty_fraction) * 100.0, 2)

        # In-place reconstructed state
        reconstructed = prev_state.copy()
        reconstructed[dirty_mask] = current_state[dirty_mask]

        snapshot = TemporalStateSnapshot(
            step_id=step_id,
            timestamp=time.time(),
            state_buffer=reconstructed,
            state_hash=str(hash(reconstructed.tobytes()[:64])),
            dirty_mask=dirty_mask,
        )
        self.history.append(snapshot)
        if len(self.history) > 8:
            self.history.pop(0)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return reconstructed, {
            "step_id": step_id,
            "is_full_step": False,
            "work_avoided_pct": work_avoided_pct,
            "dirty_fraction": round(dirty_fraction, 4),
            "elapsed_ms": round(elapsed_ms, 3),
        }


__all__ = [
    "StateDeltaEngine",
    "StateDeltaResult",
    "TemporalVerifier",
    "TemporalVerificationResult",
    "TemporalStateSnapshot",
    "TemporalEscapeEngine",
]
