"""
hyper_x/ahce/domains/media.py
=============================
Media and video residual adapter for AHCE.
"""

from typing import Dict, Any, Tuple
import numpy as np
from ..contract import AHCEContract, CorrectnessClass


class MediaDomainAdapter:
    """Media spatial filtering and video residual adapter."""

    def process_frame_residual(
        self,
        current_frame: np.ndarray,
        reference_frame: np.ndarray,
        contract: AHCEContract,
        threshold: float = 2.0
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        # Compute macroblock difference
        diff = np.abs(current_frame.astype(np.float32) - reference_frame.astype(np.float32))
        static_mask = diff <= threshold
        reused_pct = float(np.sum(static_mask) / current_frame.size) * 100.0

        # Output reconstructed frame
        reconstructed = np.where(static_mask, reference_frame, current_frame)
        return reconstructed, {
            "reused_pixels_pct": round(reused_pct, 2),
            "strategy": "motion_residual_coding",
            "path_class": "PERCEPTUAL_APPROXIMATION" if reused_pct < 100.0 else "EXACT"
        }
