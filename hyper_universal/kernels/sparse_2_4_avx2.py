"""
hyper_universal/kernels/sparse_2_4_avx2.py
===========================================
High-Performance 2:4 Structured Sparsity Engine (NVIDIA Ampere/Ada style).
Compiles to native AVX2 SIMD via LLVM/Numba, eliminating pure Python loop overhead.

Every 4 contiguous elements contain at most 2 non-zero values:
- 50% memory bandwidth reduction (packed values + 2-bit indices).
- 2x theoretical compute density (K/2 multiply-accumulates per row).
- Numerical equivalence against ground truth masked matrix multiplication.
"""

from __future__ import annotations
import time
from typing import Dict, Tuple
import numpy as np
import numba


def prune_and_pack_2_4(W: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Prunes dense matrix W (M, K) to 2:4 structured sparsity.
    Packs 2 non-zero values per 4-element block into W_packed (M, K // 2)
    and encodes the 2-bit column positions into indices_packed (M, K // 4).

    Returns:
        (W_packed, indices_packed, W_masked)
    """
    if W.ndim != 2:
        raise ValueError("W must be a 2D matrix.")
    M, K = W.shape
    if K % 4 != 0:
        raise ValueError(f"Inner dimension K ({K}) must be a multiple of 4 for 2:4 structured sparsity.")

    num_blocks = K // 4
    W_packed = np.zeros((M, num_blocks * 2), dtype=np.float32)
    indices_packed = np.zeros((M, num_blocks), dtype=np.uint8)
    W_masked = np.zeros((M, K), dtype=np.float32)

    for m in range(M):
        for b in range(num_blocks):
            block = W[m, b * 4 : (b + 1) * 4]
            # Find the 2 elements with highest absolute magnitude
            sorted_idx = np.argsort(-np.abs(block))
            i0, i1 = int(sorted_idx[0]), int(sorted_idx[1])
            # Canonical ordering of indices
            if i0 > i1:
                i0, i1 = i1, i0

            val0 = float(block[i0])
            val1 = float(block[i1])

            W_packed[m, b * 2] = val0
            W_packed[m, b * 2 + 1] = val1
            indices_packed[m, b] = (i0 & 0x03) | ((i1 & 0x03) << 2)

            W_masked[m, b * 4 + i0] = val0
            W_masked[m, b * 4 + i1] = val1

    return W_packed, indices_packed, W_masked


@numba.njit(fastmath=True, parallel=True)
def _gemm_2_4_sparse_kernel(
    X: np.ndarray,
    W_packed: np.ndarray,
    indices_packed: np.ndarray,
    Y: np.ndarray,
) -> None:
    """
    Native AVX2 JIT-compiled GEMM for 2:4 structured sparse weights:
    Y = X @ W_masked^T
    Dimensions:
        X: (N, K)
        W_packed: (M, K // 2)
        indices_packed: (M, K // 4)
        Y: (N, M)
    """
    N, K = X.shape
    M, half_K = W_packed.shape
    num_blocks = indices_packed.shape[1]

    for n in numba.prange(N):
        for m in range(M):
            acc = 0.0
            for b in range(num_blocks):
                idx_byte = indices_packed[m, b]
                i0 = idx_byte & 0x03
                i1 = (idx_byte >> 2) & 0x03

                w0 = W_packed[m, b * 2]
                w1 = W_packed[m, b * 2 + 1]

                x0 = X[n, b * 4 + i0]
                x1 = X[n, b * 4 + i1]

                acc += w0 * x0 + w1 * x1

            Y[n, m] = acc


def gemm_2_4_sparse_avx2(
    X: np.ndarray,
    W_packed: np.ndarray,
    indices_packed: np.ndarray,
) -> np.ndarray:
    """
    Executes 2:4 structured sparse matrix multiplication using compiled AVX2 SIMD.
    Computes Y = X @ W^T with 50% fewer arithmetic operations.
    """
    X_f32 = np.ascontiguousarray(X, dtype=np.float32)
    N, K = X_f32.shape
    M = W_packed.shape[0]

    Y = np.zeros((N, M), dtype=np.float32)
    _gemm_2_4_sparse_kernel(X_f32, W_packed, indices_packed, Y)
    return Y


class StructuredSparse24Engine:
    """
    Full lifecycle engine for 2:4 structured sparsity with telemetry and validation.
    """

    def __init__(self, M: int = 256, K: int = 512):
        self.M = M
        self.K = K

    def benchmark_speedup(
        self,
        N: int = 128,
        warmup: int = 3,
        reps: int = 20,
    ) -> Dict[str, float]:
        """
        Benchmarks compiled 2:4 sparse GEMM against dense baseline.
        """
        np.random.seed(42)
        X = np.random.randn(N, self.K).astype(np.float32)
        W = np.random.randn(self.M, self.K).astype(np.float32)

        W_packed, indices_packed, W_masked = prune_and_pack_2_4(W)

        # Warmup JIT compilation
        for _ in range(warmup):
            _ = gemm_2_4_sparse_avx2(X, W_packed, indices_packed)
            _ = X @ W_masked.T

        # Time dense reference (masked dense matrix via BLAS)
        t0 = time.perf_counter()
        for _ in range(reps):
            ref_Y = X @ W_masked.T
        dense_ms = (time.perf_counter() - t0) * 1000.0 / reps

        # Time compiled 2:4 sparse kernel
        t0 = time.perf_counter()
        for _ in range(reps):
            sparse_Y = gemm_2_4_sparse_avx2(X, W_packed, indices_packed)
        sparse_ms = (time.perf_counter() - t0) * 1000.0 / reps

        # Verify numerical equivalence
        max_abs_err = float(np.max(np.abs(ref_Y - sparse_Y)))
        rel_err = max_abs_err / max(float(np.max(np.abs(ref_Y))), 1e-8)

        # Memory calculation
        dense_bytes = W.nbytes
        packed_bytes = W_packed.nbytes + indices_packed.nbytes
        compression_ratio = dense_bytes / packed_bytes

        return {
            "dense_ms": dense_ms,
            "sparse_2_4_ms": sparse_ms,
            "speedup": dense_ms / max(sparse_ms, 1e-6),
            "max_abs_err": max_abs_err,
            "rel_err": rel_err,
            "compression_ratio": compression_ratio,
            "verified": max_abs_err < 1e-4,
        }
