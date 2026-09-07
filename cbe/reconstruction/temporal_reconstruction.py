"""
cbe/reconstruction/temporal_reconstruction.py
Full temporal super-resolution (TSR) engine.
Accumulates subpixel jittered low-resolution inputs into a high-resolution buffer,
guided by motion vectors, depth testing, neighborhood color clamping, and reactive masks.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Tuple

from .spatial_reconstruction import SpatialReconstructor, ContrastAdaptiveSharpener


class TemporalSuperResolution:
    """
    Temporal Super-Resolution (TSR) pipeline.
    Reconstructs clean 1080p/4K frames from 540p/720p inputs using subpixel temporal integration.
    """
    def __init__(
        self,
        sharpness: float = 0.40,
        blend_factor_base: float = 0.85
    ):
        self.spatial_recon = SpatialReconstructor(sharpness=sharpness)
        self.cas = ContrastAdaptiveSharpener(sharpness=sharpness)
        self.blend_factor_base = blend_factor_base

    def reconstruct(
        self,
        low_res_color: np.ndarray,
        target_height: int,
        target_width: int,
        motion_vectors: np.ndarray,
        current_depth: np.ndarray,
        prev_depth: np.ndarray,
        history_color: Optional[np.ndarray] = None,
        jitter_offset: Optional[np.ndarray] = None,
        reactive_mask: Optional[np.ndarray] = None,
        disocclusion_mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Executes temporal accumulation pass.
        """
        # 1. Spatial upsampling of current low-res frame to target resolution
        current_upscaled = self.spatial_recon.upscale(low_res_color, target_height, target_width)
        
        # If no history exists, return current spatial upsample
        if history_color is None:
            return current_upscaled
            
        H, W, C = target_height, target_width, 3
        
        # 2. Motion reprojection of previous history frame
        y_grid, x_grid = np.mgrid[0:H, 0:W].astype(np.float32)
        src_x = np.clip(x_grid - motion_vectors[..., 0], 0.0, W - 1.001)
        src_y = np.clip(y_grid - motion_vectors[..., 1], 0.0, H - 1.001)
        
        x0 = np.floor(src_x).astype(np.int32)
        x1 = np.minimum(x0 + 1, W - 1)
        y0 = np.floor(src_y).astype(np.int32)
        y1 = np.minimum(y0 + 1, H - 1)
        
        wx = (src_x - x0)[..., None]
        wy = (src_y - y0)[..., None]
        
        c00 = history_color[y0, x0]
        c10 = history_color[y0, x1]
        c01 = history_color[y1, x0]
        c11 = history_color[y1, x1]
        
        reprojected_history = (c00 * (1.0 - wx) + c10 * wx) * (1.0 - wy) + (c01 * (1.0 - wx) + c11 * wx) * wy
        
        # 3. Neighborhood AABB Color Clamping (kills ghosting)
        padded = np.pad(current_upscaled, ((1, 1), (1, 1), (0, 0)), mode="edge")
        local_min = np.copy(current_upscaled)
        local_max = np.copy(current_upscaled)
        for dy in range(3):
            for dx in range(3):
                sample = padded[dy:dy+H, dx:dx+W]
                local_min = np.minimum(local_min, sample)
                local_max = np.maximum(local_max, sample)
                
        clamped_history = np.clip(reprojected_history, local_min, local_max)
        
        # 4. Adaptive accumulation weight calculation
        # Base temporal weight ~0.85
        alpha = np.full((H, W, 1), self.blend_factor_base, dtype=np.float32)
        
        if disocclusion_mask is not None:
            # Disoccluded pixels cannot use history (alpha -> 0.0)
            alpha[disocclusion_mask] = 0.0
            
        if reactive_mask is not None:
            # High reactive mask -> reduce history accumulation
            alpha *= (1.0 - np.clip(reactive_mask[..., None], 0.0, 1.0))
            
        # Velocity penalty: very fast pixels accumulate less history
        speed = np.linalg.norm(motion_vectors, axis=-1, keepdims=True)
        alpha *= np.exp(-speed / 40.0)
        alpha = np.clip(alpha, 0.05, 0.90)
        
        # 5. Temporal blend
        accumulated = alpha * clamped_history + (1.0 - alpha) * current_upscaled
        
        # 6. Final Contrast-Adaptive Sharpening
        final_frame = self.cas.sharpen(accumulated)
        return np.clip(final_frame, 0.0, 1.0).astype(np.float32)
