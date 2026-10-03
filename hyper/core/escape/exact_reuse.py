"""
hyper/core/escape/exact_reuse.py
Breakthrough Engine C — Exact Semantic Reuse (Prompt Section 9).
Cryptographically strong cache identity hashing every semantic property:
- full input content (SHA-256 over all bytes, NEVER partial prefix)
- shape, dtype, memory layout
- algorithm name, software version, contract ID
- precision bits, random seed, model hash
Maintains distinct states: COLD, WARM, PERSISTENT, INVALIDATED.
"""
from __future__ import annotations
import hashlib
from enum import Enum
from typing import Any, Dict, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from hyper.core.cost.ledger import AccountingType, WorkLedger


class CacheEntryState(str, Enum):
    COLD = "COLD"
    WARM = "WARM"
    PERSISTENT = "PERSISTENT"
    INVALIDATED = "INVALIDATED"


class SemanticCacheKey(BaseModel):
    input_content_hash: str
    shape: Tuple[int, ...]
    dtype: str
    layout: str
    algorithm: str
    software_version: str = "hyper_v9_core"
    contract_id: str
    precision_bits: int
    random_seed: int
    model_hash: str = "default_model"

    def compute_composite_hash(self) -> str:
        raw = (
            f"{self.input_content_hash}:{self.shape}:{self.dtype}:{self.layout}:"
            f"{self.algorithm}:{self.software_version}:{self.contract_id}:"
            f"{self.precision_bits}:{self.random_seed}:{self.model_hash}"
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ExactReuseEngine:
    """
    Zero-approximation semantic memoization engine.
    """

    def __init__(self):
        self._cache: Dict[str, Tuple[Any, CacheEntryState, int]] = {}
        self.stats = {"cold_misses": 0, "warm_hits": 0, "invalidations": 0}

    @staticmethod
    def generate_key(
        arr: np.ndarray,
        algorithm: str,
        contract_id: str,
        precision_bits: int = 64,
        seed: int = 42,
        model_hash: str = "m0",
    ) -> SemanticCacheKey:
        # Full content hash across ALL elements
        content_hash = hashlib.sha256(arr.tobytes()).hexdigest()
        layout = "C_CONTIGUOUS" if arr.flags.c_contiguous else "F_CONTIGUOUS" if arr.flags.f_contiguous else "NON_CONTIGUOUS"
        return SemanticCacheKey(
            input_content_hash=content_hash,
            shape=arr.shape,
            dtype=str(arr.dtype),
            layout=layout,
            algorithm=algorithm,
            contract_id=contract_id,
            precision_bits=precision_bits,
            random_seed=seed,
            model_hash=model_hash,
        )

    def lookup(self, key: SemanticCacheKey) -> Tuple[Optional[Any], CacheEntryState]:
        comp_hash = key.compute_composite_hash()
        if comp_hash in self._cache:
            val, state, hits = self._cache[comp_hash]
            if state != CacheEntryState.INVALIDATED:
                self._cache[comp_hash] = (val, CacheEntryState.WARM, hits + 1)
                self.stats["warm_hits"] += 1
                return val, CacheEntryState.WARM
        self.stats["cold_misses"] += 1
        return None, CacheEntryState.COLD

    def store(self, key: SemanticCacheKey, value: Any, persistent: bool = False):
        comp_hash = key.compute_composite_hash()
        state = CacheEntryState.PERSISTENT if persistent else CacheEntryState.WARM
        self._cache[comp_hash] = (value, state, 1)

    def invalidate(self, key: SemanticCacheKey):
        comp_hash = key.compute_composite_hash()
        if comp_hash in self._cache:
            val, _, hits = self._cache[comp_hash]
            self._cache[comp_hash] = (val, CacheEntryState.INVALIDATED, hits)
            self.stats["invalidations"] += 1

    def clear(self):
        self._cache.clear()
