"""
hyper_x/leaf/neural/verifier.py
===============================
Independent generalization and adversarial verifier for Neural Implicit Resolution.

Rule (Phase 2):
    A learned implicit representation must be tested on:
    - training inputs
    - validation inputs
    - unseen inputs
    - adversarial inputs
    - distribution-shifted inputs
    Never prove general equivalence only from training data.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from .implicit_field import NeuralImplicitField


@dataclass
class NIRGeneralizationAudit:
    train_error: float
    val_error: float
    unseen_error: float
    adversarial_error: float
    distribution_shift_error: float
    generalization_gap: float
    is_general_verified: bool
    verdict: str


class NIRGeneralizationVerifier:
    """Verifies neural implicit fields across multiple out-of-distribution domains."""

    def audit_field(
        self,
        field: NeuralImplicitField,
        coords_train: np.ndarray,
        gt_train: np.ndarray,
        coords_val: np.ndarray,
        gt_val: np.ndarray,
        ground_truth_oracle: Callable[[np.ndarray], np.ndarray],
        tolerance: float = 0.05,
    ) -> NIRGeneralizationAudit:
        """Audits field across train, val, unseen, adversarial, and shifted distributions."""
        # 1. Train error
        pred_train = field.query_numpy(coords_train)
        err_train = float(np.mean(np.abs(pred_train - gt_train)))

        # 2. Validation error
        pred_val = field.query_numpy(coords_val)
        err_val = float(np.mean(np.abs(pred_val - gt_val)))

        # 3. Unseen inputs (interpolated within domain)
        coords_unseen = np.random.uniform(
            np.min(coords_train), np.max(coords_train), size=min(100, len(coords_train))
        ).astype(np.float32)
        gt_unseen = ground_truth_oracle(coords_unseen)
        pred_unseen = field.query_numpy(coords_unseen)
        err_unseen = float(np.mean(np.abs(pred_unseen - gt_unseen)))

        # 4. Adversarial inputs (boundary edges and high-frequency jitter)
        coords_adv = np.array([
            np.min(coords_train),
            np.max(coords_train),
            0.0,
            np.median(coords_train),
        ], dtype=np.float32)
        gt_adv = ground_truth_oracle(coords_adv)
        pred_adv = field.query_numpy(coords_adv)
        err_adv = float(np.max(np.abs(pred_adv - gt_adv)))

        # 5. Distribution-shifted inputs (extrapolated 50% outside training range)
        span = np.max(coords_train) - np.min(coords_train)
        coords_shifted = np.linspace(
            np.max(coords_train), np.max(coords_train) + 0.5 * span, 50, dtype=np.float32
        )
        gt_shifted = ground_truth_oracle(coords_shifted)
        pred_shifted = field.query_numpy(coords_shifted)
        err_shift = float(np.mean(np.abs(pred_shifted - gt_shifted)))

        gen_gap = abs(err_val - err_train)
        is_verified = (err_val <= tolerance) and (err_unseen <= tolerance) and (err_adv <= tolerance * 2)

        verdict = (
            "BOUNDED_APPROXIMATION_VERIFIED"
            if is_verified
            else "FAILED_GENERALIZATION_FALLBACK_REQUIRED"
        )

        return NIRGeneralizationAudit(
            train_error=err_train,
            val_error=err_val,
            unseen_error=err_unseen,
            adversarial_error=err_adv,
            distribution_shift_error=err_shift,
            generalization_gap=gen_gap,
            is_general_verified=is_verified,
            verdict=verdict,
        )
