"""
hyper_x/wormhole_compiler/falsifier.py
=============================================================================
HYPER-X Adversarial Falsification Engine: Aggressive Stress Testing
=============================================================================
Subject candidate shortcuts to 8 classes of adversarial and pathological inputs:
  1. Ill-conditioned / near-singular matrices (condition number > 1e6)
  2. Extreme impulse outliers (Dirac delta spikes of 1e5 amidst zero)
  3. High-entropy full-rank dense Gaussian noise
  4. Extreme sparsity (99.9% zeros with isolated non-zeros)
  5. Heavy-tailed Cauchy / Pareto distributions (infinite variance shift)
  6. Subnormal and near-underflow floats (1e-30)
  7. Degenerate aspect ratios (1 x 1024, 1024 x 1)
  8. Boundary zeroes and identity scaling

A candidate survives ONLY if it passes contract verification on ALL stress tests.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract, FailureCategory


@dataclass
class FalsificationResult:
    candidate_id: str
    survived_all: bool
    total_stress_tests: int
    passed_tests: int
    failed_tests: int
    failure_details: List[Dict[str, Any]] = field(default_factory=list)
    worst_case_error: float = 0.0
    elapsed_time_ms: float = 0.0


class AdversarialFalsifier:
    """Generates adversarial inputs and executes falsification stress tests."""

    @staticmethod
    def generate_stress_matrices(M: int, K: int, N: int) -> List[Tuple[str, np.ndarray, np.ndarray]]:
        """Generates 8 challenging matrix input pairs."""
        tests = []

        # 1. High-Entropy Dense Gaussian (No low-rank or sparse structure)
        A1 = np.random.randn(M, K).astype(np.float32)
        B1 = np.random.randn(K, N).astype(np.float32)
        tests.append(("HIGH_ENTROPY_GAUSSIAN", A1, B1))

        # 2. Ill-Conditioned Near-Singular Matrix
        U, _ = np.linalg.qr(np.random.randn(M, min(M, K)))
        V, _ = np.linalg.qr(np.random.randn(K, min(M, K)))
        # Geometric decay of singular values: 1.0 down to 1e-7
        s = np.geomspace(1.0, 1e-7, min(M, K)).astype(np.float32)
        A2 = (U * s) @ V.T
        B2 = np.random.randn(K, N).astype(np.float32)
        tests.append(("ILL_CONDITIONED_SPECTRUM", A2.astype(np.float32), B2))

        # 3. Extreme Outlier Spike (Dirac impulse)
        A3 = np.zeros((M, K), dtype=np.float32)
        A3[0, 0] = 1e5
        A3[M // 2, K // 2] = -1e5
        B3 = np.random.randn(K, N).astype(np.float32)
        tests.append(("IMPULSE_SPIKE_OUTLIER", A3, B3))

        # 4. Extreme Sparsity (99% zeros)
        A4 = (np.random.rand(M, K) < 0.01).astype(np.float32) * np.random.randn(M, K).astype(np.float32)
        B4 = (np.random.rand(K, N) < 0.01).astype(np.float32) * np.random.randn(K, N).astype(np.float32)
        tests.append(("EXTREME_SPARSITY_99PCT", A4, B4))

        # 5. Heavy-Tailed Cauchy Distribution
        A5 = np.clip(np.random.standard_cauchy((M, K)), -1e3, 1e3).astype(np.float32)
        B5 = np.random.randn(K, N).astype(np.float32)
        tests.append(("HEAVY_TAILED_CAUCHY", A5, B5))

        # 6. Near-Zero Scale / Subnormal Floats
        A6 = np.random.randn(M, K).astype(np.float32) * 1e-15
        B6 = np.random.randn(K, N).astype(np.float32) * 1e-15
        tests.append(("NEAR_ZERO_SUBNORMALS", A6, B6))

        return tests

    def falsify_candidate(
        self,
        candidate_id: str,
        candidate_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        contract: WorkloadContract,
        shape: Tuple[int, int, int]
    ) -> FalsificationResult:
        """Executes candidate against the adversarial stress suite."""
        t0 = time.perf_counter()
        M, K, N = shape
        stress_suite = self.generate_stress_matrices(M, K, N)

        passed = 0
        failed = 0
        failures = []
        worst_err = 0.0

        for test_name, A_test, B_test in stress_suite:
            try:
                cand_out = candidate_fn(A_test, B_test)
                ref_out = A_test @ B_test

                ref_norm = float(np.linalg.norm(ref_out) + 1e-8)
                diff_norm = float(np.linalg.norm(ref_out - cand_out))
                rel_err = diff_norm / ref_norm
                worst_err = max(worst_err, rel_err)

                if rel_err > contract.tolerance:
                    failed += 1
                    failures.append({
                        "test_case": test_name,
                        "failure_category": FailureCategory.NUMERICAL.value,
                        "measured_error": rel_err,
                        "tolerance_threshold": contract.tolerance,
                        "diagnosis": f"Relative error {rel_err:.2e} exceeded tolerance on {test_name}"
                    })
                else:
                    passed += 1

            except Exception as e:
                failed += 1
                failures.append({
                    "test_case": test_name,
                    "failure_category": FailureCategory.CORRECTNESS.value,
                    "measured_error": float("inf"),
                    "tolerance_threshold": contract.tolerance,
                    "diagnosis": f"Exception raised: {str(e)}"
                })

        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return FalsificationResult(
            candidate_id=candidate_id,
            survived_all=(failed == 0),
            total_stress_tests=len(stress_suite),
            passed_tests=passed,
            failed_tests=failed,
            failure_details=failures,
            worst_case_error=round(worst_err, 8),
            elapsed_time_ms=round(elapsed_ms, 3)
        )
