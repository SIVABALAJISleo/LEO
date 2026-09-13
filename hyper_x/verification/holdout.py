#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/verification/holdout.py
===============================
Phase 16: Blind Holdout Evaluator.

Separates discovery data from blind evaluation data.
Reports:
  - discovery_performance
  - holdout_performance
  - generalization_gap
Strict Rule: A zero generalization gap is never hard-coded.
"""

from typing import Dict, Any, Callable, Optional
import numpy as np


class BlindHoldoutVerifier:
    """Evaluates candidate performance on frozen unseen distributions."""

    def __init__(self, seed: int = 9999):
        self.seed = seed

    def evaluate_holdout(
        self,
        candidate_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        discovery_error: Optional[float] = None,
        num_samples: int = 5,
        dim: int = 64,
        tolerance: float = 0.05
    ) -> Dict[str, Any]:
        rng = np.random.default_rng(self.seed)
        passed_count = 0
        errors = []

        for _ in range(num_samples):
            A = rng.standard_normal((dim, dim)).astype(np.float32)
            B = rng.standard_normal((dim, dim)).astype(np.float32)

            out = candidate_fn(A, B)
            ref = A @ B

            err = float(np.linalg.norm(out - ref) / max(np.linalg.norm(ref), 1e-12))
            errors.append(err)
            if err <= tolerance and not np.isnan(out).any():
                passed_count += 1

        mean_holdout_err = float(np.mean(errors)) if errors else 0.0
        all_passed = (passed_count == num_samples)

        # Empirical generalization gap = |holdout_error - discovery_error|
        disc_err = discovery_error if discovery_error is not None else 0.001
        gen_gap = abs(mean_holdout_err - disc_err)

        return {
            "holdout_passed": all_passed,
            "samples_tested": num_samples,
            "passed_samples": passed_count,
            "discovery_error": round(disc_err, 6),
            "holdout_error": round(mean_holdout_err, 6),
            "generalization_gap": round(gen_gap, 6),
            "mean_holdout_error": round(mean_holdout_err, 6)
        }
