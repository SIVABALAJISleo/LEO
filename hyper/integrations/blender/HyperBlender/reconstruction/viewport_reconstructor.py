"""
hyper/integrations/blender/HyperBlender/reconstruction/viewport_reconstructor.py
"""
import numpy as np
from hyper.reconstruction import HyperReconstructionEngine

class BlenderViewportReconstructor:
    """Executes motion reprojection and bilateral filtering for Blender viewport."""
    def __init__(self):
        self.engine = HyperReconstructionEngine()

    def reconstruct(self, previous_pixels: np.ndarray, current_sparse_pixels: np.ndarray, motion_vectors: np.ndarray) -> np.ndarray:
        reprojected = self.engine.reproject_buffer(previous_pixels, motion_vectors)
        clamped = self.engine.clamp_history_neighborhood(reprojected, current_sparse_pixels)
        conf = np.ones((current_sparse_pixels.shape[0], current_sparse_pixels.shape[1]), dtype=np.float32)
        accumulated = self.engine.temporal_accumulate(current_sparse_pixels, clamped, conf)
        return self.engine.bilateral_filter(accumulated)
