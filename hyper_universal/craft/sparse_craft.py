"""
hyper_universal/craft/sparse_craft.py
====================================
10.2 SparseCraft: Sparsity-Aware Computation & Structured Optimization Engine.
Implements Section 10.2 of the Master Specification:
- Detects genuine sparsity in input tensors.
- Rejects sparse conversion when sparsity < 20% (Negative Knowledge Rule: conversion
  overhead exceeds dense BLAS speedup on dense matrices).
- When sparsity >= 20%, compares:
    1. Dense BLAS baseline
    2. Sparse CSR execution (kernel only)
    3. Sparse conversion overhead + execution (end-to-end)
    4. 2:4 Structured AVX2 SIMD sparsity (hardware-friendly 50% pruning)
- Accurately measures memory traffic, conversion cost, and numerical correctness.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional, Tuple
import numpy as np
import scipy.sparse as sp

from hyper_universal.kernels.sparse_2_4_avx2 import prune_and_pack_2_4, gemm_2_4_sparse_avx2


class SparseCraft:
    """
    Sparsity detection, evaluation, and execution engine.
    Honors negative knowledge: never assumes sparse is faster for dense inputs.
    """

    def __init__(self, sparsity_threshold: float = 0.20, zero_tolerance: float = 1e-5) -> None:
        self.sparsity_threshold = sparsity_threshold
        self.zero_tolerance = zero_tolerance

    def analyze_sparsity(self, matrix: np.ndarray) -> Dict[str, Any]:
        """
        Calculates sparsity metrics and checks preconditions for sparse acceleration.
        """
        assert isinstance(matrix, np.ndarray), "Input must be a numpy ndarray"
        total_elements = matrix.size
        zero_elements = int(np.sum(np.abs(matrix) <= self.zero_tolerance))
        sparsity_ratio = zero_elements / max(1, total_elements)

        dense_bytes = matrix.nbytes
        nnz = total_elements - zero_elements
        # CSR storage: values (nnz * 4/8 bytes) + col_indices (nnz * 4 bytes) + row_ptr ((M + 1) * 4 bytes)
        csr_bytes = (nnz * matrix.itemsize) + (nnz * 4) + ((matrix.shape[0] + 1) * 4)

        is_sparse_advantageous = sparsity_ratio >= self.sparsity_threshold

        return {
            "total_elements": total_elements,
            "nnz": nnz,
            "sparsity_ratio": round(sparsity_ratio, 4),
            "sparsity_pct": round(sparsity_ratio * 100.0, 2),
            "dense_bytes": dense_bytes,
            "estimated_csr_bytes": csr_bytes,
            "memory_reduction_ratio": round(dense_bytes / max(1, csr_bytes), 2),
            "sparse_advantageous": is_sparse_advantageous,
            "precondition_reason": (
                f"Sparsity {sparsity_ratio*100:.1f}% >= threshold {self.sparsity_threshold*100:.1f}%"
                if is_sparse_advantageous
                else f"Sparsity {sparsity_ratio*100:.1f}% < threshold {self.sparsity_threshold*100:.1f}%; sparse conversion rejected."
            ),
        }

    def execute_sparse_or_dense_gemm(
        self,
        A: np.ndarray,
        B: np.ndarray,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes matrix multiplication selecting between Dense BLAS, Sparse CSR,
        or 2:4 Structured AVX2 Sparsity based on measured end-to-end efficiency.
        """
        A_f32 = np.ascontiguousarray(A, dtype=np.float32)
        B_f32 = np.ascontiguousarray(B, dtype=np.float32)

        analysis = self.analyze_sparsity(A_f32)
        sparsity_ratio = analysis["sparsity_ratio"]

        # 1. Baseline: Dense BLAS
        t0 = time.perf_counter()
        dense_out = A_f32 @ B_f32
        t_dense = (time.perf_counter() - t0) * 1000.0

        if not analysis["sparse_advantageous"]:
            # Precondition check failed: retain Dense BLAS to avoid conversion slowdown
            metadata = {
                "selected_path": "DENSE_BLAS_AVX2",
                "sparsity_ratio": sparsity_ratio,
                "sparse_advantageous": False,
                "conversion_overhead_ms": 0.0,
                "kernel_time_ms": round(t_dense, 3),
                "end_to_end_ms": round(t_dense, 3),
                "dense_baseline_ms": round(t_dense, 3),
                "speedup": 1.0,
                "max_abs_error": 0.0,
                "reason": analysis["precondition_reason"],
            }
            return dense_out, metadata

        # 2. Sparse CSR Pathway (Conversion + Kernel)
        t_conv_start = time.perf_counter()
        A_csr = sp.csr_matrix(A_f32)
        t_conv = (time.perf_counter() - t_conv_start) * 1000.0

        t_csr_start = time.perf_counter()
        csr_out = A_csr.dot(B_f32)
        t_csr_kernel = (time.perf_counter() - t_csr_start) * 1000.0
        t_csr_total = t_conv + t_csr_kernel

        max_err = float(np.max(np.abs(csr_out - dense_out)))

        # 3. Decision Gate: Does conversion + kernel beat dense baseline?
        if t_csr_total < t_dense:
            selected_path = "SPARSE_CSR"
            output = csr_out
            e2e_ms = t_csr_total
            speedup = t_dense / max(t_csr_total, 1e-6)
        else:
            # Conversion overhead outweighed sparse kernel gains
            selected_path = "DENSE_BLAS_FALLBACK"
            output = dense_out
            e2e_ms = t_dense
            speedup = 1.0

        metadata = {
            "selected_path": selected_path,
            "sparsity_ratio": sparsity_ratio,
            "sparse_advantageous": True,
            "conversion_overhead_ms": round(t_conv, 3),
            "sparse_kernel_ms": round(t_csr_kernel, 3),
            "sparse_end_to_end_ms": round(t_csr_total, 3),
            "dense_baseline_ms": round(t_dense, 3),
            "end_to_end_ms": round(e2e_ms, 3),
            "speedup": round(speedup, 2),
            "max_abs_error": max_err,
            "verified": max_err <= 1e-4,
        }
        return output, metadata

    def execute_2_4_structured_sparsity(
        self,
        X: np.ndarray,
        W: np.ndarray,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes 2:4 structured SIMD sparse matrix multiplication using compiled AVX2 kernels.
        Guarantees exactly 2 zero elements per 4-element vector block.
        """
        X_f32 = np.ascontiguousarray(X, dtype=np.float32)
        W_f32 = np.ascontiguousarray(W, dtype=np.float32)

        # Reference dense
        t0 = time.perf_counter()
        dense_out = X_f32 @ W_f32.T
        t_dense = (time.perf_counter() - t0) * 1000.0

        # Pack W into 2:4 structure
        t_pack_start = time.perf_counter()
        W_packed, indices_packed, W_masked = prune_and_pack_2_4(W_f32)
        t_pack = (time.perf_counter() - t_pack_start) * 1000.0

        # Run 2:4 AVX2 SIMD GEMM
        t_simd_start = time.perf_counter()
        sparse_out = gemm_2_4_sparse_avx2(X_f32, W_packed, indices_packed)
        t_simd = (time.perf_counter() - t_simd_start) * 1000.0
        t_total = t_pack + t_simd

        diff = float(np.max(np.abs(sparse_out - dense_out)))
        # Relative error against dense reference
        rel_diff = diff / max(float(np.max(np.abs(dense_out))), 1e-6)

        metadata = {
            "algorithm": "2:4 Structured Sparsity AVX2 SIMD",
            "packing_ms": round(t_pack, 3),
            "kernel_simd_ms": round(t_simd, 3),
            "total_ms": round(t_total, 3),
            "dense_baseline_ms": round(t_dense, 3),
            "max_absolute_error": diff,
            "max_relative_error": rel_diff,
            "theoretical_flop_reduction": 0.50,
        }
        return sparse_out, metadata
