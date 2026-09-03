"""
hyper_v3/transforms/representation.py
Representation transformations (Dense to Sparse, Scene to Morton LBVH, Delta frames).
"""

from typing import Dict, Any, List
import numpy as np


class RepresentationTransformer:
    """Transforms representations to exploit spatial and structural hierarchies."""

    @staticmethod
    def compute_morton_codes_3d(points: np.ndarray) -> np.ndarray:
        """Computes 30-bit Morton codes for 3D coordinates normalized in [0, 1023]."""
        if points.shape[0] == 0:
            return np.array([], dtype=np.uint32)
        
        # Normalize to [0, 1023]
        mins = np.min(points, axis=0)
        maxs = np.max(points, axis=0)
        ranges = np.maximum(maxs - mins, 1e-6)
        normalized = np.clip(((points - mins) / ranges) * 1023.0, 0, 1023).astype(np.uint32)

        def expand_bits(v):
            v = (v | (v << 16)) & 0x030000FF
            v = (v | (v << 8)) & 0x0300F00F
            v = (v | (v << 4)) & 0x030C30C3
            v = (v | (v << 2)) & 0x09249249
            return v

        x = expand_bits(normalized[:, 0])
        y = expand_bits(normalized[:, 1])
        z = expand_bits(normalized[:, 2])
        return (x << 2) | (y << 1) | z
