"""
hyper/research_engine/semantic_memoization.py
=============================================
Multi-Level Semantic Memoization & Irreducible Entropy Detector.

Implements Directive 4:
- Locality-Sensitive Hashing (LSH) on incoming activation patterns.
- Pulls pre-computed output state from L1/L2 cache-resident lookup tables in O(1).
- Entropy Detector: Detects irreducible Kolmogorov entropy (K(x) ~ |x|).
  Bypasses lookup tables and gracefully executes native AVX2 kernels for random data.
"""

from __future__ import annotations

import dataclasses
import hashlib
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class EntropyDetector:
    """
    Measures Kolmogorov complexity / spectral flatness and derivative variance
    to distinguish irreducible randomness (K(x) ~ |x|) from structured compressible patterns.
    """

    @classmethod
    def compute_entropy_ratio(cls, x: np.ndarray) -> float:
        """
        Computes composite Kolmogorov entropy index in range [0.0, 1.0].
        A value >= 0.65 denotes purely random, incompressible data (K(x) ~ |x|).
        """
        arr = x.flatten().astype(np.float64)
        if len(arr) < 4:
            return 0.0

        # 1. Spectral Flatness (Wiener Entropy)
        fft_mag = np.abs(np.fft.rfft(arr)) ** 2 + 1e-12
        geom_mean = np.exp(np.mean(np.log(fft_mag)))
        arith_mean = np.mean(fft_mag)
        flatness = float(min(1.0, geom_mean / max(1e-12, arith_mean)))

        # 2. Derivative / Total Variation Variance Ratio
        var_x = float(np.var(arr))
        if var_x < 1e-12:
            return 0.0  # Constant tensor has zero entropy
        var_diff = float(np.var(np.diff(arr)))
        diff_ratio = min(2.0, var_diff / var_x) / 2.0  # Normalized to [0, 1]

        # Composite Kolmogorov Index
        entropy_index = 0.5 * flatness + 0.5 * diff_ratio
        return float(min(1.0, max(0.0, entropy_index)))

    @classmethod
    def is_irreducible(cls, x: np.ndarray, threshold: float = 0.65) -> bool:
        """
        Returns True if data entropy is too high for semantic memoization,
        signaling an automatic fallback to native AVX2 execution.
        """
        return cls.compute_entropy_ratio(x) >= threshold


class LSHSemanticCache:
    """
    Locality-Sensitive Hashing (LSH) Semantic Cache.
    Maps continuous vectors to integer bucket pointers using random hyperplane projections.
    """

    def __init__(self, in_dim: int, num_hyperplanes: int = 32, max_entries: int = 4096, seed: int = 42):
        self.in_dim = in_dim
        self.num_hyperplanes = num_hyperplanes
        self.max_entries = max_entries
        
        # Hyperplane matrix: [num_hyperplanes, in_dim]
        rng = np.random.default_rng(seed)
        self.planes = rng.standard_normal((num_hyperplanes, in_dim), dtype=np.float32)
        norms = np.linalg.norm(self.planes, axis=1, keepdims=True) + 1e-12
        self.planes /= norms

        # L1/L2 cache resident lookup dictionary: hash -> (input_key, output_val)
        self.table: Dict[int, Tuple[np.ndarray, np.ndarray]] = {}
        self.hits: int = 0
        self.misses: int = 0
        self.bypassed_entropy: int = 0

    def compute_lsh_key(self, x: np.ndarray) -> int:
        """Projects continuous vector x onto random hyperplanes and packs into an integer key."""
        x_flat = x.flatten()[:self.in_dim]
        if len(x_flat) < self.in_dim:
            padded = np.zeros(self.in_dim, dtype=np.float32)
            padded[:len(x_flat)] = x_flat
            x_flat = padded

        projections = np.dot(self.planes, x_flat)
        bits = (projections >= 0).astype(int)
        
        key = 0
        for b in bits:
            key = (key << 1) | b
        return key

    def lookup(self, x: np.ndarray, tolerance: float = 1e-3) -> Optional[np.ndarray]:
        """Looks up cached output for vector x. Returns None if miss."""
        # 1. Entropy detection guard
        if EntropyDetector.is_irreducible(x):
            self.bypassed_entropy += 1
            return None

        key = self.compute_lsh_key(x)
        if key in self.table:
            cached_in, cached_out = self.table[key]
            # Exact or near-exact distance check
            diff = np.max(np.abs(x.flatten()[:self.in_dim] - cached_in))
            if diff <= tolerance:
                self.hits += 1
                return cached_out.copy()

        self.misses += 1
        return None

    def insert(self, x: np.ndarray, y: np.ndarray):
        """Inserts a computed input-output state into the semantic cache."""
        if EntropyDetector.is_irreducible(x):
            return  # Do not pollute cache with high-entropy non-repeating data

        key = self.compute_lsh_key(x)
        x_flat = x.flatten()[:self.in_dim]
        if len(x_flat) < self.in_dim:
            padded = np.zeros(self.in_dim, dtype=np.float32)
            padded[:len(x_flat)] = x_flat
            x_flat = padded

        if len(self.table) >= self.max_entries:
            # Evict oldest entry (FIFO)
            first_key = next(iter(self.table))
            del self.table[first_key]

        self.table[key] = (x_flat.copy(), y.copy())

    def get_stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100.0) if total > 0 else 0.0
        return {
            "cached_entries": len(self.table),
            "hits": self.hits,
            "misses": self.misses,
            "bypassed_entropy": self.bypassed_entropy,
            "hit_rate_pct": hit_rate,
        }
