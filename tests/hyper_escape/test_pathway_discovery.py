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
