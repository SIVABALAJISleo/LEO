"""
tests/test_prediction_fallback.py
=================================
Tests Phase 10 predictive execution and fail-closed exact fallback.
Validates behavior under both standard and adversarial distribution shifts.
"""

import numpy as np
import pytest
from hyper.candidate import PathClass
from hyper.residual.residual_engine import PredictiveResidualEngine


def test_prediction_accepted_when_accurate():
    engine = PredictiveResidualEngine()
    current_input = np.array([10.0, 20.0, 30.0])

    # Perfect predictor
    predictor = lambda prev, curr: np.array([10.0, 20.0, 30.0])
    error_est = lambda pred, curr: float(np.max(np.abs(pred - curr)))
    verifier = lambda val, max_err: (True, 0.0)
    residual_fn = lambda curr, pred: (curr - pred, 0.01)
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

    assert telemetry["path_class"] == PathClass.PREDICTIVE.value
    assert telemetry["prediction_used"] is True
    assert telemetry["fallback_used"] is False


def test_adversarial_distribution_shift_triggers_exact_fallback():
    engine = PredictiveResidualEngine()
    current_input = np.array([100.0, -500.0, 999.0])  # Adversarial distribution shift

    # Completely wrong predictor
    predictor = lambda prev, curr: np.array([0.0, 0.0, 0.0])
    error_est = lambda pred, curr: float(np.max(np.abs(pred - curr)))
    # Verifier rejects everything that deviates from ground truth
    verifier = lambda val, max_err: (False, 999.0)
    # Residual calculation also fails verifier
    residual_fn = lambda curr, pred: (np.zeros_like(curr), 0.01)
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

    assert telemetry["path_class"] == PathClass.FALLBACK_EXACT.value
    assert telemetry["fallback_used"] is True
    assert np.array_equal(res, current_input)
