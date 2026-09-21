"""
tests/test_vaee_complete.py
===========================
Comprehensive Test Suite for the Verified Adaptive Algorithmic Escape Engine (VAEE).
Validates all 12 subsystems, research workloads, verification strategies, and APIs.
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from hyper.escape_engine import (
    VerifiedAdaptiveEscapeEngine,
    ComputationalContract,
    ContractExtractor,
    InformationBoundaryAnalyzer,
    ComputationalPathway,
    PathwayRegistry,
    PathwayGenerator,
    AdaptiveSearchEngine,
    SearchBudget,
    ExecutionSandbox,
    MasterVerifier,
    ExactVerifier,
    DifferentialVerifier,
    InvariantVerifier,
    ChecksumVerifier,
    CostAnalyzer,
    ComplexityAnalyzer,
    ParetoPoint,
    ParetoFrontier,
    BarrierDetector,
    BarrierClassification,
    ExperimentManager,
)
from hyper.escape_engine.workloads import (
    MatrixMultiplicationResearchWorkload,
    PolynomialResearchWorkload,
    SortingResearchWorkload,
    Convolution2DResearchWorkload,
    DynamicProgrammingResearchWorkload,
)
from backend.main import app


def test_contract_extraction_and_hash():
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    contract = ContractExtractor.extract_from_tensor_op(
        name="test_matmul",
        input_sample=A,
        reference_fn=lambda a: a @ B,
        tolerance=1e-4,
    )
    assert contract.input_type == "matrix"
    assert contract.input_shape == (32, 32)
    assert contract.output_shape == (32, 32)
    assert len(contract.contract_hash()) == 64


def test_information_boundary_analysis():
    contract = ComputationalContract(
        contract_id="test_sparse",
        input_type="matrix",
        output_type="matrix",
        input_shape=(64, 64),
        output_shape=(64, 64),
    )
    # Create 80% sparse matrix
    sparse_A = np.zeros((64, 64), dtype=np.float32)
    sparse_A[0:10, 0:10] = 1.0

    profile = InformationBoundaryAnalyzer.analyze(contract, sparse_A)
    assert profile.is_sparse
    assert profile.sparsity_ratio > 0.70
    assert profile.can_reduce_representation


def test_pathway_generation_and_structural_deduplication():
    contract = ComputationalContract(
        contract_id="gemm_contract",
        input_type="matrix",
        output_type="matrix",
        input_shape=(64, 64),
        output_shape=(64, 64),
    )
    A = np.random.randn(64, 64).astype(np.float32)
    profile = InformationBoundaryAnalyzer.analyze(contract, A)

    gen = PathwayGenerator(seed=42)
    candidates = gen.generate_candidates(contract, profile, max_candidates=10)
    assert len(candidates) >= 4

    registry = PathwayRegistry()
    unique_count = 0
    for cand in candidates:
        is_u, _ = registry.register(cand)
        if is_u:
            unique_count += 1

    assert unique_count == len(candidates)
    assert registry.diversity_ratio == 1.0


def test_multi_strategy_verification():
    verifier = MasterVerifier()

    # 1. Exact Verifier
    v_exact = verifier.exact.verify(np.array([1, 2, 3]), np.array([1, 2, 3]))
    assert v_exact.is_valid
    assert v_exact.trust_level == "EXACT_VERIFIED"

    # 2. Differential Verifier
    c = ComputationalContract(
        contract_id="num_test",
        input_type="vector",
        output_type="vector",
        input_shape=(3,),
        output_shape=(3,),
        numeric_tolerance=1e-3,
    )
    v_diff = verifier.differential.verify(np.array([1.0001, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]), c)
    assert v_diff.is_valid

    # 3. Invariant Verifier (Monotonic sort)
    v_inv_pass = verifier.invariant.verify_sorting_invariant(np.array([1, 2, 5, 8, 10]))
    v_inv_fail = verifier.invariant.verify_sorting_invariant(np.array([1, 5, 2, 8, 10]))
    assert v_inv_pass.is_valid
    assert not v_inv_fail.is_valid

    # 4. Freivalds Checksum Verifier
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    C_correct = A @ B
    C_wrong = C_correct.copy()
    C_wrong[0, 0] += 1.0

    v_frei_pass = verifier.checksum.verify_freivalds_gemm(A, B, C_correct)
    v_frei_fail = verifier.checksum.verify_freivalds_gemm(A, B, C_wrong)
    assert v_frei_pass.is_valid
    assert not v_frei_fail.is_valid


def test_execution_sandbox():
    sandbox = ExecutionSandbox()

    # Test normal fast function
    ok, res, ms, err = sandbox.run_safe(lambda x: x * 2, (5,))
    assert ok
    assert res == 10
    assert err is None

    # Test division by zero
    ok, res, ms, err = sandbox.run_safe(lambda x: 1 / x, (0,))
    assert not ok
    assert "ZeroDivisionError" in err

    # Test NaN detection
    ok, res, ms, err = sandbox.run_safe(lambda: np.array([1.0, np.nan]))
    assert not ok
    assert "Numerical divergence" in err


def test_pareto_frontier_dominance():
    frontier = ParetoFrontier()

    p1 = ComputationalPathway("P1", None, "matrix", ["t1"], "DENSE", "CPU", "EXACT")
    p2 = ComputationalPathway("P2", None, "matrix", ["t2"], "DENSE", "CPU", "EXACT")

    # pt1 is faster and uses less memory than pt2 -> pt1 dominates pt2
    pt1 = ParetoPoint(p1, latency_ms=10.0, memory_mb=5.0, energy_mj=50.0, confidence=1.0, speedup_vs_baseline=2.0)
    pt2 = ParetoPoint(p2, latency_ms=20.0, memory_mb=10.0, energy_mj=100.0, confidence=1.0, speedup_vs_baseline=1.0)

    assert pt1.dominates(pt2)
    assert not pt2.dominates(pt1)

    frontier.update(pt2)
    assert len(frontier.points) == 1
    # Adding pt1 should prune pt2
    frontier.update(pt1)
    assert len(frontier.points) == 1
    assert frontier.points[0].pathway.pathway_id == "P1"


def test_barrier_detector():
    # Dense incompressible matrix under exact contract
    contract = ComputationalContract(
        contract_id="dense_exact",
        input_type="matrix",
        output_type="matrix",
        input_shape=(64, 64),
        output_shape=(64, 64),
        correctness="EXACT",
    )
    A = np.random.randn(64, 64).astype(np.float32)
    profile = InformationBoundaryAnalyzer.analyze(contract, A)

    verdict = BarrierDetector.detect_barriers(contract, profile)
    assert verdict.status == BarrierClassification.PROVEN_BARRIER
    assert verdict.is_impossibility_proof


def test_research_workload_matrix_multiplication():
    wl = MatrixMultiplicationResearchWorkload(M=64, K=64, N=64, seed=42)
    res = wl.run_experiment(max_candidates=4)
    assert res["outcome"] in ["SUCCESS", "UNKNOWN"]
    assert res["search_statistics"]["total_evaluated"] > 0
    assert len(res["pareto_frontier"]) > 0


def test_research_workload_polynomial():
    wl = PolynomialResearchWorkload(degree=500)
    res = wl.run_benchmark()
    assert res["is_verified"]
    assert res["verified_speedup"] > 1.0


def test_research_workload_sorting():
    wl = SortingResearchWorkload(N=10000, key_max=500)
    res = wl.run_benchmark()
    assert res["invariant_passed"]
    assert res["exact_match"]
    assert res["verified_speedup"] > 1.0


def test_research_workload_convolution_2d():
    wl = Convolution2DResearchWorkload(H=128, W=128, K=9)
    res = wl.run_benchmark()
    assert res["is_verified"]
    assert res["verified_speedup"] > 1.0


def test_research_workload_dynamic_programming():
    wl = DynamicProgrammingResearchWorkload(N=100, W=500)
    res = wl.run_benchmark()
    assert res["is_exact"]
    assert res["verified_speedup"] > 0.8


def test_vaee_api_endpoints():
    client = TestClient(app)

    # Status endpoint
    r_status = client.get("/api/v1/escape/status")
    assert r_status.status_code == 200
    assert "Intel Core i5-12450H" in r_status.json()["hardware"]

    # Generate endpoint
    r_gen = client.post("/api/v1/escape/generate", json={
        "input_type": "matrix",
        "input_shape": [64, 64],
        "correctness": "EXACT",
    })
    assert r_gen.status_code == 200
    assert r_gen.json()["count"] > 0

    # Benchmark endpoint
    r_bench = client.post("/api/v1/escape/benchmark", json={
        "workload_name": "polynomial",
        "dimension": 200,
    })
    assert r_bench.status_code == 200
    assert r_bench.json()["verified_speedup"] > 0.5
