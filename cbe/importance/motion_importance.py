"""
cbe/importance/motion_importance.py
Motion-aware importance scaling based on temporal masking.
High motion regions naturally tolerate lower spatial shading fidelity due to motion blur,
allowing aggressive compute avoidance without perceptual quality loss.
"""

from __future__ import annotations

import numpy as np


class MotionImportance:
    """
    Evaluates motion speed and maps it to shading importance.
    Static/slow regions: High importance (crisp detail needed).
    Very fast regions: Lower shading importance (masked by optical blur).
    """
    def __init__(self, speed_threshold: float = 20.0):
        self.speed_threshold = speed_threshold

    def compute(self, motion_vectors: np.ndarray) -> np.ndarray:
        """
        motion_vectors: (H, W, 2) in pixels.
        Returns: (H, W) float32 shading importance in [0.3, 1.0].
        """
        speed = np.linalg.norm(motion_vectors, axis=-1)
        # Fast motion decreases the required shading frequency
        # Smooth decay from 1.0 (static) down to 0.35 (fast motion)
        attenuation = np.exp(-speed / self.speed_threshold)
        importance = 0.35 + 0.65 * attenuation
        return np.clip(importance, 0.35, 1.0).astype(np.float32)
