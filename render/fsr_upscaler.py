"""
render/fsr_upscaler.py
=============================================================================
Edge-Adaptive Super Resolution (FSR / CAS Implementation)
=============================================================================
Renders low-resolution frames (e.g. 540p / 720p) and upscales them using
bilinear interpolation coupled with Contrast Adaptive Sharpening (CAS).
Reduces rasterization / ray-tracing fillrate pressure by 2.25x - 4.0x.
"""

import numpy as np
from cbe.reconstruction.spatial_reconstruction import SpatialReconstructor


class FSRUpscaler:
    """
    Edge-Adaptive Spatial Upscaling with Contrast Adaptive Sharpening (CAS).
    Transforms low-resolution frame (H_in, W_in, 3) to high-resolution (H_out, W_out, 3).
    """

    def __init__(self, scale_factor: float = 2.0, sharpness: float = 0.25):
        self.scale_factor = scale_factor
        self.reconstructor = SpatialReconstructor(sharpness=sharpness)

    def upscale(self, low_res_frame: np.ndarray) -> np.ndarray:
        """
        Upscales an input float32 RGB buffer [H, W, 3] by self.scale_factor.
        Performs bilinear interpolation followed by CAS sharpening.
        """
        h, w, c = low_res_frame.shape
        target_h = int(h * self.scale_factor)
        target_w = int(w * self.scale_factor)

        # Bilinear interpolation grid
        y_indices = np.linspace(0, h - 1, target_h)
        x_indices = np.linspace(0, w - 1, target_w)

        y0 = np.floor(y_indices).astype(np.int32)
        y1 = np.clip(y0 + 1, 0, h - 1)
        x0 = np.floor(x_indices).astype(np.int32)
        x1 = np.clip(x0 + 1, 0, w - 1)

        fy = (y_indices - y0)[:, None, None].astype(np.float32)
        fx = (x_indices - x0)[None, :, None].astype(np.float32)

        # Vectorized bilinear sampling
        c00 = low_res_frame[y0[:, None], x0[None, :]]
        c01 = low_res_frame[y0[:, None], x1[None, :]]
        c10 = low_res_frame[y1[:, None], x0[None, :]]
        c11 = low_res_frame[y1[:, None], x1[None, :]]

        interpolated = (
            (1.0 - fy) * ((1.0 - fx) * c00 + fx * c01) +
            fy * ((1.0 - fx) * c10 + fx * c11)
        )

        # Apply Contrast Adaptive Sharpening (CAS)
        sharpened = self.reconstructor.sharpen_cas(interpolated)
        return np.clip(sharpened, 0.0, 1.0)
