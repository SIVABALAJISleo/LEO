"""
hyper_v3/transforms/memory.py
Data layout transforms (AoS to SoA, Cache line alignment, Packed buffers).
"""

from typing import Tuple
import numpy as np


class MemoryTransformer:
    """Transforms memory layouts for contiguous SIMD and cache access."""

    @staticmethod
    def ensure_contiguous_aligned(array: np.ndarray) -> np.ndarray:
        if not array.flags['C_CONTIGUOUS']:
            return np.ascontiguousarray(array)
        return array

    @staticmethod
    def aos_to_soa_3d(particles_aos: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Converts Array-of-Structures (Nx3) to Structure-of-Arrays (3 separate contiguous arrays)."""
        x = np.ascontiguousarray(particles_aos[:, 0])
        y = np.ascontiguousarray(particles_aos[:, 1])
        z = np.ascontiguousarray(particles_aos[:, 2])
        return x, y, z
