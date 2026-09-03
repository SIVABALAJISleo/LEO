"""
hyper_mvc_dar/memory_engine.py
Memory-First Engine: Optimizes memory layout (AoS vs SoA), working-set size,
cache residency, and buffer reuse via pre-allocated shared memory pools.
"""

from typing import Dict, Any, Tuple
import numpy as np


class MemoryEngine:
    """Manages memory locality, buffer pools, and data layout transformations."""

    def __init__(self, pool_size_mb: int = 256):
        self.pool_size_bytes = pool_size_mb * 1024 * 1024
        # Single pre-allocated byte buffer simulating pinned host pool
        self._pool = bytearray(min(self.pool_size_bytes, 16 * 1024 * 1024))
        self.allocated_bytes = 0

    def allocate_buffer(self, size_bytes: int) -> memoryview:
        if self.allocated_bytes + size_bytes > len(self._pool):
            # Reset pool pointer (circular ring buffer)
            self.allocated_bytes = 0
        mv = memoryview(self._pool)[self.allocated_bytes : self.allocated_bytes + size_bytes]
        self.allocated_bytes += size_bytes
        return mv

    @staticmethod
    def aos_to_soa(points: np.ndarray) -> Dict[str, np.ndarray]:
        """Converts Array of Structures (Nx3) to Structure of Arrays (3xN) for contiguous SIMD loads."""
        if points.ndim == 2 and points.shape[1] == 3:
            return {
                "x": np.ascontiguousarray(points[:, 0]),
                "y": np.ascontiguousarray(points[:, 1]),
                "z": np.ascontiguousarray(points[:, 2]),
            }
        return {"data": points}

    @staticmethod
    def soa_to_aos(soa: Dict[str, np.ndarray]) -> np.ndarray:
        """Converts Structure of Arrays back to Array of Structures."""
        if "x" in soa and "y" in soa and "z" in soa:
            return np.column_stack((soa["x"], soa["y"], soa["z"]))
        return next(iter(soa.values()))
