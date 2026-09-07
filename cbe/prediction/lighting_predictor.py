"""
cbe/prediction/lighting_predictor.py
Predicts dynamic lighting shifts and spherical harmonics ambient radiance changes.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, List, Optional


class LightingPredictor:
    """
    Tracks illumination trends across time to predict lighting shifts
    before invoking expensive light recalculations.
    """
    def __init__(self):
        self.last_intensity: float = 1.0
        self.intensity_velocity: float = 0.0

    def update(self, intensity: float, dt: float = 0.01667):
        if dt > 1e-4:
            self.intensity_velocity = (intensity - self.last_intensity) / dt
        self.last_intensity = intensity

    def predict_intensity(self, dt: float = 0.01667) -> float:
        return max(0.0, self.last_intensity + self.intensity_velocity * dt)
