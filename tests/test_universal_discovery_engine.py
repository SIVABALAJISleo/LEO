"""
tests/test_universal_discovery_engine.py
========================================
Comprehensive Unit & Integration Test Suite for UCTDE:
Universal Computational Transformation, Discovery & Equivalence Engine.

Covers:
  1. Epistemic state separation (TARGET != PROVEN FACT)
  2. Computational Knowledge Graph DAG traversal and JSON serialization
  3. SymPy Proof Discovery Engine (Horner equivalence, matrix associativity)
  4. Mandatory Adversarial Counterexample Gauntlet & Delta-debugging minimization
  5. Universality Ladder (Levels 0-7) and Boundary Condition derivation
  6. Meta-Search Strategy Selector and Saturation Detection
  7. Physical Resource Transcendence model vs RTX 5090 Blackwell
  8. Hostile Self-Critique Auditor
  9. Self-Improving Transformation Library
 10. End-to-End Universal Discovery Loop
 11. Discovery REST API endpoints
"""

import os
import json
import pytest
import numpy as np
from fastapi.testclient import TestClient

from hyper.discovery.hypotheses import EpistemicState, UniversalityLevel, ResearchHypothesis, TargetStatus
from hyper.discovery.knowledge_graph import ComputationalKnowledgeGraph, NodeType, EdgeType
from hyper.discovery.proof_engine import ProofDiscoveryEngine, ProofStatus
from hyper.discovery.counterexample_engine import CounterexampleDiscoveryEngine, CounterexampleDatabase, Counterexample
from hyper.discovery.universality_ladder import UniversalityLadder, UniversalityBoundaryEngine
from hyper.discovery.meta_search import MetaSearchEngine, SearchStrategyType
from hyper.discovery.resource_transcendence import ResourceTranscendenceEngine, ResourceVector
from hyper.discovery.self_critique import SelfCritiqueEngine
from hyper.discovery.transformation_library import TransformationLibrary, TransformationRule
from hyper.discovery.loop import UniversalDiscoveryLoop
from hyper.discovery.engine import UniversalComputationalDiscoveryEngine
from backend.main import app


# 1. Epistemic State & Hypothesis Tests
def test_epistemic_states_and_hypotheses():
    hyp = ResearchHypothesis(
        title="Linear Sorting Hypothesis",
        formal_statement="Sorting bounded integers can be achieved in O(N+K) time.",
        target_domain="BOUNDED_SORTING",
        epistemic_state=EpistemicState.HYPOTHESIS,
    )
    assert hyp.epistemic_state == EpistemicState.HYPOTHESIS
    assert hyp.universality_level == UniversalityLevel.LEVEL_0_CANDIDATE

    # Record evidence
    hyp.record_evidence("exp-1")
    assert hyp.epistemic_state == EpistemicState.EVIDENCE

    # Record proof
    hyp.record_proof("proof-1", ["Exact integer bounds"])
    assert hyp.epistemic_state == EpistemicState.PROOF
    assert hyp.universality_level >= UniversalityLevel.LEVEL_6_FORMAL_PROOF_UNDER_ASSUMPTIONS

    # Attack with counterexample -> Demotion occurs
    hyp.record_counterexample("cx-1", "Fails when keys are unbounded floating point")
    assert hyp.epistemic_state == EpistemicState.COUNTEREXAMPLE
    assert hyp.universality_level <= UniversalityLevel.LEVEL_1_VERIFIED_EXAMPLE


# 2. Computational Knowledge Graph Tests
def test_computational_knowledge_graph(tmp_path):
    kg = ComputationalKnowledgeGraph()
    w_node = kg.add_node("w-1", NodeType.WORKLOAD, "DenseGEMM", dimension=256)
    h_node = kg.add_node("h-1", NodeType.HYPOTHESIS, "FactoredGEMMHypothesis")
    p_node = kg.add_node("p-1", NodeType.PATHWAY, "LowRankSVD")

    kg.add_edge(h_node.node_id, w_node.node_id, EdgeType.INVESTIGATES)
    kg.add_edge(h_node.node_id, p_node.node_id, EdgeType.PROPOSES_PATHWAY)

    assert len(kg.nodes) == 3
    assert len(kg.edges) == 2

    neighbors = kg.get_neighbors(h_node.node_id)
    assert len(neighbors) == 2
    assert {n.node_id for n in neighbors} == {"w-1", "p-1"}

    # File persistence
    save_file = str(tmp_path / "kg_test.json")
    kg.save_to_file(save_file)
    loaded_kg = ComputationalKnowledgeGraph.load_from_file(save_file)
    assert len(loaded_kg.nodes) == 3
    assert len(loaded_kg.edges) == 2


# 3. SymPy Proof Discovery Engine Tests
def test_proof_engine_sympy_horner():
    engine = ProofDiscoveryEngine()
    cert = engine.attempt_polynomial_horner_proof(degree=8)
    assert cert.status == ProofStatus.FORMALLY_PROVED
    assert cert.algebraic_diff_zero is True
    assert cert.theorem_statement is not None
    assert "Horner" in cert.claim


def test_proof_engine_matrix_associativity():
    engine = ProofDiscoveryEngine()
    cert = engine.attempt_matrix_associativity_proof()
    assert cert.status == ProofStatus.FORMALLY_PROVED
    assert cert.algebraic_diff_zero is True
    assert "U (V B)" in cert.theorem_statement


def test_proof_engine_unproven_claim():
    engine = ProofDiscoveryEngine()
    cert = engine.attempt_arbitrary_claim_proof("Universal Arbitrary Speedup", ["No assumptions"])
    assert cert.status == ProofStatus.PROOF_NOT_ESTABLISHED
    assert cert.algebraic_diff_zero is False
    assert "PROOF_NOT_ESTABLISHED" in cert.symbolic_derivation[-1]


# 4. Mandatory Adversarial Counterexample Engine Tests
def test_counterexample_engine_adversarial_suite():
    engine = CounterexampleDiscoveryEngine()
    suite = engine.generate_adversarial_inputs("NUMERICAL_POLYNOMIAL")
    names = [name for name, _ in suite]
    assert "extreme_dynamic_range" in names
    assert "cauchy_noise" in names


def test_counterexample_engine_catches_divergent_candidate():
    engine = CounterexampleDiscoveryEngine()
    ref_fn = lambda x: x * 2.0
    # Buggy candidate that overflows on Cauchy/extreme inputs
    def buggy_cand(x):
        if np.any(np.abs(x) > 1e10):
            return x * 999.0
        return x * 2.0

    cx = engine.attack_pathway(
        candidate_callable=buggy_cand,
        reference_callable=ref_fn,
        domain="NUMERICAL_POLYNOMIAL",
        hypothesis_id="hyp-test",
    )
    assert cx is not None
    assert cx.failure_mode == "NUMERICAL_DIVERGENCE"
    assert len(engine.db.all()) >= 1


# 5. Universality Ladder & Boundary Engine Tests
def test_universality_ladder_climb():
    hyp = ResearchHypothesis(
        title="Test Principle",
        formal_statement="Statement",
        target_domain="TEST",
    )

    # 0 runs -> Level 0
    lvl0 = UniversalityLadder.evaluate_level(hyp, 0, 0)
    assert lvl0 == UniversalityLevel.LEVEL_0_CANDIDATE

    # 1 run -> Level 1
    lvl1 = UniversalityLadder.evaluate_level(hyp, 1, 1)
    assert lvl1 == UniversalityLevel.LEVEL_1_VERIFIED_EXAMPLE

    # 15 runs, 3 families -> Level 3
    lvl3 = UniversalityLadder.evaluate_level(hyp, 15, 3)
    assert lvl3 == UniversalityLevel.LEVEL_3_MULTIPLE_WORKLOAD_FAMILIES

    # Counterexample present -> demotes to Level 1
    cx = Counterexample(
        hypothesis_id=hyp.hypothesis_id,
        workload_domain="TEST",
        failure_mode="NUMERICAL",
        input_summary="Broken",
        minimal_input_repr="[1]",
        error_magnitude=10.0,
        explanation="Counterexample found",
    )
    demoted = UniversalityLadder.evaluate_level(hyp, 15, 3, counterexamples=[cx])
    assert demoted == UniversalityLevel.LEVEL_1_VERIFIED_EXAMPLE


def test_universality_boundary_engine():
    hyp = ResearchHypothesis(title="Boundary Test", formal_statement="S", target_domain="SORTING")
    boundary_eng = UniversalityBoundaryEngine()
    cx = Counterexample(
        hypothesis_id=hyp.hypothesis_id,
        workload_domain="SORTING",
        failure_mode="NUMERICAL_DIVERGENCE",
        input_summary="Overflow on large numbers",
        minimal_input_repr="[1e20]",
        error_magnitude=1e20,
        explanation="Keys exceed dynamic range",
    )
    report = boundary_eng.analyze_boundary(
        hypothesis=hyp,
        satisfying=["BoundedKeys_K100"],
        violating=["LargeKeys_K1e20"],
        counterexamples=[cx],
    )
    assert report.is_universal_theorem is False
    assert len(report.applicability_conditions) > 0
    assert "dynamic range" in report.boundary_separation_property.lower() or len(report.applicability_conditions) > 0


# 6. Meta-Search Strategy Selector & Saturation Tests
def test_meta_search_efficiency_and_saturation():
    meta = MetaSearchEngine()
    strat = meta.select_strategy("NUMERICAL_POLYNOMIAL", budget_candidates=100)
    assert strat == SearchStrategyType.PROGRAM_SYNTHESIS

    # Record diminishing returns
    for i in range(20):
        meta.record_evaluation(
            strategy=strat,
            domain="NUMERICAL_POLYNOMIAL",
            best_cost=1.000001,
            cost_reduction=0.0000001,
            step_time_ms=1.5,
            is_breakthrough=False,
        )

    sat = meta.check_saturation(window_size=15, cost_threshold=1e-4)
    assert sat.is_saturated is True
    assert sat.epistemic_verdict == "SEARCH_SATURATED"


# 7. Physical Resource Transcendence Model Tests
def test_resource_transcendence_model():
    engine = ResourceTranscendenceEngine()
    baseline_flops = 1e9  # 1 GFLOP
    candidate_resources = ResourceVector(
        operations_flops=1e7,  # 10 MFLOP (99% work reduction)
        memory_bytes=100 * 1024**2,
        bandwidth_required_gbps=2.0,
        parallelism_degree=8,
        synchronization_points=1,
        measured_latency_ms=0.05,
    )
    verdict = engine.evaluate_transcendence(
        baseline_flops=baseline_flops,
        candidate_resources=candidate_resources,
        rtx_projected_latency_ms=0.10,
    )
    assert verdict.is_feasible_on_local_system is True
    assert verdict.is_transcendence_achieved is True
    assert verdict.contract_parity_ratio >= 1.0


# 8. Hostile Self-Critique Auditor Tests
def test_self_critique_auditor():
    critique = SelfCritiqueEngine()
    report = critique.audit_discovery(
        contract_exactness="EXACT",
        observed_error=1e-12,
        allowed_tolerance=1e-5,
        is_independent_verifier=True,
        is_cache_flushed=True,
        adversarial_counterexample_found=False,
        trials_variance_ratio=0.05,
        dimension_generalized=True,
    )
    assert report.passed_all_scrutiny is True
    assert report.risk_score < 0.20
    assert report.verdict == "RIGOROUS_DISCOVERY_CONFIRMED"

    # Failing audit: cache not flushed + counterexample found
    failing_report = critique.audit_discovery(
        contract_exactness="EXACT",
        observed_error=1e-12,
        allowed_tolerance=1e-5,
        is_independent_verifier=True,
        is_cache_flushed=False,
        adversarial_counterexample_found=True,
        trials_variance_ratio=0.35,
        dimension_generalized=False,
    )
    assert failing_report.passed_all_scrutiny is False
    assert failing_report.risk_score > 0.50


# 9. Transformation Library Tests
def test_transformation_library():
    lib = TransformationLibrary()
    rules = lib.all_rules()
    assert len(rules) >= 3
    matched = lib.match_rules("NUMERICAL_POLYNOMIAL")
    assert len(matched) >= 1
    assert any("Horner" in r.name for r in matched)


# 10. End-to-End Universal Discovery Loop Tests
def test_end_to_end_discovery_loop():
    engine = UniversalComputationalDiscoveryEngine()
    coeffs = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
    sample_x = np.linspace(-1.0, 1.0, 100, dtype=np.float32)

    def naive_poly(x):
        res = np.zeros_like(x)
        for i, c in enumerate(coeffs):
            res += c * (x ** i)
        return res

    res = engine.discover(
        workload_fn=naive_poly,
        sample_input=sample_x,
        workload_name="PolyDegree4",
        domain_hint="NUMERICAL_POLYNOMIAL",
        max_candidates=10,
        metadata={"coeffs": coeffs},
    )
    assert res.is_verified is True
    assert res.measured_speedup >= 1.0
    assert res.proof_status in ("FORMALLY_PROVED", "PROOF_NOT_ESTABLISHED")
    assert engine.target_status.verified_workload_count >= 1


# 11. Discovery REST API Endpoints Tests
def test_discovery_rest_api_endpoints():
    client = TestClient(app)

    # 1. GET /api/v1/discovery/status
    res = client.get("/api/v1/discovery/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ONLINE"
    assert "target_status" in data

    # 2. POST /api/v1/discovery/prove
    res = client.post("/api/v1/discovery/prove", json={"claim_type": "polynomial_horner", "degree": 4})
    assert res.status_code == 200
    pdata = res.json()
    assert pdata["status"] == "FORMALLY_PROVED"

    # 3. POST /api/v1/discovery/search
    res = client.post("/api/v1/discovery/search", json={
        "workload_name": "APITestPoly",
        "domain": "NUMERICAL_POLYNOMIAL",
        "max_candidates": 5
    })
    assert res.status_code == 200
    sdata = res.json()
    assert sdata["is_verified"] is True
    assert sdata["measured_speedup"] >= 1.0

    # 4. GET /api/v1/discovery/knowledge-graph
    res = client.get("/api/v1/discovery/knowledge-graph")
    assert res.status_code == 200
    kg_data = res.json()
    assert "node_count" in kg_data
    assert "nodes" in kg_data
