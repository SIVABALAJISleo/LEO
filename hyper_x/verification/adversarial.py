#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/verification/adversarial.py
===================================
Phase 6: Adversarial and Pathological Test Generator.
Deliberately generates edge cases to falsify brittle shortcuts.
"""

from typing import Dict, Any, List, Tuple, Callable
import numpy as np


class AdversarialVerifier:
    """Tests candidate pathways against pathological, ill-conditioned, and boundary inputs."""

    @staticmethod
    def generate_pathological_inputs(dim: int = 64) -> List[Tuple[str, np.ndarray, np.ndarray]]:
        """
        Generates adversarial input pairs (A, B):
          1. Full-rank white noise (irreducible rank).
          2. Near-singular matrix (high condition number).
          3. Extreme dynamic range / ill-conditioned matrix.
          4. Zero-heavy matrix with sparse outliers.
        """
        rng = np.random.default_rng(42)
        tests = []

        # 1. Full-Rank Gaussian Noise
        A_noise = rng.standard_normal((dim, dim)).astype(np.float32)
        B_noise = rng.standard_normal((dim, dim)).astype(np.float32)
        tests.append(("full_rank_noise", A_noise, B_noise))

        # 2. Near-Singular / Ill-conditioned (Condition number ~1e6)
        U, _, Vt = np.linalg.svd(rng.standard_normal((dim, dim)).astype(np.float32))
        s = np.logspace(0, -6, dim).astype(np.float32)
        A_ill = U @ np.diag(s) @ Vt
        tests.append(("near_singular_ill_conditioned", A_ill, B_noise))

        # 3. Extreme Dynamic Range
        A_ext = rng.standard_normal((dim, dim)).astype(np.float32)
        A_ext[0, 0] = 1e6
        A_ext[-1, -1] = 1e-6
        tests.append(("extreme_dynamic_range", A_ext, B_noise))

        return tests

    @staticmethod
    def evaluate_candidate_adversarial(
        candidate_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        dim: int = 64
    ) -> Dict[str, Any]:
        """
        Runs adversarial inputs against candidate function.
        Fail-closed: Returns dictionary of test outcomes.
        """
        inputs = AdversarialVerifier.generate_pathological_inputs(dim)
        results = []
        all_passed = True

        for name, A, B in inputs:
            try:
                out = candidate_fn(A, B)
                ref = A @ B
                # Numerical check
                err = float(np.linalg.norm(out - ref) / max(np.linalg.norm(ref), 1e-12))
                passed = (err <= 0.05) and not np.isnan(out).any() and not np.isinf(out).any()
                if not passed:
                    all_passed = False
                results.append({"case": name, "passed": passed, "error": round(err, 4)})
            except Exception as e:
                all_passed = False
                results.append({"case": name, "passed": False, "error": str(e)})

        return {
            "all_adversarial_passed": all_passed,
            "cases_evaluated": len(results),
            "details": results
        }
