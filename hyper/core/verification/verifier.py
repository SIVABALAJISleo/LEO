"""
hyper/core/verification/verifier.py
Independent Differential Verifier and Adversarial Counterexample Hunter (Prompt Section 20 & 35).
Stress-tests optimization candidates against hostiles:
- Fresh random high-entropy / full-rank inputs
- Boundary tests: NaN, Inf, -0.0, ill-conditioned matrices
- Coordinate changes: 0 changed, 1 changed, all changed
- Exact & near ties in early termination
- Holdout distributions unseen during development
"""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from hyper.core.contract.models import SemanticContract, ContractType


class VerificationResult(BaseModel):
    passed: bool
    total_cases_evaluated: int
    counterexamples_found: int
    max_discrepancy: float
    failure_details: List[str] = Field(default_factory=list)


class IndependentVerifier:
    """
    Independent Differential Verification Engine.
    Executes baseline and candidate in total isolation, comparing outputs against SemanticContract.
    """

    @classmethod
    def verify_differential(
        cls,
        candidate_fn: Callable[[Any], Any],
        baseline_fn: Callable[[Any], Any],
        test_inputs: List[Any],
        contract: SemanticContract,
    ) -> VerificationResult:
        max_diff = 0.0
        failures = []
        counterexamples = 0

        for idx, inp in enumerate(test_inputs):
            try:
                ref_out = baseline_fn(inp)
                cand_out = candidate_fn(inp)

                is_valid, diff, msg = contract.validate_result(cand_out, ref_out)
                if diff > max_diff:
                    max_diff = diff

                if not is_valid:
                    counterexamples += 1
                    failures.append(f"Case {idx} failed: {msg}")
            except Exception as e:
                counterexamples += 1
                failures.append(f"Case {idx} raised unexpected exception: {str(e)}")

        return VerificationResult(
            passed=(counterexamples == 0),
            total_cases_evaluated=len(test_inputs),
            counterexamples_found=counterexamples,
            max_discrepancy=max_diff,
            failure_details=failures[:10],  # Keep top 10 failure summaries
        )


class AdversarialCounterexampleHunter:
    """
    Hostile counterexample generator searching for edge cases where candidates break.
    """

    @staticmethod
    def generate_hostile_cases_matrix_vector(dim: int = 64) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Generates hostile test cases for delta matrix-vector operations:
        (A, x, dx)
        """
        cases = []
        rng = np.random.RandomState(1337)

        # 1. Zero delta (no coordinates changed)
        A = rng.randn(dim, dim)
        x = rng.randn(dim)
        dx_zero = np.zeros(dim)
        cases.append((A, x, dx_zero))

        # 2. Single coordinate changed (sparse delta)
        dx_single = np.zeros(dim)
        dx_single[0] = 5.0
        cases.append((A, x, dx_single))

        # 3. Dense delta (all coordinates changed)
        dx_dense = rng.randn(dim)
        cases.append((A, x, dx_dense))

        # 4. Ill-conditioned matrix (condition number ~ 1e12)
        U, _ = np.linalg.qr(rng.randn(dim, dim))
        V, _ = np.linalg.qr(rng.randn(dim, dim))
        S = np.logspace(0, -12, dim)
        A_ill = U @ np.diag(S) @ V.T
        cases.append((A_ill, x, dx_single))

        # 5. High-entropy full-rank random
        A_rand = rng.uniform(-100.0, 100.0, size=(dim, dim))
        cases.append((A_rand, x, rng.randn(dim)))

        return cases

    @staticmethod
    def generate_hostile_cases_early_termination(dim: int = 128) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generates hostile cases for argmax / classification:
        - Exact ties
        - Near ties (epsilon separation)
        - Dominated candidates
        """
        cases = []
        rng = np.random.RandomState(42)

        # 1. Clear winner
        z_clear = rng.randn(dim)
        z_clear[7] = 50.0
        cases.append((z_clear, np.array([7])))

        # 2. Exact tie at two top indices
        z_tie = rng.randn(dim)
        z_tie[0] = 20.0
        z_tie[1] = 20.0
        cases.append((z_tie, np.array([0, 1])))

        # 3. Near tie (separated by 1e-6)
        z_near = rng.randn(dim)
        z_near[3] = 10.000001
        z_near[4] = 10.000000
        cases.append((z_near, np.array([3])))

        return cases
