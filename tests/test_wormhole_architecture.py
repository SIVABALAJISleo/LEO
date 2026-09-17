"""
Unit Test Suite for LEO/HYPER Ω Computational Escape / Wormhole Architecture.
Verifies all 9 components under strict IEEE 754 and Contract-100 parity standards.
"""

import pytest
import numpy as np

from contracts.contract_ir import (
    ContractIR,
    ExactnessClass,
    VerificationLevel,
    Contract100Gate
)
from hyper.proof.execution_certificate import ExecutionCertificate
from hyper.cache.wormhole_cache import (
    WormholeCacheKey,
    WormholeExactCache,
    WormholeSemanticCache
)
from hyper.necessity.necessary_work_analyzer import NecessaryWorkAnalyzer
from hyper.escape.escape_engine import ComputationalEscapeEngine, EscapeStrategy
from hyper.quantization.precision_engine import PrecisionDecisionEngine
from hyper.predictive.speculative_executor import SpeculativeExecutor
from hyper.memory.memory_wormhole import AlignedBufferPool, MemoryWormhole
from hyper.benchmark.integrity.benchmark_integrity_engine import BenchmarkIntegrityEngine


class TestContractIR:
    def test_contract_creation_and_hash(self):
        c1 = ContractIR(
            task_id="gemm_task",
            exactness_class=ExactnessClass.EXACT_FLOAT_FP32,
            max_absolute_error=1e-5
        )
        c2 = ContractIR(
            task_id="gemm_task",
            exactness_class=ExactnessClass.EXACT_FLOAT_FP32,
            max_absolute_error=1e-5
        )
        assert c1.contract_hash() == c2.contract_hash()
        assert len(c1.contract_hash()) == 64

    def test_contract_100_gate_pass(self):
        ref = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        hyp = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        contract = ContractIR(task_id="test", exactness_class=ExactnessClass.EXACT_BIT_LEVEL)
        res = Contract100Gate.validate(
            reference_output=ref,
            hyper_output=hyp,
            contract=contract,
            ref_latency_ms=10.0,
            hyper_latency_ms=2.0,
            peak_ram_bytes=1024,
            work_eliminated_ratio=0.8
        )
        assert res.passed
        assert len(res.failures) == 0

    def test_contract_100_gate_fail_error(self):
        ref = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        hyp = np.array([1.0, 2.5, 3.0], dtype=np.float32)
        contract = ContractIR(
            task_id="test",
            exactness_class=ExactnessClass.EXACT_FLOAT_FP32,
            max_absolute_error=1e-3
        )
        res = Contract100Gate.validate(
            reference_output=ref,
            hyper_output=hyp,
            contract=contract,
            ref_latency_ms=10.0,
            hyper_latency_ms=2.0,
            peak_ram_bytes=1024,
            work_eliminated_ratio=0.8
        )
        assert not res.passed
        assert any("EXACTNESS_VIOLATED" in f or "TOLERANCE_VIOLATED" in f or "max_abs" in f for f in res.failures)


class TestExecutionCertificate:
    def test_certificate_digest(self):
        cert = ExecutionCertificate(
            run_id="run_001",
            task_id="t1",
            strategy_used="EXACT_CACHE_HIT",
            hardware_target="Intel Core i5-12450H + Intel UHD Graphics (48 EU)",
            exactness_class="EXACT_FLOAT_FP32",
            reference_flops=1000000,
            executed_flops=0,
            work_eliminated_ratio=1.0,
            latency_ref_ms=10.0,
            latency_hyper_ms=0.05,
            speedup=200.0,
            peak_ram_mb=0.1,
            max_absolute_error=0.0,
            cosine_similarity=1.0,
            contract_100_passed=True
        )
        digest = cert.compute_certificate_digest()
        assert len(digest) == 64
        cert_dict = cert.to_dict()
        assert cert_dict["certificate_digest"] == digest


class TestWormholeCache:
    def test_exact_cache_hit_and_miss(self):
        cache = WormholeExactCache(max_entries=10)
        contract = ContractIR(task_id="c_test", exactness_class=ExactnessClass.EXACT_FLOAT_FP32)
        key = WormholeCacheKey.from_inputs("gemm", contract, [np.array([1.0, 2.0])])
        
        # Miss
        assert cache.lookup(key) is None
        
        # Insert
        val = np.array([3.0, 4.0])
        cache.insert(key, val)
        
        # Hit
        cached_val = cache.lookup(key)
        assert cached_val is not None
        assert np.array_equal(cached_val, val)
        assert cache.stats["hits"] == 1

    def test_semantic_cache(self):
        sem_cache = WormholeSemanticCache(similarity_threshold=0.95)
        vec_base = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        sem_cache.insert(vec_base, "result_x")

        # Query close vector
        vec_close = np.array([0.98, 0.02, 0.0], dtype=np.float32)
        match, score = sem_cache.lookup(vec_close)
        assert match == "result_x"
        assert score > 0.95

        # Query distant vector
        vec_dist = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        match, score = sem_cache.lookup(vec_dist)
        assert match is None


class TestNecessaryWorkAnalyzer:
    def test_gemm_work_accounting(self):
        analyzer = NecessaryWorkAnalyzer()
        A = np.zeros((100, 50), dtype=np.float32)
        B = np.zeros((50, 200), dtype=np.float32)
        ref_flops = analyzer.analyze_gemm_reference_work(A, B)
        assert ref_flops == 2 * 100 * 50 * 200  # 2,000,000

        metrics = analyzer.evaluate_work_reduction(
            w_ref=ref_flops,
            w_exec=400000,
            t_ref_ms=10.0,
            t_hyper_ms=2.5
        )
        assert metrics.work_eliminated_ratio == 0.8
        assert metrics.latency_speedup == 4.0
        # Work elimination and latency speedup are strictly separate numbers!
        assert metrics.work_eliminated_ratio != metrics.latency_speedup


class TestPrecisionDecisionEngine:
    def test_preserves_fp32_for_exact(self):
        engine = PrecisionDecisionEngine()
        contract = ContractIR(task_id="p1", exactness_class=ExactnessClass.EXACT_FLOAT_FP32)
        tensor = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        
        q_tensor, cert = engine.evaluate_precision(tensor, contract)
        assert q_tensor.dtype == np.float32
        assert cert.contract_compliant
        assert cert.max_absolute_error == 0.0

    def test_permits_int8_for_tolerant(self):
        engine = PrecisionDecisionEngine()
        contract = ContractIR(
            task_id="p2",
            exactness_class=ExactnessClass.CONTRACT_TOLERANT,
            max_absolute_error=0.05
        )
        tensor = np.linspace(-1.0, 1.0, 1000).astype(np.float32)
        q_tensor, cert = engine.evaluate_precision(tensor, contract)
        assert cert.contract_compliant
        assert cert.target_dtype in ("int8", "float16", "ternary_1.58bit")


class TestSpeculativeExecutor:
    def test_commit_when_valid(self):
        executor = SpeculativeExecutor()
        contract = ContractIR(task_id="s1", exactness_class=ExactnessClass.CONTRACT_TOLERANT, max_absolute_error=0.1)
        
        exact_val = np.array([1.0, 2.0, 3.0])
        draft_val = np.array([1.01, 2.01, 2.99])
        
        res, info = executor.execute(
            draft_fn=lambda: draft_val,
            verify_fn=lambda d: bool(np.max(np.abs(d - exact_val)) < 0.05),
            exact_fallback_fn=lambda: exact_val,
            contract=contract
        )
        assert np.array_equal(res, draft_val)
        assert info["committed"]

    def test_rollback_when_invalid(self):
        executor = SpeculativeExecutor()
        contract = ContractIR(task_id="s2", exactness_class=ExactnessClass.CONTRACT_TOLERANT, max_absolute_error=0.1)
        
        exact_val = np.array([1.0, 2.0, 3.0])
        draft_val = np.array([10.0, 20.0, 30.0])  # Invalid
        
        res, info = executor.execute(
            draft_fn=lambda: draft_val,
            verify_fn=lambda d: bool(np.max(np.abs(d - exact_val)) < 0.05),
            exact_fallback_fn=lambda: exact_val,
            contract=contract
        )
        assert np.array_equal(res, exact_val)
        assert not info["committed"]


class TestMemoryWormhole:
    def test_64_byte_alignment_and_pool_hit(self):
        wormhole = MemoryWormhole()
        buf1 = wormhole.allocate_buffer((64, 64), dtype=np.float32)
        assert buf1.ctypes.data % 64 == 0
        wormhole.release_buffer(buf1)

        buf2 = wormhole.allocate_buffer((64, 64), dtype=np.float32)
        assert buf2.ctypes.data % 64 == 0
        stats = wormhole.get_stats()
        assert stats["pool_hits"] == 1


class TestEscapeEngine:
    def test_exact_cache_bypass(self):
        engine = ComputationalEscapeEngine()
        contract = ContractIR(task_id="esc_1", exactness_class=ExactnessClass.EXACT_FLOAT_FP32)
        A = np.ones((64, 64), dtype=np.float32)
        B = np.ones((64, 64), dtype=np.float32)

        # Call 1: Reference Fallback & Cache Seed
        out1, cert1 = engine.execute_gemm(A, B, contract, op_name="gemm_1")
        assert "FALLBACK" in cert1.strategy_used

        # Call 2: Exact Cache Hit
        out2, cert2 = engine.execute_gemm(A, B, contract, op_name="gemm_2")
        assert "CACHE" in cert2.strategy_used
        assert cert2.work_eliminated_ratio == 1.0
        assert np.allclose(out1, out2)

    def test_delta_computation_bypass(self):
        engine = ComputationalEscapeEngine()
        contract = ContractIR(task_id="esc_2", exactness_class=ExactnessClass.EXACT_FLOAT_FP32)
        A = np.ones((64, 64), dtype=np.float32)
        B1 = np.ones((64, 64), dtype=np.float32)
        
        out1, cert1 = engine.execute_gemm(A, B1, contract, op_name="delta_base")

        # Minor perturbation: only 2 elements changed
        B2 = B1.copy()
        B2[0, 0] += 1.0
        B2[5, 5] += 2.0

        out2, cert2 = engine.execute_gemm(A, B2, contract, op_name="delta_mod")
        ref2 = np.matmul(A, B2)
        assert "DELTA" in cert2.strategy_used
        assert np.allclose(out2, ref2, atol=1e-5)



class TestBenchmarkIntegrityEngine:
    def test_six_mode_suite_execution(self):
        bench = BenchmarkIntegrityEngine(warmup_runs=1, bench_runs=3)
        results = bench.run_suite(M=64, K=64, N=64)

        assert len(results) == 6
        assert "mode_1_reference" in results
        assert "mode_2_hyper_exact" in results
        assert "mode_3_hyper_optimized" in results
        assert "mode_4_hyper_cache" in results
        assert "mode_5_hyper_adversarial" in results
        assert "mode_6_hyper_fallback" in results

        for mode_key, res in results.items():
            assert res.contract_passed, f"Mode {mode_key} failed contract parity!"
            assert res.min_latency_ms > 0.0
            assert res.median_latency_ms > 0.0
