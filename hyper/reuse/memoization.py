"""
hyper/reuse/memoization.py
==========================
Intermediate-Result & Output Memoization Engine.
Ensures precomputation cost is explicitly tracked and accounted for.
"""

import time
import hashlib
from typing import Dict, Any, Optional, Tuple, Callable
import numpy as np


class MemoizationEngine:
    """
    Manages deterministic intermediate and final result reuse.
    """
    def __init__(self, max_entries: int = 5000):
        self._table: Dict[str, Any] = {}
        self._precomputation_time_ms: float = 0.0
        self._hits: int = 0
        self._misses: int = 0
        self._max_entries = max_entries

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], Any],
        is_precomputed: bool = False
    ) -> Tuple[Any, bool, float]:
        """
        Retrieves memoized result or executes compute_fn.
        Returns: (result, is_hit, elapsed_ms)
        """
        if key in self._table:
            self._hits += 1
            return self._table[key], True, 0.01

        self._misses += 1
        t0 = time.perf_counter()
        result = compute_fn()
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        if is_precomputed:
            self._precomputation_time_ms += elapsed_ms

        if len(self._table) < self._max_entries:
            self._table[key] = result

        return result, False, elapsed_ms

    def clear(self) -> None:
        self._table.clear()

    def stats(self) -> Dict[str, Any]:
        return {
            "entries_count": len(self._table),
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio": round(self._hits / max(1, self._hits + self._misses), 4),
            "total_precomputation_time_ms": round(self._precomputation_time_ms, 2),
        }
