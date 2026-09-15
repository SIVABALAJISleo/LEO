"""
hyper_x/leaf/implicit/error_bound.py
====================================
Error bound validation for mathematical implicit representations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .field import ImplicitField


@dataclass
class RepresentationError:
    max_absolute_error: float
    relative_frobenius_error: float
    psnr_db: float
    is_exact: bool
    compression_ratio: float


class ErrorBoundVerifier:
    """Calculates rigorous numerical and perceptual error bounds."""

    def verify(
        self,
        field: ImplicitField,
        ground_truth: np.ndarray,
        sample_coordinates: np.ndarray,
    ) -> RepresentationError:
        predicted = field.query(sample_coordinates).reshape(ground_truth.shape)
        abs_diff = np.abs(predicted - ground_truth)
        max_abs = float(np.max(abs_diff))

        gt_norm = np.linalg.norm(ground_truth)
        diff_norm = np.linalg.norm(predicted - ground_truth)
        rel_frob = float(diff_norm / max(1e-12, gt_norm))

        mse = float(np.mean((predicted - ground_truth) ** 2))
        if mse < 1e-12:
            psnr = 100.0
        else:
            max_val = max(1.0, float(np.max(ground_truth)))
            psnr = float(20.0 * np.log10(max_val / np.sqrt(mse)))

        is_exact = max_abs < 1e-7

        gt_bytes = ground_truth.nbytes
        field_bytes = field.parameter_bytes
        comp_ratio = float(gt_bytes) / max(1, field_bytes)

        return RepresentationError(
            max_absolute_error=max_abs,
            relative_frobenius_error=rel_frob,
            psnr_db=psnr,
            is_exact=is_exact,
            compression_ratio=comp_ratio,
        )
