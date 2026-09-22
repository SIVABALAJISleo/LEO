"""
tests/test_complete_discovery_platform.py
=========================================
Comprehensive integration test suite for the LEO/HYPER Universal Computational
Discovery Platform across Phases 0 through 20.
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from hyper.discovery.capability_registry import (
    CapabilityRegistry,
    CapabilityEntry,
    MaturityLevel,
    FeatureStatus,
)
from hyper.discovery.search_space_compiler import (
    SearchSpaceCompiler,
    TransformationSearchSpace,
)
from hyper.discovery.counterfactual_engine import (
    CounterfactualEngine,
    CounterfactualType,
    PathwayCompositionGraph,
    PathwayGraphNode,
)
from hyper.discovery.fairness_engine import (
    BenchmarkFairnessEngine,
    FairnessViolation,
)
from hyper.discovery.alphatensor_engine import (
    AlphaTensorEngine,
    BilinearTensorProblem,
)
from hyper.discovery.alphaevolve_engine import (
    AlphaEvolveEngine,
    ProgramIndividual,
)
from hyper.discovery.meta_search import (
    FormalBarrierClassifier,
    FormalBarrierType,
    AdaptiveSearchScaler,
)
from hyper.discovery.runtime_hook import (
    RuntimeDiscoveryHook,
)
from hyper.discovery.discovery_experiments import (
    DiscoveryExperimentSuite,
)
from hyper.discovery.loop import (
    UniversalDiscoveryLoop,
)
from hyper.universal.contracts.universal_contract import (
    UniversalContract,
    ContractCorrectness,
    PrecisionTier,
)
from backend.main import app


# ---------------------------------------------------------------------------
# 1. Capability Registry Tests
# ---------------------------------------------------------------------------
def test_capability_registry():
    reg = CapabilityRegistry()
    features = reg.list_features()
    assert len(features) >= 12

    # Check highest maturity level
    maturity = reg.get_system_maturity_level()
    assert maturity in list(MaturityLevel)

    # Test dynamic registration
    custom = CapabilityEntry(
        feature="CustomQuantumAccelerator",
        status=FeatureStatus.EXPERIMENTAL,
        source_file="hyper/custom.py",
        implementation_level=MaturityLevel.LEVEL_3,
    )
    reg.register_feature(custom)
    assert reg.get_feature("CustomQuantumAccelerator") is not None


# ---------------------------------------------------------------------------
# 2. Search Space Compiler Tests
# ---------------------------------------------------------------------------
def test_search_space_compiler_exact_contract():
    compiler = SearchSpaceCompiler()
    exact_contract = UniversalContract(
        contract_id="c-exact",
        workload_id="w-sort",
        correctness=ContractCorrectness.EXACT,
        numeric_tolerance=0.0,
        relative_tolerance=0.0,
    )
    space = compiler.compile("ExactSort", exact_contract)
    assert space.is_legal("HORNER_POLYNOMIAL_REWRITE")
    # Lossy quantization must be strictly illegal under exact contract
    assert not space.is_legal("INT8_SYMMETRIC_QUANTIZATION")
    assert not space.is_legal("LOW_RANK_SVD_FACTORIZATION")


def test_search_space_compiler_approx_contract():
    compiler = SearchSpaceCompiler()
    approx_contract = UniversalContract(
        contract_id="c-approx",
        workload_id="w-conv",
        correctness=ContractCorrectness.APPROXIMATE,
        numeric_tolerance=0.05,
        relative_tolerance=0.05,
    )
    space = compiler.compile("ApproxConv", approx_contract)
    # Permitted under approximate contracts
    assert space.is_legal("INT8_SYMMETRIC_QUANTIZATION")
    assert space.is_legal("LOW_RANK_SVD_FACTORIZATION")


# ---------------------------------------------------------------------------
# 3. Counterfactual Engine Tests
# ---------------------------------------------------------------------------
def test_counterfactual_engine_generation_and_dag():
    cf_engine = CounterfactualEngine()
    contract = UniversalContract(contract_id="c-math", workload_id="w-math")
    hypotheses = cf_engine.generate_hypotheses("PolynomialEvaluation", contract)
    assert len(hypotheses) >= 3

    # Test Pathway Composition Graph
    graph = PathwayCompositionGraph()
    root = PathwayGraphNode(node_id="root", name="Baseline", transform_type="ROOT")
    child1 = PathwayGraphNode(node_id="c1", name="Horner", transform_type="ALGEBRAIC", parent_ids=["root"])
    child2 = PathwayGraphNode(node_id="c2", name="HornerAVX2", transform_type="SIMD", parent_ids=["c1"])

    graph.add_node(root)
    graph.add_node(child1)
    graph.add_node(child2)

    lineage = graph.get_lineage("c2")
    assert len(lineage) == 3
    assert lineage[0].node_id == "root"
    assert lineage[2].node_id == "c2"


# ---------------------------------------------------------------------------
# 4. Benchmark Fairness Engine Tests
# ---------------------------------------------------------------------------
def test_benchmark_fairness_clean_execution():
    fairness = BenchmarkFairnessEngine()
    contract = UniversalContract(contract_id="c-clean", workload_id="w-clean")
    inp = np.array([1.0, 2.0, 3.0])
    out = np.array([2.0, 4.0, 6.0])

    report = fairness.audit_execution(
        candidate_input=inp,
        candidate_output=out,
        reference_input=inp,
        reference_output=out,
        contract=contract,
        cache_mode="COLD",
        measured_time_ns=50000,
        is_cached_result=False,
    )
    assert report.is_fair is True
    assert report.verdict == "FAIR_BENCHMARK"


def test_benchmark_fairness_detects_cheating():
    fairness = BenchmarkFairnessEngine()
    contract = UniversalContract(contract_id="c-cheat", workload_id="w-cheat", correctness=ContractCorrectness.EXACT)
    inp1 = np.array([1.0, 2.0, 3.0])
    inp2 = np.array([1.0, 2.0, 99.0])  # Changed input!

    report = fairness.audit_execution(
        candidate_input=inp1,
        candidate_output=inp1,
        reference_input=inp2,
        reference_output=inp2,
        contract=contract,
        cache_mode="COLD",
        measured_time_ns=50000,
        is_cached_result=False,
    )
    assert report.is_fair is False
    assert report.verdict == "INVALID_COMPARISON"
    assert FairnessViolation.INPUT_TAMPERING in report.violations


# ---------------------------------------------------------------------------
# 5. AlphaTensor Bilinear Algorithm Discovery Tests
# ---------------------------------------------------------------------------
def test_alphatensor_strassen_2x2x2_verification():
    at_engine = AlphaTensorEngine()
    prob = at_engine.create_matrix_multiplication_tensor(2, 2, 2)
    assert prob.shape == (4, 4, 4)
    assert prob.canonical_rank == 8

    # Search algorithm produces Strassen R=7
    cand = at_engine.search_algorithm(prob)
    assert cand.rank == 7
    assert cand.is_exact is True
    assert cand.multiplication_reduction_pct == 12.50

    # Verify factorization explicitly
    U, V, W = at_engine.create_strassen_2x2x2_factors()
    assert at_engine.verify_factorization(prob, U, V, W) is True


# ---------------------------------------------------------------------------
# 6. AlphaEvolve Program Evolution & Novelty Tests
# ---------------------------------------------------------------------------
def test_alphaevolve_structural_novelty_and_evolution():
    engine = AlphaEvolveEngine(population_size=3, max_generations=2)
    sample_input = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    contract = UniversalContract(contract_id="c-evolve", workload_id="w-evolve")

    result = engine.evolve_workload(
        base_fn=lambda x: np.sum(x),
        sample_input=sample_input,
        contract=contract,
    )
    assert result.generations_completed == 2
    assert result.total_candidates_evaluated >= 3
    assert result.unique_structural_pathways >= 2
    assert result.best_candidate is not None


# ---------------------------------------------------------------------------
# 7. Barrier Detection & Adaptive Search Scaler Tests
# ---------------------------------------------------------------------------
def test_formal_barrier_detection():
    # 1. Bandwidth saturation
    b1 = FormalBarrierClassifier.classify(
        entropy_score=0.5,
        memory_usage_mb=1000.0,
        bandwidth_required_gbs=35.0,  # Exceeds 18.57 GB/s
        verification_failures=0,
        search_iterations=10,
    )
    assert b1.barrier_type == FormalBarrierType.BANDWIDTH_BARRIER

    # 2. Information entropy barrier
    b2 = FormalBarrierClassifier.classify(
        entropy_score=0.99,  # Incompressible
        memory_usage_mb=1000.0,
        bandwidth_required_gbs=5.0,
        verification_failures=0,
        search_iterations=10,
    )
    assert b2.barrier_type == FormalBarrierType.INFORMATION_BARRIER


def test_adaptive_search_scaler():
    scaler = AdaptiveSearchScaler()
    assert scaler.budget == 10

    # Expand budget when yield and novelty are high
    new_b = scaler.update_budget(discoveries_found=2, novelty_ratio=0.85, verification_yield=0.80)
    assert new_b == 100

    # Contract when stagnated
    stagnant_b = scaler.update_budget(discoveries_found=0, novelty_ratio=0.05, verification_yield=0.0)
    assert stagnant_b == 10


# ---------------------------------------------------------------------------
# 8. Runtime Discovery Hook Tests
# ---------------------------------------------------------------------------
def test_runtime_discovery_hook():
    hook = RuntimeDiscoveryHook()
    inp = [1, 2, 3]

    # Observe repeated identical calls -> should trigger cache opportunity
    hook.observe("w-test", inp, latency_ms=5.0)
    hook.observe("w-test", inp, latency_ms=5.0)
    opp = hook.observe("w-test", inp, latency_ms=5.0)
    assert opp is not None
    assert "EXACT_CACHE" in opp.recommended_transformation


# ---------------------------------------------------------------------------
# 9. Discovery Experiment Suite Tests
# ---------------------------------------------------------------------------
def test_discovery_experiment_suite():
    suite = DiscoveryExperimentSuite()
    poly_exp = suite.run_polynomial_experiment(degree=8)
    assert poly_exp.is_verified is True
    assert poly_exp.measured_speedup >= 1.0
    assert poly_exp.fairness_verdict == "FAIR_BENCHMARK"


# ---------------------------------------------------------------------------
# 10. FastAPI Router Integration Tests
# ---------------------------------------------------------------------------
def test_discovery_router_endpoints():
    client = TestClient(app)

    # Capability Matrix
    resp = client.get("/api/v1/discovery/capability-matrix")
    assert resp.status_code == 200
    data = resp.json()
    assert "system_maturity_level" in data
    assert data["total_features"] >= 10

    # AlphaTensor 2x2x2
    resp_at = client.get("/api/v1/discovery/alphatensor/strassen-2x2x2")
    assert resp_at.status_code == 200
    data_at = resp_at.json()
    assert data_at["rank"] == 7
    assert data_at["is_exact"] is True

    # Fairness Check
    resp_fc = client.post("/api/v1/discovery/fairness-check", json={
        "input": [1, 2, 3],
        "output": [2, 4, 6],
        "ref_input": [1, 2, 3],
        "ref_output": [2, 4, 6],
        "cache_mode": "COLD",
    })
    assert resp_fc.status_code == 200
    assert resp_fc.json()["is_fair"] is True
