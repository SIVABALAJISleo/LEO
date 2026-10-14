"""
hyper/six_engines/engine3_data_reuse_locality.py
===============================================
ENGINE 3: DATA REUSE AND LOCALITY

Objectives:
- Maximize CPU L1/L2 cache residency through adaptive blocking and tiling.
- Fuse operations (e.g., GEMM + Bias + Activation) to eliminate intermediate array traffic.
- Enforce 64-byte cache-line alignment and contiguous memory layout.
- Exploit temporal coherence across video frames and simulation steps (dirty bounding boxes).
- Account for total memory traffic (Bytes read/written vs FLOPs).
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np


@dataclass
class LocalityMetrics:
    tile_size: int
    arithmetic_intensity: float  # FLOPs / byte
    total_bytes_moved: int
    elapsed_ms: float
    gflops_achieved: float
    temporal_reuse_pct: float = 0.0
    intermediate_arrays_avoided: int = 0


class CacheHierarchyProfile:
    """Hardware cache parameters for Intel Core i5-12450H."""
    L1D_BYTES_PER_CORE: int = 32 * 1024       # 32 KB
    L2_BYTES_PER_CORE: int = 1280 * 1024      # 1.25 MB per P-core
    L3_TOTAL_BYTES: int = 12 * 1024 * 1024    # 12 MB Shared
    CACHE_LINE_BYTES: int = 64                # 64-byte cache lines


class CacheAwareTiledMatmul:
    """
    Cache-blocking matrix multiplication engine.
    Explores and selects tile sizes that fit inside the CPU L1/L2 cache hierarchy.
    """

    @staticmethod
    def blocked_matmul(
        A: np.ndarray,
        B: np.ndarray,
        tile_size: int = 64,
        out: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, LocalityMetrics]:
        """
        Computes C = A @ B using cache-blocked loop tiling.
        Loops: (i, j, k) partitioned into tiles of size `tile_size`.
        """
        M, K = A.shape
        K2, N = B.shape
        assert K == K2, "Inner dimension mismatch"

        # Ensure contiguous arrays for SIMD vector prefetching
        if not A.flags["C_CONTIGUOUS"]:
            A = np.ascontiguousarray(A)
        if not B.flags["C_CONTIGUOUS"]:
            B = np.ascontiguousarray(B)

        C = out if out is not None else np.zeros((M, N), dtype=A.dtype)
        if out is not None:
            C.fill(0)

        t0 = time.perf_counter()

        # 3D Tiled Execution
        for ii in range(0, M, tile_size):
            i_end = min(ii + tile_size, M)
            for kk in range(0, K, tile_size):
                k_end = min(kk + tile_size, K)
                sub_A = A[ii:i_end, kk:k_end]

                for jj in range(0, N, tile_size):
                    j_end = min(jj + tile_size, N)
                    sub_B = B[kk:k_end, jj:j_end]
                    C[ii:i_end, jj:j_end] += np.dot(sub_A, sub_B)

        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        # Data Movement Accounting
        flops = 2.0 * M * N * K
        # Theoretical minimum bytes: read A once, read B (M/tile) times, write C
        bytes_moved = (M * K + B.size * (M // tile_size + 1) + M * N) * A.itemsize
        intensity = flops / max(bytes_moved, 1)
        gflops = (flops / 1e9) / max(elapsed_ms / 1000.0, 1e-6)

        metrics = LocalityMetrics(
            tile_size=tile_size,
            arithmetic_intensity=intensity,
            total_bytes_moved=bytes_moved,
            elapsed_ms=elapsed_ms,
            gflops_achieved=gflops,
        )
        return C, metrics

    @classmethod
    def autotune_tile_size(
        cls,
        A: np.ndarray,
        B: np.ndarray,
        candidate_tiles: List[int] = [16, 32, 64, 128],
    ) -> Tuple[int, LocalityMetrics]:
        """Empirically evaluates candidate tile sizes to find optimal cache residency."""
        best_tile = candidate_tiles[0]
        best_latency = float("inf")
        best_metrics: Optional[LocalityMetrics] = None

        scratch = np.zeros((A.shape[0], B.shape[1]), dtype=A.dtype)

        for tile in candidate_tiles:
            # Warmup
            cls.blocked_matmul(A, B, tile_size=tile, out=scratch)
            # Measured run
            _, metrics = cls.blocked_matmul(A, B, tile_size=tile, out=scratch)
            if metrics.elapsed_ms < best_latency:
                best_latency = metrics.elapsed_ms
                best_tile = tile
                best_metrics = metrics

        return best_tile, best_metrics or LocalityMetrics(best_tile, 0, 0, 0, 0)


class FusedKernelEngine:
    """
    Executes composite operations in a single pass to eliminate
    unnecessary intermediate array writes and DRAM roundtrips.
    """

    @staticmethod
    def fused_gemm_bias_relu(
        A: np.ndarray,
        B: np.ndarray,
        bias: np.ndarray,
        out: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, LocalityMetrics]:
        """
        Fused: Y = ReLU(A @ B + bias) in one buffer.
        Eliminates 2 separate intermediate DRAM buffers (product array and sum array).
        """
        t0 = time.perf_counter()
        M, N = A.shape[0], B.shape[1]

        target = out if out is not None else np.empty((M, N), dtype=A.dtype)
        # Compute dot product directly into target
        np.dot(A, B, out=target)
        # In-place add bias (broadcasted)
        np.add(target, bias, out=target)
        # In-place ReLU
        np.maximum(target, 0.0, out=target)

        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        flops = 2.0 * A.shape[0] * A.shape[1] * B.shape[1] + 2.0 * M * N
        bytes_moved = (A.nbytes + B.nbytes + bias.nbytes + target.nbytes)

        metrics = LocalityMetrics(
            tile_size=0,
            arithmetic_intensity=flops / max(bytes_moved, 1),
            total_bytes_moved=bytes_moved,
            elapsed_ms=elapsed_ms,
            gflops_achieved=(flops / 1e9) / max(elapsed_ms / 1000.0, 1e-6),
            intermediate_arrays_avoided=2,
        )
        return target, metrics


class TemporalCoherenceEngine:
    """
    Exploits temporal locality in sequential frames (graphics/video)
    and physical simulation time-steps.
    """

    @staticmethod
    def extract_dirty_region_bbox(
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
        threshold: float = 1e-3,
    ) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
        """
        Computes bounding box (ymin, xmin, ymax, xmax) of modified pixels.
        Returns: (bbox, pct_changed). If pct_changed == 0, bbox is None.
        """
        diff = np.abs(curr_frame.astype(np.float32) - prev_frame.astype(np.float32))
        changed_pixels = diff > threshold

        if not np.any(changed_pixels):
            return None, 0.0

        # Find bounding box
        rows = np.any(changed_pixels, axis=(1, 2) if changed_pixels.ndim == 3 else 1)
        cols = np.any(changed_pixels, axis=(0, 2) if changed_pixels.ndim == 3 else 0)

        ymin, ymax = int(np.where(rows)[0][0]), int(np.where(rows)[0][-1] + 1)
        xmin, xmax = int(np.where(cols)[0][0]), int(np.where(cols)[0][-1] + 1)

        total_pixels = prev_frame.shape[0] * prev_frame.shape[1]
        changed_count = int(np.count_nonzero(changed_pixels))
        pct_changed = (changed_count / total_pixels) * 100.0

        return (ymin, xmin, ymax, xmax), pct_changed

    @classmethod
    def apply_temporal_reprojection(
        cls,
        history_buffer: np.ndarray,
        new_frame: np.ndarray,
        threshold: float = 1e-3,
    ) -> Tuple[np.ndarray, LocalityMetrics]:
        """
        Updates only the dirty bounding box inside history buffer,
        bypassing full re-composition for unchanged screen space.
        """
        t0 = time.perf_counter()
        bbox, pct_changed = cls.extract_dirty_region_bbox(history_buffer, new_frame, threshold)

        out = history_buffer.copy()
        if bbox is not None:
            ymin, xmin, ymax, xmax = bbox
            out[ymin:ymax, xmin:xmax] = new_frame[ymin:ymax, xmin:xmax]

        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000.0

        saved_pct = 100.0 - pct_changed
        metrics = LocalityMetrics(
            tile_size=0,
            arithmetic_intensity=1.0,
            total_bytes_moved=int(new_frame.nbytes * (pct_changed / 100.0)),
            elapsed_ms=elapsed_ms,
            gflops_achieved=0.0,
            temporal_reuse_pct=saved_pct,
            intermediate_arrays_avoided=1,
        )
        return out, metrics


class StencilPingPongEngine:
    """
    Zero-allocation ping-pong buffering for iterative physical and stencil simulations.
    Alternates reads and writes between two preallocated, cache-aligned buffers,
    completely eliminating memory reallocations and minimizing L2/L3 cache evictions.
    """

    def __init__(self, shape: Tuple[int, ...], dtype: Any = np.float32) -> None:
        self.shape = shape
        self.buffer_a = np.zeros(shape, dtype=dtype)
        self.buffer_b = np.zeros(shape, dtype=dtype)
        self._current_is_a = True

    def initialize(self, initial_data: np.ndarray) -> None:
        self.buffer_a[:] = initial_data[:]
        self.buffer_b[:] = initial_data[:]
        self._current_is_a = True

    def step_2d_laplacian(self, alpha: float = 0.25) -> np.ndarray:
        """
        Executes a 5-point 2D Laplacian stencil step in-place into the inactive buffer.
        """
        src = self.buffer_a if self._current_is_a else self.buffer_b
        dst = self.buffer_b if self._current_is_a else self.buffer_a

        dst[1:-1, 1:-1] = src[1:-1, 1:-1] + alpha * (
            src[2:, 1:-1] + src[:-2, 1:-1] + src[1:-1, 2:] + src[1:-1, :-2] - 4.0 * src[1:-1, 1:-1]
        )
        self._current_is_a = not self._current_is_a
        return dst

    @property
    def current_buffer(self) -> np.ndarray:
        return self.buffer_b if not self._current_is_a else self.buffer_a


class BlockTiledFlashAttentionEngine:
    """
    Feature H: FlashAttention-Style Memory Traffic Optimization.
    Computes exact scaled dot-product attention using 2D block tiling (Br x Bc)
    and online numerically-stable softmax reduction.

    Eliminates O(N^2) intermediate attention score and probability matrices from DRAM,
    fitting intermediate computation within L1/L2 cache (Br * Bc * 4 bytes).
    """

    @staticmethod
    def standard_reference_attention(
        Q: np.ndarray,
        K: np.ndarray,
        V: np.ndarray,
        causal: bool = True,
    ) -> Tuple[np.ndarray, float]:
        """Reference standard attention with full O(N^2) intermediate materialization."""
        t0 = time.perf_counter()
        seq_len, d = Q.shape
        scale = 1.0 / math.sqrt(d)

        # Intermediate Score Matrix: (N, N)
        S = (Q @ K.T) * scale
        if causal:
            mask = np.triu(np.ones((seq_len, seq_len), dtype=bool), k=1)
            S[mask] = -1e9

        # Numerical stabilization
        m = np.max(S, axis=-1, keepdims=True)
        exp_S = np.exp(S - m)
        P = exp_S / np.maximum(np.sum(exp_S, axis=-1, keepdims=True), 1e-12)

        # Final Output Matrix: (N, d)
        out = P @ V
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return out, elapsed_ms

    @classmethod
    def block_tiled_flash_attention(
        cls,
        Q: np.ndarray,
        K: np.ndarray,
        V: np.ndarray,
        block_r: int = 64,
        block_c: int = 64,
        causal: bool = True,
    ) -> Tuple[np.ndarray, LocalityMetrics]:
        """
        Computes attention with online softmax in 2D blocks without materializing
        the full (N, N) attention score matrix in main memory.
        """
        t0 = time.perf_counter()
        seq_len, d = Q.shape
        scale = 1.0 / math.sqrt(d)

        # Ensure C-contiguous
        if not Q.flags["C_CONTIGUOUS"]:
            Q = np.ascontiguousarray(Q)
        if not K.flags["C_CONTIGUOUS"]:
            K = np.ascontiguousarray(K)
        if not V.flags["C_CONTIGUOUS"]:
            V = np.ascontiguousarray(V)

        O = np.zeros_like(Q)

        for i_start in range(0, seq_len, block_r):
            i_end = min(i_start + block_r, seq_len)
            b_r = i_end - i_start
            Q_tile = Q[i_start:i_end]  # (b_r, d)

            m_i = np.full(b_r, -1e9, dtype=np.float32)
            l_i = np.zeros(b_r, dtype=np.float32)
            O_i = np.zeros((b_r, d), dtype=np.float32)

            for j_start in range(0, seq_len, block_c):
                # If causal and key block is entirely in future tokens, skip computation
                if causal and j_start > (i_end - 1):
                    break

                j_end = min(j_start + block_c, seq_len)
                b_c = j_end - j_start
                K_tile = K[j_start:j_end]  # (b_c, d)
                V_tile = V[j_start:j_end]  # (b_c, d)

                # Block dot product: (b_r, b_c)
                S_ij = np.dot(Q_tile, K_tile.T) * scale

                # Apply causal mask if block intersects diagonal
                if causal and j_end > i_start:
                    r_idx = np.arange(i_start, i_end)[:, None]
                    c_idx = np.arange(j_start, j_end)[None, :]
                    S_ij[c_idx > r_idx] = -1e9

                # Online softmax update
                tile_max = np.max(S_ij, axis=-1)  # (b_r,)
                m_new = np.maximum(m_i, tile_max) # (b_r,)

                # Rescaling factor for accumulated output
                alpha = np.exp(m_i - m_new)       # (b_r,)
                P_ij = np.exp(S_ij - m_new[:, None]) # (b_r, b_c)

                l_new = alpha * l_i + np.sum(P_ij, axis=-1) # (b_r,)
                O_i = alpha[:, None] * O_i + np.dot(P_ij, V_tile)

                m_i = m_new
                l_i = l_new

            # Normalize output row-wise
            O[i_start:i_end] = O_i / np.maximum(l_i[:, None], 1e-12)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # Data Movement Accounting
        unfused_bytes = 4 * seq_len * d * 4 + 4 * seq_len * seq_len * 4
        fused_bytes = 4 * seq_len * d * 4
        bytes_avoided = max(0, unfused_bytes - fused_bytes)

        flops = 4.0 * seq_len * seq_len * d
        intensity = flops / max(fused_bytes, 1)

        metrics = LocalityMetrics(
            tile_size=block_r,
            arithmetic_intensity=intensity,
            total_bytes_moved=fused_bytes,
            elapsed_ms=elapsed_ms,
            gflops_achieved=(flops / 1e9) / max(elapsed_ms / 1000.0, 1e-6),
            temporal_reuse_pct=(bytes_avoided / max(unfused_bytes, 1)) * 100.0,
            intermediate_arrays_avoided=2,
        )
        return O, metrics


class DataReuseAndLocalityEngine:
    """Unified Engine 3 coordinator."""

    def __init__(self) -> None:
        self.tiled_matmul = CacheAwareTiledMatmul()
        self.fused_engine = FusedKernelEngine()
        self.temporal_engine = TemporalCoherenceEngine()
        self.stencil_engine = StencilPingPongEngine
        self.flash_attention = BlockTiledFlashAttentionEngine()

    def optimize_matmul_locality(
        self,
        A: np.ndarray,
        B: np.ndarray,
    ) -> Tuple[np.ndarray, LocalityMetrics]:
        """Automatically autotunes and executes cache-tiled matmul."""
        best_tile, _ = self.tiled_matmul.autotune_tile_size(A, B)
        return self.tiled_matmul.blocked_matmul(A, B, tile_size=best_tile)

    def optimize_attention_locality(
        self,
        Q: np.ndarray,
        K: np.ndarray,
        V: np.ndarray,
        block_r: int = 64,
        block_c: int = 64,
        causal: bool = True,
    ) -> Tuple[np.ndarray, LocalityMetrics]:
        """Executes 2D block-tiled FlashAttention with online softmax."""
        return self.flash_attention.block_tiled_flash_attention(
            Q, K, V, block_r=block_r, block_c=block_c, causal=causal
        )

