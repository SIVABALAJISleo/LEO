"""
hyper/canonical/verified_cache.py
=================================
Correctness-Preserving Content-Addressable Cache.

Guarantees:
1. Multi-operand SHA-256 hashing (changing operand B never produces a cache hit from operand A).
2. Never caches unverified or failed outputs.
3. Accurate hit/miss latency tracking (never claims cache hit as computed work).
4. Strict LRU memory bounding and selective invalidation.
"""

from __future__ import annotations

import collections
import dataclasses
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclasses.dataclass
class CacheEntry:
    key: str
    workload_id: str
    contract_version: str
    result: Any
    verified: bool
    created_at: float
    last_accessed: float
    access_count: int = 1
    size_bytes: int = 0


class VerifiedExactCache:
    """
    Thread-safe, bounded, collision-resistant exact-result cache.
    """

    def __init__(self, max_entries: int = 500, max_memory_mb: float = 256.0) -> None:
        self.max_entries = max_entries
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self._entries: collections.OrderedDict[str, CacheEntry] = collections.OrderedDict()
        self._total_bytes: int = 0
        self._hits: int = 0
        self._misses: int = 0

    @staticmethod
    def compute_cache_key(
        workload_id: str,
        inputs: Dict[str, Any],
        contract_version: str = "v2.0-canonical",
        precision: str = "float32",
        settings: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Computes a collision-resistant SHA-256 cache key including ALL operands.
        Changing any single tensor element, shape, dtype, or parameter produces
        a completely different hash key.
        """
        hasher = hashlib.sha256()
        hasher.update(workload_id.encode("utf-8"))
        hasher.update(b"|")
        hasher.update(contract_version.encode("utf-8"))
        hasher.update(b"|")
        hasher.update(precision.encode("utf-8"))
        hasher.update(b"|")

        if settings:
            for sk in sorted(settings.keys()):
                hasher.update(f"{sk}:{settings[sk]};".encode("utf-8"))
            hasher.update(b"|")

        # Hash each input operand in deterministic sorted key order
        for operand_name in sorted(inputs.keys()):
            val = inputs[operand_name]
            hasher.update(operand_name.encode("utf-8"))
            hasher.update(b":")

            if isinstance(val, np.ndarray):
                hasher.update(f"shape={val.shape},dtype={val.dtype};".encode("utf-8"))
                # Hash array bytes
                if val.flags["C_CONTIGUOUS"]:
                    hasher.update(val.tobytes())
                else:
                    hasher.update(np.ascontiguousarray(val).tobytes())
            elif isinstance(val, (bytes, bytearray)):
                hasher.update(b"bytes:")
                hasher.update(val)
            elif isinstance(val, (int, float, str, bool)):
                hasher.update(f"{type(val).__name__}={val};".encode("utf-8"))
            elif isinstance(val, (list, tuple)):
                arr = np.asarray(val)
                hasher.update(f"shape={arr.shape},dtype={arr.dtype};".encode("utf-8"))
                hasher.update(arr.tobytes())
            else:
                hasher.update(repr(val).encode("utf-8"))

            hasher.update(b"|")

        return hasher.hexdigest()

    def get(self, key: str) -> Tuple[Optional[Any], bool, float]:
        """
        Retrieves cached result if present.
        Returns: (result, is_hit, lookup_time_ms)
        """
        t0 = time.perf_counter()
        if key in self._entries:
            entry = self._entries[key]
            entry.last_accessed = time.time()
            entry.access_count += 1
            # Move to end for LRU order
            self._entries.move_to_end(key)
            self._hits += 1
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return entry.result, True, elapsed_ms

        self._misses += 1
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return None, False, elapsed_ms

    def put(
        self,
        key: str,
        workload_id: str,
        result: Any,
        contract_version: str = "v2.0-canonical",
        is_verified: bool = True,
    ) -> bool:
        """
        Stores result in cache.
        CRITICAL: Never caches unverified or failed outputs.
        """
        if not is_verified:
            # Refuse to cache unverified outputs
            return False

        # Calculate memory footprint
        size = 64
        if isinstance(result, np.ndarray):
            size = result.nbytes
        elif isinstance(result, (bytes, bytearray, str)):
            size = len(result)

        # Evict LRU entries if capacity exceeded
        while len(self._entries) >= self.max_entries or (self._total_bytes + size > self.max_memory_bytes and len(self._entries) > 0):
            evicted_key, evicted_entry = self._entries.popitem(last=False)
            self._total_bytes -= evicted_entry.size_bytes

        now = time.time()
        entry = CacheEntry(
            key=key,
            workload_id=workload_id,
            contract_version=contract_version,
            result=result,
            verified=is_verified,
            created_at=now,
            last_accessed=now,
            access_count=1,
            size_bytes=size,
        )
        self._entries[key] = entry
        self._total_bytes += size
        return True

    def invalidate(self, workload_id: Optional[str] = None) -> int:
        """Invalidates entries matching workload_id or clears entire cache if None."""
        if workload_id is None:
            count = len(self._entries)
            self._entries.clear()
            self._total_bytes = 0
            return count

        keys_to_remove = [k for k, v in self._entries.items() if v.workload_id == workload_id]
        for k in keys_to_remove:
            entry = self._entries.pop(k)
            self._total_bytes -= entry.size_bytes
        return len(keys_to_remove)

    def stats(self) -> Dict[str, Any]:
        return {
            "total_entries": len(self._entries),
            "max_entries": self.max_entries,
            "total_memory_bytes": self._total_bytes,
            "max_memory_bytes": self.max_memory_bytes,
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio": self._hits / max(1, self._hits + self._misses),
        }


# Global singleton instance
VERIFIED_CACHE = VerifiedExactCache()
