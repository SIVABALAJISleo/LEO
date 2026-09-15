"""
tests/test_residual_correction.py
=================================
Tests Phase 10 residual correction: y = y_hat + r.
Verifies that computing residual fixes sub-threshold errors without full recompute.
"""

import numpy as np
import pytest
from hyper.candidate import PathClass
from hyper.residual.residual_engine import PredictiveResidualEngine


def test_residual_correction_success():
    engine = PredictiveResidualEngine()
    current_input = np.array([10.0, 20.0, 30.0], dtype=np.float32)

    # Predictor with small offset
    predictor = lambda prev, curr: np.array([9.5, 20.2, 29.8], dtype=np.float32)
    # Estimated error exceeds 0.01 limit
    error_est = lambda pred, curr: float(np.max(np.abs(pred - curr)))
    # Verifier passes if max error <= 0.01
    verifier = lambda val, max_err: (bool(np.max(np.abs(val - current_input)) <= max_err), float(np.max(np.abs(val - current_input))))
    # Residual accurately computes difference
    residual_fn = lambda curr, pred: (curr - pred, 0.05)
    fallback_fn = lambda curr: (curr * 1.0, 0.5)

    res, telemetry = engine.execute_pipeline(
        current_input=current_input,
        previous_state=None,
        predictor_fn=predictor,
        error_estimator_fn=error_est,
        verifier_fn=verifier,
        residual_fn=residual_fn,
        exact_fallback_fn=fallback_fn,
        max_allowed_error=0.01,
    )

    assert telemetry["path_class"] == PathClass.REDUCED_WORK.value
    assert telemetry["prediction_used"] is True
    assert telemetry["residual_used"] is True
    assert telemetry["fallback_used"] is False
    assert np.allclose(res, current_input, atol=0.01)
