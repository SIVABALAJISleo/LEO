"""
tests/hostile/test_nir_holdout.py
=================================
Blind Holdout Attack on Neural Implicit Resolution (Phases 14, 18, 33).
Evaluates NIR surrogate on unseen test coordinates with independent oracle.
"""

import numpy as np
import pytest
from hyper_x.leaf.verification import BlindHoldoutEvaluator
from hyper_x.leaf.implicit import ImplicitEncoder, ImplicitDecoder


def test_nir_blind_holdout():
    evaluator = BlindHoldoutEvaluator()
    encoder = ImplicitEncoder()
    decoder = ImplicitDecoder()

    # Ground truth function: smooth cubic polynomial
    def oracle_fn(x: np.ndarray) -> np.ndarray:
        return 0.5 * (x ** 3) - 1.2 * (x ** 2) + 0.8 * x + 2.0

    # Fit polynomial field on training interval [-2, 2]
    x_train = np.linspace(-2.0, 2.0, 50, dtype=np.float32)
    y_train = oracle_fn(x_train)
    poly_field = encoder.fit_polynomial(x_train, y_train, degree=3)

    # Candidate runner queries the implicit field
    def candidate_runner(x_query: np.ndarray) -> np.ndarray:
        return decoder.decode_points(poly_field, x_query)

    # Holdout generator samples random unseen points in [-2, 2]
    def holdout_gen() -> np.ndarray:
        return np.random.uniform(-1.8, 1.8, 20).astype(np.float32)

    passed, max_err, avg_err = evaluator.evaluate_holdout(
        candidate_fn=candidate_runner,
        reference_fn=oracle_fn,
        holdout_generator=holdout_gen,
        trials=10,
        tolerance=1e-3,
    )

    assert passed is True, f"Holdout evaluation failed with max_err={max_err}"
    assert avg_err < 1e-3
