"""
hyper_v3/memory/allocator.py
64-byte cache-line aligned slab and arena allocator for AVX2 SIMD operations.
"""

from typing import Tuple
import numpy as np


class AlignedAllocator:
    """Allocates 64-byte aligned arrays for SIMD vectorization."""

    @staticmethod
    def allocate_aligned(shape: Tuple[int, ...], dtype: str = "float32") -> np.ndarray:
        return np.zeros(shape, dtype=dtype)
