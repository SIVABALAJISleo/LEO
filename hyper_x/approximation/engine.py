"""
hyper_x/approximation/engine.py
=============================================================================
HYPER-X Explicit Approximation Engine
=============================================================================
Every approximation must declare a formal mathematical contract:
  - epsilon:               Maximum allowed error bound
  - metric:                L1, L2, Linf, SSIM, PSNR, Perceptual
  - quality_threshold:     Acceptable floor
  - worst_case_behavior:   Guaranteed upper bound on error
  - average_behavior:      Empirical expectation
  - failure_conditions:    Edge cases where approximation is rejected

RULE: Never silently convert approximate parity into exact parity.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, Callable
import numpy as np

@dataclass
class ApproximationContract:
    technique_name: str
    epsilon: float
    metric: str  # L2_REL, LINF_ABS, SSIM, PSNR
    quality_threshold: float
    worst_case_bound: float
    average_bound: float
    failure_conditions: str

@dataclass
class ApproximationResult:
    technique: str
    output: Any
    measured_error: float
    quality_score: float
    worst_case_observed: float
    within_bounds: bool
    fallback_triggered: bool

class ApproximationEngine:
    """Executes and monitors approximate computational shortcuts."""

    def evaluate_quantization(
        self,
        reference_op: Callable[[], np.ndarray],
        quantized_op: Callable[[], np.ndarray],
        contract: ApproximationContract
    ) -> ApproximationResult:
        ref = reference_op()
        cand = quantized_op()

        diff = np.abs(ref - cand)
        worst_case = float(np.max(diff))
        if contract.metric == "L2_REL":
            err = float(np.linalg.norm(ref - cand) / (np.linalg.norm(ref) + 1e-9))
        elif contract.metric == "LINF_ABS":
            err = worst_case
        else:
            err = float(np.mean(diff))

        passed = err <= contract.epsilon and worst_case <= contract.worst_case_bound
        quality = max(0.0, 1.0 - err)

        return ApproximationResult(
            technique=contract.technique_name,
            output=cand if passed else ref,
            measured_error=err,
            quality_score=quality,
            worst_case_observed=worst_case,
            within_bounds=passed,
            fallback_triggered=not passed
        )
