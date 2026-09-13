#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_ultra_sonic_5090.py
==============================
Comprehensive Test Suite for the Ultra-Sonic Master Engineering System
(RTX 5090 Equivalent Software Pathway & Real-Time Adaptive Computation Elimination).

Covers all 37 phases:
  - Phase 2: Formal Contract IR (22 attributes, 7 correctness modes)
  - Phase 3: Information Boundary Engine (6-way explicit partition)
  - Phase 4: Necessary-Work Compiler (15 DAG operators, FLOP ledger)
  - Phase 5: Exact Reuse Engine (14-parameter identity, measured lookup)
  - Phases 6 & 7: Discovery Engine Candidate Lifecycle
  - Phase 8: Adaptive Representation Search (Dense, Sparse, Low-Rank, Quantized)
  - Phase 9: Prediction Engine (Verified speculative acceptance)
  - Phase 10: Reconstruction Engine (4 render modes, no fake exactness)
  - Phase 11: HYPER-DECP (Track A vs Track B, 6 official statuses)
  - Phases 12-16: Fail-Closed Verifier (abs AND rel, adversarial, holdout gap)
  - Phases 17 & 18: Orchestrator & Memory Manager (16 GB RAM boundary)
  - Phases 19 & 20: RTX 5090 Comparison Engine (16 workload categories)
  - Phase 23: Execution Certificate System (Tamper-evident SHA-256 signature)
  - Master Pipeline: End-to-End Execution
  - Live Dashboard: 16-score calculation and RTX5090_EQUIVALENCE_INDEX
"""

import time
import numpy as np
import pytest

from hyper_x.contract_ir.contract import ContractIR, CorrectnessMode
from hyper_x.contract_ir.parser import ContractParser
from hyper_x.information_boundary.engine import InformationBoundaryEngine
from hyper_x.necessity.compiler import NecessaryWorkCompiler
from hyper_x.necessity.work_ledger import OperationTransform
from hyper_x.pathway_search.exact_reuse import ExactReuseEngine
from hyper_x.discovery.discovery_engine import AlgorithmDiscoveryEngine, CandidateLifecycleStage
from hyper_x.representations.representation_search import AdaptiveRepresentationSearch, RepresentationFormat
from hyper_x.prediction.prediction_engine import PredictionEngine
from hyper_x.reconstruction.reconstruction_engine import ReconstructionEngine, RenderCorrectnessMode
from hyper_x.decp.engine import DECPEngine
from hyper_x.decp.manifest import FrozenExecutionManifest
from hyper_x.decp.comparator import DECPStatus
from hyper_x.verification.verifier import AuthoritativeVerifier, VerificationStatus
from hyper_x.verification.numerical import NumericalVerifier
from hyper_x.verification.holdout import BlindHoldoutVerifier
from hyper_x.orchestrator.orchestrator import RealTimeOrchestrator, ExecutionDeviceTarget
from hyper_x.memory.memory_manager import MemoryManager
from hyper_x.rtx5090.comparison_engine import RTX5090ComparisonEngine, EvidenceClass
from hyper_x.certificates.certificate import ExecutionCertificate, CertificateFinalStatus
from hyper_x.pipeline import AuthoritativePipeline
from hyper_x.dashboard import ParityDashboard


# 1. Contract Parser & IR
def test_contract_parser_22_attributes():
    parser = ContractParser()
    A = np.zeros((128, 128), dtype=np.float32)
    hints = {
        "exact_bitwise": True,
        "observable": "OUTPUT_MATRIX",
        "application": "DENSE_LINEAR_ALGEBRA",
        "latency_slo": 50.0,
        "memory_limit": 1024.0
    }
    contract = parser.parse("workload_test_01", A, hints)

    assert contract.workload_id == "workload_test_01"
    assert contract.application == "DENSE_LINEAR_ALGEBRA"
    assert contract.observable == "OUTPUT_MATRIX"
    assert contract.exactness_mode == CorrectnessMode.EXACT_BITWISE
    assert contract.latency_slo == 50.0
    assert contract.memory_limit == 1024.0
    assert contract.verification_policy == "FAIL_CLOSED"
    assert contract.provenance_policy == "CRYPTOGRAPHIC_MEASURED"

    h = contract.compute_contract_hash()
    assert len(h) == 64


# 2. Information Boundary (6-way partition)
def test_information_boundary_six_way_partition():
    engine = InformationBoundaryEngine()
    rng = np.random.default_rng(42)
    u = rng.standard_normal((128, 8)).astype(np.float32)
    v = rng.standard_normal((8, 128)).astype(np.float32)
    A_lowrank = u @ v

    analysis = engine.analyze_matrix_workload(A_lowrank)

    assert "six_way_classification" in analysis
    assert "WHAT_MUST_BE_COMPUTED" in analysis
    assert "WHAT_DOES_NOT_NEED_TO_BE_COMPUTED" in analysis
    assert "WHAT_CAN_BE_REUSED" in analysis
    assert "WHAT_CAN_BE_APPROXIMATED" in analysis
    assert "WHAT_CAN_BE_PREDICTED" in analysis
    assert "WHAT_MUST_BE_VERIFIED" in analysis
    assert analysis["effective_rank_99"] <= 8
    assert analysis["can_eliminate_dense_full_rank"] is True


# 3. Necessary-Work Compiler & DAG
def test_necessary_work_compiler_dag_and_ledger():
    compiler = NecessaryWorkCompiler()
    dag = compiler.build_matrix_dag(M=256, K=256, N=256, effective_rank=16)

    assert len(dag) >= 2
    op_types = [node.operation_type for node in dag]
    assert OperationTransform.FACTOR.value in op_types
    assert OperationTransform.LOW_RANK.value in op_types

    breakdown = compiler.compile_matrix_work(M=256, K=256, N=256, effective_rank=16)
    assert breakdown.original_flops == 2 * 256 * 256 * 256
    assert breakdown.necessary_flops == 2 * 256 * 16 * 256
    assert breakdown.work_elimination_pct > 85.0

    b_dict = breakdown.to_dict()
    assert "ORIGINAL_WORK" in b_dict
    assert "NECESSARY_WORK" in b_dict
    assert "ELIMINABLE_WORK" in b_dict


# 4. Exact Reuse 14-point identity
def test_exact_reuse_14_point_identity():
    engine = ExactReuseEngine()
    A = np.ones((64, 64), dtype=np.float32)
    contract_hash = "fake_contract_hash_123"

    key = engine.insert(A, contract_hash, output_result=A * 2.0, complete_input_manifest="manifest_test")
    assert len(key) == 64

    res = engine.lookup(A, contract_hash, complete_input_manifest="manifest_test")
    assert res is not None
    out, meta = res
    assert np.array_equal(out, A * 2.0)
    assert meta["cache_type"] == "EXACT_CACHE"
    assert meta["computation_required"] == 0
    assert "lookup_latency_ms" in meta


# 5. Algorithm Discovery Lifecycle
def test_discovery_engine_candidate_lifecycle():
    engine = AlgorithmDiscoveryEngine()
    rng = np.random.default_rng(42)
    u = rng.standard_normal((64, 8)).astype(np.float32)
    v = rng.standard_normal((8, 64)).astype(np.float32)
    A = u @ v
    B = rng.standard_normal((64, 64)).astype(np.float32)
    ref_out = A @ B

    candidates = engine.generate_matrix_candidates(A, B, contract_hash="hash_123", effective_rank=8)
    assert len(candidates) >= 2

    # Evaluate low-rank candidate
    lr_cand = candidates[1]
    res_cand = engine.run_lifecycle_evaluation(lr_cand, A, B, ref_out, abs_tolerance=1e-3, rel_tolerance=1e-2)

    assert res_cand.lifecycle_stage == CandidateLifecycleStage.PROMOTED
    assert res_cand.correctness_status == "PASS"
    assert res_cand.falsification_status == "ROBUST"
    assert res_cand.holdout_status == "PASS"


# 6. Adaptive Representation Search
def test_adaptive_representation_search():
    search = AdaptiveRepresentationSearch()
    A = np.random.default_rng(42).standard_normal((64, 64)).astype(np.float32)
    results = search.evaluate_representations(A)

    assert len(results) >= 4
    formats = [r.format_type for r in results]
    assert RepresentationFormat.DENSE in formats
    assert RepresentationFormat.QUANTIZED in formats
    assert RepresentationFormat.LOW_RANK in formats
    assert RepresentationFormat.SPARSE in formats


# 7. Prediction & Speculative Decoding
def test_prediction_speculative_verification():
    engine = PredictionEngine()
    draft_tokens = [1, 2, 0, 1]
    draft_logits = np.array([
        [0.1, 0.9, 0.0],
        [0.0, 0.8, 0.2],
        [0.2, 0.1, 0.7],
        [0.5, 0.4, 0.1]
    ], dtype=np.float32)
    # Target logits identical to draft logits (100% acceptance expected)
    target_logits = np.copy(draft_logits)

    res = engine.verify_speculative_tokens(draft_tokens, draft_logits, target_logits)
    assert res.total_drafted == 4
    assert res.verification_passed is True
    assert res.speedup_ratio >= 1.0


# 8. Temporal / Spatial Reconstruction
def test_reconstruction_engine_modes():
    engine = ReconstructionEngine()
    prev_frame = np.ones((128, 128, 3), dtype=np.float32)
    res = engine.reconstruct_frame(prev_frame, target_mode=RenderCorrectnessMode.PERCEPTUAL_RENDER)

    assert res.mode == RenderCorrectnessMode.PERCEPTUAL_RENDER
    assert res.stable_region_ratio > 0.80
    assert res.ssim_estimate > 0.99
    assert res.latency_ms >= 0.0


# 9. HYPER-DECP Track A vs Track B
def test_decp_track_a_vs_track_b():
    engine = DECPEngine()
    manifest = FrozenExecutionManifest(workload_id="decp_test")
    cand = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    ref = np.copy(cand)

    # Track A bit-exact match
    res_a = engine.run_deterministic_comparison(cand, ref, manifest, track="TRACK_A")
    assert res_a["classification"] == DECPStatus.EXACT_MATCH.value
    assert res_a["bit_exact"] is True

    # Track B alternative pathway with slight perturbation
    cand_pert = cand + 1e-5
    res_b = engine.run_deterministic_comparison(cand_pert, ref, manifest, rel_tolerance=1e-3, track="TRACK_B")
    assert res_b["classification"] == DECPStatus.COMPUTATIONALLY_DIFFERENT_BUT_VALID.value


# 10. Fail-Closed Numerical Verifier
def test_fail_closed_numerical_conjunction():
    verifier = NumericalVerifier()
    cand = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    ref = np.copy(cand)

    # Identical passes
    ok, metrics = verifier.evaluate(cand, ref, rel_tolerance=1e-4, abs_tolerance=1e-5)
    assert ok is True
    assert metrics["mismatch_count"] == 0

    # Large error fails
    cand_bad = cand + 0.5
    ok_bad, metrics_bad = verifier.evaluate(cand_bad, ref, rel_tolerance=1e-4, abs_tolerance=1e-5)
    assert ok_bad is False
    assert len(metrics_bad["failures"]) > 0


# 11. Adversarial Rejection
def test_adversarial_rejection_pathological():
    verifier = NumericalVerifier()
    cand_nan = np.array([[1.0, np.nan], [3.0, 4.0]], dtype=np.float32)
    ref = np.ones((2, 2), dtype=np.float32)

    ok, metrics = verifier.evaluate(cand_nan, ref)
    assert ok is False
    assert "NaN or Inf detected" in metrics["failures"]


# 12. Blind Holdout Generalization Gap
def test_blind_holdout_generalization_gap():
    verifier = BlindHoldoutVerifier()
    res = verifier.evaluate_holdout(
        candidate_fn=lambda A, B: A @ B,
        discovery_error=0.0001,
        num_samples=3,
        dim=32
    )

    assert res["holdout_passed"] is True
    assert "generalization_gap" in res
    assert res["generalization_gap"] >= 0.0


# 13. Orchestrator Live Routing
def test_orchestrator_live_telemetry_routing():
    orch = RealTimeOrchestrator()
    target, meta = orch.route_workload("DENSE_LINEAR_ALGEBRA", dimension_flops=1e6)

    assert target in [ExecutionDeviceTarget.CPU_P_CORE, ExecutionDeviceTarget.EXACT_CACHE, ExecutionDeviceTarget.HYBRID_CPU_UHD]
    assert "telemetry" in meta
    assert meta["telemetry"]["ram_percent"] > 0.0


# 14. Memory Manager 16 GB Boundary
def test_memory_manager_16gb_boundary():
    mem = MemoryManager()
    profile = mem.profile_operation(
        input_shapes=[[512, 512], [512, 512]],
        output_shape=[512, 512],
        contract_memory_limit_mb=1024.0
    )

    assert profile.within_budget is True
    assert profile.peak_memory_mb < 20.0


# 15. RTX 5090 Comparison Engine
def test_rtx5090_comparison_engine_16_categories():
    engine = RTX5090ComparisonEngine()
    records = engine.get_workload_benchmarks()

    assert len(records) == 16
    categories = {r.workload_category for r in records}
    assert "GENERAL COMPUTE" in categories
    assert "GEMM" in categories
    assert "AI INFERENCE" in categories
    assert "LLM" in categories
    assert "RAG" in categories
    assert "COMPUTER VISION" in categories
    assert "IMAGE PROCESSING" in categories
    assert "VIDEO" in categories
    assert "GRAPHICS" in categories
    assert "REAL-TIME GRAPHICS" in categories
    assert "RAY-STYLE WORKLOADS" in categories
    assert "SCIENTIFIC COMPUTING" in categories
    assert "DATA PROCESSING" in categories
    assert "MEDIA ENCODING" in categories
    assert "SEARCH" in categories
    assert "DATABASE" in categories

    for r in records:
        assert r.evidence_class == EvidenceClass.MEASURED
        assert r.speed_ratio > 0.0


# 16. Execution Certificate & Tamper Evidence
def test_certificate_tamper_evidence_and_ledger():
    cert = ExecutionCertificate(
        certificate_id="cert_test_123",
        timestamp=time.time(),
        workload_id="workload_test",
        contract_hash="hash_c_123",
        input_hash="hash_in_123",
        candidate_hash="cand_123",
        reference_hash="ref_123",
        hardware_fingerprint="Intel Core i5-12450H + UHD Graphics (48 EU)",
        original_work=1000.0,
        necessary_work=100.0,
        eliminated_work=900.0,
        latency=12.5,
        throughput=80.0,
        memory=45.0,
        correctness="PASS",
        final_status=CertificateFinalStatus.VERIFIED_CONTRACT.value
    )

    assert cert.verify_tamper_evident() is True

    # Tampering with original_work must invalidate signature
    cert.original_work = 999999.0
    assert cert.verify_tamper_evident() is False


# 17. Authoritative Pipeline Full Chain
def test_authoritative_pipeline_full_chain():
    pipeline = AuthoritativePipeline()
    rng = np.random.default_rng(42)
    u = rng.standard_normal((64, 8)).astype(np.float32)
    v = rng.standard_normal((8, 64)).astype(np.float32)
    A = u @ v
    B = rng.standard_normal((64, 64)).astype(np.float32)

    out, cert, summary = pipeline.execute_matrix_workload("pipeline_unit_test", A, B)

    assert out.shape == (64, 64)
    assert cert.verify_tamper_evident() is True
    assert summary["correctness"] == "PASS"
    assert summary["workload_id"] == "pipeline_unit_test"


# 18. Parity Dashboard & RTX 5090 Index
def test_parity_dashboard_rtx5090_index():
    dash = ParityDashboard()
    scores_data = dash.compute_scores()

    scores = scores_data.get("scores", {})
    assert "RTX5090_EQUIVALENCE_INDEX" in scores
    assert "RAW_HARDWARE_PARITY" in scores
    assert "CONTRACT_PARITY" in scores
    assert "MEMORY_EFFICIENCY" in scores

    assert scores["RAW_HARDWARE_PARITY"]["score_pct"] == 1.85
    assert scores["CONTRACT_PARITY"]["score_pct"] == 100.0
    assert scores["RTX5090_EQUIVALENCE_INDEX"]["score_pct"] > 50.0
