"""
tests/test_research_engine.py
==============================
Unit and integration tests for the HYPER research engine subsystem.
Verifies all core modules: exactness, contracts, independent reference,
solution space compiler, counterexample verification, anti-cheat, and parity gating.
"""

import math
import numpy as np
import pytest

from hyper.research_engine.exactness import ExactnessMode
from hyper.research_engine.contracts import ProblemContract
from hyper.research_engine.independent_reference import IndependentReferenceEngine
from hyper.research_engine.minimal_sufficient_computation import MinimalSufficientComputationEngine
from hyper.research_engine.solution_space_compiler import SolutionSpaceCompiler
from hyper.research_engine.counterexample_verifier import (
    CounterexampleGenerator,
    EquivalenceVerifier,
)
from hyper.research_engine.anti_cheat_and_holdout import (
    AntiHardcodingEngine,
    MetamorphicTestingEngine,
)
from hyper.research_engine.workload_suite import Canonical15WorkloadSuite
from hyper.research_engine.parity_and_proofs import (
    ParityMatrix,
    Parity100Gate,
)
from hyper.discovery.cir import CIRGraph


def test_exactness_modes():
    mode_bit = ExactnessMode.BIT_EXACT
    assert mode_bit.is_truly_exact
    assert not mode_bit.allows_numerical_slack

    mode_num = ExactnessMode.NUMERIC_TOLERANCE
    assert not mode_num.is_truly_exact
    assert mode_num.allows_numerical_slack

    # Disallows claiming BIT_EXACT when mode is NUMERIC_TOLERANCE
    assert not mode_num.validate_claim(ExactnessMode.BIT_EXACT)
    assert mode_bit.validate_claim(ExactnessMode.NUMERIC_TOLERANCE)


def test_independent_reference_matmul():
    A = np.random.randn(8, 8).astype(np.float32)
    B = np.random.randn(8, 8).astype(np.float32)
    naive = IndependentReferenceEngine.naive_matmul(A, B)
    ref = IndependentReferenceEngine.reference_matmul(A, B)
    assert np.allclose(naive, ref, atol=1e-5)


def test_independent_reference_conv2d():
    img = np.random.randn(16, 16).astype(np.float32)
    ker = np.random.randn(3, 3).astype(np.float32)
    ref = IndependentReferenceEngine.reference_conv2d(img, ker)
    assert ref.shape == (14, 14)


def test_canonical_15_contracts_coverage():
    contracts = Canonical15WorkloadSuite.get_all_workload_contracts()
    assert len(contracts) == 15
    for w_id, contract in contracts.items():
        assert contract.workload_id == w_id
        sample_in = Canonical15WorkloadSuite.get_sample_inputs_for_workload(w_id)
        assert isinstance(sample_in, dict)
        ref_out = IndependentReferenceEngine.execute_reference(w_id, sample_in)
        assert ref_out is not None


def test_anti_cheat_detects_sleep():
    def suspicious_candidate(inputs):
        import time
        time.sleep(0.01)
        return inputs.get("A", 0)

    clean, violations = AntiHardcodingEngine.audit_candidate_callable(suspicious_candidate)
    assert not clean
    assert any("sleep" in v.lower() for v in violations)


def test_anti_cheat_clean_function():
    def clean_candidate(inputs):
        return inputs["A"] @ inputs["B"]

    clean, violations = AntiHardcodingEngine.audit_candidate_callable(clean_candidate)
    assert clean
    assert len(violations) == 0


def test_metamorphic_testing_homogeneity():
    contract = Canonical15WorkloadSuite.get_all_workload_contracts()["GEMM_STANDARD"]
    sample_in = Canonical15WorkloadSuite.get_sample_inputs_for_workload("GEMM_STANDARD")

    def gemm_fn(inputs):
        return inputs["A"] @ inputs["B"]

    is_valid, report = MetamorphicTestingEngine.verify_metamorphic_invariants(
        gemm_fn, sample_in, contract
    )
    assert is_valid


def test_solution_space_expansion():
    contract = Canonical15WorkloadSuite.get_all_workload_contracts()["GEMM_STANDARD"]
    cir = CIRGraph(name="test_gemm")
    initial = SolutionSpaceCompiler.generate_initial_candidate(contract, cir)
    assert initial.transformation_history == ["CANONICAL_BASELINE"]

    children = SolutionSpaceCompiler.expand_candidate(initial, contract)
    assert len(children) >= 3
    trans_names = [c.transformation_history[-1] for c in children]
    assert any("STRASSEN" in t for t in trans_names)


def test_parity_gate_rejection_of_false_claims():
    # If exact parity is 26.7%, gate MUST fail-closed with NOT_VERIFIED
    matrix = ParityMatrix(
        hardware_parity=0.0,
        exact_compute_parity=26.7,
        contract_parity=100.0,
        performance_parity=82.5,
        energy_parity=78.0,
        memory_parity=85.0,
        throughput_parity=80.0,
    )
    passed, reasons = Parity100Gate.evaluate(
        parity_matrix=matrix,
        all_workloads_verified=True,
        blind_holdout_passed=True,
        anti_cheat_clean=True,
        resource_constraints_satisfied=True,
    )
    assert not passed
    assert any("Exact-compute parity" in r for r in reasons)
