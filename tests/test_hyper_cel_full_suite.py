"""
tests/test_hyper_cel_full_suite.py
=============================================================================
Unit & Integration Test Suite for HYPER-CEL (Contractual Elimination Layer)
=============================================================================
"""

import pytest
import numpy as np

from hyper_cel.contract.contract import ExactContract, NumericContract, PerceptualContract
from hyper_cel.contract.verifier import ContractVerifier
from hyper_cel.prediction.predictor import LowRankPredictor, KANSplinePredictor, SpeculativeDraftPredictor
from hyper_cel.prediction.residual import ResidualEngine
from hyper_cel.reuse.exact_cache import ExactResultCache, ComputationalDNA
from hyper_cel.reuse.temporal_cache import ComputationReservoir, TemporalFrameBuffer
from hyper_cel.execution.cpu import CPUExecutionBackend
from hyper_cel.execution.igpu import iGPUExecutionBackend
from hyper_cel.execution.hybrid import HybridCPUiGPUPipeline
from hyper_cel.scheduler.cost_model import HyperCostModel, ExecutionCandidate
from hyper_cel.runtime import HyperCELRuntime

def test_exact_and_numeric_contracts():
    exact = ExactContract()
    passed, q, _ = exact.validate("test", "test")
    assert passed is True
    assert q == 1.0

    passed_fail, q_fail, _ = exact.validate("test", "other")
    assert passed_fail is False

    num = NumericContract(epsilon=1e-2)
    A = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    A_noisy = A + 0.001
    passed_num, q_num, meta = num.validate(A_noisy, A)
    assert passed_num is True
    assert q_num > 0.99

def test_perceptual_contract():
    perp = PerceptualContract(min_ssim=0.90, min_psnr=25.0, data_range=1.0)
    x, y = np.meshgrid(np.linspace(0, 1, 64), np.linspace(0, 1, 64))
    img = (0.5 * (x + y)).astype(np.float32)
    noisy = img + (np.random.randn(64, 64) * 0.01).astype(np.float32)
    passed, ssim_val, meta = perp.validate(noisy, img)
    assert passed is True
    assert ssim_val >= 0.90

def test_verifier_fallback():
    verifier = ContractVerifier(NumericContract(epsilon=1e-4))
    candidate = np.array([1.0, 2.0])
    reference = np.array([5.0, 5.0]) # large difference

    fallback_called = False
    def exact_fallback():
        nonlocal fallback_called
        fallback_called = True
        return reference

    result, verified, meta = verifier.verify_or_fallback(candidate, reference, exact_fallback)
    assert verified is False
    assert fallback_called is True
    assert np.array_equal(result, reference)

def test_low_rank_predictor_and_residual():
    M, K, N = 64, 64, 64
    u = np.random.randn(M, 8).astype(np.float32)
    v = np.random.randn(8, K).astype(np.float32)
    A = u @ v # Rank 8 matrix
    B = np.random.randn(K, N).astype(np.float32)

    predictor = LowRankPredictor(rank=8)
    Y_hat, pred_meta = predictor.predict(A, B)
    assert pred_meta["cer"] > 0.0

    res_engine = ResidualEngine(epsilon=1e-3)
    Y_final, res_meta = res_engine.solve_matrix_residual(A, B, Y_hat, exact_reference=A @ B)
    assert np.allclose(Y_final, A @ B, atol=1e-2)

def test_temporal_frame_buffer_and_image_residual():
    buffer = TemporalFrameBuffer(history_len=4)
    frame1 = np.ones((32, 32), dtype=np.float32)
    buffer.push_frame(frame1)

    # Frame 2 has small modified region (10% changed)
    frame2 = np.ones((32, 32), dtype=np.float32)
    frame2[0:8, 0:8] = 0.0

    prev = buffer.project_previous_frame()
    res_engine = ResidualEngine(epsilon=1e-2)
    reconstructed, meta = res_engine.solve_image_residual(prev, frame2)

    assert meta["eliminated_samples_pct"] > 80.0
    assert np.array_equal(reconstructed, frame2)

def test_computational_dna_and_exact_cache():
    cache = ExactResultCache(max_entries=100)
    dna1 = ComputationalDNA.fingerprint("gemm", [np.ones((4,4))], {"opt": 1}, "ExactContract")
    dna2 = ComputationalDNA.fingerprint("gemm", [np.ones((4,4))], {"opt": 1}, "ExactContract")
    assert dna1 == dna2

    cache.put(dna1, "RESULT_VALUE")
    assert cache.get(dna1) == "RESULT_VALUE"
    assert cache.stats()["hits"] == 1

def test_overlapped_hybrid_execution():
    pipeline = HybridCPUiGPUPipeline()
    W1 = np.random.randn(32, 32).astype(np.float32)
    W2 = np.random.randn(32, 32).astype(np.float32)
    x = np.random.randn(4, 32).astype(np.float32)

    out, meta = pipeline.execute_overlapped_layers(
        layers=[{"name": "L1"}, {"name": "L2"}],
        layer_weights=[W1, W2],
        input_state=x
    )
    assert meta["layers_executed"] == 2
    assert out.shape == (4, 32)

def test_hyper_cost_model():
    model = HyperCostModel()
    candidates = [
        ExecutionCandidate("EXACT_CACHE", level=0, estimated_latency_ms=0.5, estimated_energy_joules=0.001, estimated_memory_mb=1.0, estimated_quality=1.0, action_type="CACHE"),
        ExecutionCandidate("LOW_RANK", level=3, estimated_latency_ms=5.0, estimated_energy_joules=0.05, estimated_memory_mb=10.0, estimated_quality=0.98, action_type="PREDICT"),
        ExecutionCandidate("FAILED_APPROX", level=3, estimated_latency_ms=1.0, estimated_energy_joules=0.01, estimated_memory_mb=2.0, estimated_quality=0.60, action_type="PREDICT"),
    ]
    chosen = model.choose_optimal_pathway(candidates, min_quality=0.95)
    assert chosen.name == "EXACT_CACHE"

def test_hyper_cel_runtime_end_to_end():
    runtime = HyperCELRuntime()
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)

    # Pass 1: Cold execution (Predict + Residual / Fallback)
    out1, meta1 = runtime.execute_matrix_multiplication(A, B)
    assert meta1["contract_verified"] is True
    assert np.allclose(out1, A @ B, atol=1e-2)

    # Pass 2: Warm execution (Level 0 Exact Cache Hit -> 0 FLOPs)
    out2, meta2 = runtime.execute_matrix_multiplication(A, B)
    assert meta2["level"] == 0
    assert meta2["pathway"] == "EXACT_CACHE_HIT"
    assert meta2["cer"] == 1.0
    assert np.array_equal(out1, out2)
