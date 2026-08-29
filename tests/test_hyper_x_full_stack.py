"""
tests/test_hyper_x_full_stack.py
=============================================================================
Unit & Integration Tests for HYPER-X (Computation Invention Engine)
=============================================================================
"""

import pytest
import numpy as np

from hyper_x.contract_miner import ContractMiner, WorkloadContract
from hyper_x.necessity_map import NecessityMap
from hyper_x.algorithmic_escape_search import AlgorithmicEscapeSearch
from hyper_x.falsification_loop import ScientificFalsificationLoop
from hyper_x.proof_engine import HeterogeneousProofEngine
from hyper_x.engine import HyperXEngine

def test_contract_miner_domains():
    miner = ContractMiner()
    
    mat_contract = miner.mine_contract("matrix", np.zeros((10, 10)), {"epsilon": 1e-4})
    assert mat_contract.domain == "matrix"
    assert mat_contract.tolerance_epsilon == 1e-4

    gfx_contract = miner.mine_contract("graphics", np.zeros((256, 256)), {"min_ssim": 0.95})
    assert gfx_contract.domain == "graphics"
    assert gfx_contract.min_ssim == 0.95
    assert gfx_contract.max_latency_ms == pytest.approx(16.67, rel=1e-2)

    nlp_contract = miner.mine_contract("language", "Sample query prompt")
    assert nlp_contract.domain == "language"

def test_necessity_map_classification():
    nmap = NecessityMap(sparsity_threshold=1e-3)
    
    # Test sparse matrix (50% zeros)
    A_sparse = np.random.randn(32, 32).astype(np.float32)
    A_sparse[:16, :] = 0.0
    B = np.random.randn(32, 32).astype(np.float32)
    
    nodes = nmap.analyze_tensor_operation("sparse_test", A_sparse, B)
    assert len(nodes) > 0
    assert nodes[0].necessity_class in ("REDUNDANT", "PREDICTABLE")

    summary = nmap.compute_elimination_summary(nodes)
    assert summary["compute_elimination_ratio"] > 0.0

def test_algorithmic_escape_search_matrix():
    search = AlgorithmicEscapeSearch()
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    forms = search.generate_formulations_for_matrix_op(A, B, contract_epsilon=1e-2)
    assert len(forms) >= 5

    for f in forms:
        out, meta = f.execute_fn()
        assert out.shape == (32, 32)
        assert "cer" in meta or "latency_ms" in meta

def test_falsification_loop_ranking_and_reinforcement():
    loop = ScientificFalsificationLoop()
    
    # Record a failure
    loop.record_falsification(
        domain="matrix",
        formulation_id="FORM_SPARSE",
        formulation_name="Sparse Zero-Skipping",
        failure_mode="TOLERANCE_VIOLATION",
        measured_val=0.05,
        threshold_val=0.01,
        diagnosis="Error exceeded bound",
        adaptation="Use low-rank"
    )
    assert loop.formulation_scores["FORM_SPARSE"] < 1.0

    # Record a success on another formulation
    loop.record_success("FORM_RESIDUAL", cer=0.80)
    assert loop.formulation_scores["FORM_RESIDUAL"] > 1.5

    summary = loop.get_falsification_summary()
    assert summary["total_falsifications_recorded"] == 1

def test_heterogeneous_proof_engine():
    proof = HeterogeneousProofEngine(shared_mem_mb=32)
    contract = WorkloadContract(domain="matrix", tolerance_epsilon=1e-2)

    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    C_exact = A @ B

    # Candidate with slight noise
    C_candidate = C_exact + (np.random.randn(32, 32) * 0.0001).astype(np.float32)
    verified, q_score, meta = proof.prove_matrix_result(C_candidate, A, B, contract)

    assert verified is True
    assert q_score > 0.99
    assert meta["proof_method"] == "FREIVALDS_O(N^2)_PROOF"

def test_hyper_x_engine_matrix_challenge():
    engine = HyperXEngine()
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)

    result, telemetry = engine.execute_matrix_challenge(A, B, {"epsilon": 1e-2})

    assert telemetry["contract_verified"] is True
    assert telemetry["application_parity_pct"] >= 99.0
    assert "formulation_selected" in telemetry
    rel_error = float(np.linalg.norm(result - A @ B) / np.linalg.norm(A @ B))
    assert rel_error <= 1e-2

def test_hyper_x_engine_graphics_challenge():
    engine = HyperXEngine()
    H, W = 64, 64
    x, y = np.meshgrid(np.linspace(0, 1, W), np.linspace(0, 1, H))
    base = (0.5 * (x + y)).astype(np.float32)

    prev_frame = np.copy(base)
    gt_frame = np.copy(base)
    gt_frame[10:30, 10:30] = 0.9

    noisy_4spp = np.clip(gt_frame + (np.random.randn(H, W) * 0.05).astype(np.float32), 0.0, 1.0)

    result_frame, telemetry = engine.execute_graphics_challenge(
        prev_frame=prev_frame,
        current_noisy_4spp=noisy_4spp,
        ground_truth_100spp=gt_frame,
        target_fps=60.0
    )

    assert telemetry["contract_verified"] is True
    assert telemetry["application_parity_pct"] >= 99.0
    assert telemetry["achieved_fps"] >= 60.0
    assert telemetry["ssim"] >= 0.92
