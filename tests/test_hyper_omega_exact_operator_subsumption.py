"""
tests/test_hyper_omega_exact_operator_subsumption.py
=====================================================
Unit & Integration Test Suite for HYPER-Omega Exact Operator & Zero-Copy Subsumption Engine.
Hardware Target: Intel Core i5-12450H + Intel UHD Graphics 48-EU (USM Zero-Copy).
"""

import math
import numpy as np
import pytest

from backend.canonical.hyper_omega_exact_operator_subsumption import (
    ZeroCopyUSMAllocator,
    HyperOmegaSubsumptionEngine,
    ParityAuditRecord,
    run_hyper_omega_verification_suite,
)


class TestHyperOmegaExactOperatorSubsumption:
    """Rigorous verification of the 5 Operator Subsumption Breakthroughs."""

    def test_1_zero_copy_usm_allocator_alignment(self):
        """Test: ZeroCopyUSMAllocator guarantees 64-byte cache-line and 4096-byte page alignment."""
        # 1. Empty aligned
        arr1 = ZeroCopyUSMAllocator.empty_aligned((512, 128), dtype=np.float32)
        assert arr1.shape == (512, 128)
        assert arr1.dtype == np.float32
        assert ZeroCopyUSMAllocator.is_page_aligned(arr1)
        assert ZeroCopyUSMAllocator.is_cache_aligned(arr1)
        assert (arr1.ctypes.data % 4096) == 0
        assert (arr1.ctypes.data % 64) == 0

        # 2. Zeros aligned
        arr2 = ZeroCopyUSMAllocator.zeros_aligned((256,), dtype=np.float64)
        assert arr2.shape == (256,)
        assert np.all(arr2 == 0.0)
        assert ZeroCopyUSMAllocator.is_page_aligned(arr2)
        assert ZeroCopyUSMAllocator.is_cache_aligned(arr2)

        # 3. From unaligned array
        unaligned = np.random.randn(128, 64).astype(np.float32)
        arr3 = ZeroCopyUSMAllocator.from_array_aligned(unaligned)
        assert ZeroCopyUSMAllocator.is_cache_aligned(arr3)
        assert np.allclose(arr3, unaligned)

    def test_2_exact_krylov_operator_linear_system(self):
        """Test: Exact Krylov-Woodbury operator solve achieves 100% computational parity."""
        rng = np.random.default_rng(42)
        n_dim, rank_r = 512, 16
        diag = rng.uniform(2.0, 10.0, size=(n_dim,))
        u_mat = rng.standard_normal((n_dim, rank_r)) * 0.1
        v_mat = rng.standard_normal((n_dim, rank_r)) * 0.1
        b_vec = rng.standard_normal((n_dim,))

        record = HyperOmegaSubsumptionEngine.solve_exact_krylov_operator(
            diag, u_mat, v_mat, b_vec, tol=1e-6
        )

        assert isinstance(record, ParityAuditRecord)
        assert record.exact_computational_parity_met is True
        assert record.contract_parity_met is True
        assert record.relative_l2_error <= 1e-6
        assert record.operations_eliminated_pct > 95.0
        assert record.execution_mode == "EXACT_OPERATOR_WOODBURY_KRYLOV"
        assert record.falsification_triggered is False
        assert record.fallback_used is False

    def test_3_nonlinear_koopman_woodbury_adaptation(self):
        """Test: Koopman-ORFF lifting solves nonlinear adaptation in one closed-form pass."""
        rng = np.random.default_rng(2026)
        x_tr = rng.uniform(-1.5, 1.5, size=(512, 8))
        y_tr = np.sin(x_tr[:, 0:2]) + 0.5 * np.cos(x_tr[:, 2:4] * x_tr[:, 4:6])
        x_te = rng.uniform(-1.5, 1.5, size=(128, 8))
        y_te = np.sin(x_te[:, 0:2]) + 0.5 * np.cos(x_te[:, 2:4] * x_te[:, 4:6])

        record = HyperOmegaSubsumptionEngine.solve_nonlinear_koopman_woodbury(
            x_tr, y_tr, x_te, y_te, lifted_dim=128, mlp_epochs=100
        )

        assert isinstance(record, ParityAuditRecord)
        assert record.contract_parity_met is True
        assert record.relative_l2_error <= record.error_tolerance
        assert record.measured_speedup > 1.0
        assert record.operations_eliminated_pct >= 90.0

    def test_4_multipole_taylor_linear_attention(self):
        """Test: Multipole 2nd-order polynomial kernel factorizes attention in O(L) time."""
        rng = np.random.default_rng(2026)
        seq_len, head_dim = 1024, 8
        q_m = rng.uniform(-0.35, 0.35, size=(seq_len, head_dim))
        k_m = rng.uniform(-0.35, 0.35, size=(seq_len, head_dim))
        v_m = rng.standard_normal((seq_len, head_dim))

        record = HyperOmegaSubsumptionEngine.multipole_taylor_linear_attention(
            q_m, k_m, v_m, rel_tol=0.02
        )

        assert isinstance(record, ParityAuditRecord)
        assert record.contract_parity_met is True
        assert record.relative_l2_error <= 0.02
        assert record.execution_mode == "MULTIPOLE_POLYNOMIAL_MOMENT_O_L"
        assert record.operations_eliminated_pct > 70.0
        assert record.falsification_triggered is False

    def test_5_adversarial_counterexamples_and_fallbacks(self):
        """Test: Engine detects ill-conditioned matrices and sharp attention, triggering fallback."""
        records = HyperOmegaSubsumptionEngine.audit_counterexamples()
        assert len(records) >= 2

        # Check that high-temperature/sharp peak triggered fallback to exact tiled attention
        peak_rec = [r for r in records if "Attention" in r.workload_name][0]
        assert peak_rec.falsification_triggered is True
        assert peak_rec.fallback_used is True
        assert peak_rec.execution_mode == "FALLBACK_EXACT_TILED_ATTENTION"
        assert peak_rec.relative_l2_error == 0.0

    def test_6_full_verification_suite(self):
        """Test: Comprehensive verification suite passes 100% of contracts with zero mocks."""
        report = run_hyper_omega_verification_suite()
        assert report["engine"] == "HYPER_OMEGA_EXACT_OPERATOR_SUBSUMPTION"
        assert report["usm_64byte_cacheline_aligned"] is True
        assert report["usm_4096byte_page_aligned"] is True
        assert report["all_contract_parities_met"] is True
        assert report["raw_hardware_parity_claimed"] is False
        assert len(report["benchmarks"]) == 3
        assert len(report["adversarial_counterexamples"]) >= 2

