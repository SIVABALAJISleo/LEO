"""
tests/test_approximation_error_bounds.py
========================================
Tests Phase 9 approximation error bounding across precision tiers.
Ensures that errors are rigorously computed and bounded.
"""

import numpy as np
import pytest
from hyper.precision.precision_engine import PrecisionEngine


def test_precision_modes_error_ordering():
    engine = PrecisionEngine()
    rng = np.random.RandomState(42)
    A = rng.randn(64, 64).astype(np.float32)
    B = rng.randn(64, 64).astype(np.float32)

    _, r_f64 = engine.execute_matmul(A, B, mode="float64")
    _, r_f32 = engine.execute_matmul(A, B, mode="float32")
    _, r_f16 = engine.execute_matmul(A, B, mode="float16")
    _, r_i8 = engine.execute_matmul(A, B, mode="int8")

    assert r_f64["max_abs_error"] == 0.0
    # FP32 error relative to FP64 should be very small
    assert r_f32["max_abs_error"] < 1e-4
    # FP16 error should be bounded
    assert r_f16["max_abs_error"] < 0.1
    # INT8 error should be bounded
    assert r_i8["relative_error"] < 0.1


def test_invalid_precision_mode_rejected():
    engine = PrecisionEngine()
    A = np.eye(4, dtype=np.float32)
    B = np.eye(4, dtype=np.float32)
    with pytest.raises(ValueError, match="Unsupported precision mode"):
        engine.execute_matmul(A, B, mode="super_float_128")
