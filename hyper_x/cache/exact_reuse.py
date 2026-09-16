"""
hyper_x/cache/exact_reuse.py
============================
Phase 4: Exact Reuse Engine.
Enforces cryptographic identity conditions for exact reuse:
- SHA-256 input identity
- Tensor shape, dtype, memory layout
- Model version / algorithm version
- Contract hash & environment hash
Rule: A cache hit is reported strictly as COMPUTATION_AVOIDED_BY_EXACT_REUSE
with separate measurement of lookup latency vs avoided computation latency.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple
import numpy as np


@dataclass
class ExactReuseEntry:
    key_hash: str
    output_data: Any
    shape: Tuple[int, ...]
    dtype: str
    layout: str
    model_version: str
    algorithm_version: str
    contract_hash: str
    environment_hash: str
    created_timestamp: float
    original_compute_latency_ms: float
    access_count: int = 0
    size_bytes: int = 0


@dataclass
class ReuseLookupResult:
    is_hit: bool
    data: Optional[Any] = None
    lookup_latency_ms: float = 0.0
    computation_avoided_ms: float = 0.0
    classification: str = "CACHE_MISS"  # "COMPUTATION_AVOIDED_BY_EXACT_REUSE" or "CACHE_MISS"


class ExactReuseEngine:
    """
    Cryptographic identity-based memoization engine.
    Never uses semantic similarity or approximation as exact cache hits.
    """

    def __init__(self, max_memory_mb: float = 1024.0):
        self.max_memory_mb = max_memory_mb
        self._store: Dict[str, ExactReuseEntry] = {}
        self._total_bytes: int = 0

    def compute_composite_key(
        self,
        input_data: Any,
        model_version: str = "v1.0",
        algorithm_version: str = "v1.0",
        contract_hash: str = "DEFAULT",
        environment_hash: str = "LOCAL",
    ) -> Tuple[str, Tuple[int, ...], str, str]:
        """
        Computes SHA-256 over raw contiguous bytes + structural metadata.
        """
        if isinstance(input_data, np.ndarray):
            shape = input_data.shape
            dtype = str(input_data.dtype)
            layout = "C_CONTIGUOUS" if input_data.flags.c_contiguous else "F_CONTIGUOUS"
            raw_bytes = np.ascontiguousarray(input_data).tobytes()
        elif isinstance(input_data, (tuple, list)):
            shape = (len(input_data),)
            dtype = "composite"
            layout = "sequence"
            raw_bytes = json.dumps(str(input_data)).encode("utf-8")
        else:
            shape = (1,)
            dtype = type(input_data).__name__
            layout = "scalar"
            raw_bytes = json.dumps(str(input_data)).encode("utf-8")

        h = hashlib.sha256()
        h.update(raw_bytes)
        h.update(str(shape).encode("utf-8"))
        h.update(dtype.encode("utf-8"))
        h.update(layout.encode("utf-8"))
        h.update(model_version.encode("utf-8"))
        h.update(algorithm_version.encode("utf-8"))
        h.update(contract_hash.encode("utf-8"))
        h.update(environment_hash.encode("utf-8"))

        return h.hexdigest(), shape, dtype, layout

    def lookup(
        self,
        input_data: Any,
        model_version: str = "v1.0",
        algorithm_version: str = "v1.0",
        contract_hash: str = "DEFAULT",
        environment_hash: str = "LOCAL",
    ) -> ReuseLookupResult:
        t0 = time.perf_counter()
        key, shape, dtype, layout = self.compute_composite_key(
            input_data, model_version, algorithm_version, contract_hash, environment_hash
        )

        if key in self._store:
            entry = self._store[key]
            # Strict secondary identity check
            if (
                entry.shape == shape and
                entry.dtype == dtype and
                entry.layout == layout and
                entry.contract_hash == contract_hash
            ):
                entry.access_count += 1
                lookup_ms = (time.perf_counter() - t0) * 1000.0
                return ReuseLookupResult(
                    is_hit=True,
                    data=entry.output_data.copy() if hasattr(entry.output_data, "copy") else entry.output_data,
                    lookup_latency_ms=round(lookup_ms, 4),
                    computation_avoided_ms=round(entry.original_compute_latency_ms, 4),
                    classification="COMPUTATION_AVOIDED_BY_EXACT_REUSE",
                )

        lookup_ms = (time.perf_counter() - t0) * 1000.0
        return ReuseLookupResult(
            is_hit=False,
            data=None,
            lookup_latency_ms=round(lookup_ms, 4),
            computation_avoided_ms=0.0,
            classification="CACHE_MISS",
        )

    def store(
        self,
        input_data: Any,
        output_data: Any,
        original_compute_latency_ms: float,
        model_version: str = "v1.0",
        algorithm_version: str = "v1.0",
        contract_hash: str = "DEFAULT",
        environment_hash: str = "LOCAL",
    ) -> str:
        key, shape, dtype, layout = self.compute_composite_key(
            input_data, model_version, algorithm_version, contract_hash, environment_hash
        )

        size_bytes = 0
        if hasattr(output_data, "nbytes"):
            size_bytes = output_data.nbytes
        elif isinstance(output_data, (str, bytes)):
            size_bytes = len(output_data)

        entry = ExactReuseEntry(
            key_hash=key,
            output_data=output_data.copy() if hasattr(output_data, "copy") else output_data,
            shape=shape,
            dtype=dtype,
            layout=layout,
            model_version=model_version,
            algorithm_version=algorithm_version,
            contract_hash=contract_hash,
            environment_hash=environment_hash,
            created_timestamp=time.time(),
            original_compute_latency_ms=original_compute_latency_ms,
            size_bytes=size_bytes,
        )

        self._store[key] = entry
        self._total_bytes += size_bytes
        return key

    def clear(self) -> None:
        self._store.clear()
        self._total_bytes = 0
