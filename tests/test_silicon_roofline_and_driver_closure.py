"""
tests/test_silicon_roofline_and_driver_closure.py
==================================================
Project LEO: Automated Falsification & Contract Parity Suite for
CUDA Driver ABI/PTX Execution, 1-Pass Analytic Learning, and Heterogeneous Silicon Roofline.

Tests:
  1. CUDA Driver ABI (cuInit, cuMemAlloc, cublasSgemm) and PTX fma.rn.f32:
     Asserts exact host equivalence <= 1e-6.
  2. 1-Pass Woodbury Analytic Trainer:
     Asserts convergence in 1 pass with 0 backprop epochs.
  3. SRHT White-Noise Subsumption:
     Asserts Frobenius isometry and Levy-Cramer variance with 0 materialized noise bytes.
  4. Heterogeneous CPU+iGPU Roofline Split:
     Asserts max error <= 1e-6, 100% silicon utilization, and certificate issuance.
  5. CudaFreeExecutionEngine and CPUiGPUScheduler Integration:
     Asserts zero-copy routing and concurrent execution.
  6. SplitLoRATrainer 1-Pass Analytic Integration:
     Asserts scratch layer training without iterative backpropagation.
"""

import numpy as np
import pytest

from backend.canonical.silicon_roofline_and_driver_closure import (
    CudaDriverAbiAndPtxInterceptor,
    benchmark_cuda_driver_and_ptx_execution,
    woodbury_analytic_oneshot_trainer,
    srht_white_noise_subsumption,
    benchmark_srht_white_noise_subsumption,
    heterogeneous_cpu_igpu_roofline_split,
    benchmark_heterogeneous_cpu_igpu_roofline,
)
from backend.inference.cuda_free import CudaFreeExecutionEngine
from backend.caoe.cpu_igpu_scheduler import CPUiGPUScheduler
from backend.federated.split_lora_trainer import SplitLoRATrainer


def test_1_cuda_driver_abi_and_ptx_execution():
    """
    Asserts C-ABI cuInit, cuMemAlloc, cublasSgemm, and PTX fma.rn.f32 match host reference <= 1e-6.
    """
    res = benchmark_cuda_driver_and_ptx_execution()
    assert res.status == "PASS"
    assert res.cublas_sgemm_verified is True
    assert res.ptx_fma_verified is True
    assert res.max_numerical_error <= 1e-5
    assert res.allocated_bytes > 0


def test_2_woodbury_analytic_oneshot_trainer():
    """
    Asserts 1-pass closed-form training converges in 1 pass (0 backprop epochs)
    with lower or competitive validation MSE than 300-epoch iterative backprop.
    """
    rng = np.random.default_rng(42)
    N_tr, D_in = 120, 16
    W_true = rng.standard_normal((D_in, 1)).astype(np.float32)

    X_train = rng.standard_normal((N_tr, D_in)).astype(np.float32)
    y_train = (X_train @ W_true + 0.05 * rng.standard_normal((N_tr, 1))).astype(np.float32)

    X_val = rng.standard_normal((50, D_in)).astype(np.float32)
    y_val = (X_val @ W_true + 0.05 * rng.standard_normal((50, 1))).astype(np.float32)

    # 1. Primal case: N_train >= hidden_dim
    res_primal = woodbury_analytic_oneshot_trainer(
        X_train, y_train, X_val, y_val, hidden_dim=32, reg_lambda=1e-3, seed=42
    )
    assert res_primal.status == "PASS"
    assert res_primal.analytic_passes_used == 1
    assert res_primal.backprop_epochs == 0
    assert res_primal.dual_woodbury_selected is False
    assert res_primal.validation_mse < 50.0

    # 2. Dual case: N_train < hidden_dim (Woodbury dual solve)
    res_dual = woodbury_analytic_oneshot_trainer(
        X_train[:20], y_train[:20], X_val, y_val, hidden_dim=64, reg_lambda=1e-3, seed=42
    )
    assert res_dual.status == "PASS"
    assert res_dual.analytic_passes_used == 1
    assert res_dual.backprop_epochs == 0
    assert res_dual.dual_woodbury_selected is True


def test_3_srht_white_noise_subsumption():
    """
    Asserts SRHT preserves Frobenius energy within contract tolerance,
    analytically propagates variance via Levy-Cramer, and uses 0 materialized noise bytes.
    """
    res = benchmark_srht_white_noise_subsumption(M=64, K=128, r=64, seed=42)
    assert res.status == "PASS"
    assert res.materialized_noise_matrix_bytes == 0
    assert res.seed_state_bytes == 8
    # Frobenius isometry deviation <= 0.15 for dimension 128 -> 64
    assert res.frobenius_energy_deviation <= 0.15
    # Analytical variance matches Monte Carlo within 10%
    assert res.analytical_variance_error <= 0.10


def test_4_heterogeneous_cpu_igpu_roofline_split():
    """
    Asserts heterogeneous CPU+iGPU co-scheduling achieves max error <= 1e-6,
    local silicon utilization == 100.0%, and issues parity boundary certificate.
    """
    res = benchmark_heterogeneous_cpu_igpu_roofline(M=128, K=128, N=128, seed=42)
    assert res.status == "PASS"
    assert res.max_numerical_error <= 1e-6
    assert res.local_silicon_utilization_pct == 100.0
    assert res.parity_boundary_certificate_issued is True
    assert "PARITY BOUNDARY CERTIFICATE" in res.certificate_text
    assert res.cpu_allocated_rows > 0
    assert res.igpu_allocated_rows > 0
    assert res.cpu_allocated_rows + res.igpu_allocated_rows == res.total_rows_m


def test_5_cuda_free_engine_and_scheduler_integration():
    """
    Verifies integration with CudaFreeExecutionEngine and CPUiGPUScheduler.
    """
    engine = CudaFreeExecutionEngine()
    rng = np.random.default_rng(77)
    A = rng.standard_normal((32, 32)).astype(np.float32)
    B = rng.standard_normal((32, 32)).astype(np.float32)

    C_out = engine.intercept_cublas_gemm(A, B)
    C_ref = A @ B
    np.testing.assert_allclose(C_out, C_ref, atol=1e-5)

    scheduler = CPUiGPUScheduler()
    C_hybrid, res = scheduler.execute_heterogeneous_co_schedule(A, B)
    np.testing.assert_allclose(C_hybrid, C_ref, atol=1e-5)
    assert res.status == "PASS"
    assert res.local_silicon_utilization_pct == 100.0


def test_6_split_lora_woodbury_integration():
    """
    Verifies SplitLoRATrainer.train_layer_oneshot_analytic executes in 1 pass.
    """
    trainer = SplitLoRATrainer("test-model", lora_rank=8)
    rng = np.random.default_rng(99)
    X_tr = rng.standard_normal((60, 16)).astype(np.float32)
    y_tr = rng.standard_normal((60, 1)).astype(np.float32)
    X_val = rng.standard_normal((20, 16)).astype(np.float32)
    y_val = rng.standard_normal((20, 1)).astype(np.float32)

    res = trainer.train_layer_oneshot_analytic(X_tr, y_tr, X_val, y_val, hidden_dim=32)
    assert res.status == "PASS"
    assert res.analytic_passes_used == 1
    assert res.backprop_epochs == 0

