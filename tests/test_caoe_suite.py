"""
tests/test_caoe_suite.py
========================
Comprehensive test suite for CAOE (Contract-Aware Optimization Engine).
Tests all 7 layers on the Intel Core i5-12450H + Intel UHD environment.
"""

import numpy as np
import pytest

from backend.caoe import (
    ContractAwareOptimizationEngine,
    ContractAnalyzer,
    WorkloadSpec,
    PrecisionReducer,
    SparsityDetector,
    CacheManager,
    CPUiGPUScheduler,
    Verifier,
    TelemetryLayer,
)


def test_layer1_contract_analyzer_sweep():
    spec = WorkloadSpec(name="dense_gemm", shape=(64, 64), task_type="GEMM")
    contract = ContractAnalyzer.analyze_workload(spec)
    assert contract.name == "dense_gemm"
    assert contract.precision == 32

    # Sample input and computation fn
    sample = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    ref = sample @ B

    def compute(inp, prec, sparsity):
        if prec == 16:
            return (inp.astype(np.float16) @ B.astype(np.float16)).astype(np.float32)
        return inp @ B

    sweep = ContractAnalyzer.sweep_tolerance(compute, sample, ref, threshold=1e-2)
    assert len(sweep) == 15  # 3 precisions * 5 sparsities
    assert any(s["acceptable"] for s in sweep)


def test_layer2_precision_reducer():
    tensor = np.random.randn(32, 32).astype(np.float32)
    t16, s16 = PrecisionReducer.apply_precision(tensor, 16)
    t8, s8 = PrecisionReducer.apply_precision(tensor, 8)

    assert t16.dtype == np.float16
    assert t8.shape == tensor.shape
    # Check bounded error for INT8
    err8 = np.max(np.abs(t8 - tensor))
    assert err8 < 0.2  # Dynamic range quant bound


def test_layer3_sparsity_detector():
    detector = SparsityDetector()
    sparse_mat = np.zeros((64, 64), dtype=np.float32)
    sparse_mat[0, 0] = 5.0
    sparse_mat[10, 10] = 2.0

    info = detector.detect_sparsity(sparse_mat)
    assert info["structural_zeros"] > 0.95
    assert info["best_strategy"] == "SPARSE_CSR"


def test_layer4_cache_manager():
    cache = CacheManager(max_size_mb=10.0)
    spec = WorkloadSpec(name="test_cache", shape=(10, 10))
    contract = ContractAnalyzer.analyze_workload(spec)
    contract.cache_ttl = 10.0

    inp = np.ones((10, 10), dtype=np.float32)
    call_count = [0]

    def fn():
        call_count[0] += 1
        return inp * 2.0

    res1, meta1 = cache.get_or_compute(inp, fn, contract)
    assert not meta1["hit"]
    assert call_count[0] == 1

    res2, meta2 = cache.get_or_compute(inp, fn, contract)
    assert meta2["hit"]
    assert call_count[0] == 1  # Not recomputed
    assert cache.hit_rate == 0.5


def test_layer5_scheduler():
    scheduler = CPUiGPUScheduler()
    sched = scheduler.schedule((64, 64), None)
    assert sched["executor"] == "cpu"


def test_layer6_verifier():
    spec = WorkloadSpec(name="test_verif", shape=(10, 10))
    contract = ContractAnalyzer.analyze_workload(spec)

    ref = np.ones((10, 10), dtype=np.float32)
    cand_pass = ref + 1e-5
    cand_fail = ref + 0.5

    v_pass = Verifier.verify(cand_pass, ref, contract)
    v_fail = Verifier.verify(cand_fail, ref, contract)

    assert v_pass.contract_met
    assert not v_fail.contract_met


def test_layer7_caoe_end_to_end():
    engine = ContractAwareOptimizationEngine()
    spec = WorkloadSpec(name="e2e_gemm", shape=(32, 32), task_type="GEMM")
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    def compute(x, prec, sp):
        return x @ B

    out, meta = engine.optimize_and_execute(spec, compute, A)
    assert meta["verification"]["contract_met"]
    assert np.allclose(out, A @ B, atol=1e-3)

    metrics = engine.telemetry.aggregate_metrics()
    assert metrics["contract_parity_pct"] == 100.0


def test_phase3_intent_layer_v2():
    from backend.caoe.intent_router import IntentLayer_v2

    router = IntentLayer_v2()
    # Test intent classifications
    assert router.classify_query("render dynamic frame 60fps").intent_type == "RENDERING"
    assert router.classify_query("generate embedding token top_k").intent_type == "INFERENCE"
    assert router.classify_query("fourier spectral transform").intent_type == "FFT"
    assert router.classify_query("matrix multiplication gemm").intent_type == "GEMM"

    # Test route and execute
    A = np.ones((16, 16), dtype=np.float32)
    res, meta = router.route_and_execute(
        query="render dynamic frame",
        input_tensor=A,
        computation_fn=lambda x, p, s: x * 2.0,
        reference_execution=A * 2.0,
    )
    assert meta["verification"]["contract_met"]
    assert meta["classified_intent"] == "RENDERING"


def test_phase5_benchmark_suite_execution():
    from backend.caoe.benchmark_suite import CAOEBenchmarkSuite

    suite = CAOEBenchmarkSuite()
    # Run falsification checklist
    falsify = suite.run_falsification_checklist()
    assert falsify["falsification_verdict"] == "PASS"
    assert falsify["cold_start"]["contract_met"]
    assert falsify["hot_cache"]["contract_met"]
    assert falsify["adversarial_input"]["contract_met"]

