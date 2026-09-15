"""
hyper_x/leaf/neural/distillation.py
===================================
Teacher-to-student distillation for compact NIR models.
"""

from typing import Any, Callable, Dict, List, Tuple
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from .implicit_field import NeuralImplicitField


class NeuralDistiller:
    """Distills heavy reference outputs or large models into a compact NIR student."""

    def distill(
        self,
        teacher_fn: Callable[[np.ndarray], np.ndarray],
        student_field: NeuralImplicitField,
        sample_coordinates: np.ndarray,
        epochs: int = 30,
        lr: float = 1e-2,
    ) -> NeuralImplicitField:
        targets = teacher_fn(sample_coordinates)
        optimizer = optim.Adam(student_field.parameters(), lr=lr)
        criterion = nn.MSELoss()

        x = torch.from_numpy(np.asarray(sample_coordinates, dtype=np.float32))
        if x.ndim == 1 and student_field.in_dim == 1:
            x = x.unsqueeze(-1)
        y = torch.from_numpy(np.asarray(targets, dtype=np.float32))
        if y.ndim == 1 and student_field.out_dim == 1:
            y = y.unsqueeze(-1)

        student_field.train()
        for _ in range(epochs):
            optimizer.zero_grad()
            out = student_field(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()

        student_field.eval()
        return student_field
