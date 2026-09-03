"""
hyper_mvc_dar/redundancy.py
Redundancy & Memoization Engine: Automatically detects common subexpressions,
repeated embeddings, identical transform inputs, and cached intermediate states.
"""

import hashlib
from typing import Dict, Any, Optional, Tuple
import numpy as np


class RedundancyEngine:
    """Detects repeated computations and manages an in-memory subgraph cache."""

    def __init__(self, max_cache_entries: int = 10000):
        self._cache: Dict[str, Any] = {}
        self.hits = 0
        self.misses = 0
        self.max_entries = max_cache_entries

    def compute_subexpression_hash(self, op_name: str, input_hashes: Tuple[str, ...], params: Dict[str, Any]) -> str:
        h = hashlib.sha256()
        h.update(op_name.encode("utf-8"))
        for ih in input_hashes:
            h.update(ih.encode("utf-8"))
        for k in sorted(params.keys()):
            h.update(f"{k}:{params[k]}".encode("utf-8"))
        return h.hexdigest()

    def lookup(self, key: str) -> Optional[Any]:
        if key in self._cache:
            self.hits += 1
            return self._cache[key]
        self.misses += 1
        return None

    def store(self, key: str, value: Any):
        if len(self._cache) >= self.max_entries:
            # Simple eviction
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        self._cache[key] = value

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 4) if total > 0 else 0.0
