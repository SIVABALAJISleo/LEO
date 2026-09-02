"""
hyper_v2/optimization/memory_optimizer.py
Memory buffer reuse, allocation pooling, and transfer elimination.
"""

from typing import Dict, Any, Tuple, List
import numpy as np


class MemoryOptimizer:
    """Manages pre-allocated tensor buffer pools to prevent GC stalls and malloc overhead."""

    _buffer_pool: Dict[Tuple[Tuple[int, ...], str], List[np.ndarray]] = {}

    @classmethod
    def acquire_buffer(cls, shape: Tuple[int, ...], dtype: str = "float32") -> np.ndarray:
        key = (shape, dtype)
        if key in cls._buffer_pool and len(cls._buffer_pool[key]) > 0:
            return cls._buffer_pool[key].pop()
        return np.empty(shape, dtype=dtype)

    @classmethod
    def release_buffer(cls, buffer: np.ndarray):
        key = (buffer.shape, str(buffer.dtype))
        if key not in cls._buffer_pool:
            cls._buffer_pool[key] = []
        if len(cls._buffer_pool[key]) < 8:  # Cap pool size
            cls._buffer_pool[key].append(buffer)
