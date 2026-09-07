"""
cbe/validation/visual_quality.py
=============================================================================
Visual Quality & Rendering Contract Validator
=============================================================================
Audits sequences of rendered frames against reference ground truth to ensure
that aggressive compute elimination does not violate visual fidelity contracts.
"""

from __future__ import annotations

import numpy as np
from typing import Dict, Any, List, Optional
from cbe.telemetry.quality_metrics import QualityMetrics


class VisualQualityValidator:
    """
    Validates that a rendering pipeline or sequence meets declared perceptual tolerances.
    """

    def __init__(self, target_ssim: float = 0.90, target_psnr: float = 28.0):
        self.target_ssim = target_ssim
        self.target_psnr = target_psnr
        self.metrics = QualityMetrics(ssim_min=target_ssim, psnr_min=target_psnr)

    def validate_frame(
        self,
        frame_idx: int,
        test_frame: np.ndarray,
        reference_frame: np.ndarray
    ) -> Dict[str, Any]:
        """Audits a single frame against reference."""
        sample = self.metrics.evaluate_frame(
            frame_index=frame_idx,
            reconstructed=test_frame,
            ground_truth=reference_frame
        )
        return {
            "frame_index": frame_idx,
            "ssim": sample.ssim,
            "psnr": sample.psnr,
            "temporal_flicker": sample.temporal_flicker,
            "passed": sample.passes_contract,
        }

    def validate_sequence(
        self,
        test_sequence: List[np.ndarray],
        reference_sequence: List[np.ndarray]
    ) -> Dict[str, Any]:
        """Audits an entire video sequence."""
        assert len(test_sequence) == len(reference_sequence)
        results = []
        for i, (t, r) in enumerate(zip(test_sequence, reference_sequence)):
            res = self.validate_frame(i, t, r)
            results.append(res)

        summary = self.metrics.get_summary()
        all_passed = summary["pass_rate"] >= 0.95
        return {
            "all_passed": all_passed,
            "pass_rate": summary["pass_rate"],
            "avg_ssim": summary["avg_ssim"],
            "min_ssim": summary["min_ssim"],
            "avg_psnr": summary["avg_psnr"],
            "frame_results": results,
        }
