"""
hyper/godmode/graphics_video.py
===============================
Graphics, Gaming, and Video Optimization Engine (Feature Module L).

Adapts workloads for high-throughput visual computing on CPU+iGPU:
- 3D Frustum Culling: Vectorized rejection of out-of-view bounding spheres
- Level of Detail (LOD) Distance Selection
- Video Dirty-Region Differential Tracking: Eliminates static macroblocks
- Bounded Tiled Spatial Processing for High-Resolution Imagery
"""

from __future__ import annotations
import math
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field


class CullingResult(BaseModel):
    total_primitives: int
    visible_primitives: int
    culled_primitives: int
    cull_ratio_pct: float
    elapsed_ms: float


class DirtyRegionResult(BaseModel):
    frame_width: int
    frame_height: int
    dirty_bbox: Tuple[int, int, int, int]  # (min_x, min_y, max_x, max_y)
    changed_pixels: int
    total_pixels: int
    work_reduction_pct: float
    elapsed_ms: float


class GraphicsVideoOptimizer:
    """
    Algorithmic visual optimization for graphics rasterization and video frames.
    """

    @staticmethod
    def frustum_cull_bounding_spheres(
        centers: np.ndarray,  # Shape (N, 3)
        radii: np.ndarray,    # Shape (N,)
        view_distance_max: float = 100.0,
        view_distance_min: float = 0.5,
    ) -> Tuple[np.ndarray, CullingResult]:
        """
        Fast view-frustum depth and radial distance culling.
        Returns boolean visibility mask and metrics.
        """
        t0 = time.perf_counter_ns()
        n = centers.shape[0]

        # Radial distance from camera at origin (0, 0, 0)
        dist = np.linalg.norm(centers, axis=1)

        # Distance gating
        visible_mask = (dist - radii >= view_distance_min) & (dist + radii <= view_distance_max)

        # Simple 60-degree field-of-view cone test: |x| <= z * tan(30deg)
        z = centers[:, 2]
        x = centers[:, 0]
        y = centers[:, 1]
        tan30 = 0.57735

        cone_mask = (z > 0) & (np.abs(x) - radii <= z * tan30) & (np.abs(y) - radii <= z * tan30)
        final_mask = visible_mask & cone_mask

        elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
        visible_count = int(np.sum(final_mask))
        culled_count = n - visible_count
        ratio = (culled_count / max(n, 1)) * 100.0

        res = CullingResult(
            total_primitives=n,
            visible_primitives=visible_count,
            culled_primitives=culled_count,
            cull_ratio_pct=round(ratio, 2),
            elapsed_ms=round(elapsed_ms, 3),
        )
        return final_mask, res

    @staticmethod
    def select_lod(
        distances: np.ndarray,
        thresholds: Tuple[float, float] = (25.0, 60.0),
    ) -> np.ndarray:
        """
        Assigns Level of Detail (0 = full detail, 1 = medium, 2 = low)
        based on distance from viewpoint.
        """
        lod = np.zeros_like(distances, dtype=np.uint8)
        lod[distances > thresholds[0]] = 1
        lod[distances > thresholds[1]] = 2
        return lod

    @staticmethod
    def extract_video_dirty_region(
        frame_prev: np.ndarray,
        frame_curr: np.ndarray,
        threshold: float = 0.05,
    ) -> Tuple[Optional[Tuple[int, int, int, int]], DirtyRegionResult]:
        """
        Extracts temporal dirty-region bounding box between consecutive video frames.
        Avoids redundant pixel pipeline execution for static areas.
        """
        t0 = time.perf_counter_ns()
        h, w = frame_prev.shape[:2]
        total_px = h * w

        diff = np.abs(frame_curr.astype(np.float32) - frame_prev.astype(np.float32))
        if diff.ndim == 3:
            diff = np.max(diff, axis=2)

        changed_mask = diff > threshold
        changed_count = int(np.sum(changed_mask))

        if changed_count == 0:
            elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
            res = DirtyRegionResult(
                frame_width=w,
                frame_height=h,
                dirty_bbox=(0, 0, 0, 0),
                changed_pixels=0,
                total_pixels=total_px,
                work_reduction_pct=100.0,
                elapsed_ms=round(elapsed_ms, 3),
            )
            return None, res

        y_indices, x_indices = np.where(changed_mask)
        min_x = int(np.min(x_indices))
        max_x = int(np.max(x_indices))
        min_y = int(np.min(y_indices))
        max_y = int(np.max(y_indices))

        dirty_area = (max_x - min_x + 1) * (max_y - min_y + 1)
        work_red = ((total_px - dirty_area) / total_px) * 100.0
        elapsed_ms = (time.perf_counter_ns() - t0) / 1e6

        res = DirtyRegionResult(
            frame_width=w,
            frame_height=h,
            dirty_bbox=(min_x, min_y, max_x, max_y),
            changed_pixels=changed_count,
            total_pixels=total_px,
            work_reduction_pct=round(work_red, 2),
            elapsed_ms=round(elapsed_ms, 3),
        )
        return (min_x, min_y, max_x, max_y), res
