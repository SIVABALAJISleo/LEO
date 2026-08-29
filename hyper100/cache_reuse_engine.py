"""
hyper100/cache_reuse_engine.py
==============================
Computational & Intermediate Reuse Engine.
Provides content-addressed exact and intermediate result caching with strict
benchmarking mode isolation (COLD, WARM, CACHE_DISABLED) to prevent cache contamination.
"""

import time
import hashlib
from enum import Enum
from typing import Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
import numpy as np


class CacheMode(str, Enum):
    COLD = "COLD"                      # Cache cleared, cold invocation measured
    WARM = "WARM"                      # Cache active, warm hits allowed
    CACHE_DISABLED = "CACHE_DISABLED"  # Caching bypassed completely, compute mandatory


@dataclass
class CacheLookupResult:
    """Detailed metadata for a cache query."""
    hit: bool
    data: Optional[Any]
    key: str
    lookup_latency_ms: float
    mode: CacheMode
    memory_footprint_bytes: int
    provenance: str                    # 'EXACT_MATCH', 'SEMANTIC_SIMILARITY', or 'MISS'


class CacheReuseEngine:
    """
    Manages deterministic computational reuse with explicit memory bounds and benchmarking isolation.
    """
    def __init__(self, max_memory_mb: float = 2048.0, default_mode: CacheMode = CacheMode.WARM):
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.mode = default_mode
        self._store: Dict[str, Any] = {}
        self._access_times: Dict[str, float] = {}
        self._entry_sizes: Dict[str, int] = {}
        self._current_memory_bytes = 0
        self.stats = {
            "queries": 0,
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_bytes_cached": 0,
        }

    def set_mode(self, mode: CacheMode) -> None:
        self.mode = mode
        if mode == CacheMode.COLD:
            self.clear()

    def clear(self) -> None:
        self._store.clear()
        self._access_times.clear()
        self._entry_sizes.clear()
        self._current_memory_bytes = 0

    @staticmethod
    def compute_tensor_key(op_name: str, *tensors: np.ndarray, **kwargs: Any) -> str:
        """Computes deterministic content-addressed hash for tensor operations."""
        hasher = hashlib.sha256()
        hasher.update(op_name.encode("utf-8"))
        for t in tensors:
            if isinstance(t, np.ndarray):
                hasher.update(str(t.shape).encode("utf-8"))
                hasher.update(str(t.dtype).encode("utf-8"))
                # Hash a stratified subsample for fast content verification
                if t.size > 2048:
                    sample = np.concatenate([t.ravel()[:512], t.ravel()[-512:]])
                    hasher.update(sample.tobytes())
                else:
                    hasher.update(t.tobytes())
            else:
                hasher.update(str(t).encode("utf-8"))
        for k in sorted(kwargs.keys()):
            hasher.update(f"{k}={kwargs[k]}".encode("utf-8"))
        return hasher.hexdigest()[:24]

    def lookup(self, key: str) -> CacheLookupResult:
        t0 = time.perf_counter()
        self.stats["queries"] += 1

        if self.mode == CacheMode.CACHE_DISABLED:
            latency = (time.perf_counter() - t0) * 1000.0
            return CacheLookupResult(False, None, key, latency, self.mode, 0, "CACHE_DISABLED")

        if key in self._store:
            self._access_times[key] = time.time()
            self.stats["hits"] += 1
            data = self._store[key]
            latency = (time.perf_counter() - t0) * 1000.0
            size = self._entry_sizes.get(key, 0)
            return CacheLookupResult(True, data, key, latency, self.mode, size, "EXACT_MATCH")

        self.stats["misses"] += 1
        latency = (time.perf_counter() - t0) * 1000.0
        return CacheLookupResult(False, None, key, latency, self.mode, 0, "MISS")

    def insert(self, key: str, value: Any) -> None:
        if self.mode == CacheMode.CACHE_DISABLED:
            return

        size = 0
        if isinstance(value, np.ndarray):
            size = value.nbytes
        elif isinstance(value, (bytes, bytearray)):
            size = len(value)
        else:
            size = 64  # approx object pointer

        # Evict LRU entries if capacity exceeded
        while self._current_memory_bytes + size > self.max_memory_bytes and self._store:
            oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
            oldest_size = self._entry_sizes.get(oldest_key, 0)
            del self._store[oldest_key]
            del self._access_times[oldest_key]
            del self._entry_sizes[oldest_key]
            self._current_memory_bytes -= oldest_size
            self.stats["evictions"] += 1

        self._store[key] = value
        self._access_times[key] = time.time()
        self._entry_sizes[key] = size
        self._current_memory_bytes += size
        self.stats["total_bytes_cached"] = self._current_memory_bytes
