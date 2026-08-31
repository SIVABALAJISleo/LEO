"""
hyper/compression/compression_engine.py
=======================================
Compression Engine:
- Lossless delta encoding for sequential states
- Hierarchical feature compression
- Intermediate representation compression
"""

import zlib
import time
import numpy as np
from typing import Dict, Any, Tuple


class CompressionEngine:
    """
    Manages state and tensor delta compression.
    """
    def __init__(self):
        pass

    def delta_compress(self, current: np.ndarray, previous: np.ndarray) -> Tuple[bytes, float]:
        delta = current - previous
        compressed = zlib.compress(delta.tobytes(), level=1)
        ratio = float(len(compressed) / max(1, current.nbytes))
        return compressed, ratio

    def delta_decompress(self, compressed: bytes, previous: np.ndarray) -> np.ndarray:
        raw_bytes = zlib.decompress(compressed)
        delta = np.frombuffer(raw_bytes, dtype=previous.dtype).reshape(previous.shape)
        return previous + delta
