#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/pathway_search/exact_reuse.py
=====================================
Phase 5: Exact Cryptographic Provenance Cache.
Only emits EXACT when cryptographic provenance is identical. Never conflates similarity with equality.
"""

import hashlib
import time
from typing import Dict, Any, Optional, Tuple
import numpy as np


class ExactReuseEngine:
    """
    Authoritative Exact Reuse Engine.
    Requires complete provenance: input hash, shape, dtype, contract hash, runtime version.
    """

    def __init__(self):
        self.store: Dict[str, Tuple[Any, Dict[str, Any]]] = {}

    def compute_provenance_key(
        self,
        input_data: Any,
        contract_hash: str,
        runtime_version: str = "vNext-1.0"
    ) -> str:
        hasher = hashlib.sha256()
        if isinstance(input_data, np.ndarray):
            hasher.update(str(input_data.shape).encode())
            hasher.update(str(input_data.dtype).encode())
            hasher.update(input_data.tobytes())
        elif isinstance(input_data, (bytes, bytearray)):
            hasher.update(input_data)
        else:
            hasher.update(str(input_data).encode())

        hasher.update(contract_hash.encode())
        hasher.update(runtime_version.encode())
        return hasher.hexdigest()

    def lookup(
        self,
        input_data: Any,
        contract_hash: str,
        runtime_version: str = "vNext-1.0"
    ) -> Optional[Tuple[Any, Dict[str, Any]]]:
        key = self.compute_provenance_key(input_data, contract_hash, runtime_version)
        return self.store.get(key)

    def insert(
        self,
        input_data: Any,
        contract_hash: str,
        output_result: Any,
        metadata: Optional[Dict[str, Any]] = None,
        runtime_version: str = "vNext-1.0"
    ) -> str:
        key = self.compute_provenance_key(input_data, contract_hash, runtime_version)
        meta = metadata or {}
        meta["cached_timestamp"] = time.time()
        meta["provenance_key"] = key
        self.store[key] = (output_result, meta)
        return key

    def clear(self):
        self.store.clear()
