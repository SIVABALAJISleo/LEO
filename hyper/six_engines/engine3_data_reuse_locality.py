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


class DataReuseAndLocalityEngine:
    """Unified Engine 3 coordinator."""

    def __init__(self) -> None:
        self.tiled_matmul = CacheAwareTiledMatmul()
        self.fused_engine = FusedKernelEngine()
        self.temporal_engine = TemporalCoherenceEngine()

    def optimize_matmul_locality(
        self,
        A: np.ndarray,
        B: np.ndarray,
    ) -> Tuple[np.ndarray, LocalityMetrics]:
        """Automatically autotunes and executes cache-tiled matmul."""
        best_tile, _ = self.tiled_matmul.autotune_tile_size(A, B)
        return self.tiled_matmul.blocked_matmul(A, B, tile_size=best_tile)
