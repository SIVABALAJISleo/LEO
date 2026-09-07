"""
cbe/reconstruction/spatial_reconstruction.py
Edge-directed spatial upscaling and Contrast-Adaptive Sharpening (CAS).
Eliminates blur without halo artifacts or overshooting high-frequency edges.
"""

from __future__ import annotations

import numpy as np


class ContrastAdaptiveSharpener:
    """
    Contrast-Adaptive Sharpening (CAS) algorithm.
    Sharpens edges adaptively based on local neighborhood contrast, preventing ringing.
    """
    def __init__(self, sharpness: float = 0.5):
        # Sharpness parameter in [0.0, 1.0]
        self.sharpness = sharpness

    def sharpen(self, image: np.ndarray) -> np.ndarray:
        """
        image: (H, W, 3) float32 in [0, 1].
        """
        H, W, C = image.shape
        padded = np.pad(image, ((1, 1), (1, 1), (0, 0)), mode="edge")
        
        # 5-tap cross filter (center, top, bottom, left, right)
        center = image
        top = padded[0:H, 1:W+1]
        bottom = padded[2:H+2, 1:W+1]
        left = padded[1:H+1, 0:W]
        right = padded[1:H+1, 2:W+2]
        
        # Local min and max
        min_rgb = np.minimum(center, np.minimum(np.minimum(top, bottom), np.minimum(left, right)))
        max_rgb = np.maximum(center, np.maximum(np.maximum(top, bottom), np.maximum(left, right)))
        
        # Smooth step weight
        amp = np.minimum(min_rgb, 1.0 - max_rgb) / np.maximum(max_rgb, 1e-4)
        w = -np.sqrt(np.clip(amp, 0.0, 1.0)) * (self.sharpness * 0.1875)
        
        # Filter output: (center + w * (top + bottom + left + right)) / (1 + 4*w)
        cross_sum = top + bottom + left + right
        sharpened = (center + w * cross_sum) / (1.0 + 4.0 * w)
        
        return np.clip(sharpened, 0.0, 1.0).astype(np.float32)


class SpatialReconstructor:
    """
    Edge-directed spatial upscaler integrating bilinear/bicubic resampling and CAS.
    """
    def __init__(self, sharpness: float = 0.5):
        self.cas = ContrastAdaptiveSharpener(sharpness=sharpness)

    def upscale(self, low_res_frame: np.ndarray, target_height: int, target_width: int) -> np.ndarray:
        """
        Resamples low_res_frame (H_in, W_in, 3) to (target_height, target_width, 3).
        """
        H_in, W_in, C = low_res_frame.shape
        if H_in == target_height and W_in == target_width:
            return self.cas.sharpen(low_res_frame)
            
        y_coords = np.linspace(0, H_in - 1, target_height)
        x_coords = np.linspace(0, W_in - 1, target_width)
        
        y_grid, x_grid = np.meshgrid(y_coords, x_coords, indexing="ij")
        
        x0 = np.floor(x_grid).astype(np.int32)
        x1 = np.minimum(x0 + 1, W_in - 1)
        y0 = np.floor(y_grid).astype(np.int32)
        y1 = np.minimum(y0 + 1, H_in - 1)
        
        wx = (x_grid - x0)[..., None]
        wy = (y_grid - y0)[..., None]
        
        c00 = low_res_frame[y0, x0]
        c10 = low_res_frame[y0, x1]
        c01 = low_res_frame[y1, x0]
        c11 = low_res_frame[y1, x1]
        
        top = c00 * (1.0 - wx) + c10 * wx
        bottom = c01 * (1.0 - wx) + c11 * wx
        interpolated = top * (1.0 - wy) + bottom * wy
        
        # Apply Contrast-Adaptive Sharpening
        return self.cas.sharpen(interpolated)

    def sharpen_cas(self, image: np.ndarray) -> np.ndarray:
        """Applies Contrast Adaptive Sharpening directly to an image buffer."""
        return self.cas.sharpen(image)

    def reconstruct_sparse(self, color: np.ndarray, confidence: np.ndarray, k_size: int = 3) -> np.ndarray:
        """
        Fills missing/low-confidence regions using a spatial gather from high-confidence neighbors.
        """
        H, W, C = color.shape
        result = np.copy(color)
        invalid = confidence < 0.5
        if not np.any(invalid):
            return result

        pad_r = k_size // 2
        padded_c = np.pad(color, ((pad_r, pad_r), (pad_r, pad_r), (0, 0)), mode="edge")
        padded_conf = np.pad(confidence, ((pad_r, pad_r), (pad_r, pad_r)), mode="edge")

        # Vectorized local patch weighted sum for low confidence pixels
        accum = np.zeros_like(color)
        weight_sum = np.zeros((H, W, 1), dtype=np.float32)

        for dy in range(-pad_r, pad_r + 1):
            for dx in range(-pad_r, pad_r + 1):
                neighbor_c = padded_c[pad_r + dy : H + pad_r + dy, pad_r + dx : W + pad_r + dx]
                neighbor_conf = padded_conf[pad_r + dy : H + pad_r + dy, pad_r + dx : W + pad_r + dx, None]
                dist_sq = float(dx * dx + dy * dy)
                weight = np.exp(-dist_sq / 2.0) * neighbor_conf
                accum += neighbor_c * weight
                weight_sum += weight

        reconstructed = accum / np.maximum(1e-5, weight_sum)
        result = np.where(invalid[..., None], reconstructed, color)
        return np.clip(result, 0.0, 1.0).astype(np.float32)
