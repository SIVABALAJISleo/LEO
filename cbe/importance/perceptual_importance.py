"""
cbe/importance/perceptual_importance.py
Human visual system (HVS) contrast sensitivity and edge-density evaluation.
High spatial frequency and high contrast regions demand higher shading fidelity.
"""

from __future__ import annotations

import numpy as np


class PerceptualImportance:
    """
    Evaluates perceptual importance using luminance contrast and gradient energy.
    """
    def compute(self, color_buffer: np.ndarray) -> np.ndarray:
        """
        color_buffer: (H, W, 3) float32 in [0, 1].
        Returns: (H, W) float32 importance field in [0, 1].
        """
        H, W, C = color_buffer.shape
        # Rec. 709 luminance weights
        lum = 0.2126 * color_buffer[..., 0] + 0.7152 * color_buffer[..., 1] + 0.0722 * color_buffer[..., 2]
        
        # Spatial gradients (Sobel approximation via finite difference)
        padded = np.pad(lum, ((1, 1), (1, 1)), mode="edge")
        gx = (padded[1:H+1, 2:W+2] - padded[1:H+1, 0:W]) * 0.5
        gy = (padded[2:H+2, 1:W+1] - padded[0:H, 1:W+1]) * 0.5
        
        gradient_mag = np.sqrt(gx**2 + gy**2)
        
        # Local contrast: variance in 3x3 neighborhood
        contrast_boost = np.clip(gradient_mag * 3.0, 0.0, 1.0)
        
        # Base importance threshold of 0.2 so even flat areas receive acceptable baseline quality
        importance = 0.2 + 0.8 * contrast_boost
        return np.clip(importance, 0.0, 1.0).astype(np.float32)
