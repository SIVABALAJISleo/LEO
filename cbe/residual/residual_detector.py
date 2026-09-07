"""
cbe/residual/residual_detector.py
Detects residual error between predicted/reprojected state and required target state.
Measures residual magnitude, spatial density, and temporal persistence.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class ResidualMetrics:
    residual_map: np.ndarray      # (H, W) float32 in [0, 1]
    mean_magnitude: float
    max_magnitude: float
    spatial_density: float        # Fraction of pixels where residual > threshold
    temporal_persistence: float   # Persistence between consecutive frame residuals


class ResidualDetector:
    """
    Detects and analyzes the mathematical residual:
    Target = Predicted + Residual.
    Identifies exact spatial coordinates where fresh computation is necessary.
    """
    def __init__(self, residual_threshold: float = 0.05):
        self.residual_threshold = residual_threshold
        self._prev_residual_map: Optional[np.ndarray] = None

    def detect_exact(
        self,
        target_frame: np.ndarray,
        predicted_frame: np.ndarray
    ) -> ResidualMetrics:
        """Computes ground-truth pixel residual when both target and prediction are present."""
        diff = np.abs(target_frame - predicted_frame)
        if diff.ndim == 3:
            residual_map = np.max(diff, axis=-1).astype(np.float32)
        else:
            residual_map = diff.astype(np.float32)
            
        return self._build_metrics(residual_map)

    def estimate_predictive(
        self,
        confidence_map: np.ndarray,
        disocclusion_mask: np.ndarray,
        motion_vectors: np.ndarray,
        importance_map: Optional[np.ndarray] = None
    ) -> ResidualMetrics:
        """
        Estimates residual prior to rendering using disocclusion signals,
        confidence deficits, and motion discontinuities.
        """
        H, W = confidence_map.shape
        # Base residual from confidence deficiency
        res_map = (1.0 - np.clip(confidence_map, 0.0, 1.0)).astype(np.float32)
        
        # Disocclusions guarantee high residual
        res_map[disocclusion_mask] = 1.0
        
        # Importance weighting: higher perceptual importance amplifies sensitivity to residual
        if importance_map is not None:
            res_map *= (0.5 + 0.5 * np.clip(importance_map, 0.0, 1.0))
            
        res_map = np.clip(res_map, 0.0, 1.0)
        return self._build_metrics(res_map)

    def _build_metrics(self, residual_map: np.ndarray) -> ResidualMetrics:
        mean_mag = float(np.mean(residual_map))
        max_mag = float(np.max(residual_map))
        active_pixels = residual_map > self.residual_threshold
        density = float(np.sum(active_pixels)) / float(residual_map.size)
        
        # Temporal persistence: correlation with prior residual map
        persistence = 0.0
        if self._prev_residual_map is not None and self._prev_residual_map.shape == residual_map.shape:
            overlap = active_pixels & (self._prev_residual_map > self.residual_threshold)
            persistence = float(np.sum(overlap)) / float(max(1, np.sum(active_pixels)))
            
        self._prev_residual_map = residual_map.copy()
        
        return ResidualMetrics(
            residual_map=residual_map,
            mean_magnitude=mean_mag,
            max_magnitude=max_mag,
            spatial_density=density,
            temporal_persistence=persistence
        )
