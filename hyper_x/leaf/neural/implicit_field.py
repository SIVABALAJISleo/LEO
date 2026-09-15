"""
hyper_x/leaf/neural/implicit_field.py
=====================================
Neural Implicit Field (NIR) architecture: compact coordinate MLP.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch
import torch.nn as nn


class SinusoidalActivation(nn.Module):
    """SIREN-style sinusoidal activation: sin(omega * x)."""
    def __init__(self, omega: float = 30.0):
        super().__init__()
        self.omega = omega

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.sin(self.omega * x)


class NeuralImplicitField(nn.Module):
    """
    Compact Neural Implicit Resolution network:
    Maps spatial/temporal/parameter coordinates (d_in) -> observables (d_out).
    """

    def __init__(
        self,
        in_dim: int = 1,
        out_dim: int = 1,
        hidden_dim: int = 32,
        num_layers: int = 2,
    ):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.hidden_dim = hidden_dim

        layers: List[nn.Module] = []
        layers.append(nn.Linear(in_dim, hidden_dim))
        layers.append(SinusoidalActivation(omega=30.0))

        for _ in range(num_layers - 1):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(SinusoidalActivation(omega=1.0))

        layers.append(nn.Linear(hidden_dim, out_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

    def query_numpy(self, coords: np.ndarray) -> np.ndarray:
        """Evaluates neural field on numpy coordinate array."""
        self.eval()
        with torch.no_grad():
            inp = torch.from_numpy(np.asarray(coords, dtype=np.float32))
            if inp.ndim == 1 and self.in_dim == 1:
                inp = inp.unsqueeze(-1)
            out = self.net(inp)
            return out.cpu().numpy().squeeze()

    @property
    def parameter_bytes(self) -> int:
        """Calculates exact parameter footprint in bytes."""
        total = sum(p.numel() * p.element_size() for p in self.parameters())
        return total
