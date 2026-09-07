"""
cbe/reuse/spatial_reuse.py
Cross-bilateral spatial sample and radiance reuse.
Exchanges samples across coplanar neighboring pixels on identical geometric surfaces
to fill missing or noisy regions without expensive ray queries.
"""

from __future__ import annotations

import numpy as np


class SpatialReuseEngine:
    """
    Evaluates spatial neighborhood geometry (normals, depth, material)
    and propagates confident samples across coplanar surface patches.
    """
    def __init__(self, filter_radius: int = 2, normal_threshold: float = 0.90, depth_threshold: float = 0.05):
        self.radius = filter_radius
        self.normal_thresh = normal_threshold
        self.depth_thresh = depth_threshold

    def filter_spatial(
        self,
        color_buffer: np.ndarray,      # (H, W, 3) float32
        normal_buffer: np.ndarray,     # (H, W, 3) normalized float32
        depth_buffer: np.ndarray,      # (H, W) float32
        confidence_mask: np.ndarray    # (H, W) float32 in [0, 1]
    ) -> np.ndarray:
        """
        Executes cross-bilateral geometry-guided spatial filtering.
        Propagates high-confidence pixels into low-confidence neighbors on the same surface.
        """
        H, W, C = color_buffer.shape
        output = color_buffer.copy()
        r = self.radius
        
        padded_color = np.pad(color_buffer, ((r, r), (r, r), (0, 0)), mode="edge")
        padded_normal = np.pad(normal_buffer, ((r, r), (r, r), (0, 0)), mode="edge")
        padded_depth = np.pad(depth_buffer, ((r, r), (r, r)), mode="edge")
        padded_conf = np.pad(confidence_mask, ((r, r), (r, r)), mode="edge")
        
        # Only pixels with low confidence (<0.80) need spatial sample gathering
        needy_mask = confidence_mask < 0.80
        if not np.any(needy_mask):
            return output
            
        weight_sum = np.zeros((H, W, 1), dtype=np.float32)
        accum_color = np.zeros((H, W, C), dtype=np.float32)
        
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                ny = dy + r
                nx = dx + r
                
                n_sample = padded_normal[ny:ny+H, nx:nx+W]
                d_sample = padded_depth[ny:ny+H, nx:nx+W]
                c_sample = padded_color[ny:ny+H, nx:nx+W]
                conf_sample = padded_conf[ny:ny+H, nx:nx+W]
                
                # Normal agreement
                normal_dot = np.sum(normal_buffer * n_sample, axis=-1, keepdims=True)
                normal_weight = np.maximum(0.0, normal_dot)**8.0
                
                # Depth agreement
                depth_denom = np.maximum(np.abs(depth_buffer), 1e-4)[..., None]
                rel_depth = np.abs(depth_buffer[..., None] - d_sample[..., None]) / depth_denom
                depth_weight = np.exp(-rel_depth / self.depth_thresh)
                
                # Spatial distance
                spatial_weight = float(np.exp(-(dx**2 + dy**2) / (2.0 * (r**2))))
                
                total_w = normal_weight * depth_weight * spatial_weight * conf_sample[..., None]
                accum_color += c_sample * total_w
                weight_sum += total_w
                
        # Blend into needy pixels
        filtered = accum_color / (weight_sum + 1e-6)
        valid = (weight_sum[..., 0] > 0.1) & needy_mask
        output[valid] = filtered[valid]
        
        return np.clip(output, 0.0, 1.0).astype(np.float32)
