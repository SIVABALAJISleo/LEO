"""
tests/test_hyper_v2_execution.py
Unit tests for HYPER 2.0 Backends, Memory Optimizer, Kernel Fusion, and Cost Model.
"""

import pytest
import numpy as np
from hyper_v2.execution.cpu_backend import CPUBackend
from hyper_v2.execution.igpu_backend import IntelIGPUBackend
from hyper_v2.execution.hybrid_backend import HybridBackend
from hyper_v2.optimization.memory_optimizer import MemoryOptimizer
from hyper_v2.optimization.kernel_fusion import KernelFusionEngine
from hyper_v2.search.cost_model import PredictiveCostModel
from hyper_v2.compiler.intermediate_representation import DeviceTarget


def test_cpu_and_igpu_backends():
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)

    C_cpu, t_cpu = CPUBackend.execute_gemm_dense(A, B)
    assert C_cpu.shape == (64, 64)
    assert t_cpu > 0.0

    C_igpu, t_igpu = IntelIGPUBackend.execute_matmul(A, B)
    assert C_igpu.shape == (64, 64)
    np.testing.assert_allclose(C_cpu, C_igpu, rtol=1e-4)


def test_hybrid_partitioned_gemm():
    A = np.random.randn(128, 64).astype(np.float32)
    B = np.random.randn(64, 128).astype(np.float32)

    C_hyb, t_hyb = HybridBackend.execute_partitioned_gemm(A, B, cpu_ratio=0.5)
    C_ref = np.matmul(A, B)
    assert C_hyb.shape == (128, 128)
    np.testing.assert_allclose(C_hyb, C_ref, rtol=1e-4)


def test_memory_optimizer_buffer_pool():
    buf1 = MemoryOptimizer.acquire_buffer((32, 32), dtype="float32")
    assert buf1.shape == (32, 32)
    MemoryOptimizer.release_buffer(buf1)
    buf2 = MemoryOptimizer.acquire_buffer((32, 32), dtype="float32")
    assert buf2.shape == (32, 32)


def test_kernel_fusion():
    A = np.ones((16, 16), dtype=np.float32)
    B = np.ones((16, 16), dtype=np.float32)
    bias = np.ones((16, 16), dtype=np.float32) * -5.0

    C_fused = KernelFusionEngine.fused_gemm_bias_relu(A, B, bias)
    # (16 * 1) - 5 = 11 >= 0
    assert np.all(C_fused == 11.0)


def test_cost_model():
    cost = PredictiveCostModel.evaluate_strategy_cost(
        strategy_name="test_strat",
        flops=1_000_000,
        bytes_read=100_000,
        bytes_written=100_000,
        device=DeviceTarget.INTEL_IGPU,
        tolerance_budget=1e-3,
        error_estimate=1e-4
    )
    assert cost.total_estimated_latency_ms > 0.0
    assert cost.is_contract_viable is True
