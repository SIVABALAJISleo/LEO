"""
phoenix/pabee_early_exit.py
PABEE: Patience-Based Early Exit for Transformers (Sun et al., 2020).
Exits inference at an intermediate layer when predictions stabilize
across `patience` consecutive layers — saving 40-60% of computation.
"""

import torch
import torch.nn as nn
from typing import List, Optional, Tuple


class PABEEClassifier(nn.Module):
    """Lightweight exit head attached to each transformer layer."""
    def __init__(self, hidden_dim: int, num_classes: int):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.cls  = nn.Linear(hidden_dim, num_classes)

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        # hidden: (batch, seq, hidden) → pool → (batch, hidden) → logits
        h = hidden.transpose(1, 2)          # (batch, hidden, seq)
        h = self.pool(h).squeeze(-1)        # (batch, hidden)
        return self.cls(h)                  # (batch, num_classes)


class PABEEController:
    """
    Wraps a stack of transformer layers + exit classifiers.
    At inference time, monitors when predictions stabilize across
    `patience` consecutive layer exits and returns early.
    """

    def __init__(self, layers: nn.ModuleList, hidden_dim: int,
                 num_classes: int, patience: int = 3,
                 confidence_threshold: float = 0.0):
        self.layers    = layers
        self.patience  = patience
        self.threshold = confidence_threshold

        # One exit classifier per layer
        self.exit_classifiers = nn.ModuleList([
            PABEEClassifier(hidden_dim, num_classes)
            for _ in layers
        ])

        # Profiling counters
        self.total_calls  = 0
        self.total_layers = 0
        self.exit_counts  = [0] * len(layers)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, int]:
        """
        Runs layers sequentially, returning (final_logits, exit_layer_idx).
        Exits when predictions agree across `patience` consecutive layers.
        """
        self.total_calls += 1
        prev_predictions: List[torch.Tensor] = []

        for i, (layer, classifier) in enumerate(
            zip(self.layers, self.exit_classifiers)
        ):
            x = layer(x)
            self.total_layers += 1

            logits = classifier(x)
            pred   = logits.argmax(dim=-1)          # (batch,)

            prev_predictions.append(pred)

            # Check if last `patience` predictions are identical
            if len(prev_predictions) >= self.patience:
                recent = prev_predictions[-self.patience:]
                if all(torch.equal(recent[0], p) for p in recent[1:]):
                    self.exit_counts[i] += 1
                    return logits, i

        # Full depth (no early exit)
        self.exit_counts[-1] += 1
        return logits, len(self.layers) - 1

    def compute_savings(self) -> dict:
        """Returns average layers used and compute saved vs full depth."""
        if self.total_calls == 0:
            return {"avg_layers": 0, "savings_pct": 0.0}

        avg = self.total_layers / self.total_calls
        full = len(self.layers)
        return {
            "total_calls":     self.total_calls,
            "avg_layers_used": round(avg, 2),
            "full_depth":      full,
            "savings_pct":     round((1 - avg / full) * 100, 1),
            "exit_distribution": self.exit_counts,
        }
