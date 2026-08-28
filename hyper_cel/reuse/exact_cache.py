"""
hyper_cel/reuse/exact_cache.py
=============================================================================
HYPER-CEL: Computational DNA & Exact Result Cache (Level 0)
=============================================================================
Hashes the full computational context into a unique fingerprint:
    F = Hash(op_name, inputs_digest, parameters, contract)
Enables instantaneous 0-FLOP result retrieval.
"""

import hashlib
import time
import numpy as np
from typing import Dict, Any, Tuple, Optional

class ComputationalDNA:
    """Computes deterministic cryptographic fingerprint for a workload."""

    @staticmethod
    def fingerprint(op_name: str, inputs: Any, params: Dict[str, Any], contract_name: str) -> str:
        h = hashlib.sha256()
        h.update(op_name.encode("utf-8"))
        h.update(contract_name.encode("utf-8"))
        
        # Digest parameters
        param_str = str(sorted(params.items()))
        h.update(param_str.encode("utf-8"))

        # Digest inputs
        if isinstance(inputs, np.ndarray):
            h.update(str(inputs.shape).encode("utf-8"))
            h.update(str(inputs.dtype).encode("utf-8"))
            # Sample sample bytes for fast hashing
            sample = inputs.flat[::max(1, inputs.size // 64)].tobytes()
            h.update(sample)
        elif isinstance(inputs, (list, tuple)):
            for item in inputs:
                if isinstance(item, np.ndarray):
                    sample = item.flat[::max(1, item.size // 64)].tobytes()
                    h.update(sample)
                else:
                    h.update(str(item).encode("utf-8"))
        else:
            h.update(str(inputs).encode("utf-8"))

        return h.hexdigest()

class ExactResultCache:
    """In-memory Level 0 Exact Result Store with LRU eviction."""

    def __init__(self, max_entries: int = 1024):
        self.max_entries = max_entries
        self.cache: Dict[str, Tuple[Any, float, int]] = {} # key -> (result, timestamp, hit_count)
        self.hits = 0
        self.misses = 0

    def get(self, dna: str) -> Optional[Any]:
        if dna in self.cache:
            result, _, hits = self.cache[dna]
            self.cache[dna] = (result, time.time(), hits + 1)
            self.hits += 1
            return result
        self.misses += 1
        return None

    def put(self, dna: str, result: Any):
        if len(self.cache) >= self.max_entries:
            # Evict oldest
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        self.cache[dna] = (result, time.time(), 0)

    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        rate = (self.hits / total * 100.0) if total > 0 else 0.0
        return {
            "cached_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(rate, 2)
        }
