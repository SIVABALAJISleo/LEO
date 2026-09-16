"""
hyper/uncertainty/uncertainty_engine.py
=======================================
HYPER Uncertainty Engine:
Maintains spatial confidence maps in [0.0, 1.0] and drives compute budgets:
- High Confidence (>= 0.75)   -> Reuse / Reconstruct with minimal work
- Medium Confidence (0.35–0.75) -> Partial computation + Bilateral Reconstruction
- Low Confidence (< 0.35)     -> Full compute fallback
Directs computational resources strictly where uncertainty is high.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class HyperUncertaintyEngine:
    """
    Evaluates temporal and spatial uncertainty from:
    1. Depth discontinuities (occlusion boundaries)
    2. High-magnitude or divergent motion vectors
    3. Material/lighting delta changes
    4. Historical error metrics
    """

    def __init__(self, high_conf_thresh: float = 0.75, med_conf_thresh: float = 0.35):
        self.high_conf_thresh = high_conf_thresh
        self.med_conf_thresh = med_conf_thresh

    def compute_confidence_map(
        self,
        motion_vectors: np.ndarray,      # (H, W, 2) in pixels
        depth_current: np.ndarray,       # (H, W) float
        depth_previous_reprojected: Optional[np.ndarray] = None, # (H, W) float
        change_mask: Optional[np.ndarray] = None,  # (H, W) float
    ) -> np.ndarray:
        """
        Derives spatial confidence map in [0.0, 1.0] across the viewport.
        """
        h, w = depth_current.shape
        confidence = np.ones((h, w), dtype=np.float32)

        # 1. Depth disocclusion penalty
        if depth_previous_reprojected is not None:
            depth_diff = np.abs(depth_current - depth_previous_reprojected)
            # Relative depth error
            rel_depth_diff = depth_diff / np.maximum(1e-4, depth_current)
            disocclusion_penalty = np.clip(rel_depth_diff * 4.0, 0.0, 1.0)
            confidence -= disocclusion_penalty * 0.6

        # 2. Fast motion vector penalty (rapid movement introduces reprojection blur)
        motion_mag = np.sqrt(motion_vectors[..., 0]**2 + motion_vectors[..., 1]**2)
        # Anything moving faster than 50 pixels/frame reduces confidence
        motion_penalty = np.clip(motion_mag / 50.0, 0.0, 0.4)
        confidence -= motion_penalty

        # 3. Dynamic change mask penalty
        if change_mask is not None:
            confidence -= np.clip(change_mask * 0.5, 0.0, 0.5)

        return np.clip(confidence, 0.0, 1.0)

    def decide_execution_tier(self, confidence_score: float) -> str:
        """
        Maps confidence score to concrete HYPER decision tier:
        - 'REUSE_RECONSTRUCT'
        - 'PARTIAL_RECONSTRUCT'
        - 'FULL_COMPUTE'
        """
        if confidence_score >= self.high_conf_thresh:
            return "REUSE_RECONSTRUCT"
        elif confidence_score >= self.med_conf_thresh:
            return "PARTIAL_RECONSTRUCT"
        else:
            return "FULL_COMPUTE"
