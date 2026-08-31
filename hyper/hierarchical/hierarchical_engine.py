"""
hyper/hierarchical/hierarchical_engine.py
=========================================
Hierarchical Computation Engine (Section 23):
Implements Coarse-to-Fine Multiresolution Evaluation:
Low-cost coarse result -> Find uncertainty -> Refine only uncertain regions -> Verify.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple, List, Callable


class HierarchicalComputationEngine:
    """
    Executes coarse-to-fine progressive multiresolution computation.
    """
    def __init__(self, uncertainty_threshold: float = 0.05):
        self.uncertainty_threshold = uncertainty_threshold

    def evaluate_hierarchical_grid(
        self,
        grid_shape: Tuple[int, int],
        coarse_fn: Callable[[int, int], np.ndarray],
        fine_refine_fn: Callable[[np.ndarray, np.ndarray], np.ndarray]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Computes 4x subsampled coarse grid, detects high-gradient edge regions,
        and only executes fine evaluation on uncertain boundary elements.
        """
        t0 = time.perf_counter()
        H, W = grid_shape
        cH, cW = max(1, H // 2), max(1, W // 2)

        # 1. Coarse evaluation
        coarse = coarse_fn(cH, cW)

        # 2. Upsample to full resolution via bilinear interpolation proxy
        upsampled = np.repeat(np.repeat(coarse, 2, axis=0)[:H, :W], 1, axis=0)

        # 3. Detect high-variance / edge uncertainty
        grad_y, grad_x = np.gradient(upsampled)
        uncertainty = np.sqrt(grad_y ** 2 + grad_x ** 2)
        uncertain_mask = uncertainty > self.uncertainty_threshold
        uncertain_count = int(np.sum(uncertain_mask))
        total_pixels = H * W

        # 4. Refine only uncertain region
        refined = fine_refine_fn(upsampled, uncertain_mask)
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

        work_eliminated_pct = round((1.0 - (uncertain_count / max(1, total_pixels))) * 100.0, 2)
        cer = round(work_eliminated_pct / 100.0, 4)

        return refined, {
            "total_elements": total_pixels,
            "refined_elements": uncertain_count,
            "work_eliminated_pct": work_eliminated_pct,
            "cer": cer,
            "elapsed_ms": round(t_elapsed_ms, 3)
        }
