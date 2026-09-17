"""
backend/caoe/cache_manager.py
=============================
CAOE Layer 4: Caching & Memoization Layer.

Smart, bounded in-memory cache with:
- SHA-256 / fast hashing
- Configurable TTL (Time-to-Live)
- Memory footprint ceiling (max_size_mb)
- Detailed hit / miss telemetry
"""

from __future__ import annotations

import collections
import hashlib
import time
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

from .contract_analyzer import Contract


class CacheManager:
    """Reuse computed results under declared contract parameters."""

    def __init__(self, max_size_mb: float = 512.0) -> None:
        self.cache: Dict[str, Tuple[Any, Dict[str, Any]]] = collections.OrderedDict()
        self.max_bytes = int(max_size_mb * 1024 * 1024)
        self.current_bytes = 0
        self.hits = 0
        self.misses = 0

    def _make_key(self, input_data: Any) -> str:
        if isinstance(input_data, np.ndarray):
            h = hashlib.sha256()
            h.update(input_data.tobytes())
            h.update(str(input_data.shape).encode())
            h.update(str(input_data.dtype).encode())
            return h.hexdigest()
        return hashlib.sha256(str(input_data).encode()).hexdigest()

    def get_or_compute(
        self,
        input_data: Any,
        computation_fn: Callable[[], Any],
        contract: Contract,
    ) -> Tuple[Any, Dict[str, Any]]:
        key = self._make_key(input_data)
        now = time.time()

        # Check Cache
        if key in self.cache:
            result, meta = self.cache[key]
            is_expired = (now - meta["created"]) > meta["ttl"] if meta["ttl"] > 0 else False
            if not is_expired:
                self.hits += 1
                # Move to end for LRU order
                self.cache.move_to_end(key)
                return result, {
                    "source": "cache",
                    "latency_ms": 0.05,
                    "hit": True,
                }
            else:
                # Evict expired
                del self.cache[key]
                self.current_bytes -= meta.get("size_bytes", 0)

        self.misses += 1

        # Compute
        t0 = time.perf_counter_ns()
        result = computation_fn()
        compute_ms = max(1e-6, (time.perf_counter_ns() - t0) / 1e6)

        # Cache Insertion if contract permits
        size_bytes = getattr(result, "nbytes", 1024)
        if contract.cache_ttl > 0 and (self.current_bytes + size_bytes) <= self.max_bytes:
            # Evict LRU if needed
            while self.cache and (self.current_bytes + size_bytes) > self.max_bytes:
                k, (old_res, old_meta) = self.cache.popitem(last=False)
                self.current_bytes -= old_meta.get("size_bytes", 0)

            self.cache[key] = (result, {
                "created": now,
                "ttl": contract.cache_ttl,
                "precision": contract.precision,
                "size_bytes": size_bytes,
            })
            self.current_bytes += size_bytes

        return result, {
            "source": "computed",
            "latency_ms": compute_ms,
            "hit": False,
        }

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0

    def clear(self) -> None:
        self.cache.clear()
        self.current_bytes = 0
        self.hits = 0
        self.misses = 0
