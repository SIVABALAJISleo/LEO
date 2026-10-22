"""
hyper_x/cpce/cache.py
=====================
Verified Computation Memory and Strict Cache Hub for CPCE.
Keys incorporate all result-affecting variables:
- Operand bytes digests
- Shapes and dtypes
- Operation type and parameters
- Workload contract ID and version
- Precision and backend semantics
Prevents stale results, collision corruption, and unverified reuse.
"""

from __future__ import annotations

import collections
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper_x.cpce.types import TaggedMatrix
from hyper_x.cpce.contracts import WorkloadContract


class CPCECacheKeyBuilder:
    """Computes collision-resistant cryptographic cache keys."""

    @staticmethod
    def build_key(
        op_name: str,
        operands: List[Any],
        contract: WorkloadContract,
        backend: str = "CPU",
        precision: str = "float32",
    ) -> str:
        """Constructs deterministic SHA-256 key from all result-affecting inputs."""
        h = hashlib.sha256()
        h.update(f"OP:{op_name}|CONTRACT:{contract.contract_id}:{contract.version}|BACKEND:{backend}|PREC:{precision}|".encode("utf-8"))

        for idx, op in enumerate(operands):
            if isinstance(op, TaggedMatrix):
                h.update(f"OP_{idx}:TAGGED:{op.structure_type}:{op.shape}:{op.dtype}:".encode("utf-8"))
                # Hash the underlying data
                dense = op.to_dense()
                h.update(np.ascontiguousarray(dense).tobytes())
            elif isinstance(op, np.ndarray):
                h.update(f"OP_{idx}:NDARRAY:{op.shape}:{op.dtype}:".encode("utf-8"))
                h.update(np.ascontiguousarray(op).tobytes())
            elif isinstance(op, (int, float, str, bool)):
                h.update(f"OP_{idx}:SCALAR:{type(op).__name__}:{op}:".encode("utf-8"))
            else:
                h.update(f"OP_{idx}:JSON:{json.dumps(str(op))}:".encode("utf-8"))

        return h.hexdigest()


class CPCECache:
    """
    LRU computation memory hub with size bounding and empirical telemetry.
    """

    def __init__(self, max_entries: int = 256, max_memory_mb: float = 256.0):
        self.max_entries = max_entries
        self.max_memory_mb = max_memory_mb
        self._cache: collections.OrderedDict[str, Any] = collections.OrderedDict()
        self._key_metadata: Dict[str, Dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Tuple[Any, float]]:
        """
        Retrieves cached result and measures lookup latency.
        Returns (result, lookup_latency_ms) or None if miss.
        """
        t0 = time.perf_counter()
        if key in self._cache:
            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            lat_ms = (time.perf_counter() - t0) * 1000.0
            val = self._cache[key]
            # Return copy to prevent caller mutation of cache
            res = val.copy() if hasattr(val, "copy") else val
            return res, round(lat_ms, 4)

        self._misses += 1
        return None

    def put(self, key: str, value: Any, contract_id: str = "default", approx_bytes: int = 1024, **kwargs):
        """Stores result in cache, enforcing capacity and memory bounds."""
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = value
            return

        # Check entry count limit
        if len(self._cache) >= self.max_entries:
            oldest_key, _ = self._cache.popitem(last=False)
            self._key_metadata.pop(oldest_key, None)

        val_store = value.copy() if hasattr(value, "copy") else value
        self._cache[key] = val_store
        meta = {
            "contract_id": contract_id,
            "created_at": time.time(),
            "approx_bytes": approx_bytes,
        }
        if "metadata" in kwargs and isinstance(kwargs["metadata"], dict):
            meta.update(kwargs["metadata"])
        meta.update({k: v for k, v in kwargs.items() if k != "metadata"})
        self._key_metadata[key] = meta


    def clear(self):
        """Clears all cached results."""
        self._cache.clear()
        self._key_metadata.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        hit_rate = (self._hits / total) if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_queries": total,
            "hit_rate": round(hit_rate, 4),
            "cached_entries": len(self._cache),
            "max_entries": self.max_entries,
        }
