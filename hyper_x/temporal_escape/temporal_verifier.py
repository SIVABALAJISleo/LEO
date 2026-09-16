#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/temporal_escape/temporal_verifier.py
============================================
Phase 9: Temporal State & Reprojection Verifier.
Validates that temporal reuse or reprojection meets contract fidelity bounds:
  - PSNR >= threshold (e.g. 35.0 dB)
  - SSIM >= threshold (e.g. 0.95)
  - Relative L2 drift <= threshold
Fail-closed by default.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class TemporalVerificationResult:
    passed: bool
    mse: float
    psnr_db: float
    ssim: float
    max_relative_error: float
    reason: str


class TemporalVerifier:
    """
    Verifies frame-to-frame and step-to-step temporal fidelity against reference.
    """

    def __init__(
        self,
        min_psnr_db: float = 35.0,
        min_ssim: float = 0.95,
        max_rel_error: float = 0.05,
    ):
        self.min_psnr_db = min_psnr_db
        self.min_ssim = min_ssim
        self.max_rel_error = max_rel_error

    def verify(
        self,
        reference_frame: np.ndarray,
        reconstructed_frame: np.ndarray,
    ) -> TemporalVerificationResult:
        """
        Calculates fidelity metrics with fail-closed default.
        """
        passed = False
        reason = "UNVERIFIED"

        ref = np.asarray(reference_frame, dtype=np.float64)
        rec = np.asarray(reconstructed_frame, dtype=np.float64)

        if ref.shape != rec.shape:
            return TemporalVerificationResult(
                passed=False,
                mse=float("inf"),
                psnr_db=0.0,
                ssim=0.0,
                max_relative_error=1.0,
                reason=f"Shape mismatch: {ref.shape} vs {rec.shape}",
            )

        mse = float(np.mean((ref - rec) ** 2))
        max_val = max(float(np.max(ref)), 1.0)

        if mse == 0.0:
            psnr = 99.99
            ssim = 1.0
            max_rel = 0.0
        else:
            psnr = float(20.0 * np.log10(max_val / np.sqrt(mse)))
            # Simplified SSIM estimate
            mu_x = float(np.mean(ref))
            mu_y = float(np.mean(rec))
            var_x = float(np.var(ref))
            var_y = float(np.var(rec))
            covar = float(np.mean((ref - mu_x) * (rec - mu_y)))
            c1 = (0.01 * max_val) ** 2
            c2 = (0.03 * max_val) ** 2
            ssim = float(((2 * mu_x * mu_y + c1) * (2 * covar + c2)) / ((mu_x**2 + mu_y**2 + c1) * (var_x + var_y + c2)))
            denom = np.abs(ref) + 1e-12
            max_rel = float(np.max(np.abs(ref - rec) / denom))

        if psnr >= self.min_psnr_db and ssim >= self.min_ssim and max_rel <= self.max_rel_error:
            passed = True
            reason = f"VERIFIED: PSNR={psnr:.2f}dB >= {self.min_psnr_db}dB, SSIM={ssim:.4f} >= {self.min_ssim}."
        else:
            passed = False
            reason = f"REJECTED: Fidelity violation (PSNR={psnr:.2f}dB, SSIM={ssim:.4f}, RelErr={max_rel:.4f})."

        return TemporalVerificationResult(
            passed=passed,
            mse=mse,
            psnr_db=round(psnr, 2),
            ssim=round(ssim, 4),
            max_relative_error=round(max_rel, 6),
            reason=reason,
        )
