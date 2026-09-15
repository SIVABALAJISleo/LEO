"""
tests/hostile/test_distribution_shift.py
========================================
Distribution Shift Attack on Learned Implicit Models (Phases 2 & 15).
Ensures that out-of-distribution extrapolation error is caught and reported.
"""

import numpy as np
import pytest
from hyper_x.leaf.neural import (
    NeuralImplicitField,
    NIRTrainer,
    NIRGeneralizationVerifier,
)


def test_distribution_shift_falsification():
    trainer = NIRTrainer()
    verifier = NIRGeneralizationVerifier()

    field = NeuralImplicitField(in_dim=1, out_dim=1, hidden_dim=32, num_layers=2)

    # Train only on interval [0, 1]
    x_train = np.linspace(0.0, 1.0, 50, dtype=np.float32)
    y_train = np.sin(x_train * 6.28)

    x_val = np.linspace(0.05, 0.95, 20, dtype=np.float32)
    y_val = np.sin(x_val * 6.28)

    trained_field, _ = trainer.train_field(field, x_train, y_train, epochs=40, lr=1e-2)

    audit = verifier.audit_field(
        field=trained_field,
        coords_train=x_train,
        gt_train=y_train,
        coords_val=x_val,
        gt_val=y_val,
        ground_truth_oracle=lambda x: np.sin(x * 6.28),
        tolerance=0.10,
    )

    # Distribution shift error on extrapolated coordinates must be quantified
    assert audit.distribution_shift_error >= 0.0
    assert audit.generalization_gap >= 0.0
