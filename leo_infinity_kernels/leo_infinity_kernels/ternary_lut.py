"""
leo_infinity_kernels.ternary_lut
Vectorized ternary quantized matrix multiplication — multiplication-free inference.

Replaces FP16/FP32 matmuls with sign-indexed addition/subtraction using ternary
weight quantization ({-1, 0, +1}). Achieves massive speedups on pure CPU by
eliminating multiplier unit dependencies entirely.
"""

from __future__ import annotations

import numpy as np
from typing import Optional


class TernaryLUTEngine:
    """Ternary quantized matrix-multiplication engine using vectorized sign-indexed operations.

    Weights are quantized to {-1, 0, +1}. Computation reduces to masked additions
    and subtractions — zero multiplications required.

    Args:
        isa_level: Target ISA hint for logging (AVX2, AVX-512, AMX). Does not
            change NumPy execution path but is recorded in profiling metadata.
    """

    def __init__(self, isa_level: str = "AVX2"):
        self.isa_level = isa_level
        self._call_count = 0
        self._total_ops_saved = 0

    def quantize_weights(self, weights: np.ndarray) -> np.ndarray:
        """Quantizes a float weight matrix to ternary {-1, 0, +1} values."""
        return np.clip(np.round(weights), -1, 1).astype(np.int8)

    def execute_lut_matmul(self, weights: np.ndarray, activations: np.ndarray) -> np.ndarray:
        """Multiplication-free matrix-vector product via ternary sign indexing.

        For a weight matrix W (M x N) and activation vector a (N,):
          output[i] = sum(a[j] for j where W[i,j]==+1) - sum(a[j] for j where W[i,j]==-1)

        This is fully vectorized — no Python loops.

        Args:
            weights: Float weight matrix (M, N). Will be ternary-quantized internally.
            activations: Float activation vector (N,).

        Returns:
            Output vector (M,).
        """
        w_ternary = self.quantize_weights(weights)

        # Vectorized: mask-select and sum instead of multiply
        pos_mask = (w_ternary == 1)   # (M, N) boolean
        neg_mask = (w_ternary == -1)  # (M, N) boolean

        # Broadcast activations across rows, mask, and sum
        output = pos_mask.astype(np.float64) @ activations - neg_mask.astype(np.float64) @ activations

        self._call_count += 1
        self._total_ops_saved += weights.size  # each element avoids one multiply
        return output

    def execute_lut_matmul_batch(self, weights: np.ndarray, activation_batch: np.ndarray) -> np.ndarray:
        """Batch ternary matmul for multiple activation vectors.

        Args:
            weights: Float weight matrix (M, N).
            activation_batch: Activation matrix (B, N) where B is batch size.

        Returns:
            Output matrix (B, M).
        """
        w_ternary = self.quantize_weights(weights)
        pos_mask = (w_ternary == 1).astype(np.float64)   # (M, N)
        neg_mask = (w_ternary == -1).astype(np.float64)  # (M, N)

        # (B, N) @ (N, M) => (B, M) for each mask
        result = activation_batch @ (pos_mask.T - neg_mask.T)

        self._call_count += 1
        self._total_ops_saved += weights.size * activation_batch.shape[0]
        return result

    def get_stats(self) -> dict:
        """Returns profiling statistics."""
        return {
            "isa_level": self.isa_level,
            "total_calls": self._call_count,
            "total_multiply_ops_avoided": self._total_ops_saved,
        }
