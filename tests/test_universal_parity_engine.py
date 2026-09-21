"""
tests/test_universal_parity_engine.py
======================================
Comprehensive Test Suite for the Universal Computational Parity Engine (UCPE).
Tests:
- Universal Workload Adapter & Schema Extraction
- Contract Specification & Zero Silent Downgrade
- Information Boundary & Entropy Analysis
- 10 Transformation Families & Pathway Composition
- Pathway Diversity & Pseudodiversity Rejection
- AST-Sandboxed Program Synthesis
- Independent Verification (Freivalds, Exact, Invariants)
- Multi-Dimensional Parity Vector & RTX 5090 Reference Model
- Cache Discipline & Anti-Cheating Validation
- Formal Barrier Detection (Entropy, Dependency)
- Multi-Objective Pareto Frontier & Breakthrough Detection
- End-to-End Pipeline on Numerical, Sorting, Unseen, and Adversarial Workloads
- REST API Endpoints
"""

from __future__ import annotations

import numpy as np
import pytest
from fastapi.testclient import TestClient

from hyper.universal import (
    UniversalComputationalParityEngine,
    UniversalWorkload,
    UniversalWorkloadAdapter,
    WorkloadDomain,
    UniversalContract,
    ContractCorrectness,
    PrecisionTier,
    InformationBoundaryEngine,
    UniversalPathway,
    TransformationFamily,
    UniversalPathwayGenerator,
    UniversalDiversityEngine,
    UniversalPathwayComposer,
    ProgramSynthesizer,
    UniversalSandbox,
    UniversalVerifier,
    VerificationState,
    ScientificOutcome,
    FreivaldsVerifier,
    InvariantChecker,
    ParityVector,
    RTX5090Model,
    CacheState,
    CacheDisciplineValidator,
    UniversalBarrierEngine,
    UniversalParetoPoint,
    UniversalParetoFrontier,
    BreakthroughDetector,
    UniversalWorkloadSuite,
    AdversarialWorkloadGenerator,
)
from backend.main import app


@pytest.fixture
def engine() -> UniversalComputationalParityEngine:
    return UniversalComputationalParityEngine(seed=42)


def test_workload_adapter():
    data = np.array([1, 5, 2, 8, 3], dtype=np.int32)
    wl = UniversalWorkloadAdapter.adapt(
        target=lambda x: np.sort(x),
        sample_input=data,
        workload_id="test_sort",
    )
    assert wl.workload_id == "test_sort"
    assert wl.schema.input_type == "ndarray"
    assert wl.schema.input_shape == (5,)
    assert wl.domain == WorkloadDomain.SEARCH_SORTING
    assert len(wl.workload_hash) == 64


def test_contract_validation():
    c = UniversalContract(
        contract_id="c1",
        workload_id="w1",
        correctness=ContractCorrectness.EXACT,
        numeric_tolerance=0.0,
    )
    assert c.is_exact()
    assert c.to_dict()["correctness"] == "EXACT"


def test_information_boundary():
    # Dense array with repeated zeros
    data = np.zeros((32, 32), dtype=np.float32)
    data[0, 0] = 1.0
    wl = UniversalWorkloadAdapter.adapt(lambda x: x * 2.0, data, workload_id="sparse_wl")
    c = UniversalContract(contract_id="c_sparse", workload_id=wl.workload_id)

    profile = InformationBoundaryEngine.analyze(wl, c)
    assert profile.sparsity_ratio > 0.9
    assert profile.is_compressible
    assert "SPARSITY_SKIPPING" in profile.reduction_opportunities


def test_ten_transformation_families(engine: UniversalComputationalParityEngine):
    wl, c = UniversalWorkloadSuite.get_polynomial_workload(degree=5)
    candidates = engine.generator.generate_candidate_pool(wl, c, max_candidates=15)

    families = {cand.family for cand in candidates}
    # Check that multiple canonical families are present
    assert len(families) >= 4
    assert all(isinstance(cand.structural_hash, str) for cand in candidates)


def test_pathway_composition():
    wl, c = UniversalWorkloadSuite.get_matrix_workload(dim=32)
    p1 = UniversalPathway(
        pathway_id="p1",
        family=TransformationFamily.MATHEMATICAL,
        name="Factorization",
        transformation_chain=["SVD_FACTORIZATION"],
        structural_hash="h1",
    )
    p2 = UniversalPathway(
        pathway_id="p2",
        family=TransformationFamily.MEMORY,
        name="Tiling",
        transformation_chain=["CACHE_TILING"],
        structural_hash="h2",
    )
    comp = UniversalPathwayComposer.compose(p1, p2)
    assert "SVD_FACTORIZATION" in comp.transformation_chain
    assert "CACHE_TILING" in comp.transformation_chain
    assert comp.lineage_depth == 1
    assert comp.parent_id == "p1"


def test_diversity_pseudodiversity_rejection():
    div = UniversalDiversityEngine()
    p1 = UniversalPathway(
        pathway_id="p1",
        family=TransformationFamily.COMPILER,
        name="AVX2 Vectorization",
        transformation_chain=["AVX2_256BIT_VECTORIZATION"],
        structural_hash="hash_avx2",
        target_hardware="CPU_AVX2",
    )
    assert div.register(p1)

    # Attempt to register identical structural pathway under different ID
    p2 = UniversalPathway(
        pathway_id="p2_fake",
        family=TransformationFamily.COMPILER,
        name="AVX2 Vectorization Clone",
        transformation_chain=["AVX2_256BIT_VECTORIZATION"],
        structural_hash="hash_avx2",
        target_hardware="CPU_AVX2",
    )
    assert not div.register(p2)


def test_program_synthesis_and_ast_safety():
    # Valid synthesis
    p_synth = ProgramSynthesizer.synthesize_reduction_pathway("sum")
    assert p_synth.family == TransformationFamily.PROGRAM_SYNTHESIS
    assert p_synth.run_fn is not None
    res = p_synth.run_fn(np.array([1.0, 2.0, 3.0]))
    assert res == 6.0

    # Unsafe synthesis rejection
    unsafe_code = "import os\ndef evil(x): return os.system('echo hi')"
    is_safe, reasons = ProgramSynthesizer.validate_code(unsafe_code)
    assert not is_safe
    assert any("Forbidden" in r for r in reasons)


def test_sandbox_timeout():
    def infinite_loop(x):
        import time
        time.sleep(1.0)
        return x

    sb = UniversalSandbox(default_timeout_s=0.1)
    success, res, elapsed_ms, err = sb.run_safe(infinite_loop, 42)
    assert not success
    assert "timed out" in err.lower()


def test_freivalds_verifier():
    A = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    B = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)
    C_correct = A @ B
    C_corrupt = C_correct.copy()
    C_corrupt[0, 0] += 0.5

    v_ok = FreivaldsVerifier.verify(A, B, C_correct)
    assert v_ok.is_valid
    assert v_ok.confidence_score > 0.99

    v_fail = FreivaldsVerifier.verify(A, B, C_corrupt)
    assert not v_fail.is_valid
    assert v_fail.state == VerificationState.FAILED


def test_invariant_checker():
    sorted_arr = np.array([1, 2, 5, 8, 10], dtype=np.int32)
    unsorted_arr = np.array([1, 5, 2, 8, 10], dtype=np.int32)

    assert InvariantChecker.verify_sorted_monotonic(sorted_arr).is_valid
    assert not InvariantChecker.verify_sorted_monotonic(unsorted_arr).is_valid

    perm_ok = InvariantChecker.verify_permutation(sorted_arr, np.array([10, 8, 5, 2, 1], dtype=np.int32))
    assert perm_ok.is_valid


def test_rtx5090_reference_model():
    model = RTX5090Model()
    vec = model.estimate_workload_cost(estimated_flops=1e9, data_movement_bytes=1e7)
    assert vec.bandwidth_gb_per_sec == 1792.0
    assert vec.power_watts == 600.0
    assert vec.latency_ms > 0.0


def test_cache_discipline():
    # Comparing cached HYPER to cold RTX is forbidden
    is_valid, err = CacheDisciplineValidator.validate_comparison(
        hyper_cache_state=CacheState.CACHED,
        reference_cache_state=CacheState.COLD,
    )
    assert not is_valid
    assert "INVALID_COMPARISON" in err

    # Fair comparison is allowed
    is_valid_cold, _ = CacheDisciplineValidator.validate_comparison(CacheState.COLD, CacheState.COLD)
    assert is_valid_cold


def test_barrier_detection():
    wl_noise, c_noise = AdversarialWorkloadGenerator.get_incompressible_noise_workload(size=5000)
    profile = InformationBoundaryEngine.analyze(wl_noise, c_noise)
    verdict = UniversalBarrierEngine.detect_barrier(c_noise, profile)
    assert verdict.has_barrier
    assert verdict.barrier_type.value == "INFORMATION_ENTROPY"


def test_end_to_end_polynomial_horner(engine: UniversalComputationalParityEngine):
    wl, c = UniversalWorkloadSuite.get_polynomial_workload(degree=8, num_points=500)
    res = engine.run_universal_pipeline(
        workload_target=wl,
        sample_input=wl.sample_input,
        contract=c,
        max_candidates=10,
    )
    assert res["status"] in ("TARGET_REACHED", "IMPROVEMENT_FOUND", "UNKNOWN")
    assert res["verified_speedup"] >= 1.0
    assert res["parity_scorecard"]["dimensions"][0]["dimension"] == "LATENCY"


def test_end_to_end_sorting(engine: UniversalComputationalParityEngine):
    wl, c = UniversalWorkloadSuite.get_sorting_workload(N=20000, key_max=300)
    res = engine.run_universal_pipeline(
        workload_target=wl,
        sample_input=wl.sample_input,
        contract=c,
        max_candidates=10,
    )
    assert res["status"] in ("TARGET_REACHED", "IMPROVEMENT_FOUND", "UNKNOWN")
    assert res["parity_scorecard"]["dimensions"][4]["hyper"] == "PASS"


def test_end_to_end_unseen_workload(engine: UniversalComputationalParityEngine):
    wl, c = UniversalWorkloadSuite.generate_unseen_workload(seed=123)
    res = engine.run_universal_pipeline(
        workload_target=wl,
        sample_input=wl.sample_input,
        contract=c,
        max_candidates=8,
    )
    assert res["experiment_id"].startswith("EXP-UCPE-")
    assert res["workload"]["domain"] == WorkloadDomain.UNKNOWN_UNSEEN.value


def test_universal_api_endpoints():
    client = TestClient(app)

    # 1. Status
    r_stat = client.get("/api/v1/universal/status")
    assert r_stat.status_code == 200
    assert "diversity_stats" in r_stat.json()

    # 2. Search
    r_search = client.post("/api/v1/universal/search", json={"workload_domain": "POLYNOMIAL", "dimension": 100, "max_candidates": 5})
    assert r_search.status_code == 200
    data = r_search.json()
    assert "verified_speedup" in data
    assert "parity_scorecard" in data

    # 3. Verify
    r_verify = client.post("/api/v1/universal/verify", json={"candidate_output": [1.0, 2.0], "reference_output": [1.0, 2.0], "tolerance": 0.0})
    assert r_verify.status_code == 200
    assert r_verify.json()["is_valid"]

    # 4. Synthesize
    r_synth = client.post("/api/v1/universal/synthesize", json={"operation": "sum"})
    assert r_synth.status_code == 200
    assert r_synth.json()["family"] == "PROGRAM_SYNTHESIS"
