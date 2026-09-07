"""
cbe/telemetry/quality_metrics.py
=============================================================================
Visual Quality Telemetry: SSIM, PSNR, Temporal Flicker & Ghosting Metrics
=============================================================================
Evaluates visual fidelity against physical reference frames and detects
temporal reprojection artifacts without relying on subjective appraisals.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class QualityMetricSample:
    frame_index: int
    ssim: float
    psnr: float
    temporal_flicker: float
    ghosting_metric: float
    passes_contract: bool


class QualityMetrics:
    """
    Evaluator for visual fidelity, temporal stability, and ghosting suppression.
    """

    def __init__(self, ssim_min: float = 0.92, psnr_min: float = 28.0):
        self.ssim_min = ssim_min
        self.psnr_min = psnr_min
        self.history: List[QualityMetricSample] = []
        self._prev_frame: Optional[np.ndarray] = None

    @staticmethod
    def compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
        """Computes SSIM between two float32 RGB images in [0, 1]."""
        c1 = (0.01) ** 2
        c2 = (0.03) ** 2

        # Luminance
        if img1.ndim == 3:
            y1 = 0.299 * img1[..., 0] + 0.587 * img1[..., 1] + 0.114 * img1[..., 2]
            y2 = 0.299 * img2[..., 0] + 0.587 * img2[..., 1] + 0.114 * img2[..., 2]
        else:
            y1, y2 = img1, img2

        mu1 = float(np.mean(y1))
        mu2 = float(np.mean(y2))
        sigma1_sq = float(np.var(y1))
        sigma2_sq = float(np.var(y2))
        sigma12 = float(np.mean((y1 - mu1) * (y2 - mu2)))

        num = (2.0 * mu1 * mu2 + c1) * (2.0 * sigma12 + c2)
        den = (mu1**2 + mu2**2 + c1) * (sigma1_sq + sigma2_sq + c2)
        ssim = num / max(1e-8, den)
        return float(np.clip(ssim, 0.0, 1.0))

    @staticmethod
    def compute_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
        """Computes PSNR between two images in dB."""
        mse = float(np.mean((img1 - img2) ** 2))
        if mse < 1e-10:
            return 100.0
        return float(20.0 * np.log10(1.0 / np.sqrt(mse)))

    @staticmethod
    def compute_temporal_flicker(curr_frame: np.ndarray, prev_frame: np.ndarray) -> float:
        """
        Measures high-frequency temporal flicker as normalized variance of frame delta.
        """
        delta = np.abs(curr_frame - prev_frame)
        # High temporal flicker shows up as high localized delta variance
        return float(np.mean(delta**2))

    @staticmethod
    def compute_ghosting_metric(
        reprojected: np.ndarray,
        reference: np.ndarray,
        disocclusion_mask: Optional[np.ndarray] = None
    ) -> float:
        """
        Measures ghosting error specifically along disoccluded edges.
        """
        diff = np.abs(reprojected - reference)
        if disocclusion_mask is not None and np.any(disocclusion_mask):
            return float(np.mean(diff[disocclusion_mask]))
        return float(np.mean(diff))

    def evaluate_frame(
        self,
        frame_index: int,
        reconstructed: np.ndarray,
        ground_truth: np.ndarray,
        disocclusion_mask: Optional[np.ndarray] = None
    ) -> QualityMetricSample:
        """
        Full frame visual quality evaluation.
        """
        ssim = self.compute_ssim(reconstructed, ground_truth)
        psnr = self.compute_psnr(reconstructed, ground_truth)

        flicker = 0.0
        if self._prev_frame is not None:
            flicker = self.compute_temporal_flicker(reconstructed, self._prev_frame)
        self._prev_frame = np.copy(reconstructed)

        ghosting = self.compute_ghosting_metric(
            reconstructed, ground_truth, disocclusion_mask
        )

        passes = (ssim >= self.ssim_min) and (psnr >= self.psnr_min)

        sample = QualityMetricSample(
            frame_index=frame_index,
            ssim=round(ssim, 4),
            psnr=round(psnr, 2),
            temporal_flicker=round(flicker, 6),
            ghosting_metric=round(ghosting, 4),
            passes_contract=passes,
        )
        self.history.append(sample)
        return sample

    def get_summary(self) -> Dict[str, Any]:
        """Returns aggregate quality statistics."""
        if not self.history:
            return {"total_frames": 0, "avg_ssim": 0.0, "avg_psnr": 0.0}

        ssims = [s.ssim for s in self.history]
        psnrs = [s.psnr for s in self.history]

        return {
            "total_frames": len(self.history),
            "avg_ssim": round(float(np.mean(ssims)), 4),
            "min_ssim": round(float(np.min(ssims)), 4),
            "p5_ssim": round(float(np.percentile(ssims, 5)), 4),
            "avg_psnr": round(float(np.mean(psnrs)), 2),
            "pass_rate": round(float(np.mean([1.0 if s.passes_contract else 0.0 for s in self.history])), 4),
        }
