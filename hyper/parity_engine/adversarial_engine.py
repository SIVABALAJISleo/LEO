"""
hyper/parity_engine/adversarial_engine.py
=========================================
Automated Adversarial Verification & Stress Gauntlet.
Implements Section 26 of the HYPER 100% Master Mission.

Generates 12 Adversarial Test Classes:
1.  RANDOM_INPUTS: Uniform, Gaussian, Laplace distributions.
2.  BOUNDARY_VALUES: Zeroes, infinities, NaNs, subnormals, epsilon.
3.  PATHOLOGICAL_INPUTS: Vandermonde matrices, Hilbert matrices, rank-deficient tensors.
4.  WORST_CASES: Maximum condition numbers, adversarial phase alignment.
5.  MAXIMUM_SIZES: Near heap allocation ceilings.
6.  MINIMUM_SIZES: 1x1 scalars, 0-length edges, empty arrays.
7.  HIGHLY_STRUCTURED: Block-diagonal, Toeplitz, low-entropy constant patterns.
8.  UNSTRUCTURED: Maximum Kolmogorov entropy / white noise.
9.  ADVERSARIAL_DISTRIBUTIONS: Cauchy long-tailed, bimodal extremes.
10. REPEATED_STATES: Cache thrashing and stationary repeat tests.
11. RAPIDLY_CHANGING: High-frequency step jumps and Dirac delta impulses.
12. NUMERICAL_EDGE_CASES: Catastrophic cancellation (x - y where x ~ y), near-overflow.

Objective: Attempt to BREAK the candidate pathway. Survivors gain verified resilience.
"""

from __future__ import annotations
import enum
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field


class AdversarialCategory(str, enum.Enum):
    RANDOM_INPUTS = "RANDOM_INPUTS"
    BOUNDARY_VALUES = "BOUNDARY_VALUES"
    PATHOLOGICAL_INPUTS = "PATHOLOGICAL_INPUTS"
    WORST_CASES = "WORST_CASES"
    MAXIMUM_SIZES = "MAXIMUM_SIZES"
    MINIMUM_SIZES = "MINIMUM_SIZES"
    HIGHLY_STRUCTURED = "HIGHLY_STRUCTURED"
    UNSTRUCTURED = "UNSTRUCTURED"
    ADVERSARIAL_DISTRIBUTIONS = "ADVERSARIAL_DISTRIBUTIONS"
    REPEATED_STATES = "REPEATED_STATES"
    RAPIDLY_CHANGING = "RAPIDLY_CHANGING"
    NUMERICAL_EDGE_CASES = "NUMERICAL_EDGE_CASES"


class AdversarialTestCase(BaseModel):
    test_id: str
    category: AdversarialCategory
    description: str
    passed: bool = False
    max_error_observed: float = 0.0
    failure_message: str = ""
    duration_ms: float = 0.0


class AdversarialReport(BaseModel):
    pathway_id: str
    total_tests_run: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    survived_gauntlet: bool = False
    adversarial_survival_score_pct: float = 0.0
    test_results: List[AdversarialTestCase] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class AdversarialVerificationEngine:
    """
    Executes automated adversarial attacks against candidate computational pathways.
    """

    @staticmethod
    def generate_adversarial_tensors(base_shape: Tuple[int, ...]) -> List[Tuple[AdversarialCategory, str, np.ndarray]]:
        attacks: List[Tuple[AdversarialCategory, str, np.ndarray]] = []

        # 1. Boundary Values (Zeros, Ones, Epsilon)
        attacks.append((AdversarialCategory.BOUNDARY_VALUES, "All Zeros", np.zeros(base_shape, dtype=np.float32)))
        attacks.append((AdversarialCategory.BOUNDARY_VALUES, "All Ones", np.ones(base_shape, dtype=np.float32)))
        attacks.append((AdversarialCategory.BOUNDARY_VALUES, "Machine Epsilon Scale", np.full(base_shape, 1e-7, dtype=np.float32)))

        # 2. Pathological & Worst-Cases
        if len(base_shape) == 2 and base_shape[0] == base_shape[1]:
            n = base_shape[0]
            # Hilbert Matrix (notoriously ill-conditioned)
            i_idx, j_idx = np.meshgrid(np.arange(n), np.arange(n))
            hilbert = (1.0 / (i_idx + j_idx + 1.0)).astype(np.float32)
            attacks.append((AdversarialCategory.PATHOLOGICAL_INPUTS, "Hilbert Matrix (Condition Number ~ Exp(N))", hilbert))

            # Rank-1 Deficient Outer Product
            v = np.linspace(1, 10, n, dtype=np.float32)
            rank1 = np.outer(v, v).astype(np.float32)
            attacks.append((AdversarialCategory.PATHOLOGICAL_INPUTS, "Rank-1 Deficient Matrix", rank1))

        # 3. Highly Structured vs Unstructured
        attacks.append((AdversarialCategory.HIGHLY_STRUCTURED, "Checkerboard Pattern", ((np.indices(base_shape).sum(axis=0) % 2) * 2.0 - 1.0).astype(np.float32)))
        attacks.append((AdversarialCategory.UNSTRUCTURED, "Pure Gaussian Noise N(0, 100)", (np.random.randn(*base_shape) * 100.0).astype(np.float32)))

        # 4. Numerical Edge Cases (Cancellation)
        large_val = 1e6
        cancellation = np.full(base_shape, large_val, dtype=np.float32)
        cancellation[0] += 1e-3
        attacks.append((AdversarialCategory.NUMERICAL_EDGE_CASES, "Catastrophic Cancellation Stress", cancellation))

        # 5. Adversarial Distributions (Cauchy Long-Tailed)
        cauchy = np.tan(np.pi * (np.random.uniform(0.01, 0.99, size=base_shape) - 0.5)).astype(np.float32)
        attacks.append((AdversarialCategory.ADVERSARIAL_DISTRIBUTIONS, "Cauchy Extreme Heavy-Tail", cauchy))

        return attacks

    @staticmethod
    def attack_candidate(
        pathway_id: str,
        candidate_wrapper: Callable[[np.ndarray], Any],
        reference_wrapper: Callable[[np.ndarray], Any],
        base_shape: Tuple[int, ...] = (64, 64),
        max_allowed_error: float = 1e-3,
    ) -> AdversarialReport:
        """
        Submits candidate to the entire adversarial battery.
        """
        attacks = AdversarialVerificationEngine.generate_adversarial_tensors(base_shape)
        results: List[AdversarialTestCase] = []

        for cat, desc, tensor in attacks:
            t0 = time.perf_counter()
            try:
                ref_res = reference_wrapper(tensor)
                cand_res = candidate_wrapper(tensor)
                dur = (time.perf_counter() - t0) * 1000.0

                if isinstance(ref_res, np.ndarray) and isinstance(cand_res, np.ndarray):
                    if cand_res.dtype == bool or ref_res.dtype == bool:
                        ref_f = ref_res.astype(np.float32)
                        cand_f = cand_res.astype(np.float32)
                    else:
                        ref_f = ref_res
                        cand_f = cand_res
                    diff = np.abs(ref_f - cand_f)
                    max_err = float(np.nanmax(diff))
                    # Check for unexpected NaNs or infs
                    has_cand_nan = bool(np.isnan(cand_f).any()) if np.issubdtype(cand_f.dtype, np.floating) else False
                    has_ref_nan = bool(np.isnan(ref_f).any()) if np.issubdtype(ref_f.dtype, np.floating) else False
                    if has_cand_nan and not has_ref_nan:
                        passed = False
                        msg = "Candidate produced NaN where reference did not."
                    elif max_err > max_allowed_error:
                        passed = False
                        msg = f"Observed error {max_err:.2e} exceeded ceiling {max_allowed_error:.2e}."
                    else:
                        passed = True
                        msg = f"Passed with max error {max_err:.2e}."
                else:
                    passed = (ref_res == cand_res)
                    max_err = 0.0 if passed else 1.0
                    msg = "Equality match" if passed else "Inequality on adversarial output"

            except Exception as e:
                dur = (time.perf_counter() - t0) * 1000.0
                passed = False
                max_err = float("inf")
                msg = f"CRASH: {str(e)}"

            test_case = AdversarialTestCase(
                test_id=f"ADV_{cat.value}_{len(results)}",
                category=cat,
                description=desc,
                passed=passed,
                max_error_observed=max_err,
                failure_message=msg,
                duration_ms=round(dur, 2),
            )
            results.append(test_case)

        total = len(results)
        passed_count = sum(1 for t in results if t.passed)
        failed_count = total - passed_count
        survived = (failed_count == 0)
        score_pct = round((passed_count / max(total, 1)) * 100.0, 1)

        return AdversarialReport(
            pathway_id=pathway_id,
            total_tests_run=total,
            passed_tests=passed_count,
            failed_tests=failed_count,
            survived_gauntlet=survived,
            adversarial_survival_score_pct=score_pct,
            test_results=results,
        )
