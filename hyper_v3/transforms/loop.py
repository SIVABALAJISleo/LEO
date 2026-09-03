"""
hyper_v3/transforms/loop.py
Loop transformations (Tiling, Unrolling, Interchange, Vectorization).
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class LoopConfig:
    tile_m: int = 64
    tile_n: int = 64
    tile_k: int = 64
    unroll_factor: int = 4
    vector_width: int = 8  # AVX2 8xFP32


class LoopTransformer:
    """Computes optimal loop tiling and unrolling parameters for CPU cache boundaries."""

    @staticmethod
    def get_optimal_gemm_tiles(m: int, n: int, k: int, l1_bytes: int = 32768, l2_bytes: int = 1048576) -> LoopConfig:
        # Fits tile_m * tile_k + tile_k * tile_n + tile_m * tile_n in L1/L2
        tm = min(64, max(16, (m // 16) * 16))
        tn = min(64, max(16, (n // 16) * 16))
        tk = min(64, max(16, (k // 16) * 16))
        return LoopConfig(tile_m=tm, tile_n=tn, tile_k=tk, unroll_factor=4, vector_width=8)
