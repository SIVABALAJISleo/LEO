"""
tests/hostile/test_precomputation_attack.py
===========================================
Precomputation Attack (Phases 2 & 18).
Ensures all offline precomputation and training overhead is accounted for in
the total lifetime cost calculation and never hidden.
"""

import numpy as np
import pytest
from hyper_x.leaf.neural import NeuralImplicitField, NIRTrainer


def test_precomputation_cost_transparency():
    trainer = NIRTrainer()
    field = NeuralImplicitField(in_dim=1, out_dim=1, hidden_dim=16, num_layers=2)

    x_train = np.linspace(-1, 1, 50, dtype=np.float32)
    y_train = np.sin(x_train * 3.14159)

    trained_field, cost_report = trainer.train_field(
        field, x_train, y_train, epochs=20, lr=1e-2
    )

    # Precomputation / training overhead MUST be strictly positive and reported
    assert cost_report.training_time_ms > 0.0
    assert cost_report.training_flops > 0
    assert cost_report.representation_size_bytes > 0
    assert cost_report.total_lifetime_cost_ms >= cost_report.training_time_ms
    assert cost_report.amortized_break_even_queries > 0
