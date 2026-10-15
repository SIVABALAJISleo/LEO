import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import os
import warnings

# Attempt to load the custom AVX2 C++ extension
try:
    from core_ai.kernels import bitnet_avx2_ext
    HAS_AVX2_EXT = True
except ImportError:
    HAS_AVX2_EXT = False

try:
    import numpy as np
    from hyper_universal.kernels.bitnet_ternary_avx2 import bitnet_ternary_gemm_avx2
    HAS_NUMBA_AVX2 = True
except ImportError:
    HAS_NUMBA_AVX2 = False

class LinearBitNet(nn.Module):
    """
    1.58-bit Singularity Linear Layer.
    Bypasses standard floating-point multiplication in favor of AVX2 integer addition/subtraction.
    """
    def __init__(self, in_features, out_features, bias=True):
        super(LinearBitNet, self).__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # Store weights in fp32 initially (for loading checkpoints), we will quantize at inference.
        self.weight = nn.Parameter(torch.Tensor(out_features, in_features))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features))
        else:
            self.register_parameter('bias', None)
            
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5)) if 'math' in globals() else None
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in) if 'math' in globals() else 0.1
            nn.init.uniform_(self.bias, -bound, bound)

    def absmean_quantize_weights(self, w):
        """Quantizes weights to {-1, 0, 1}."""
        scale = w.abs().mean().clamp(min=1e-5)
        # Quantize to ternary
        w_quant = torch.round(w / scale).clamp(-1, 1)
        return w_quant, scale

    def forward(self, x):
        # 1. Quantize weights to 1.58-bit (-1, 0, 1)
        w_quant, w_scale = self.absmean_quantize_weights(self.weight)
        
        # 2. Quantize inputs to int16 (to eliminate FPU during the core loop)
        x_scale = x.abs().max(dim=-1, keepdim=True)[0].clamp(min=1e-5) / 32767.0
        x_int16 = torch.round(x / x_scale).to(torch.int16)
        w_int8 = w_quant.to(torch.int8)
        
        # 3. Route through custom AVX2 kernel if available
        if HAS_AVX2_EXT:
            original_shape = x_int16.shape
            if x_int16.dim() > 2:
                x_int16 = x_int16.view(-1, self.in_features)
                
            out_int32 = bitnet_avx2_ext.bitnet_matmul(x_int16, w_int8)
            
            if len(original_shape) > 2:
                out_int32 = out_int32.view(*original_shape[:-1], self.out_features)
                
            # Dequantize back to float for the output edges
            out = out_int32.to(torch.float32) * (x_scale * w_scale)
        elif HAS_NUMBA_AVX2:
            # Compiled AVX2 SIMD path (LLVM JIT native instructions, zero FPU multiplications)
            original_shape = x.shape
            x_2d = x.reshape(-1, self.in_features).detach().cpu().numpy().astype(np.float32)
            w_2d = w_quant.detach().cpu().numpy().astype(np.int8)
            out_simd = bitnet_ternary_gemm_avx2(x_2d, w_2d, gamma=1.0)
            out = torch.from_numpy(out_simd).to(device=x.device, dtype=torch.float32)
            if len(original_shape) > 2:
                out = out.reshape(*original_shape[:-1], self.out_features)
        else:
            # Fallback simulated forward (Standard Torch)
            out = F.linear(x, w_quant)
            
        if self.bias is not None:
            out += self.bias
            
        return out

