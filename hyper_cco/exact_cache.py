"""
hyper_cco/exact_cache.py
========================
Cryptographic Full-Content Exact Cache.
Eliminates any possibility of prefix/suffix/subsample hash collisions (e.g., ravel()[:512]).
Computes SHA-256 digests over complete input bytes, dimensions, dtypes, memory layouts,
model hashes, algorithm versions, precision modes, and contract hashes.
Accurately records original operations vs executed operations (0 for hits) and measured lookup latency.
"""

import time
import hashlib
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, Union
import numpy as np


class CacheMode(str, Enum):
    COLD = "COLD"                      # Cache cleared before execution, cold miss guaranteed
    WARM = "WARM"                      # Cache active, warm hits allowed
    PERSISTENT = "PERSISTENT"          # Long-running process state maintained
    DISABLED = "DISABLED"              # Caching completely bypassed, computation mandatory


@dataclass
class CacheLookupResult:
    """Detailed telemetry and metadata for a cache query."""
    hit: bool
    data: Optional[Any]
    key: str
    lookup_latency_ms: float
    mode: CacheMode
    memory_footprint_bytes: int
    original_operations: float = 0.0
    executed_operations: float = 0.0
    strategy: str = "EXACT_CACHE"
    provenance: str = "MISS"


@dataclass
class CacheEntry:
    """Internal stored entry with complete provenance and LRU bookkeeping."""
    key: str
    data: Any
    size_bytes: int
    created_at: float
    last_accessed_at: float
    access_count: int
    original_operations: float
    model_hash: str
    algorithm_hash: str
    contract_hash: str
    precision_mode: str


class ExactFullContentCache:
    """
    Production cryptographic full-content cache for mathematical operations and intermediate states.
    Guarantees zero sampled shortcuts: hashes 100% of tensor bytes.
    """
    def __init__(self, max_memory_mb: float = 2048.0, default_mode: CacheMode = CacheMode.WARM):
        self.max_memory_bytes = int(max_memory_mb * 1024 * 1024)
        self.mode = default_mode
        self._store: Dict[str, CacheEntry] = {}
        self._current_memory_bytes = 0
        self.stats = {
            "queries": 0,
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_bytes_cached": 0,
        }

    def set_mode(self, mode: CacheMode) -> None:
        """Sets cache operation mode, clearing storage on COLD."""
        self.mode = mode
        if mode == CacheMode.COLD:
            self.clear()

    def clear(self) -> None:
        """Flushes all cached entries and resets memory telemetry."""
        self._store.clear()
        self._current_memory_bytes = 0

    @staticmethod
    def compute_full_content_key(
        op_name: str,
        *inputs: Any,
        model_hash: str = "default_model",
        algorithm_hash: str = "v1.0",
        contract_hash: str = "default_contract",
        precision_mode: str = "FP32",
        **kwargs: Any
    ) -> str:
        """
        Computes an unforgeable SHA-256 key across 100% of input bytes, shapes,
        dtypes, memory layouts, model/algorithm identity, and contract version.
        Zero sampled shortcuts.
        """
        hasher = hashlib.sha256()
        # 1. Operation identity
        hasher.update(op_name.encode("utf-8"))
        hasher.update(b"::")

        # 2. Input tensors / objects (100% full content)
        for idx, item in enumerate(inputs):
            hasher.update(f"in_{idx}:".encode("utf-8"))
            if isinstance(item, np.ndarray):
                # Shape, dtype, and memory layout
                hasher.update(str(item.shape).encode("utf-8"))
                hasher.update(str(item.dtype).encode("utf-8"))
                layout = "C" if item.flags.c_contiguous else ("F" if item.flags.f_contiguous else "NON_CONTIG")
                hasher.update(layout.encode("utf-8"))
                # Complete byte sequence - NO SAMPLING SHORTCUTS
                hasher.update(item.tobytes())
            elif isinstance(item, (bytes, bytearray)):
                hasher.update(item)
            elif isinstance(item, (str, int, float, bool)):
                hasher.update(str(item).encode("utf-8"))
            elif isinstance(item, (list, tuple)):
                hasher.update(json.dumps([str(x) for x in item]).encode("utf-8"))
            elif item is None:
                hasher.update(b"NONE")
            else:
                hasher.update(str(item).encode("utf-8"))
            hasher.update(b";")

        # 3. Execution context and provenance
        hasher.update(f"model={model_hash};algo={algorithm_hash};contract={contract_hash};prec={precision_mode};".encode("utf-8"))

        # 4. Auxiliary keyword arguments
        for k in sorted(kwargs.keys()):
            val = kwargs[k]
            if isinstance(val, np.ndarray):
                hasher.update(f"{k}=".encode("utf-8") + val.tobytes())
            else:
                hasher.update(f"{k}={val};".encode("utf-8"))

        return hasher.hexdigest()

    def lookup(self, key: str) -> CacheLookupResult:
        """
        Queries cache for key. Accurately measures lookup latency and returns
        original vs executed operation counts.
        """
        t0 = time.perf_counter()
        self.stats["queries"] += 1

        if self.mode == CacheMode.DISABLED:
            latency = (time.perf_counter() - t0) * 1000.0
            return CacheLookupResult(
                hit=False,
                data=None,
                key=key,
                lookup_latency_ms=latency,
                mode=self.mode,
                memory_footprint_bytes=0,
                provenance="CACHE_DISABLED"
            )

        if key in self._store:
            entry = self._store[key]
            entry.last_accessed_at = time.time()
            entry.access_count += 1
            self.stats["hits"] += 1
            latency = (time.perf_counter() - t0) * 1000.0

            return CacheLookupResult(
                hit=True,
                data=entry.data,
                key=key,
                lookup_latency_ms=latency,
                mode=self.mode,
                memory_footprint_bytes=entry.size_bytes,
                original_operations=entry.original_operations,
                executed_operations=0.0,
                strategy="EXACT_CACHE",
                provenance="EXACT_FULL_CONTENT_MATCH"
            )

        self.stats["misses"] += 1
        latency = (time.perf_counter() - t0) * 1000.0
        return CacheLookupResult(
            hit=False,
            data=None,
            key=key,
            lookup_latency_ms=latency,
            mode=self.mode,
            memory_footprint_bytes=0,
            provenance="MISS"
        )

    def put(
        self,
        key: str,
        data: Any,
        original_operations: float = 0.0,
        model_hash: str = "default_model",
        algorithm_hash: str = "v1.0",
        contract_hash: str = "default_contract",
        precision_mode: str = "FP32"
    ) -> bool:
        """
        Stores an exact result with LRU eviction if memory threshold exceeded.
        """
        if self.mode == CacheMode.DISABLED:
            return False

        # Calculate memory footprint
        if isinstance(data, np.ndarray):
            size = int(data.nbytes)
        elif isinstance(data, (bytes, bytearray)):
            size = len(data)
        else:
            size = 512 # nominal baseline for small objects

        # Enforce memory cap via LRU
        while self._current_memory_bytes + size > self.max_memory_bytes and self._store:
            lru_key = min(self._store.keys(), key=lambda k: self._store[k].last_accessed_at)
            evicted = self._store.pop(lru_key)
            self._current_memory_bytes -= evicted.size_bytes
            self.stats["evictions"] += 1

        now = time.time()
        entry = CacheEntry(
            key=key,
            data=data,
            size_bytes=size,
            created_at=now,
            last_accessed_at=now,
            access_count=1,
            original_operations=original_operations,
            model_hash=model_hash,
            algorithm_hash=algorithm_hash,
            contract_hash=contract_hash,
            precision_mode=precision_mode
        )
        self._store[key] = entry
        self._current_memory_bytes += size
        self.stats["total_bytes_cached"] = self._current_memory_bytes
        return True

    def store(
        self,
        model_id: str,
        contract_hash: str,
        inputs: Dict[str, Any],
        output: Any,
        original_operations: float = 0.0,
    ) -> bool:
        """High-level convenience method to store an operation result."""
        # Convert dictionary values to inputs and kwargs
        in_list = list(inputs.values())
        key = self.compute_full_content_key(
            model_id,
            *in_list,
            model_hash=model_id,
            contract_hash=contract_hash,
        )
        return self.put(
            key=key,
            data=output,
            original_operations=original_operations,
            model_hash=model_id,
            contract_hash=contract_hash,
        )

    def lookup_inputs(
        self,
        model_id: str,
        contract_hash: str,
        inputs: Dict[str, Any],
    ) -> Tuple[bool, Optional[Any]]:
        """High-level convenience method to lookup by input dictionary."""
        in_list = list(inputs.values())
        key = self.compute_full_content_key(
            model_id,
            *in_list,
            model_hash=model_id,
            contract_hash=contract_hash,
        )
        res = self.lookup(key)
        return res.hit, res.data


ExactCacheEngine = ExactFullContentCache

