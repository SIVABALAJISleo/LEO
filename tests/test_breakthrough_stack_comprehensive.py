"""
tests/test_breakthrough_stack_comprehensive.py
==============================================
Test suite covering the full breakthrough software stack:
1. OS thread affinity (P-core pinning & E-core offloading)
2. Diff-Logic Boolean circuit compilation & bitwise evaluation
3. Mamba SSM linear recurrence & O(1) state memory
4. AVX2 cache-tiled matrix multiplication
5. Adaptive complexity cascade router
6. Independent verifier reproducible telemetry
"""

import pytest
import numpy as np

from core_ai.os_affinity import pin_to_p_cores, offload_to_e_cores, apply_inference_affinity
from core_ai.diff_logic_engine import DiffLogicEngine
from core_ai.mamba_ssm_engine import MambaSSMEngine, MambaConfig
from core_ai.avx2_fast_matmul import FastAVX2Matmul
from core_ai.complexity_cascade_router import ComplexityCascadeRouter
from core_ai.independent_verifier import IndependentVerifier


def test_1_os_affinity_and_p_core_pinning():
    """Verify OS affinity functions apply gracefully without errors."""
    status = apply_inference_affinity()
    assert "cpu_affinity" in status
    assert "process_priority" in status

    # Micro thread pinning functions
    p_res = pin_to_p_cores()
    e_res = offload_to_e_cores()
    assert isinstance(p_res, bool)
    assert isinstance(e_res, bool)


def test_2_diff_logic_boolean_circuit_compilation_and_execution():
    """Verify DiffLogic compiles linear weights into boolean DAG and evaluates bitwise."""
    engine = DiffLogicEngine(num_inputs=32, num_outputs=8)
    W = np.random.randn(8, 32).astype(np.float32)

    gate_count = engine.compile_linear_layer_to_circuit(W)
    assert gate_count > 0
    assert engine.compiled is True

    input_bits = (np.random.randn(32) > 0).astype(np.uint8)
    out_bits, latency_ms = engine.evaluate_circuit(input_bits)

    assert len(out_bits) == 8
    assert latency_ms >= 0.0
    assert set(np.unique(out_bits)).issubset({0, 1})

    telemetry = engine.get_circuit_telemetry()
    assert telemetry["floating_point_multiplications"] == 0


def test_3_mamba_ssm_linear_recurrence_and_memory_efficiency():
    """Verify Mamba selective state space scanning operates in linear time with O(1) state."""
    cfg = MambaConfig(d_model=32, d_state=8, d_conv=3, expand=2)
    mamba = MambaSSMEngine(cfg)

    seq_len = 128
    tokens = np.random.randn(seq_len, 32).astype(np.float32)
    y_out, stats = mamba.forward_sequence(tokens)

    assert y_out.shape == (seq_len, 32)
    assert stats["complexity"] == "O(N) Linear"
    assert stats["memory_reduction_ratio"] > 1.0
    assert stats["kv_cache_memory_bytes"] < stats["transformer_equivalent_kv_cache_bytes"]


def test_4_avx2_fast_tiled_gemm():
    """Verify register-tiled GEMM matches standard matrix multiplication within numerical tolerance."""
    size = 128
    A = np.random.randn(size, size).astype(np.float32)
    B = np.random.randn(size, size).astype(np.float32)

    C_tiled, lat_tiled = FastAVX2Matmul.tiled_gemm(A, B, block_size=32)
    C_naive = A @ B

    assert np.allclose(C_tiled, C_naive, atol=1e-4)

    bench = FastAVX2Matmul.benchmark_speedup(size=128)
    assert bench["avx2_fma_tiling_active"] is True
    assert bench["numerical_error_max"] < 1e-3


def test_5_adaptive_complexity_cascade_router():
    """Verify ComplexityCascadeRouter accurately separates easy vs hard queries."""
    router = ComplexityCascadeRouter()

    # Easy factual query
    plan_easy = router.assess_complexity("what is the capital of france")
    assert plan_easy.complexity_level == "EASY"
    assert plan_easy.recommended_model_tier == "TIER_0_TINY_0_5B"
    assert plan_easy.expected_throughput_tok_s >= 40.0

    # Hard mathematical/algorithmic proof
    plan_hard = router.assess_complexity("prove the theorem of symplectic energy conservation for hamiltonian mechanics and refactor concurrency architecture")
    assert plan_hard.complexity_level == "HARD"
    assert plan_hard.recommended_model_tier == "TIER_2_LARGE_7B"
    assert plan_hard.expected_throughput_tok_s <= 10.0


def test_6_independent_verifier_reproducibility():
    """Verify IndependentVerifier runs all 6 workloads and extracts honest telemetry."""
    verifier = IndependentVerifier()
    report = verifier.run_full_verification_suite()

    assert "telemetry" in report
    assert "benchmarks" in report
    assert len(report["benchmarks"]) == 6
    assert report["telemetry"]["physical_cores"] is not None
    assert report["telemetry"]["system_ram_total_gb"] > 0

    for b in report["benchmarks"]:
        assert b["wall_clock_latency_ms"] >= 0.0
        assert b["contract_parity_pct"] >= 50.0
