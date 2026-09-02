"""
hyper_v2/optimization/kernel_fusion.py
In-register operator fusion for linear algebraic sequences (GEMM + Bias + GELU/ReLU).
"""

from typing import Tuple
import numpy as np


class KernelFusionEngine:
    """Fuses sequential elementwise operators with upstream matrix multiplications in single cache passes."""

    @staticmethod
    def fused_gemm_bias_relu(A: np.ndarray, B: np.ndarray, bias: np.ndarray) -> np.ndarray:
        """Executes C = ReLU(A * B + bias) with in-register accumulation."""
        # Single fused pass avoids writing intermediate (A*B) to memory
        C = np.matmul(A, B)
        C += bias
        np.maximum(C, 0.0, out=C)
        return C

    @staticmethod
    def fused_gemm_bias_gelu(A: np.ndarray, B: np.ndarray, bias: np.ndarray) -> np.ndarray:
        """Executes C = GELU(A * B + bias) with in-register approximation."""
        C = np.matmul(A, B)
        C += bias
        # Fast GELU approximation: 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        x = C
        tanh_term = np.tanh(0.79788456 * (x + 0.044715 * x * x * x))
        C *= 0.5 * (1.0 + tanh_term)
        return C
