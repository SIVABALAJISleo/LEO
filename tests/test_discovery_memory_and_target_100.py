"""
tests/test_discovery_memory_and_target_100.py
=============================================
Validation suite for Phase 13 (Discovery Memory & Failure Learning) & Phase 14 (100% Target Engine).
"""

import os
import tempfile
from pathlib import Path
import numpy as np
import pytest

from hyper.research_engine.contracts import ComputationalContract
from hyper.research_engine.exactness import ExactnessCategory, ExactnessMode
from hyper.research_engine.counterexample_verifier import EquivalenceProof
from hyper.research_engine.learning_and_benchmarking import (
    FailureKnowledgeBase,
    FailureRecord,
    ProofCarryingComputation,
    Target100Engine,
    TransformationLibrary,
)


def test_failure_knowledge_base():
    rec = FailureKnowledgeBase.record_failure(
        workload_id="TEST_GEMM",
        transformation_sequence=["CANONICAL", "BAD_TRUNCATION"],
        failure_category="NUMERICAL_INSTABILITY",
        reason="Exceeded error tolerance 1e-4",
    )

    assert isinstance(rec, FailureRecord)
    assert FailureKnowledgeBase.is_known_failure("TEST_GEMM", ["CANONICAL", "BAD_TRUNCATION"]) is True
    assert FailureKnowledgeBase.is_known_failure("TEST_GEMM", ["CANONICAL", "OTHER"]) is False


def test_transformation_library_knowledge():
    TransformationLibrary.register_success(
        transformation_name="HOMOTOPIC_HOARE_CONTRACTION",
        domain="MLP_INFERENCE",
        speedup=1.96,
    )

    lib = TransformationLibrary.load_all()
    assert "HOMOTOPIC_HOARE_CONTRACTION" in lib
    entry = lib["HOMOTOPIC_HOARE_CONTRACTION"]
    assert "MLP_INFERENCE" in entry["applicable_domains"]
    assert entry["verified_discoveries_count"] >= 1


def test_proof_carrying_computation_artifact():
    contract = ComputationalContract(
        workload_id="GEMM_TEST",
        description="Proof Artifact Test",
        input_domain={"A": {"shape": [16, 16], "dtype": "FP32"}, "B": {"shape": [16, 16], "dtype": "FP32"}},
        output_domain={"C": {"shape": [16, 16], "dtype": "FP32"}},
    )

    proof = EquivalenceProof(
        is_verified=True,
        exactness_mode=ExactnessMode.NUMERIC_TOLERANCE,
        exactness_category=ExactnessCategory.NUMERICALLY_EQUIVALENT,
        verification_method="INDEPENDENT_DUAL_PATH",
        max_error=1e-5,
        l2_error=1e-4,
        tests_evaluated=10,
        counterexamples_found=[],
        assumptions_verified=True,
        proof_hash="a" * 64,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = ProofCarryingComputation.create_proof_artifact(
            original_hash="hash_orig",
            candidate_hash="hash_cand",
            transformation_chain=["CANONICAL", "TILING"],
            contract=contract,
            proof=proof,
            cost_breakdown={"latency_ms": 1.2, "flops": 1000},
            output_dir=Path(tmpdir),
        )

        assert os.path.exists(out_path)
        assert "pathway_proof.json" in out_path


def test_target_100_engine_coverage_accounting():
    # Run target loop for 1 iteration on the canonical suite
    report = Target100Engine.execute_target_loop(max_iterations=1)

    assert report["total_workloads"] == 15
    assert report["verified_workloads"] >= 1
    assert report["exact_workload_coverage"] > 0.0
    assert report["hardware_parity"] == "NOT CLAIMED (PHYSICALLY_DISJOINT)"
    assert len(report["workloads"]) == 15
