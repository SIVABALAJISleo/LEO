#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/verification/holdout.py
===============================
Phase 6: Blind Holdout Evaluator.
Evaluates candidates against frozen unseen evaluation sets to prevent benchmark gaming.
"""

from typing import Dict, Any, Callable
import numpy as np


class BlindHoldoutVerifier:
    """Evaluates candidate performance on frozen unseen distributions."""

    def __init__(self, seed: int = 9999):
        self.seed = seed

    def evaluate_holdout(
        self,
        candidate_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
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

        all_passed = (passed_count == num_samples)
        return {
            "holdout_passed": all_passed,
            "samples_tested": num_samples,
            "passed_samples": passed_count,
            "mean_holdout_error": round(float(np.mean(errors)), 4) if errors else 0.0
        }
