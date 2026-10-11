"""
tests/hyper_escape/test_pathway_discovery.py
Validates Alternative Algorithm Discovery Engine (Feature E / Section 7).
Tests candidate generation strategies, bounded search space, precondition filtering,
and evidence collection.
"""
import pytest
import numpy as np

from hyper_universal.contracts.contract_engine import ContractRegistry
from hyper_universal.pathway_discovery.search import AlternativeAlgorithmDiscoveryEngine


def test_discovery_engine_evaluation():
    registry = ContractRegistry()
    contract = registry.get("dense_gemm_512x512")
    assert contract is not None

    engine = AlternativeAlgorithmDiscoveryEngine()

    # Create test input 256x256
    np.random.seed(42)
    sample_data = np.random.randn(256, 256).astype(np.float32)

    report = engine.discover_and_evaluate(
        workload_id="dense_gemm_512x512",
        contract=contract,
        sample_input=sample_data,
        max_candidates=4,
    )

    assert report.workload_id == "dense_gemm_512x512"
    assert len(report.evaluated_candidates) > 0
    # Must have evaluated the baseline
    cand_families = [c.algorithm_family for c in report.evaluated_candidates]
    assert "BASELINE_DENSE" in cand_families

    # Check that best candidate is identified
    assert report.best_verified_candidate is not None
    assert report.best_verified_candidate.verification_status in [
        "EXACT_VERIFIED",
        "CONTRACT_VERIFIED",
    ]


def test_discovery_engine_records_failure_reasons():
    registry = ContractRegistry()
    contract = registry.get("dense_gemm_512x512")
    engine = AlternativeAlgorithmDiscoveryEngine()

    sample_data = np.random.randn(128, 128).astype(np.float32)
    report = engine.discover_and_evaluate(
        workload_id="dense_gemm_512x512",
        contract=contract,
        sample_input=sample_data,
        max_candidates=5,
    )

    # Any failed candidates must record failure reason
    for cand in report.evaluated_candidates:
        if cand.verification_status == "FAILED_CORRECTNESS":
            assert cand.failure_reason is not None

    # Check search completeness reporting
    assert report.search_completeness.value in [
        "BEST_CANDIDATE_FOUND",
        "PROVEN_OPTIMUM_BOUNDED_SPACE",
    ]
    assert report.search_coverage_ratio > 0.0

    # Check candidate representation fields
    winner = report.best_verified_candidate
    assert winner is not None
    assert winner.data_representation == "DENSE_CONTIGUOUS"
    assert winner.memory_strategy == "BOUNDED_POOL"
    assert winner.backend == "CPU_AVX2"


def test_discovery_engine_failure_classification():
    from hyper_universal.pathway_discovery.search import (
        PathwayCandidate,
        SearchCompletenessStatus,
        FailureCauseClassification,
    )
    from hyper_universal.contracts.contract_engine import UniversalContract, ExactnessRequirement

    contract = UniversalContract(
        workload_id="impossible_workload",
        exactness=ExactnessRequirement.BITWISE_EXACT,
    )
    engine = AlternativeAlgorithmDiscoveryEngine()

    # All candidates intentionally produce wrong answers
    bad_candidates = [
        PathwayCandidate(
            candidate_id="bad_1",
            name="Faulty Kernel 1",
            algorithm_family="FAULTY",
            transformation_kind="BUGGY",
            kernel_fn=lambda x: x + 999.0,
            precondition_check=lambda x: True,
        ),
        PathwayCandidate(
            candidate_id="bad_2",
            name="Faulty Kernel 2",
            algorithm_family="FAULTY",
            transformation_kind="BUGGY",
            kernel_fn=lambda x: x - 999.0,
            precondition_check=lambda x: True,
        ),
    ]

    report = engine.search_and_evaluate(
        contract=contract,
        reference_fn=lambda x: x * 2.0,
        sample_input=np.ones(10, dtype=np.float32),
        candidate_pool=bad_candidates,
    )

    assert report.winning_candidate is None
    assert report.search_completeness == SearchCompletenessStatus.NO_SUCCESSFUL_CANDIDATE_FOUND
    assert report.failure_classification == FailureCauseClassification.NUMERICAL_INCOMPATIBILITY

