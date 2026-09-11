"""
tests/test_counterfactual_execution.py
======================================
Unit tests for Mechanism 2: Counterfactual Execution with Lipschitz Bounds.
"""

import pytest
import numpy as np
from hyper_cco.contract import ComputeContract, ExactnessClass
from hyper_cco.counterfactual import (
    CounterfactualSkipEngine,
    CounterfactualDecision,
    LipschitzEstimator
)


def test_lipschitz_matrix_operator_norm():
    # Construct matrix with known spectral radius
    A = np.array([[3.0, 0.0], [0.0, 4.0]], dtype=np.float64)
    # ||A||_2 = 4.0, power iteration with safety margin should be >= 4.0
    L = LipschitzEstimator.estimate_matrix_operator_norm(A)
    assert L >= 4.0


def test_counterfactual_skip_within_tolerance():
    contract = ComputeContract(
        workload_id="CF_SKIP_TEST",
        exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
        max_absolute_error=0.10
    )
    engine = CounterfactualSkipEngine(default_safety_margin=1.5, verification_sample_rate=0.0)

    # Linear operator y = A x
    A = np.array([[0.5, 0.0], [0.0, 0.5]], dtype=np.float32)
    x_prev = np.array([1.0, 1.0], dtype=np.float32)
    # Perturbation delta_x = 0.01 -> delta_y <= 0.5 * 0.0141 ~ 0.007 << 0.10 / 1.5
    x_curr = np.array([1.01, 1.0], dtype=np.float32)

    engine.register_operator_lipschitz("linear_op", 0.6)

    out, decision = engine.evaluate_region_skip(
        region_id="reg_linear",
        operator_key="linear_op",
        x_current=x_curr,
        x_previous=x_prev,
        contract=contract,
        execute_fn=lambda x: A @ x
    )

    assert decision.decision == "SKIP"
    assert decision.estimated_impact <= (0.10 / 1.5)
    assert decision.confidence_score >= 0.70


def test_counterfactual_skip_rejected_on_large_delta():
    contract = ComputeContract(
        workload_id="CF_REJECT_TEST",
        max_absolute_error=0.01
    )
    engine = CounterfactualSkipEngine(default_safety_margin=2.0, verification_sample_rate=0.0)
    engine.register_operator_lipschitz("linear_op", 2.0)

    x_prev = np.array([1.0, 1.0], dtype=np.float32)
    x_curr = np.array([2.0, 2.0], dtype=np.float32)  # delta norm = 1.414 -> L * delta = 2.82 >> 0.01

    out, decision = engine.evaluate_region_skip(
        region_id="reg_large_delta",
        operator_key="linear_op",
        x_current=x_curr,
        x_previous=x_prev,
        contract=contract,
        execute_fn=lambda x: x * 2.0
    )

    assert decision.decision == "EXECUTE"
    assert decision.estimated_impact > (0.01 / 2.0)
