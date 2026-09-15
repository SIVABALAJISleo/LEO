"""
hyper/cache/exact_cache.py
==========================
Cryptographic Multi-State Exact Cache for LEO/HYPER.
Fulfills Phase 5 of the Master Architectural Specification.
Guarantees zero leakage, full provenance, and distinct hit/miss telemetry.
"""

import hashlib
import json
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


def compute_cache_key(
    input_data: Any,
    model_identifier: str,
    parameters: Optional[Dict[str, Any]] = None,
    precision: str = "float32",
    random_seed: Optional[int] = None,
    software_version: str = "10.0.0",
    hardware_backend: str = "CPU_AVX2",
    contract_repr: str = "default_contract",
    algorithm_version: str = "1.0",
) -> str:
    """
    Construct a complete cryptographic multi-state cache key incorporating all execution factors:
    input hash, model hash, parameters, precision, random seed, software version,
    hardware backend, contract version, algorithm version.
    """
    hasher = hashlib.sha256()

    # 1. Input hash
    if isinstance(input_data, np.ndarray):
        hasher.update(input_data.tobytes())
        hasher.update(str(input_data.shape).encode("utf-8"))
        hasher.update(str(input_data.dtype).encode("utf-8"))
    elif isinstance(input_data, (bytes, bytearray)):
        hasher.update(input_data)
    elif isinstance(input_data, (dict, list)):
        hasher.update(json.dumps(input_data, sort_keys=True).encode("utf-8"))
    else:
        hasher.update(str(input_data).encode("utf-8"))

    # 2. Model hash / identifier
    hasher.update(hashlib.sha256(model_identifier.encode("utf-8")).digest())

    # 3. Parameters
    norm_params = json.dumps(parameters or {}, sort_keys=True)
    hasher.update(norm_params.encode("utf-8"))

    # 4. Precision
    hasher.update(precision.lower().encode("utf-8"))

    # 5. Random seed
    hasher.update(str(random_seed if random_seed is not None else "NONE").encode("utf-8"))

    # 6. Software version
    hasher.update(software_version.encode("utf-8"))

    # 7. Hardware backend
    hasher.update(hardware_backend.upper().encode("utf-8"))

    # 8. Contract representation
    hasher.update(contract_repr.encode("utf-8"))

    # 9. Algorithm version
    hasher.update(algorithm_version.encode("utf-8"))

    return hasher.hexdigest()


class ExactCache:
    """
    Thread-safe, contract-isolated cryptographic cache.
    Never equates a cache hit with a computation speedup.
    """

    def __init__(self, is_enabled: bool = True, max_entries: int = 10000):
        self._store: Dict[str, Tuple[Any, float, Dict[str, Any]]] = {}
        self._lock = threading.RLock()
        self.is_enabled = is_enabled
        self.max_entries = max_entries

        # Telemetry
        self.hits = 0
        self.misses = 0
        self.hit_latencies_ns: List[int] = []
        self.miss_latencies_ns: List[int] = []
        self.cold_latency_ms: Optional[float] = None
        self.warm_latencies_ms: List[float] = []

    def get(self, key: str) -> Tuple[Optional[Any], bool, float]:
        """
        Lookup entry by key.
        Returns (value, cache_hit, lookup_time_ns).
        """
        t0 = time.perf_counter_ns()
        with self._lock:
            if not self.is_enabled:
                elapsed = time.perf_counter_ns() - t0
                self.misses += 1
                self.miss_latencies_ns.append(elapsed)
                return None, False, elapsed

            entry = self._store.get(key)
            elapsed = time.perf_counter_ns() - t0

            if entry is not None:
                val, timestamp, meta = entry
                self.hits += 1
                self.hit_latencies_ns.append(elapsed)
                return val, True, elapsed
            else:
                self.misses += 1
                self.miss_latencies_ns.append(elapsed)
                return None, False, elapsed

    def put(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Store a verified value with associated provenance metadata."""
        if not self.is_enabled:
            return
        with self._lock:
            if len(self._store) >= self.max_entries:
                # Evict oldest entry
                oldest_key = min(self._store.keys(), key=lambda k: self._store[k][1])
                del self._store[oldest_key]

            self._store[key] = (value, time.time(), metadata or {})

    def invalidate(self, key: str) -> bool:
        """Evict an entry explicitly (e.g. on corruption or invalidation)."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def clear(self) -> None:
        """Wipe all entries and reset telemetry."""
        with self._lock:
            self._store.clear()
            self.hits = 0
            self.misses = 0
            self.hit_latencies_ns.clear()
            self.miss_latencies_ns.clear()
            self.cold_latency_ms = None
            self.warm_latencies_ms.clear()

    def record_execution_latencies(self, latency_ms: float, is_cold: bool) -> None:
        """Track cold and warm execution latencies separately from cache lookup overhead."""
        with self._lock:
            if is_cold or self.cold_latency_ms is None:
                self.cold_latency_ms = latency_ms
            else:
                self.warm_latencies_ms.append(latency_ms)

    def report_metrics(self) -> Dict[str, Any]:
        """Produce honest, separated cache telemetry."""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total) if total > 0 else 0.0

            avg_hit_ns = float(np.mean(self.hit_latencies_ns)) if self.hit_latencies_ns else 0.0
            avg_miss_ns = float(np.mean(self.miss_latencies_ns)) if self.miss_latencies_ns else 0.0

            return {
                "cache_enabled": self.is_enabled,
                "total_queries": total,
                "cache_hits": self.hits,
                "cache_misses": self.misses,
                "cache_hit_rate": hit_rate,
                "cache_hit_latency_ns_median": float(np.median(self.hit_latencies_ns)) if self.hit_latencies_ns else 0.0,
                "cache_hit_latency_ns_mean": avg_hit_ns,
                "cache_miss_latency_ns_median": float(np.median(self.miss_latencies_ns)) if self.miss_latencies_ns else 0.0,
                "cache_miss_latency_ns_mean": avg_miss_ns,
                "cold_latency_ms": self.cold_latency_ms,
                "warm_latency_ms_median": float(np.median(self.warm_latencies_ms)) if self.warm_latencies_ms else None,
                "warm_latency_ms_mean": float(np.mean(self.warm_latencies_ms)) if self.warm_latencies_ms else None,
                "entry_count": len(self._store),
            }
