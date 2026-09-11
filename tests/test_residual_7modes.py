"""
tests/test_residual_7modes.py
=============================
Unit tests for Mechanism 3: 7-Mode Residual-Only Recalculation Engine.
"""

import pytest
import numpy as np
from hyper_cco.contract import ComputeContract, ExactnessClass, VerificationStatus
from hyper_cco.residual_engine import ResidualEngine, ResidualMode


def test_low_rank_residual_gemm():
    contract = ComputeContract(
        workload_id="RESIDUAL_GEMM_TEST",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=1e-2
    )
    engine = ResidualEngine()

    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    res = engine.execute_low_rank_residual_gemm(A, B, contract, rank_k=4)

    assert res.verification_status == VerificationStatus.PASS
    assert res.telemetry.prediction_cost_ms >= 0.0
    assert res.telemetry.residual_cost_ms >= 0.0
    assert res.telemetry.end_to_end_latency_ms > 0.0

    ref = A @ B
    err = float(np.max(np.abs(res.output - ref)))
    assert err < 1e-4  # Full residual + prediction reconstructs exact


def test_temporal_residual():
    contract = ComputeContract(
        workload_id="RESIDUAL_TEMPORAL_TEST",
        max_absolute_error=1e-3
    )
    engine = ResidualEngine()

    x_prev = np.ones((16,), dtype=np.float32)
    y_prev = x_prev * 2.0
    x_curr = x_prev + 0.05

    res = engine.execute_temporal_residual(
        current_input=x_curr,
        previous_input=x_prev,
        previous_output=y_prev,
        operator_fn=lambda x: x * 2.0,
        contract=contract
    )

    assert res.verification_status == VerificationStatus.PASS
    assert np.allclose(res.output, x_curr * 2.0, atol=1e-5)
    assert res.telemetry.fallback_triggered is False


def test_residual_escalation_to_exact_fallback():
    contract = ComputeContract(
        workload_id="RESIDUAL_ESCALATE_TEST",
        exactness_class=ExactnessClass.EXACT,
        max_absolute_error=0.0
    )
    engine = ResidualEngine()

    # Inexact prediction
    def bad_predict():
        return np.zeros((10,), dtype=np.float32), 0.1

    # Incomplete residual
    def bad_residual(y_hat):
        return np.ones((10,), dtype=np.float32) * 0.5

    def exact():
        return np.ones((10,), dtype=np.float32) * 100.0

    res = engine.execute(
        mode=ResidualMode.EXACT_RESIDUAL,
        exact_fn=exact,
        contract=contract,
        predict_fn=bad_predict,
        residual_fn=bad_residual
    )

    # Should escalate to exact recomputation
    assert res.telemetry.fallback_triggered is True
    assert np.allclose(res.output, 100.0)
