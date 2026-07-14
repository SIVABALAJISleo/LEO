"""
phoenix/bitnet_b158.py
BitNet b1.58: 1.58-bit (Ternary) Quantization.
Quantizes weights to {-1, 0, 1}, eliminating multiplications in matmul
and replacing them with integer additions. Massive speedup on CPU/iGPU.
"""

import torch
import torch.nn as nn

def activation_quant(x: torch.Tensor) -> torch.Tensor:
    """Scale activations to [-128, 127] (INT8)."""
    scale = 127.0 / x.abs().max(dim=-1, keepdim=True).values.clamp_(min=1e-5)
    y = (x * scale).round().clamp_(-128, 127) / scale
    return y

def weight_quant(w: torch.Tensor) -> torch.Tensor:
    """Scale weights to ternary values {-1, 0, 1}."""
    scale = 1.0 / w.abs().mean().clamp_(min=1e-5)
    e = (w * scale).round().clamp_(-1, 1)
    # STE: straight-through estimator for gradients
    return (e - w).detach() + w

class BitLinear(nn.Linear):
    """
    BitNet Linear Layer.
    Uses 1.58-bit ternary weights and 8-bit activations.
    """
    def __init__(self, in_features: int, out_features: int, bias: bool = False):
        super().__init__(in_features, out_features, bias)
        self.layernorm = nn.LayerNorm(in_features)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass applying activation and weight quantization.
        """
        # 1. Normalize and quantize activations
        x_norm = self.layernorm(x)
        x_quant = activation_quant(x_norm)
        
        # 2. Quantize weights to {-1, 0, 1}
        w_quant = weight_quant(self.weight)
        
        # 3. Dense operation (simulated here; true impl uses int8/int2 kernels)
        out = torch.nn.functional.linear(x_quant, w_quant)
        
        return out

class BitNetb158Model(nn.Module):
    """
    Demo architecture replacing all nn.Linear with BitLinear
    """
    def __init__(self, d_model: int):
        super().__init__()
        self.net = nn.Sequential(
            BitLinear(d_model, d_model * 4),
            nn.SiLU(),
            BitLinear(d_model * 4, d_model)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
