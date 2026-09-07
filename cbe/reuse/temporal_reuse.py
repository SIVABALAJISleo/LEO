"""
cbe/reuse/temporal_reuse.py
True motion-compensated temporal reprojection with depth-aware disocclusion
detection, history clamping (ghosting suppression), and pixel confidence scoring.
Replaces naive sparse pixel diffing with physically sound temporal reuse.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class ReprojectionResult:
    reprojected_color: np.ndarray  # (H, W, 3) float32
    confidence_map: np.ndarray     # (H, W) float32 in [0, 1]
    disocclusion_mask: np.ndarray  # (H, W) bool, True where disoccluded (needs compute)
    reusable_pixel_ratio: float    # Ratio of pixels with confidence >= threshold
    avg_confidence: float


class TemporalReuseEngine:
    """
    Subpixel motion-compensated temporal reprojection and validation engine.
    Solves ghosting, trailing, and disocclusion artifacts via depth testing and AABB color clamping.
    """
    def __init__(
        self,
        depth_threshold: float = 0.05,
        confidence_threshold: float = 0.85,
        enable_clamping: bool = True
    ):
        self.depth_threshold = depth_threshold
        self.confidence_threshold = confidence_threshold
        self.enable_clamping = enable_clamping

    def reproject(
        self,
        prev_color: np.ndarray,
        motion_vectors: np.ndarray
    ) -> np.ndarray:
        """
        Warps prev_color according to motion_vectors using bilinear interpolation.
        motion_vectors: (H, W, 2) where [y, x, 0] is dx and [y, x, 1] is dy.
        prev_pos = (x - dx, y - dy).
        """
        H, W, C = prev_color.shape
        y_grid, x_grid = np.mgrid[0:H, 0:W].astype(np.float32)
        
        # Source coordinate in previous frame
        src_x = x_grid - motion_vectors[..., 0]
        src_y = y_grid - motion_vectors[..., 1]
        
        # Clamp to valid image bounds
        src_x = np.clip(src_x, 0.0, W - 1.001)
        src_y = np.clip(src_y, 0.0, H - 1.001)
        
        x0 = np.floor(src_x).astype(np.int32)
        x1 = np.minimum(x0 + 1, W - 1)
        y0 = np.floor(src_y).astype(np.int32)
        y1 = np.minimum(y0 + 1, H - 1)
        
        wx = (src_x - x0)[..., None]
        wy = (src_y - y0)[..., None]
        
        # 4-tap bilinear filter
        c00 = prev_color[y0, x0]
        c10 = prev_color[y0, x1]
        c01 = prev_color[y1, x0]
        c11 = prev_color[y1, x1]
        
        top = c00 * (1.0 - wx) + c10 * wx
        bottom = c01 * (1.0 - wx) + c11 * wx
        warped = top * (1.0 - wy) + bottom * wy
        
        return np.clip(warped, 0.0, 1.0)

    def detect_disocclusions(
        self,
        current_depth: np.ndarray,
        prev_depth: np.ndarray,
        motion_vectors: np.ndarray
    ) -> np.ndarray:
        """
        Detects newly revealed geometry via depth delta.
        Returns boolean mask where True indicates a disocclusion (geometry changed).
        """
        H, W = current_depth.shape
        y_grid, x_grid = np.mgrid[0:H, 0:W].astype(np.float32)
        src_x = np.clip(x_grid - motion_vectors[..., 0], 0, W - 1).astype(np.int32)
        src_y = np.clip(y_grid - motion_vectors[..., 1], 0, H - 1).astype(np.int32)
        
        reprojected_depth = prev_depth[src_y, src_x]
        
        # Disocclusion occurs if current surface is significantly in front of or behind reprojected surface
        depth_denom = np.maximum(np.abs(current_depth), 1e-4)
        relative_diff = np.abs(current_depth - reprojected_depth) / depth_denom
        disoccluded = relative_diff > self.depth_threshold
        return disoccluded

    def compute_confidence(
        self,
        current_depth: np.ndarray,
        prev_depth: np.ndarray,
        motion_vectors: np.ndarray,
        reactive_mask: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates per-pixel confidence map [0, 1] factoring motion stability,
        depth continuity, and reactive mask exclusion.
        """
        disocclusion = self.detect_disocclusions(current_depth, prev_depth, motion_vectors)
        
        # Base confidence from depth consistency
        depth_denom = np.maximum(np.abs(current_depth), 1e-4)
        rel_diff = np.abs(current_depth - prev_depth) / depth_denom
        depth_confidence = np.exp(-rel_diff / (self.depth_threshold + 1e-4))
        
        # Motion speed penalty (ultra-fast pixels have higher sampling uncertainty)
        motion_mag = np.linalg.norm(motion_vectors, axis=-1)
        motion_confidence = np.exp(-motion_mag / 50.0)  # Soft decay over 50px displacement
        
        confidence = depth_confidence * motion_confidence
        
        # Disoccluded pixels immediately drop to 0.0 confidence
        confidence[disocclusion] = 0.0
        
        # Reactive mask suppression (particles, transparencies, dynamic UI)
        if reactive_mask is not None:
            confidence *= (1.0 - np.clip(reactive_mask, 0.0, 1.0))
            
        confidence = np.clip(confidence, 0.0, 1.0).astype(np.float32)
        return confidence, disocclusion

    def clamp_history(
        self,
        reprojected_color: np.ndarray,
        guide_color: np.ndarray
    ) -> np.ndarray:
        """
        AABB color clamping: clamps reprojected color into the local 3x3
        neighborhood color box of the current guide frame to kill ghosting.
        """
        if not self.enable_clamping:
            return reprojected_color
            
        H, W, C = guide_color.shape
        padded = np.pad(guide_color, ((1, 1), (1, 1), (0, 0)), mode="edge")
        
        # Compute local 3x3 min and max bounds
        box_min = np.copy(guide_color)
        box_max = np.copy(guide_color)
        
        for dy in range(3):
            for dx in range(3):
                sample = padded[dy:dy+H, dx:dx+W]
                box_min = np.minimum(box_min, sample)
                box_max = np.maximum(box_max, sample)
                
        # Clamp reprojected color to [box_min, box_max]
        clamped = np.clip(reprojected_color, box_min, box_max)
        return clamped

    def evaluate_temporal_reuse(
        self,
        prev_color: np.ndarray,
        prev_depth: np.ndarray,
        current_depth: np.ndarray,
        motion_vectors: np.ndarray,
        reactive_mask: Optional[np.ndarray] = None,
        guide_color: Optional[np.ndarray] = None
    ) -> ReprojectionResult:
        """
        Executes end-to-end temporal reprojection, validation, and history clamping.
        """
        reprojected = self.reproject(prev_color, motion_vectors)
        
        if guide_color is not None:
            reprojected = self.clamp_history(reprojected, guide_color)
            
        confidence, disocclusion = self.compute_confidence(
            current_depth=current_depth,
            prev_depth=prev_depth,
            motion_vectors=motion_vectors,
            reactive_mask=reactive_mask
        )
        
        reusable_mask = (confidence >= self.confidence_threshold) & (~disocclusion)
        reusable_ratio = float(np.sum(reusable_mask)) / float(reusable_mask.size)
        avg_conf = float(np.mean(confidence))
        
        return ReprojectionResult(
            reprojected_color=reprojected,
            confidence_map=confidence,
            disocclusion_mask=disocclusion,
            reusable_pixel_ratio=reusable_ratio,
            avg_confidence=avg_conf
        )
