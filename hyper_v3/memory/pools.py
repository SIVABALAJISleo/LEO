"""
hyper_v3/memory/pools.py
Pre-allocated tensor buffer memory pools preventing runtime malloc fragmentation.
"""

from typing import Dict, List, Tuple
import numpy as np


class BufferPool:
    """Pre-allocated pool of NumPy memory blocks for zero-allocation kernel reuse."""

    def __init__(self):
        self.pools: Dict[Tuple[int, str], List[np.ndarray]] = {}

    def acquire(self, shape: Tuple[int, ...], dtype: str = "float32") -> np.ndarray:
        key = (int(np.prod(shape)), dtype)
        if key in self.pools and len(self.pools[key]) > 0:
            buf = self.pools[key].pop()
            return buf.reshape(shape)
        return np.zeros(shape, dtype=dtype)

    def release(self, buffer: np.ndarray):
        key = (buffer.size, str(buffer.dtype))
        if key not in self.pools:
            self.pools[key] = []
        if len(self.pools[key]) < 16:  # Max 16 buffers per size class
            self.pools[key].append(buffer.ravel())
