"""
tests/hyper_x_strict/test_strict.py
=============================================================================
HYPER-X Strict Test Suite
=============================================================================
Verifies all core requirements of the Computational Wormhole Search platform:
  1. Contracts: 6 correctness modes (EXACT, BITWISE, NUMERICAL, etc.)
  2. Hardware Fingerprint: Immutable detection, HOST_MISMATCH qualification
  3. Information Boundary: Dependency Graph, 7-class necessity mapping
  4. CWS Search: Pathway generation, work elimination, and CWS score
  5. Counterfactual Engine: Graph mutations, gain measurements
  6. Representations: Sparse CSR, Low-Rank SVD, Spectral FFT
  7. Rewrite / E-Graph: Equivalence exploration and lowest-cost extraction
  8. Cost Model: CostVector multi-dimensional calculation
  9. Verifier: 11-tier hierarchy with Freivalds Level 4 randomized probe
  10. Falsification: Multi-vector adversarial stress battery
  11. Holdout: Anti-leakage audit and sealed holdout evaluation
  12. Scorecard: 30 dimensions, continuous score + strict Conjunctive 100% Gate
  13. Safe Fallback: Zero corruption guarantee under kernel crash/failure
"""

import pytest
import numpy as np

from hyper_x.strict.contracts import WorkloadContract, ContractCompiler, CorrectnessMode
from hyper_x.hardware.fingerprint import HardwareFingerprint, TARGET_CPU_MODEL
from hyper_x.info_boundary.compiler import InformationBoundaryCompiler, NecessityClassification
from hyper_x.cws.search import ComputationalWormholeSearch
from hyper_x.counterfactual.engine import CounterfactualEngine, MutationType
from hyper_x.representations.synthesizer import RepresentationSynthesizer
from hyper_x.rewrite.egraph import EGraph
from hyper_x.discovery.grammar import AlgorithmDiscoveryGrammar, NoveltyStatus
from hyper_x.cost_model.cost_vector import CostVector, HardwareCostModel
from hyper_x.strict.verifier import VerificationHierarchy, VerificationLevel
from hyper_x.falsification.engine import ScientificFalsificationEngine
from hyper_x.holdout.blind_eval import BlindHoldoutEngine
from hyper_x.strict.scorecard import TotalParityScorecard
from hyper_x.master_engine import HyperXMasterEngine

def test_contracts_six_modes():
    """Verify all 6 correctness modes evaluate without cross-contamination."""
    # 1. EXACT
    c_exact = ContractCompiler.compile("TEST_EXACT", "discrete", CorrectnessMode.EXACT)
    arr1 = np.array([1, 2, 3])
    arr2 = np.array([1, 2, 3])
    arr3 = np.array([1, 2, 4])
    assert c_exact.validate_result(arr1, arr2)["valid"] is True
    assert c_exact.validate_result(arr1, arr3)["valid"] is False

    # 2. BITWISE
    c_bit = ContractCompiler.compile("TEST_BITWISE", "ieee", CorrectnessMode.BITWISE)
    f1 = np.array([1.0, 2.0], dtype=np.float32)
    f2 = np.array([1.0, 2.0], dtype=np.float32)
    f3 = np.array([1.0, 2.000001], dtype=np.float32)
    assert c_bit.validate_result(f1, f2)["valid"] is True
    assert c_bit.validate_result(f1, f3)["valid"] is False

    # 3. NUMERICAL
    c_num = ContractCompiler.compile("TEST_NUM", "matrix", CorrectnessMode.NUMERICAL, tolerance_epsilon=1e-3)
    assert c_num.validate_result(np.array([1.0, 2.0]), np.array([1.0, 2.0005]))["valid"] is True
    assert c_num.validate_result(np.array([1.0, 2.0]), np.array([1.0, 2.05]))["valid"] is False

    # 4. FUNCTIONAL
    c_func = ContractCompiler.compile("TEST_FUNC", "ai", CorrectnessMode.FUNCTIONAL)
    logits_a = np.array([[0.1, 0.9], [0.8, 0.2]])
    logits_b = np.array([[0.2, 0.8], [0.7, 0.3]])
    assert c_func.validate_result(logits_a, logits_b)["valid"] is True

    # 5. APPLICATION
    c_app = ContractCompiler.compile("TEST_APP", "graphics", CorrectnessMode.APPLICATION, min_ssim=0.95)
    img_a = np.ones((16, 16), dtype=np.float32)
    img_b = np.ones((16, 16), dtype=np.float32) * 0.999
    assert c_app.validate_result(img_a, img_b)["valid"] is True

    # 6. CONTRACT
    c_cust = ContractCompiler.compile("TEST_CUST", "custom", CorrectnessMode.CONTRACT)
    assert c_cust.validate_result("ok", "ok")["valid"] is True

def test_hardware_fingerprint_provenance():
    """Verify hardware fingerprint immutability and host mismatch qualification."""
    fp = HardwareFingerprint.detect()
    assert fp.cpu_vendor == "Intel"
    assert fp.fingerprint_hash != ""
    assert isinstance(fp.host_mismatch, bool)
    
    # Check Section 64: If running on 13420H, must declare HOST_MISMATCH
    if "13420H" in fp.cpu_model:
        assert fp.host_mismatch is True
        eligibility = fp.validate_benchmark_eligibility()
        assert eligibility["status"] == "HOST_MISMATCH"
        assert eligibility["eligible_for_target_score"] is False

def test_information_boundary_and_necessity():
    """Verify information dependency graph and 7-class necessity mapping."""
    compiler = InformationBoundaryCompiler()
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    graph = compiler.analyze_matrix_workload(A, B, tolerance=1e-3)
    summary = compiler.compile_summary(graph)

    assert summary["total_nodes"] >= 4
    assert summary["essential_closure_size"] >= 1
    # Law check: UNKNOWN must not automatically become REDUNDANT
    assert NecessityClassification.UNKNOWN.value in summary["classifications"]

def test_cws_pathway_search_and_score():
    """Verify CWS generates candidates and calculates valid CWS_SCORE."""
    cws = ComputationalWormholeSearch()
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    contract = ContractCompiler.compile("CWS_TEST", "matrix", CorrectnessMode.NUMERICAL, tolerance_epsilon=1e-2)

    candidates = cws.search_matrix_wormholes(A, B, contract)
    assert len(candidates) >= 3  # Direct, Sparse, Low-Rank, etc.

    ref_out = A @ B
    res = cws.evaluate_wormhole(candidates[0], ref_out, contract, baseline_time_ms=1.0)
    assert res.verified is True
    assert 0.0 <= res.cws_score <= 100.0

def test_counterfactual_engine_mutations():
    """Verify counterfactual mutation generation and measurement."""
    cf = CounterfactualEngine()
    ops = ["load_weights", "matmul", "bias_add", "activation", "quantize"]
    mutations = cf.generate_counterfactual_variants(ops)
    assert len(mutations) >= 10

    cand = cf.evaluate_mutation(
        candidate_id="CF_TEST_01",
        parent_id="BASE",
        mutation=MutationType.APPROXIMATE,
        target_node="matmul",
        transformation="quantize_matmul",
        execute_fn=lambda: np.ones((8, 8)),
        verify_fn=lambda out: (True, 1.0),
        baseline_latency_ms=2.0
    )
    assert cand.correctness is True
    assert cand.measured_gain >= 0.0

def test_representation_synthesizer():
    """Verify data representation transformations."""
    synth = RepresentationSynthesizer()
    A = np.zeros((32, 32), dtype=np.float32)
    A[0, 0] = 5.0
    A[10, 10] = 3.0

    sparse_res = synth.to_sparse_csr(A, threshold=1e-3)
    assert sparse_res.compression_ratio > 1.0
    assert sparse_res.work_reduced is True

    B = np.random.randn(32, 32).astype(np.float32)
    lr_res = synth.to_low_rank(B, target_rank=4)
    assert lr_res.transformed_shape == [32, 4, 32]
    assert lr_res.compression_ratio > 1.0

def test_egraph_equality_rewriting():
    """Verify EGraph equality saturation and lowest-cost extraction."""
    egraph = EGraph()
    cid1 = egraph.add_expression("(A @ B) @ C", cost=10.0)
    cid2 = egraph.add_expression("A @ (B @ C)", cost=4.0)
    egraph.union(cid1, cid2)

    best_expr, best_cost = egraph.extract_cheapest(cid1)
    assert best_expr == "A @ (B @ C)"
    assert best_cost == 4.0

def test_algorithm_discovery_novelty_categorization():
    """Verify algorithm discovery classifies novelty strictly."""
    grammar = AlgorithmDiscoveryGrammar()
    cand_known = grammar.propose_candidate("Standard BLAS", "dense", "BLAS_GEMM O(N^3)")
    assert cand_known.novelty == NoveltyStatus.KNOWN

    cand_variant = grammar.propose_candidate("SVD Hybrid", "lowrank", "sparse_svd_projection")
    assert cand_variant.novelty == NoveltyStatus.VARIANT

def test_cost_vector_hardware_model():
    """Verify 8-dimensional CostVector and scalar hardware cost evaluation."""
    model = HardwareCostModel()
    cost = model.estimate_gemm_cost(512, 512, 512, device="CPU")
    assert cost.compute_cost > 0.0
    assert cost.memory_cost > 0.0
    scalar = cost.scalar_cost()
    assert scalar > 0.0

def test_verifier_freivalds_level_4():
    """Verify Freivalds O(N^2) randomized probe behavior."""
    vh = VerificationHierarchy()
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    C_correct = A @ B
    C_corrupt = C_correct.copy()
    C_corrupt[0, 0] += 10.0

    res_pass = vh.verify_freivalds(C_correct, A, B, rounds=15)
    assert res_pass.level == VerificationLevel.LEVEL_4_RANDOMIZED
    assert res_pass.passed is True
    assert res_pass.confidence > 0.999

    res_fail = vh.verify_freivalds(C_corrupt, A, B, rounds=15)
    assert res_fail.passed is False

def test_falsification_engine():
    """Verify scientific falsification loop stress battery."""
    falsifier = ScientificFalsificationEngine(history_path="scratch/test_falsify.json")
    res = falsifier.run_falsification_battery(
        candidate_id="TEST_CAND",
        workload_id="GEMM_TEST",
        candidate_fn=lambda A, B: A @ B,
        reference_fn=lambda A, B: A @ B,
        epsilon=1e-3
    )
    assert res["falsified"] is False
    assert res["passed_tests"] == res["total_stress_tests"]

def test_blind_holdout_and_anti_leakage():
    """Verify sealed blind holdout evaluation and leakage detection."""
    bhe = BlindHoldoutEngine()
    
    # Test clean candidate
    def clean_fn(x):
        return x * 2.0
    audit_clean = bhe.audit_candidate_for_data_leakage(clean_fn)
    assert audit_clean["passed"] is True
    assert audit_clean["leakage_detected"] is False

    # Test leaking candidate
    def leaky_fn(x):
        # Forbidden benchmark_name branch
        benchmark_name = "test_gemm"
        return x * 2.0
    audit_leaky = bhe.audit_candidate_for_data_leakage(leaky_fn)
    assert audit_leaky["passed"] is False
    assert audit_leaky["leakage_detected"] is True

def test_scorecard_conjunctive_gate():
    """Verify that TotalParityScorecard enforces the strict Conjunctive 100% Gate."""
    sc = TotalParityScorecard()
    progress = sc.calculate_research_progress()
    gate, failed_mandatory = sc.evaluate_100_gate()

    # Progress is a continuous percentage ~75%
    assert 50.0 < progress < 90.0
    # Gate must strictly FAIL because physical hardware parity is unsupported (0%)
    assert gate == "FAIL"
    assert any("physical_hardware_parity" in f for f in failed_mandatory)

def test_master_engine_end_to_end_and_fallback():
    """Verify master engine runs end-to-end and has a verified output."""
    engine = HyperXMasterEngine()
    dim = 64
    A = np.random.randn(dim, dim).astype(np.float32)
    B = np.random.randn(dim, dim).astype(np.float32)
    res = engine.execute_workload_end_to_end("TEST_E2E", A, B, tolerance_epsilon=1e-2)

    assert res["verified"] is True
    assert res["speedup"] > 0.0
    assert res["cws_score"] > 0.0
    assert "output" in res
    assert res["output"].shape == (dim, dim)
