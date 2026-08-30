"""
tests/test_c_gace_engine.py
=============================================================================
Tests for Contract-Gated Adaptive Computation Elimination (C-GACE)
=============================================================================
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from core_ai.c_gace_engine import CGACEEngine, ExecutionContract

client = TestClient(app)


def test_contract_dominance_logic():
    """Verifies contract dominance semantics."""
    tight_contract = ExecutionContract(metric="relative_l2_error", error_bound_eps=0.001, perceptual_threshold=0.98)
    loose_contract = ExecutionContract(metric="relative_l2_error", error_bound_eps=0.05, perceptual_threshold=0.90)
    
    assert tight_contract.dominates(loose_contract) is True
    assert loose_contract.dominates(tight_contract) is False

    different_metric = ExecutionContract(metric="ssim", error_bound_eps=0.001)
    assert tight_contract.dominates(different_metric) is False


def test_level_2_randomized_sketch_and_freivalds_probe():
    """Verifies Level 2 Low-Rank Sketch GEMM with Freivalds stochastic check."""
    engine = CGACEEngine()
    contract = ExecutionContract(metric="relative_l2_error", error_bound_eps=0.05)

    rng = np.random.RandomState(42)
    # Generate low-rank structured matrix
    U = rng.randn(128, 16).astype(np.float32)
    V = rng.randn(16, 128).astype(np.float32)
    A = U @ V + rng.randn(128, 128).astype(np.float32) * 0.0001
    B = rng.randn(128, 128).astype(np.float32)

    res = engine.execute_with_contract("matrix_gemm", A, contract, secondary_data=B)
    assert res["status"] == "ACCEPTED"
    assert res["level_executed"] in [0, 2]
    assert res["contract_satisfied"] is True
    assert res["verified_error"] <= contract.error_bound_eps


def test_level_0_contract_cache_hit():
    """Verifies Level 0 contract cache retrieval when stored contract dominates requested."""
    engine = CGACEEngine()
    tight_contract = ExecutionContract(metric="relative_l2_error", error_bound_eps=0.01)
    loose_contract = ExecutionContract(metric="relative_l2_error", error_bound_eps=0.05)

    rng = np.random.RandomState(42)
    U = rng.randn(64, 8).astype(np.float32)
    V = rng.randn(8, 64).astype(np.float32)
    A = U @ V
    B = rng.randn(64, 64).astype(np.float32)

    # 1. First execution stores result with tight_contract
    res1 = engine.execute_with_contract("matrix_gemm", A, tight_contract, secondary_data=B, force_level=2)
    assert res1["status"] == "ACCEPTED"
    assert res1["level_executed"] == 2

    # 2. Second execution with loose_contract should hit Level 0 cache
    res2 = engine.execute_with_contract("matrix_gemm", A, loose_contract, secondary_data=B)
    assert res2["level_executed"] == 0
    assert res2["path_name"] == "LEVEL_0_CONTRACT_CACHE"
    assert res2["work_eliminated_pct"] >= 99.0


def test_level_3_bitnet_tmac_lut_execution():
    """Verifies Level 3 addition-only BitNet multiplication-free evaluation."""
    engine = CGACEEngine()
    contract = ExecutionContract(metric="relative_l2_error", error_bound_eps=0.01)

    x = np.random.randn(128).astype(np.float32)
    res = engine.execute_with_contract("ternary_layer", x, contract, force_level=3)
    
    assert res["level_executed"] == 3
    assert res["path_name"] == "LEVEL_3_BITNET_TMAC_LUT"
    assert res["multiplication_free"] is True
    assert res["work_eliminated_pct"] >= 90.0


def test_level_4_speculative_cascade():
    """Verifies Level 4 Speculative Cascade decoding."""
    engine = CGACEEngine()
    contract = ExecutionContract(metric="token_match", error_bound_eps=0.01)

    prompt = "the quick brown fox jumps over the lazy dog and the quick brown fox"
    res = engine.execute_with_contract("text_llm", prompt, contract, force_level=4)
    
    assert res["level_executed"] == 4
    assert res["path_name"] == "LEVEL_4_SPECULATIVE_CASCADE"
    assert "result" in res
    assert res["contract_satisfied"] is True


def test_self_falsification_audit():
    """Verifies the mandatory self-falsification loop and adversarial checks."""
    engine = CGACEEngine()
    audit = engine.run_self_falsification_audit()
    
    assert "status" in audit
    assert audit["status"] == "ALL_INVARIANTS_VERIFIED"
    assert audit["tests_executed"] >= 2
    assert "path_promotions" in audit


def test_cgace_api_endpoints():
    """Verifies FastAPI REST endpoints for C-GACE."""
    # 1. Execute Matrix GEMM
    res = client.post("/api/v1/cgace/execute", json={
        "workload_type": "matrix_gemm",
        "error_bound_eps": 0.05,
        "matrix_dim": 128
    })
    assert res.status_code == 200
    data = res.json()
    assert data["workload_type"] == "matrix_gemm"
    assert data["pipeline_result"]["contract_satisfied"] is True

    # 2. Trigger Self-Falsification
    res_falsify = client.post("/api/v1/cgace/falsify")
    assert res_falsify.status_code == 200
    assert res_falsify.json()["status"] == "ALL_INVARIANTS_VERIFIED"

    # 3. Get Telemetry
    res_telem = client.get("/api/v1/cgace/telemetry")
    assert res_telem.status_code == 200
    assert "total_queries" in res_telem.json()
