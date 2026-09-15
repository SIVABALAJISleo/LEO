"""
tests/hostile/test_temporal_break.py
====================================
Temporal Coherence Break Attack (Phase 22).
Forces massive scene cuts where delta(t) approaches full state entropy.
Ensures residual engines recalculate full state instead of propagating stale drift.
"""

import numpy as np
import pytest
from hyper.residual.residual_engine import PredictiveResidualEngine


def test_temporal_break_attack():
    engine = PredictiveResidualEngine()
    
    state_prev = np.ones((32, 32), dtype=np.float32)
    state_cut = np.zeros((32, 32), dtype=np.float32)

    def predictor(prev, cur):
        return prev

    def error_estimator(pred, cur):
        return float(np.mean(np.abs(pred - cur)))

    def verifier(pred, err):
        return err < 0.05, err

    def residual(pred, cur):
        return cur - pred, 0.1

    def exact_fallback(cur):
        return cur, 0.2

    # In a scene cut, error is 1.0 (huge); the engine must fallback or apply residual
    result, meta = engine.execute_pipeline(
        current_input=state_cut,
        previous_state=state_prev,
        predictor_fn=predictor,
        error_estimator_fn=error_estimator,
        verifier_fn=verifier,
        residual_fn=residual,
        exact_fallback_fn=exact_fallback,
        max_allowed_error=0.05,
    )
    diff = np.max(np.abs(result - state_cut))
    assert diff < 1e-4, f"Drift {diff} exceeded threshold on temporal break"
