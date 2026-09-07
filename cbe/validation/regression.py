"""
cbe/validation/regression.py
=============================================================================
Regression Testing Suite for CBE Performance and Elimination Ratios
=============================================================================
Stores, tracks, and verifies that key metrics (CER, FPS, latency, SSIM) do not
regress across code changes.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class BaselineThresholds:
    min_cer_static: float = 0.85
    min_cer_low_motion: float = 0.50
    min_cer_high_motion: float = 0.20
    min_ssim: float = 0.88
    max_latency_p95_ms: float = 33.33  # Minimum 30 FPS under load


class RegressionAuditor:
    """
    Automated regression auditor ensuring CBE maintains its acceleration promises.
    """

    def __init__(self, thresholds: Optional[BaselineThresholds] = None):
        self.thresholds = thresholds if thresholds is not None else BaselineThresholds()

    def evaluate_run(
        self,
        cer_static: float,
        cer_low_motion: float,
        cer_high_motion: float,
        ssim: float,
        latency_p95_ms: float
    ) -> Dict[str, Any]:
        """
        Evaluates run metrics against declared regression baselines.
        """
        checks = {
            "cer_static_pass": cer_static >= self.thresholds.min_cer_static,
            "cer_low_motion_pass": cer_low_motion >= self.thresholds.min_cer_low_motion,
            "cer_high_motion_pass": cer_high_motion >= self.thresholds.min_cer_high_motion,
            "ssim_pass": ssim >= self.thresholds.min_ssim,
            "latency_p95_pass": latency_p95_ms <= self.thresholds.max_latency_p95_ms,
        }
        all_passed = all(checks.values())
        return {
            "passed": all_passed,
            "checks": checks,
            "metrics": {
                "cer_static": cer_static,
                "cer_low_motion": cer_low_motion,
                "cer_high_motion": cer_high_motion,
                "ssim": ssim,
                "latency_p95_ms": latency_p95_ms,
            },
            "thresholds": asdict(self.thresholds),
        }
