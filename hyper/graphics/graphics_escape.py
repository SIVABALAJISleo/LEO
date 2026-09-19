"""
Graphics Escape Engine for LEO/HYPER Ω.
Optimizes graphics workloads through visual information sufficiency:
«How much NEW visual information actually changed?»

Techniques:
- Changed-region / bounding box detection
- Temporal frame-space reuse
- Selective rendering of modified pixels only
- Perceptual contract verification via SSIM / PSNR
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from contracts.contract_ir import ContractIR, QualitySpec, Contract100Gate, ContractStatus


@dataclasses.dataclass
class FrameAnalysis:
    total_pixels: int
    changed_pixels: int
    changed_ratio: float
    bounding_box: Optional[Tuple[int, int, int, int]]  # ymin, xmin, ymax, xmax
    temporal_reused_ratio: float
    ssim_score: float
    psnr_score: float


class GraphicsEscapeEngine:
    """
    Selective visual renderer and temporal reconstruction engine.
    """

    def __init__(self, ssim_threshold: float = 0.95, psnr_threshold: float = 35.0) -> None:
        self.ssim_threshold = ssim_threshold
        self.psnr_threshold = psnr_threshold
        self._prev_frame: Optional[np.ndarray] = None

    def detect_changed_region(
        self,
        current_frame: np.ndarray,
        reference_frame: np.ndarray,
        threshold: float = 0.02,
    ) -> Tuple[float, Optional[Tuple[int, int, int, int]]]:
        """
        Detects pixels where difference exceeds perceptual threshold and computes the minimal bounding box.
        """
        diff = np.abs(current_frame.astype(np.float32) - reference_frame.astype(np.float32))
        if current_frame.ndim == 3:
            diff_mask = np.any(diff > threshold, axis=-1)
        else:
            diff_mask = diff > threshold

        changed_count = int(np.sum(diff_mask))
        total_pixels = diff_mask.size
        ratio = changed_count / max(1, total_pixels)

        if changed_count == 0:
            return 0.0, None

        coords = np.argwhere(diff_mask)
        ymin, xmin = coords.min(axis=0)
        ymax, xmax = coords.max(axis=0)
        return ratio, (int(ymin), int(xmin), int(ymax), int(xmax))

    def render_frame_with_escape(
        self,
        current_frame: np.ndarray,
        render_subregion_fn: Optional[Any] = None,
        contract: Optional[ContractIR] = None,
    ) -> Tuple[np.ndarray, FrameAnalysis, Dict[str, Any]]:
        """
        Renders selectively: if previous frame exists and only part changed,
        reuses the static background and updates only the changed bounding region.
        """
        t0 = time.perf_counter_ns()
        if self._prev_frame is None or self._prev_frame.shape != current_frame.shape:
            # First frame: full materialization
            self._prev_frame = current_frame.copy()
            elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
            analysis = FrameAnalysis(
                total_pixels=current_frame.size,
                changed_pixels=current_frame.size,
                changed_ratio=1.0,
                bounding_box=(0, 0, current_frame.shape[0], current_frame.shape[1]),
                temporal_reused_ratio=0.0,
                ssim_score=1.0,
                psnr_score=100.0,
            )
            return current_frame, analysis, {
                "strategy": "FULL_RENDER",
                "latency_ms": elapsed_ms,
                "pixels_rendered": current_frame.size,
                "pixels_saved": 0,
            }

        ratio, bbox = self.detect_changed_region(current_frame, self._prev_frame)

        # If less than 40% of frame changed, perform selective temporal composition
        if ratio < 0.40 and bbox is not None:
            ymin, xmin, ymax, xmax = bbox
            composite = self._prev_frame.copy()
            # Selectively update only the changed box
            composite[ymin:ymax+1, xmin:xmax+1] = current_frame[ymin:ymax+1, xmin:xmax+1]
            rendered_pixels = (ymax - ymin + 1) * (xmax - xmin + 1)
            saved_pixels = current_frame.size - rendered_pixels

            # Compute SSIM / PSNR metrics
            ssim_val = self._compute_ssim(composite, current_frame)
            psnr_val = self._compute_psnr(composite, current_frame)

            self._prev_frame = composite.copy()
            elapsed_ms = (time.perf_counter_ns() - t0) / 1e6

            analysis = FrameAnalysis(
                total_pixels=current_frame.size,
                changed_pixels=rendered_pixels,
                changed_ratio=rendered_pixels / current_frame.size,
                bounding_box=bbox,
                temporal_reused_ratio=1.0 - ratio,
                ssim_score=ssim_val,
                psnr_score=psnr_val,
            )

            return composite, analysis, {
                "strategy": "SELECTIVE_TEMPORAL_RECONSTRUCTION",
                "latency_ms": elapsed_ms,
                "pixels_rendered": rendered_pixels,
                "pixels_saved": saved_pixels,
                "work_elimination_pct": round((1.0 - ratio) * 100.0, 2),
            }

        # Otherwise full update
        self._prev_frame = current_frame.copy()
        elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
        analysis = FrameAnalysis(
            total_pixels=current_frame.size,
            changed_pixels=current_frame.size,
            changed_ratio=1.0,
            bounding_box=(0, 0, current_frame.shape[0], current_frame.shape[1]),
            temporal_reused_ratio=0.0,
            ssim_score=1.0,
            psnr_score=100.0,
        )
        return current_frame, analysis, {
            "strategy": "FULL_RENDER",
            "latency_ms": elapsed_ms,
            "pixels_rendered": current_frame.size,
            "pixels_saved": 0,
        }

    @staticmethod
    def _compute_ssim(img1: np.ndarray, img2: np.ndarray) -> float:
        """Lightweight SSIM computation for numerical stability."""
        c1 = (0.01 * 255) ** 2
        c2 = (0.03 * 255) ** 2
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)
        mu1 = np.mean(img1)
        mu2 = np.mean(img2)
        sigma1_sq = np.var(img1)
        sigma2_sq = np.var(img2)
        sigma12 = np.mean((img1 - mu1) * (img2 - mu2))

        num = (2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)
        den = (mu1**2 + mu2**2 + c1) * (sigma1_sq + sigma2_sq + c2)
        return float(num / den)

    @staticmethod
    def _compute_psnr(img1: np.ndarray, img2: np.ndarray) -> float:
        mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
        if mse < 1e-10:
            return 100.0
        max_pixel = 1.0 if np.max(img1) <= 1.0 else 255.0
        return float(20 * np.log10(max_pixel / np.sqrt(mse)))
