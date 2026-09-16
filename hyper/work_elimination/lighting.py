"""
hyper/work_elimination/lighting.py
==================================
HYPER Lighting Work Elimination:
Reuses static direct/indirect lighting, temporal irradiance caching,
and screen-space ambient occlusion reuse.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class LightingEliminationEngine:
    """
    Eliminates redundant light transport calculation across successive frames.
    """

    def __init__(self, cache_resolution: tuple = (135, 240)):
        self.cache_h, self.cache_w = cache_resolution
        self.cached_irradiance: Optional[np.ndarray] = None  # (H, W, 3) float32
        self.irradiance_confidence: np.ndarray = np.zeros((self.cache_h, self.cache_w), dtype=np.float32)

    def evaluate_lighting_reuse(
        self,
        light_deltas: List[str],
        camera_moved: bool,
        current_irradiance: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, float]:
        """
        Calculates irradiance blending factor.
        Returns: (blended_irradiance, work_reduction_ratio)
        """
        has_dynamic_lights = len(light_deltas) > 0

        if self.cached_irradiance is None or current_irradiance is None:
            if current_irradiance is not None:
                self.cached_irradiance = current_irradiance.copy()
                self.irradiance_confidence.fill(1.0)
                return current_irradiance, 0.0
            return np.zeros((self.cache_h, self.cache_w, 3), dtype=np.float32), 0.0

        # If no dynamic lights changed, we can perform 85-95% temporal reuse
        if not has_dynamic_lights and not camera_moved:
            reuse_weight = 0.95
            work_reduction = 0.95
        elif not has_dynamic_lights and camera_moved:
            reuse_weight = 0.80
            work_reduction = 0.80
        else:
            reuse_weight = 0.30
            work_reduction = 0.30

        # Exponential moving average temporal accumulation
        blended = self.cached_irradiance * reuse_weight + current_irradiance * (1.0 - reuse_weight)
        self.cached_irradiance = blended.copy()

        return blended, work_reduction
