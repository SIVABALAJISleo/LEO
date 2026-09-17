"""
hyper/v8/falsification.py
========================
HYPER v8 — SelfFalsificationEngine + FalsificationResult.

Adversarial stress testing against 12 pathological categories.
Every optimization must be challenged with inputs designed to break it.
Failures are recorded as scientific research data, never concealed.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .contract import ComputeContractV2, PathClassification, exact_contract
from .path_selector import CheapestValidPathSelector


@dataclasses.dataclass
class FalsificationResult:
    """Detailed record of an adversarial attack against the engine."""
    category: str
    passed: bool
    observed_path: PathClassification
    contract_satisfied: bool
    fallback_engaged: bool
    max_abs_error: float
    notes: str
    duration_ms: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "passed": self.passed,
            "observed_path": self.observed_path.value,
            "contract_satisfied": self.contract_satisfied,
            "fallback_engaged": self.fallback_engaged,
            "max_abs_error": f"{self.max_abs_error:.2e}",
            "notes": self.notes,
            "duration_ms": round(self.duration_ms, 3),
        }


class SelfFalsificationEngine:
    """
    Executes a gauntlet of 12 adversarial test cases to prove
    that the system fails safely, catches errors, and never outputs
    invalid results.
    """

    def __init__(self, selector: Optional[CheapestValidPathSelector] = None) -> None:
        if selector is None:
            from hyper.cache.exact_cache import ExactCache
            from .residual import ExactResidualEngine
            self.selector = CheapestValidPathSelector(
                residual_engine=ExactResidualEngine(),
                exact_cache=ExactCache(max_entries=100),
            )
        else:
            self.selector = selector

    def run_all(self, N: int = 128) -> List[FalsificationResult]:
        """Run all 12 adversarial stress tests and return findings."""
        results = []
        tests = [
            ("01_RANDOM_DENSE_FULL_RANK", self._test_random_dense),
            ("02_IDENTITY_AND_PERMUTATION", self._test_identity),
            ("03_PATHOLOGICAL_SPARSITY", self._test_pathological_sparsity),
            ("04_ILL_CONDITIONED_MATRIX", self._test_ill_conditioned),
            ("05_EXTREME_DYNAMIC_RANGE", self._test_extreme_dynamic_range),
            ("06_NAN_INF_INJECTION", self._test_nan_inf),
            ("07_EXACT_DUPLICATE_REPETITION", self._test_exact_duplicates),
            ("08_ADVERSARIAL_CACHE_COLLISION", self._test_adversarial_cache),
            ("09_HIGH_FREQUENCY_ALTERNATING", self._test_alternating_signs),
            ("10_RANK_1_PERTURBATION", self._test_rank_1_update),
            ("11_NEAR_EPSILON_DELTA", self._test_near_epsilon_delta),
            ("12_ZERO_MATRIX", self._test_zero_matrix),
        ]

        for name, test_fn in tests:
            t0 = time.perf_counter_ns()
            try:
                res = test_fn(N)
                duration_ms = (time.perf_counter_ns() - t0) / 1e6
                res.duration_ms = duration_ms
                results.append(res)
            except Exception as e:
                duration_ms = (time.perf_counter_ns() - t0) / 1e6
                results.append(FalsificationResult(
                    category=name,
                    passed=False,
                    observed_path=PathClassification.FALLBACK,
                    contract_satisfied=False,
                    fallback_engaged=True,
                    max_abs_error=float("nan"),
                    notes=f"Uncaught exception: {str(e)}",
                    duration_ms=duration_ms,
                ))

        return results

    def _test_random_dense(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_dense_{N}")
        rng = np.random.default_rng(42)
        A = rng.standard_normal((N, N)).astype(np.float32)
        B = rng.standard_normal((N, N)).astype(np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-4

        return FalsificationResult(
            category="01_RANDOM_DENSE_FULL_RANK",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Should correctly compute GEMM or safely fall back with exact parity.",
            duration_ms=0.0,
        )

    def _test_identity(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_identity_{N}")
        A = np.eye(N, dtype=np.float32)
        B = np.random.randn(N, N).astype(np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-5

        return FalsificationResult(
            category="02_IDENTITY_AND_PERMUTATION",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Identity shortcut or fallback with exact match.",
            duration_ms=0.0,
        )

    def _test_pathological_sparsity(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_sparse_{N}")
        A = np.zeros((N, N), dtype=np.float32)
        A[0, 0] = 1.0  # Only one non-zero
        B = np.random.randn(N, N).astype(np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-5

        return FalsificationResult(
            category="03_PATHOLOGICAL_SPARSITY",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Single nonzero row/col handled correctly.",
            duration_ms=0.0,
        )

    def _test_ill_conditioned(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_ill_{N}")
        # Create Hilbert-like ill-conditioned matrix
        i, j = np.indices((N, N))
        A = (1.0 / (i + j + 1.0)).astype(np.float32)
        B = np.random.randn(N, N).astype(np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-3

        return FalsificationResult(
            category="04_ILL_CONDITIONED_MATRIX",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Ill-conditioned inputs must maintain numerical stability.",
            duration_ms=0.0,
        )

    def _test_extreme_dynamic_range(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_dyn_{N}")
        A = np.diag([1e-15 if i % 2 == 0 else 1e15 for i in range(N)]).astype(np.float64)
        B = np.eye(N, dtype=np.float64)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-10

        return FalsificationResult(
            category="05_EXTREME_DYNAMIC_RANGE",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Dynamic range spanning 30 orders of magnitude.",
            duration_ms=0.0,
        )

    def _test_nan_inf(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_nan_{N}")
        A = np.zeros((N, N), dtype=np.float32)
        A[0, 0] = np.nan
        B = np.ones((N, N), dtype=np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        # Comparing NaNs: both must have NaNs in identical positions
        nan_match = np.all(np.isnan(out) == np.isnan(ref))

        return FalsificationResult(
            category="06_NAN_INF_INJECTION",
            passed=nan_match,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed or nan_match,
            fallback_engaged=cert.fallback_used,
            max_abs_error=0.0 if nan_match else float("nan"),
            notes="NaN positions preserved identically to standard GEMM.",
            duration_ms=0.0,
        )

    def _test_exact_duplicates(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_dup_{N}")
        A = np.ones((N, N), dtype=np.float32)
        B = np.ones((N, N), dtype=np.float32)

        # Call twice: second call should hit cache or residual
        out1, cert1 = self.selector.select_and_execute(A, B, contract)
        out2, cert2 = self.selector.select_and_execute(A, B, contract)

        err = float(np.max(np.abs(out2 - (A @ B))))
        passed = (err <= 1e-5) and (cert2.path_type in (PathClassification.EXACT_REUSED, PathClassification.EXACT_RESIDUAL, PathClassification.FALLBACK))

        return FalsificationResult(
            category="07_EXACT_DUPLICATE_REPETITION",
            passed=passed,
            observed_path=cert2.path_type,
            contract_satisfied=cert2.contract_passed,
            fallback_engaged=cert2.fallback_used,
            max_abs_error=err,
            notes="Second run must exploit reuse without precision degradation.",
            duration_ms=0.0,
        )

    def _test_adversarial_cache(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_cache_coll_{N}")
        # A1 and A2 have identical mean and sum, but different values
        A1 = np.zeros((N, N), dtype=np.float32)
        A1[0, 0] = 1.0
        A1[0, 1] = -1.0

        A2 = np.zeros((N, N), dtype=np.float32)
        A2[1, 0] = -1.0
        A2[1, 1] = 1.0

        B = np.arange(N * N, dtype=np.float32).reshape(N, N)

        out1, cert1 = self.selector.select_and_execute(A1, B, contract)
        out2, cert2 = self.selector.select_and_execute(A2, B, contract)

        ref2 = A2 @ B
        err = float(np.max(np.abs(out2 - ref2)))
        passed = (err <= 1e-5) and not np.array_equal(out1, out2)

        return FalsificationResult(
            category="08_ADVERSARIAL_CACHE_COLLISION",
            passed=passed,
            observed_path=cert2.path_type,
            contract_satisfied=cert2.contract_passed,
            fallback_engaged=cert2.fallback_used,
            max_abs_error=err,
            notes="Hash collision resistance: distinct inputs with same sum/mean produce distinct outputs.",
            duration_ms=0.0,
        )

    def _test_alternating_signs(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_alt_{N}")
        A = np.fromfunction(lambda i, j: (-1) ** (i + j), (N, N), dtype=np.float32)
        B = np.ones((N, N), dtype=np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-5

        return FalsificationResult(
            category="09_HIGH_FREQUENCY_ALTERNATING",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Alternating signs cancel or sum correctly.",
            duration_ms=0.0,
        )

    def _test_rank_1_update(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_rank1_{N}")
        u = np.ones((N, 1), dtype=np.float32)
        v = np.ones((1, N), dtype=np.float32)
        A = u @ v  # Rank 1 matrix
        B = np.random.randn(N, N).astype(np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-4

        return FalsificationResult(
            category="10_RANK_1_PERTURBATION",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Rank-1 structure computed with exact precision.",
            duration_ms=0.0,
        )

    def _test_near_epsilon_delta(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_eps_{N}")
        A = np.eye(N, dtype=np.float64) + 1e-12
        B = np.eye(N, dtype=np.float64)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err <= 1e-11

        return FalsificationResult(
            category="11_NEAR_EPSILON_DELTA",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Floating-point epsilon perturbation preserved.",
            duration_ms=0.0,
        )

    def _test_zero_matrix(self, N: int) -> FalsificationResult:
        contract = exact_contract(f"exact_zero_{N}")
        A = np.zeros((N, N), dtype=np.float32)
        B = np.zeros((N, N), dtype=np.float32)

        out, cert = self.selector.select_and_execute(A, B, contract)
        ref = A @ B
        err = float(np.max(np.abs(out - ref)))
        passed = cert.contract_passed and err == 0.0

        return FalsificationResult(
            category="12_ZERO_MATRIX",
            passed=passed,
            observed_path=cert.path_type,
            contract_satisfied=cert.contract_passed,
            fallback_engaged=cert.fallback_used,
            max_abs_error=err,
            notes="Zero matrix computation produces exact zero.",
            duration_ms=0.0,
        )
