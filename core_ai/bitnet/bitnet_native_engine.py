"""
LEO AI V42 - The Irrelevance Engine
Phase 1: BitNet Native Layer (1.58-bit Ternary Weights)

Provides a PyTorch `nn.Module` replacement for `nn.Linear` that uses
1.58-bit (ternary) weights with absmean scaling and 8-bit activations.
Optimized for consumer CPU execution by completely avoiding CUDA/GPU dependencies.
"""

import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


@njit(parallel=True, fastmath=True)
def _unpack_and_gemm_cpu_kernel(packed_w, scale_w, x_quant, out):
    """
    Numba JIT optimized kernel for 1.58-bit matrix multiplication on CPU.
    packed_w: uint32 array of shape (out_features, in_features // 16)
    scale_w: float32 array of shape (out_features, 1)
    x_quant: int8 array of shape (batch, in_features)
    out: float32 array of shape (batch, out_features)
    
    Ternary encoding mapping (2-bit):
    00 -> -1
    01 -> 0
    10 -> +1
    11 -> unused
    """
    batch_size = x_quant.shape[0]
    out_features = packed_w.shape[0]
    in_features = x_quant.shape[1]
    
    # Pre-compute decode table for 2-bit sequences (optional, but inline shift/mask is fast)
    for b in prange(batch_size):
        for o in prange(out_features):
            acc = 0.0
            for i_blk in range(packed_w.shape[1]):
                val32 = packed_w[o, i_blk]
                for i_sub in range(16):
                    in_idx = i_blk * 16 + i_sub
                    if in_idx >= in_features:
                        break
                    
                    # Extract 2 bits
                    bits = (val32 >> (i_sub * 2)) & 0b11
                    
                    # Map to ternary: 00(-1), 01(0), 10(+1)
                    ternary = bits - 1
                    
                    # Multiply with activation
                    acc += ternary * x_quant[b, in_idx]
            
            # Dequantize
            out[b, o] = acc * scale_w[o, 0]


class BitLinear(nn.Linear):
    """
    Drop-in replacement for `nn.Linear` that uses BitNet b1.58 ternary weights.
    Maintains floating point input/output interfaces but internally operates
    on 8-bit activations and packed 2-bit weights.
    """
    def __init__(self, in_features, out_features, bias=False, numba_fallback=True):
        super().__init__(in_features, out_features, bias)
        self.in_features = in_features
        self.out_features = out_features
        self.numba_fallback = numba_fallback
        
        # We don't need regular weights once packed
        self.weight.requires_grad_(False)
        self.register_buffer("packed_weight", torch.zeros((out_features, math.ceil(in_features / 16)), dtype=torch.int32))
        self.register_buffer("weight_scale", torch.ones((out_features, 1), dtype=torch.float32))
        self.is_packed = False
        
    def pack_weights(self):
        """Quantizes the fp32 weight matrix into packed 1.58-bit (ternary) representations."""
        w = self.weight.detach()
        
        # Absmean quantization per output channel
        scale = w.abs().mean(dim=1, keepdim=True)
        scale = scale.clamp(min=1e-5)
        
        w_quant = torch.round(w / scale).clamp(-1, 1).to(torch.int8)
        self.weight_scale.copy_(scale)
        
        # Pack 16 weights into 1 int32
        packed = torch.zeros((self.out_features, math.ceil(self.in_features / 16)), dtype=torch.int32)
        
        for i in range(self.out_features):
            for j in range(self.in_features):
                block = j // 16
                offset = j % 16
                
                val = w_quant[i, j].item()
                # Map -1 -> 0, 0 -> 1, +1 -> 2
                mapped = val + 1
                
                packed[i, block] |= (mapped << (offset * 2))
                
        self.packed_weight.copy_(packed)
        self.is_packed = True
        
        # Free up the original fp32 weights
        self.weight = None

    def _quantize_activations(self, x: torch.Tensor):
        """Quantize activations to 8-bit per token using absmax quantization."""
        x_absmax = x.abs().max(dim=-1, keepdim=True).values.clamp(min=1e-5)
        scale = 127.0 / x_absmax
        x_quant = torch.round(x * scale).clamp(-127, 127).to(torch.int8)
        return x_quant, 1.0 / scale

    def forward(self, x: torch.Tensor):
        if not self.is_packed:
            # Fallback to standard linear if not packed yet
            return F.linear(x, self.weight, self.bias)
            
        x_quant, x_scale = self._quantize_activations(x)
        
        # Reshape to 2D for batched GEMM
        original_shape = x.shape
        x_2d = x_quant.view(-1, self.in_features)
        
        out_2d = torch.zeros((x_2d.shape[0], self.out_features), dtype=torch.float32, device=x.device)
        
        if NUMBA_AVAILABLE and self.numba_fallback and x.device.type == 'cpu':
            # Run optimized C/NumPy kernel
            _unpack_and_gemm_cpu_kernel(
                self.packed_weight.numpy().astype(np.uint32),
                self.weight_scale.numpy(),
                x_2d.numpy(),
                out_2d.numpy()
            )
        else:
            # Slow PyTorch fallback for unpacking (should only run if numba isn't available)
            # Not meant for production speed, only correctness.
            # In production, a C++ extension would be bound here.
            w_unpacked = torch.zeros((self.out_features, self.in_features), dtype=torch.float32, device=x.device)
            for i in range(16):
                bits = (self.packed_weight >> (i * 2)) & 0b11
                ternary = bits - 1
                
                # Assign only up to in_features bounds
                mask = (torch.arange(self.packed_weight.shape[1]) * 16 + i) < self.in_features
                idx = (torch.arange(self.packed_weight.shape[1])[mask] * 16 + i)
                w_unpacked[:, idx] = ternary[:, mask].float()
                
            w_dequant = w_unpacked * self.weight_scale
            out_2d = F.linear(x_2d.float(), w_dequant)
            
        # Re-apply activation scaling
        out_2d = out_2d * x_scale.view(-1, 1)
        
        if self.bias is not None:
            out_2d += self.bias
            
        return out_2d.view(*original_shape[:-1], self.out_features)
