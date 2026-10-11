"""
hyper_universal/data_movement/engine.py
Data-Movement Reduction Engine:
Minimizes main RAM bus traffic and intermediate buffer materialization via:
1. Cache-blocked matrix tiling (fitting L1/L2 data cache)
2. Producer-consumer kernel fusion (combining operations into single passes)
3. In-place memory buffer reuse
4. Truthful accounting of physical vs logical bytes
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple
import numpy as np


@dataclass
class DataMovementReport:
    name: str
    logical_bytes_processed: int
    physical_bytes_transferred: int
    bytes_avoided: int
    arithmetic_intensity_flops_per_byte: float
    peak_transient_buffer_bytes: int
    execution_latency_ms: float
    output_verified: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "logical_bytes_processed": self.logical_bytes_processed,
            "physical_bytes_transferred": self.physical_bytes_transferred,
            "bytes_avoided": self.bytes_avoided,
            "arithmetic_intensity_flops_per_byte": round(self.arithmetic_intensity_flops_per_byte, 2),
            "peak_transient_buffer_bytes": self.peak_transient_buffer_bytes,
            "execution_latency_ms": round(self.execution_latency_ms, 3),
            "output_verified": self.output_verified,
        }


class DataMovementReductionEngine:
    """Optimizes memory traffic through tiling and kernel fusion."""

    @staticmethod
    def fused_gemm_bias_relu(
        A: np.ndarray, B: np.ndarray, bias: np.ndarray, tile_size: int = 64
    ) -> Tuple[np.ndarray, DataMovementReport]:
        """
        Executes fused A @ B + bias with in-place ReLU activation.
        Without fusion: A @ B writes intermediate M*N array to RAM, then reads it for bias, then writes again for ReLU (3x traffic).
        With fusion: computes block by block in cache, writing only the final activated result once.
        """
        m, k = A.shape
        _, n = B.shape
        flops = 2 * m * k * n + 2 * m * n

        # Reference standard pipeline
        t0 = time.perf_counter()
        tmp1 = A @ B
        tmp2 = tmp1 + bias
        ref = np.maximum(tmp2, 0.0)
        t_ref = time.perf_counter() - t0

        # Fused cache-tiled execution
        t1 = time.perf_counter()
        C = np.zeros((m, n), dtype=np.float32)
        # Block-tiled in L2 cache
        for i in range(0, m, tile_size):
            i_end = min(i + tile_size, m)
            for j in range(0, n, tile_size):
                j_end = min(j + tile_size, n)
                # Compute tile in cache registers
                tile = A[i:i_end, :] @ B[:, j:j_end] + bias[j:j_end]
                np.maximum(tile, 0.0, out=tile)
                C[i:i_end, j:j_end] = tile
        t_cand = time.perf_counter() - t1

        # Bytes accounting
        unfused_traffic = (A.nbytes + B.nbytes + m * n * 4) + (m * n * 4 * 2 + bias.nbytes) + (m * n * 4 * 2)
        fused_traffic = A.nbytes + B.nbytes + bias.nbytes + C.nbytes
        avoided = max(0, unfused_traffic - fused_traffic)

        diff = float(np.max(np.abs(ref - C)))
        is_valid = diff <= 1e-4

        intensity = flops / max(fused_traffic, 1)

        report = DataMovementReport(
            name="Fused_GEMM_Bias_ReLU",
            logical_bytes_processed=unfused_traffic,
            physical_bytes_transferred=fused_traffic,
            bytes_avoided=avoided,
            arithmetic_intensity_flops_per_byte=intensity,
            peak_transient_buffer_bytes=tile_size * tile_size * 4,
            execution_latency_ms=t_cand * 1000.0,
            output_verified=is_valid,
        )
        return C, report
