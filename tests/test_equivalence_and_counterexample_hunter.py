"""
tests/test_equivalence_and_counterexample_hunter.py
===================================================
Validation suite for Phase 3 (EquivalenceEngine) & Phase 4 (CounterexampleHunter).
Tests the testing system against intentional bugs, edge cases, and adversarial falsification.
"""

import numpy as np
import pytest

from hyper.research_engine.contracts import ComputationalContract
from hyper.research_engine.exactness import ExactnessCategory, ExactnessMode
from hyper.research_engine.counterexample_verifier import (
    CounterexampleHunter,
    CounterexampleRecord,
    EquivalenceEngine,
    EquivalenceProof,
    EquivalenceVerifier,
)
from hyper.research_engine.independent_reference import IndependentReferenceEngine


def test_independent_reference_coverage():
    # Test that reference engine executes key workloads accurately
    A = np.eye(8, dtype=np.float32)
    B = np.ones((8, 8), dtype=np.float32) * 2.0
    res_mm = IndependentReferenceEngine.execute_reference("GEMM_STANDARD", {"A": A, "B": B})
    np.testing.assert_allclose(res_mm, B, atol=1e-6)

    # Naive vs vectorized matmul
    naive_mm = IndependentReferenceEngine.naive_matmul(A, B)
    np.testing.assert_array_equal(res_mm, naive_mm)


def test_equivalence_engine_accepts_valid_candidate():
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="Standard Matmul Contract",
        input_domain={
            "A": {"shape": [64, 64], "dtype": "FP32"},
            "B": {"shape": [64, 64], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [64, 64], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.NUMERICALLY_EQUIVALENT,
        tolerance_epsilon=1e-4,
    )

    # Genuine valid candidate (e.g. standard matmul)
    def valid_candidate(inputs):
        return inputs["A"] @ inputs["B"]

    proof = EquivalenceEngine.verify_candidate(valid_candidate, "valid_gemm_cand", contract)
    assert proof.is_verified is True
    assert proof.counterexamples_found == []
    assert proof.tests_evaluated > 0
    assert len(proof.proof_hash) == 64


def test_verifier_rejects_broken_candidates():
    """
    MASTER PROMPT SECTION 30: TEST THE TESTING SYSTEM.
    Intentionally broken candidates must NEVER be accepted by the verifier.
    """
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="Standard Matmul Strict Contract",
        input_domain={
            "A": {"shape": [64, 64], "dtype": "FP32"},
            "B": {"shape": [64, 64], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [64, 64], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.EXACT,
        tolerance_epsilon=0.0,
    )

    # 1. Off-by-one bug
    def off_by_one_candidate(inputs):
        return (inputs["A"] @ inputs["B"]) + 1.0

    proof1 = EquivalenceEngine.verify_candidate(off_by_one_candidate, "cand_off_by_one", contract)
    assert proof1.is_verified is False
    assert len(proof1.counterexamples_found) > 0

    # 2. Wrong constant bug
    def wrong_constant_candidate(inputs):
        return (inputs["A"] @ inputs["B"]) * 1.05

    proof2 = EquivalenceEngine.verify_candidate(wrong_constant_candidate, "cand_wrong_constant", contract)
    assert proof2.is_verified is False
    assert len(proof2.counterexamples_found) > 0

    # 3. Wrong dimension bug
    def wrong_dimension_candidate(inputs):
        return (inputs["A"] @ inputs["B"])[:32, :32]

    proof3 = EquivalenceEngine.verify_candidate(wrong_dimension_candidate, "cand_wrong_dim", contract)
    assert proof3.is_verified is False

    # 4. Precision drift bug (> epsilon)
    def precision_drift_candidate(inputs):
        return (inputs["A"] @ inputs["B"]) + 1e-3

    proof4 = EquivalenceEngine.verify_candidate(precision_drift_candidate, "cand_precision_drift", contract)
    assert proof4.is_verified is False

    # 5. Nan injection
    def nan_candidate(inputs):
        out = (inputs["A"] @ inputs["B"]).copy()
        out[0, 0] = np.nan
        return out

    proof5 = EquivalenceEngine.verify_candidate(nan_candidate, "cand_nan", contract)
    assert proof5.is_verified is False

    # 6. Exception throwing candidate
    def throwing_candidate(inputs):
        raise RuntimeError("Fatal memory access error")

    proof6 = EquivalenceEngine.verify_candidate(throwing_candidate, "cand_throw", contract)
    assert proof6.is_verified is False


def test_counterexample_hunter_active_search():
    contract = ComputationalContract(
        workload_id="GEMM_STANDARD",
        description="Standard Matmul",
        input_domain={
            "A": {"shape": [64, 64], "dtype": "FP32"},
            "B": {"shape": [64, 64], "dtype": "FP32"},
        },
        output_domain={"C": {"shape": [64, 64], "dtype": "FP32"}},
        exactness_category=ExactnessCategory.EXACT,
    )

    # Bug that only triggers on negative inputs
    def signed_buggy_candidate(inputs):
        res = inputs["A"] @ inputs["B"]
        if np.any(inputs["A"] < 0):
            res = np.abs(res)  # Bug: strips negative sign!
        return res

    # The hunter must track down the bug and return a counterexample
    cex = CounterexampleHunter.hunt(signed_buggy_candidate, contract, "cand_signed_bug")
    assert cex is not None
    assert isinstance(cex, CounterexampleRecord)
    assert cex.workload_id == "GEMM_STANDARD"
    assert cex.failure_reason != ""
