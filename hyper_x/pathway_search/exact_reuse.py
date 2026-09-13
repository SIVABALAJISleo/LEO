#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/pathway_search/exact_reuse.py
=====================================
Phase 5: Exact Cryptographic Provenance Cache (EXACT_CACHE).

Requires complete 14-point provenance:
  - input_hash
  - complete_input_manifest
  - model_hash
  - tokenizer_hash
  - weights_hash
  - algorithm_hash
  - runtime_hash
  - contract_hash
  - precision
  - dtype
  - layout
  - seed
  - relevant environment
  - software version

Measures lookup latency separately; never conflates lookup with arithmetic compute throughput.
"""

import hashlib
import time
from typing import Dict, Any, Optional, Tuple
import numpy as np


class ExactReuseEngine:
    """
    Authoritative Exact Reuse Engine (EXACT_CACHE).
    Guarantees bit-exactness via full 14-parameter cryptographic identity.
    """

    def __init__(self):
        self.store: Dict[str, Tuple[Any, Dict[str, Any]]] = {}
        self.last_lookup_latency_ms: float = 0.0

    def compute_provenance_key(
        self,
        input_data: Any,
        contract_hash: str,
        complete_input_manifest: str = "manifest_v1",
        model_hash: str = "none",
        tokenizer_hash: str = "none",
        weights_hash: str = "none",
        algorithm_hash: str = "blas_exact",
        runtime_hash: str = "native_cpu_uhd",
        precision: str = "fp32",
        dtype: str = "float32",
        layout: str = "C_CONTIGUOUS",
        seed: int = 42,
        environment: str = "Windows11_i5_12450H_UHD48",
        software_version: str = "vNext-2.0"
    ) -> str:
        """Constructs 14-point deterministic SHA-256 identity key."""
        hasher = hashlib.sha256()

        # 1. input_hash
        if isinstance(input_data, np.ndarray):
            hasher.update(str(input_data.shape).encode())
            hasher.update(str(input_data.dtype).encode())
            hasher.update(input_data.tobytes())
            dtype = str(input_data.dtype)
        elif isinstance(input_data, (bytes, bytearray)):
            hasher.update(input_data)
        else:
            hasher.update(str(input_data).encode())

        # 2-14: Complete system & execution parameters
        hasher.update(complete_input_manifest.encode())
        hasher.update(model_hash.encode())
        hasher.update(tokenizer_hash.encode())
        hasher.update(weights_hash.encode())
        hasher.update(algorithm_hash.encode())
        hasher.update(runtime_hash.encode())
        hasher.update(contract_hash.encode())
        hasher.update(precision.encode())
        hasher.update(dtype.encode())
        hasher.update(layout.encode())
        hasher.update(str(seed).encode())
        hasher.update(environment.encode())
        hasher.update(software_version.encode())

        return hasher.hexdigest()

    def lookup(
        self,
        input_data: Any,
        contract_hash: str,
        **kwargs: Any
    ) -> Optional[Tuple[Any, Dict[str, Any]]]:
        """
        Looks up an exact cryptographic match and measures lookup latency separately.
        """
        t0 = time.perf_counter()
        key = self.compute_provenance_key(input_data, contract_hash, **kwargs)
        result = self.store.get(key)
        self.last_lookup_latency_ms = (time.perf_counter() - t0) * 1000.0

        if result is not None:
            val, meta = result
            meta_copy = dict(meta)
            meta_copy["lookup_latency_ms"] = round(self.last_lookup_latency_ms, 4)
            meta_copy["cache_type"] = "EXACT_CACHE"
            meta_copy["computation_required"] = 0
            return val, meta_copy

        return None

    def insert(
        self,
        input_data: Any,
        contract_hash: str,
        output_result: Any,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> str:
        key = self.compute_provenance_key(input_data, contract_hash, **kwargs)
        meta = metadata or {}
        meta["inserted_at"] = time.time()
        meta["cache_type"] = "EXACT_CACHE"
        self.store[key] = (output_result, meta)
        return key

    def clear(self) -> None:
        self.store.clear()
