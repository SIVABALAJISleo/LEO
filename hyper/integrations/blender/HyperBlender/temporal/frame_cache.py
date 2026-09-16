"""
hyper/integrations/blender/HyperBlender/temporal/frame_cache.py
"""
import numpy as np
from typing import Optional

class BlenderTemporalCache:
    """Maintains viewport render buffer history for interactive reprojection."""
    def __init__(self):
        self.previous_viewport_pixels: Optional[np.ndarray] = None

    def store(self, pixels: np.ndarray):
        self.previous_viewport_pixels = pixels.copy()

    def get(self) -> Optional[np.ndarray]:
        return self.previous_viewport_pixels
