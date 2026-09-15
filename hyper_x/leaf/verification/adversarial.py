"""
hyper_x/leaf/verification/adversarial.py
========================================
Adversarial and Anti-Structure Falsification Suite for LEAF.

Rules (Phase 15):
- Claim LOW_RANK        -> Attack with FULL_RANK white noise.
- Claim SPARSITY        -> Attack with UNIFORM DENSE matrices.
- Claim TEMPORAL_REUSE  -> Attack with RANDOMIZED frames.
- Claim SYMBOLIC_REDUCTION -> Attack with ARBITRARY non-affine parameters.
- Claim CACHED          -> Attack with NON-REPEATING entropy streams.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class AdversarialAuditOutcome:
    attack_type: str
    shortcut_detected: bool
    fallback_successfully_triggered: bool
    error_without_fallback: float
    is_resilient: bool
    verdict: str


class AntiStructureFalsifier:
    """Attacks candidate escape algorithms with worst-case adversarial inputs."""

    def attack_low_rank(
        self,
        candidate_fn: Callable[[np.ndarray], np.ndarray],
        dim: int = 64,
        tolerance: float = 1e-4,
    ) -> AdversarialAuditOutcome:
        """Attacks low-rank shortcut with full-rank i.i.d. Gaussian white noise."""
        full_rank_noise = np.random.randn(dim, dim).astype(np.float32)
        ref_norm = np.linalg.norm(full_rank_noise)

        out = candidate_fn(full_rank_noise)
        err = float(np.linalg.norm(out - full_rank_noise) / max(1e-12, ref_norm))

        resilient = err <= tolerance
        return AdversarialAuditOutcome(
            attack_type="FULL_RANK_WHITE_NOISE",
            shortcut_detected=(err > tolerance),
            fallback_successfully_triggered=resilient,
            error_without_fallback=err,
            is_resilient=resilient,
            verdict="PASSED_ADVERSARIAL_STRESS" if resilient else "FAILED_SHORTCUT_EXPOSED",
        )

    def attack_sparsity(
        self,
        candidate_fn: Callable[[np.ndarray], np.ndarray],
        dim: int = 64,
        tolerance: float = 1e-4,
    ) -> AdversarialAuditOutcome:
        """Attacks sparse solver with 100% dense non-zero matrix."""
        dense_matrix = np.random.uniform(0.5, 1.5, (dim, dim)).astype(np.float32)
        out = candidate_fn(dense_matrix)
        err = float(np.max(np.abs(out - dense_matrix)))

        resilient = err <= tolerance
        return AdversarialAuditOutcome(
            attack_type="UNIFORM_DENSE_MATRIX",
            shortcut_detected=(err > tolerance),
            fallback_successfully_triggered=resilient,
            error_without_fallback=err,
            is_resilient=resilient,
            verdict="PASSED_DENSE_ATTACK" if resilient else "FAILED_DENSE_ATTACK",
        )
