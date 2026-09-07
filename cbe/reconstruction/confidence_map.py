"""
cbe/reconstruction/confidence_map.py
Calculates per-pixel and tile-level temporal confidence fields.
Drives history blending weights and identifies regions requiring fresh computation.
"""

from __future__ import annotations

import numpy as np
from typing import Optional


class ConfidenceMapCalculator:
    """
    Computes normalized [0, 1] confidence maps based on depth agreement,
    motion vector consistency, and reactive transparency masks.
    """
    def __init__(self, depth_tolerance: float = 0.05, motion_decay: float = 30.0):
        self.depth_tolerance = depth_tolerance
        self.motion_decay = motion_decay

    def compute(
        self,
        current_depth: np.ndarray,
        reprojected_depth: np.ndarray,
        motion_vectors: np.ndarray,
        reactive_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Returns: (H, W) float32 confidence map in [0, 1].
        """
        # Depth similarity
        denom = np.maximum(np.abs(current_depth), 1e-4)
        depth_delta = np.abs(current_depth - reprojected_depth) / denom
        depth_conf = np.exp(-depth_delta / (self.depth_tolerance + 1e-4))
        
        # Motion stability
        speed = np.linalg.norm(motion_vectors, axis=-1)
        motion_conf = np.exp(-speed / self.motion_decay)
        
        confidence = depth_conf * motion_conf
        
        if reactive_mask is not None:
            confidence *= (1.0 - np.clip(reactive_mask, 0.0, 1.0))
            
        return np.clip(confidence, 0.0, 1.0).astype(np.float32)
