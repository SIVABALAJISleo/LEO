"""
hyper_universal/incremental/engine.py
Incremental Computation and Temporal Reuse Engine:
Tracks dirty regions, invalidates stale state, and reuses invariant computations
across sequential frames, simulation time-steps, and interactive queries.
"""
from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np


@dataclass
class IncrementalUpdateReport:
    total_elements: int
    dirty_elements: int
    elements_reused: int
    reuse_ratio: float
    execution_latency_ms: float
    full_compute_latency_ms: float
    effective_speedup: float
    exactness_preserved: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_elements": self.total_elements,
            "dirty_elements": self.dirty_elements,
            "elements_reused": self.elements_reused,
            "reuse_ratio": round(self.reuse_ratio, 4),
            "execution_latency_ms": round(self.execution_latency_ms, 3),
            "full_compute_latency_ms": round(self.full_compute_latency_ms, 3),
            "effective_speedup": round(self.effective_speedup, 2),
            "exactness_preserved": self.exactness_preserved,
        }


class IncrementalStateCache:
    """Manages cached computational states with dependency hashing."""

    def __init__(self, max_entries: int = 128):
        self.max_entries = max_entries
        self.cache: Dict[str, Tuple[Any, float]] = {}

    def get(self, key_hash: str) -> Optional[Any]:
        if key_hash in self.cache:
            val, _ = self.cache[key_hash]
            return val
        return None

    def put(self, key_hash: str, value: Any):
        if len(self.cache) >= self.max_entries:
            # Simple FIFO eviction
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key_hash] = (value, time.time())

    def invalidate_all(self):
        self.cache.clear()


class IncrementalExecutionEngine:
    """Detects dirty regions and executes incremental updates."""

    def __init__(self):
        self.cache = IncrementalStateCache()

    @staticmethod
    def incremental_matrix_vector_update(
        A: np.ndarray,
        prev_x: np.ndarray,
        new_x: np.ndarray,
        prev_y: np.ndarray,
    ) -> Tuple[np.ndarray, IncrementalUpdateReport]:
        """
        Updates y = A @ new_x given prev_y = A @ prev_x.
        Instead of full O(M*K) matmul, computes delta y_delta = A[:, dirty_cols] @ delta_x[dirty_cols]
        where delta_x is non-zero.
        """
        m, k = A.shape
        total_elements = k

        t_full_0 = time.perf_counter()
        _ = A @ new_x
        t_full = time.perf_counter() - t_full_0

        t0 = time.perf_counter()
        delta_x = new_x - prev_x
        dirty_indices = np.flatnonzero(delta_x != 0)
        dirty_count = len(dirty_indices)

        if dirty_count == 0:
            # 100% temporal reuse
            y_out = prev_y.copy()
        elif dirty_count < k // 2:
            # Incremental update wins
            delta_y = A[:, dirty_indices] @ delta_x[dirty_indices]
            y_out = prev_y + delta_y
        else:
            # Full recalculation
            y_out = A @ new_x
        t_inc = time.perf_counter() - t0

        speedup = (t_full / t_inc) if t_inc > 0 else 1.0
        reused_elements = total_elements - dirty_count
        ratio = reused_elements / max(total_elements, 1)

        diff = float(np.max(np.abs(y_out - (A @ new_x))))
        is_exact = diff <= 1e-5

        report = IncrementalUpdateReport(
            total_elements=total_elements,
            dirty_elements=dirty_count,
            elements_reused=reused_elements,
            reuse_ratio=ratio,
            execution_latency_ms=t_inc * 1000.0,
            full_compute_latency_ms=t_full * 1000.0,
            effective_speedup=speedup,
            exactness_preserved=is_exact,
        )
        return y_out, report
