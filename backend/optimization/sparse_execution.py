"""
backend/optimization/sparse_execution.py
Subsystem 9: Sparse Execution Engine.
Implements:
- Dynamic layer skipping via confidence-based early exit
- Adaptive computation depth
- Mixture-of-Experts (MoE) routing stub
"""

import torch
import torch.nn as nn
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class EarlyExitClassifier(nn.Module):
    """
    Lightweight exit-gate attached to each transformer layer.
    If the intermediate representation's confidence exceeds a threshold,
    skip remaining layers and return the early prediction.
    """
    def __init__(self, hidden_dim: int, num_classes: int = 2):
        super().__init__()
        self.gate = nn.Linear(hidden_dim, num_classes)

    def forward(self, hidden: torch.Tensor) -> Tuple[torch.Tensor, float]:
        logits = self.gate(hidden.mean(dim=1))  # Pool over sequence
        probs = torch.softmax(logits, dim=-1)
        confidence = float(probs.max())
        return logits, confidence


class AdaptiveDepthModel(nn.Module):
    """
    Wraps a stack of transformer layers with early-exit gates.
    Skips remaining layers once confidence threshold is reached.
    """
    def __init__(self, layers: nn.ModuleList, hidden_dim: int,
                 exit_threshold: float = 0.90, num_classes: int = 2):
        super().__init__()
        self.layers = layers
        self.exit_threshold = exit_threshold
        self.exit_gates = nn.ModuleList([
            EarlyExitClassifier(hidden_dim, num_classes) for _ in layers
        ])
        self.layers_executed = 0

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, int]:
        self.layers_executed = 0
        for i, (layer, gate) in enumerate(zip(self.layers, self.exit_gates)):
            x = layer(x)
            self.layers_executed = i + 1
            logits, confidence = gate(x)
            if confidence >= self.exit_threshold:
                logger.debug(f"Early exit at layer {i+1}/{len(self.layers)} "
                             f"(confidence: {confidence:.3f})")
                return logits, self.layers_executed
        return logits, self.layers_executed


class MixtureOfExpertsRouter(nn.Module):
    """
    Sparse MoE: Routes each token to the top-K most relevant experts.
    Reduces average computation per token while maintaining capacity.
    """
    def __init__(self, num_experts: int = 8, hidden_dim: int = 256, top_k: int = 2):
        super().__init__()
        self.num_experts = num_experts
        self.top_k = top_k
        self.gate = nn.Linear(hidden_dim, num_experts)
        self.experts = nn.ModuleList([
            nn.Sequential(nn.Linear(hidden_dim, hidden_dim * 2), nn.GELU(),
                          nn.Linear(hidden_dim * 2, hidden_dim))
            for _ in range(num_experts)
        ])

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, hidden_dim)
        gate_logits = self.gate(x)                        # (B, S, num_experts)
        weights, indices = torch.topk(gate_logits, self.top_k, dim=-1)
        weights = torch.softmax(weights, dim=-1)           # (B, S, top_k)

        output = torch.zeros_like(x)
        for k in range(self.top_k):
            expert_idx = indices[..., k]                  # (B, S)
            w = weights[..., k].unsqueeze(-1)             # (B, S, 1)
            # Dispatch each token to the assigned expert
            # Simplified: apply all experts and mask (true sparse dispatch needs custom CUDA)
            for e in range(self.num_experts):
                mask = (expert_idx == e).unsqueeze(-1).float()
                output += mask * w * self.experts[e](x)

        return output
