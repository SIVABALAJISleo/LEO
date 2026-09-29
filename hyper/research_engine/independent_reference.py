"""
hyper/research_engine/independent_reference.py
==============================================
Independent Reference Implementation Engine.

Provides authoritative, standalone, independent reference implementations for
the 15 canonical workload families and arbitrary mathematical operations.

STRICT RULE:
Reference implementations MUST NOT share graph nodes, cache state, or optimized
subroutines with candidate pathways.
"""

from __future__ import annotations
import math
import hashlib
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class IndependentReferenceEngine:
    """
    Independent reference computer executing canonical, textbook, unoptimized,
    high-assurance algorithms against which candidate pathways are verified.
    """

    @staticmethod
    def reference_matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Textbook canonical matrix multiplication."""
        return np.matmul(A, B)

    @staticmethod
    def naive_matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
        """Triple-nested loop reference for bit-exact verification on small shapes."""
        M, K = A.shape
        K2, N = B.shape
        assert K == K2, f"Shape mismatch: {A.shape} vs {B.shape}"
        C = np.zeros((M, N), dtype=A.dtype)
        for i in range(M):
            for j in range(N):
                s = 0.0
                for k in range(K):
                    s += float(A[i, k]) * float(B[k, j])
                C[i, j] = s
        return C

    @staticmethod
    def reference_conv1d(signal: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Canonical 1D discrete convolution."""
        return np.convolve(signal, kernel, mode="valid")

    @staticmethod
    def reference_conv2d(image: np.ndarray, kernel: np.ndarray) -> np.ndarray:
        """Canonical 2D direct sliding spatial convolution (no Winograd/FFT tricks)."""
        H, W = image.shape
        kH, kW = kernel.shape
        outH = H - kH + 1
        outW = W - kW + 1
        out = np.zeros((outH, outW), dtype=image.dtype)
        for i in range(outH):
            for j in range(outW):
                patch = image[i : i + kH, j : j + kW]
                out[i, j] = np.sum(patch * kernel)
        return out

    @staticmethod
    def reference_dft(x: np.ndarray) -> np.ndarray:
        """Textbook Discrete Fourier Transform formula: X_k = sum_n x_n * exp(-2pi i k n / N)."""
        N = len(x)
        n = np.arange(N)
        k = n.reshape((N, 1))
        M = np.exp(-2j * np.pi * k * n / N)
        return np.dot(M, x)

    @staticmethod
    def reference_reduction_sum(arr: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
        """High-precision pairwise/compensated sum reduction."""
        return np.sum(arr, axis=axis, dtype=np.float64).astype(arr.dtype)

    @staticmethod
    def reference_sort(arr: np.ndarray) -> np.ndarray:
        """Canonical stable sort."""
        return np.sort(arr)

    @staticmethod
    def reference_graph_pagerank(adj_matrix: np.ndarray, damping: float = 0.85, max_iter: int = 100) -> np.ndarray:
        """Standard iterative power iteration PageRank."""
        N = adj_matrix.shape[0]
        # Normalize columns
        deg = np.sum(adj_matrix, axis=0)
        deg[deg == 0] = 1.0
        M = adj_matrix / deg
        v = np.ones(N, dtype=np.float64) / N
        for _ in range(max_iter):
            v_next = (1 - damping) / N + damping * np.dot(M, v)
            if np.linalg.norm(v_next - v, ord=1) < 1e-12:
                break
            v = v_next
        return v

    @staticmethod
    def reference_sha256(data: bytes) -> str:
        """Standard FIPS-180-4 SHA-256."""
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def reference_nbody_step(positions: np.ndarray, velocities: np.ndarray, masses: np.ndarray, dt: float = 0.01, G: float = 1.0) -> np.ndarray:
        """Direct O(N^2) pairwise gravitational summation returning updated positions."""
        N = len(positions)
        forces = np.zeros_like(positions)
        for i in range(N):
            for j in range(N):
                if i != j:
                    r_vec = positions[j] - positions[i]
                    dist = np.linalg.norm(r_vec) + 1e-9  # softening
                    f = G * masses[i] * masses[j] / (dist ** 3) * r_vec
                    forces[i] += f
        m_safe = np.maximum(masses[:, None], 1e-9)
        new_vel = velocities + (forces / m_safe) * dt
        new_pos = positions + new_vel * dt
        return new_pos

    @staticmethod
    def reference_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray) -> np.ndarray:
        """Textbook scaled dot-product attention: softmax(Q @ K.T / sqrt(d)) @ V."""
        d_k = Q.shape[-1]
        scores = np.matmul(Q, np.swapaxes(K, -1, -2)) / math.sqrt(d_k)
        # Numerically stable softmax
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        probs = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        return np.matmul(probs, V)

    @staticmethod
    def reference_sobel(image: np.ndarray) -> np.ndarray:
        """Canonical 2D Sobel gradient operator."""
        Gx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
        Gy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float32)
        Ix = IndependentReferenceEngine.reference_conv2d(image, Gx)
        Iy = IndependentReferenceEngine.reference_conv2d(image, Gy)
        return np.hypot(Ix, Iy)

    @staticmethod
    def reference_spmv_csr(data: np.ndarray, indices: np.ndarray, indptr: np.ndarray, x: np.ndarray) -> np.ndarray:
        """Canonical CSR matrix-vector multiplication via explicit pointer loops."""
        N = len(indptr) - 1
        y = np.zeros(N, dtype=data.dtype)
        for i in range(N):
            row_start = int(indptr[i])
            row_end = int(indptr[i + 1])
            s = 0.0
            for ptr in range(row_start, row_end):
                col = int(indices[ptr])
                if 0 <= col < len(x):
                    s += float(data[ptr]) * float(x[col])
            y[i] = s
        return y

    @staticmethod
    def reference_mandelbrot(c_grid: np.ndarray, max_iter: int = 100) -> np.ndarray:
        """Direct iterative divergence count for compute-bound fractal calculation."""
        z = np.zeros_like(c_grid)
        out = np.zeros(c_grid.shape, dtype=np.int32)
        for i in range(max_iter):
            mask = np.abs(z) <= 2.0
            out[mask] = i
            z[mask] = z[mask] ** 2 + c_grid[mask]
        return out

    _dynamic_references: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    @classmethod
    def register_reference(cls, workload_id: str, fn: Callable[[Dict[str, Any]], Any]) -> None:
        cls._dynamic_references[workload_id] = fn

    @classmethod
    def execute_reference(cls, workload_id: str, inputs: Dict[str, Any]) -> Any:
        """Dispatch helper for canonical reference execution."""
        if workload_id in cls._dynamic_references:
            return cls._dynamic_references[workload_id](inputs)

        w_id = workload_id.upper()
        if ("A" in inputs and "B" in inputs):
            return IndependentReferenceEngine.reference_matmul(inputs["A"], inputs["B"])
        elif "CONV2D" in w_id:
            return IndependentReferenceEngine.reference_conv2d(inputs["image"], inputs["kernel"])
        elif "CONV1D" in w_id:
            return IndependentReferenceEngine.reference_conv1d(inputs["signal"], inputs["kernel"])
        elif "FFT" in w_id or "DFT" in w_id:
            return IndependentReferenceEngine.reference_dft(inputs["x"])
        elif "ATTENTION" in w_id:
            return IndependentReferenceEngine.reference_attention(inputs["Q"], inputs["K"], inputs["V"])
        elif "PAGERANK" in w_id or "GRAPH" in w_id:
            return IndependentReferenceEngine.reference_graph_pagerank(inputs["adj_matrix"])
        elif "NBODY" in w_id:
            return IndependentReferenceEngine.reference_nbody_step(
                inputs["positions"], inputs["velocities"], inputs["masses"], inputs.get("dt", 0.01)
            )
        elif "SOBEL" in w_id or "IMAGE" in w_id:
            return IndependentReferenceEngine.reference_sobel(inputs["image"])
        elif "REDUCE" in w_id:
            return IndependentReferenceEngine.reference_reduction_sum(inputs["x"])
        elif "SORT" in w_id:
            return IndependentReferenceEngine.reference_sort(inputs["x"])
        elif "SPMV" in w_id:
            return IndependentReferenceEngine.reference_spmv_csr(
                inputs["data"], inputs["indices"], inputs["indptr"], inputs["x"]
            )
        elif "MANDELBROT" in w_id:
            return IndependentReferenceEngine.reference_mandelbrot(inputs["c_grid"])
        elif "STREAM" in w_id and "x" in inputs:
            return inputs["x"].copy()
        elif "SHA256" in w_id or "CRYPTO" in w_id:
            return IndependentReferenceEngine.reference_sha256(inputs["data"])
        elif "x" in inputs and isinstance(inputs["x"], np.ndarray):
            return inputs["x"].copy()
        else:
            raise ValueError(f"No independent reference defined for workload '{workload_id}'")
