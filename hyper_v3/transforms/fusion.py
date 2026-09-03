"""
hyper_v3/transforms/fusion.py
In-register operator fusion for linear algebraic sequences (GEMM + Bias + GELU/ReLU).
"""

from typing import Tuple
import numpy as np


class FusionTransformer:
    """Fuses sequential elementwise operators into single compute passes."""

    @staticmethod
    def fused_gemm_bias_relu(a: np.ndarray, b: np.ndarray, bias: np.ndarray) -> np.ndarray:
        c = np.matmul(a, b)
        c += bias
        np.maximum(c, 0, out=c)
        return c

    @staticmethod
    def fused_gemm_bias_gelu(a: np.ndarray, b: np.ndarray, bias: np.ndarray) -> np.ndarray:
        c = np.matmul(a, b)
        c += bias
        # Fast tanh approximation of GELU
        sqrt_2_over_pi = 0.7978845608028654
        c = 0.5 * c * (1.0 + np.tanh(sqrt_2_over_pi * (c + 0.044715 * np.power(c, 3))))
        return c
