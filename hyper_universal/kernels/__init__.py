"""
hyper_universal/kernels
=======================
High-performance compiled AVX2 SIMD kernels for:
1. 2:4 Structured Sparsity GEMM (50% memory traffic reduction, 2x compute density).
2. BitNet 1.58b Ternary GEMM (pure additions/subtractions, 16x memory compression).
"""

from .sparse_2_4_avx2 import (
    prune_and_pack_2_4,
    gemm_2_4_sparse_avx2,
    StructuredSparse24Engine,
)
from .bitnet_ternary_avx2 import (
    quantize_to_bitnet_ternary,
    bitnet_ternary_gemm_avx2,
    BitNetTernaryEngine,
)

__all__ = [
    "prune_and_pack_2_4",
    "gemm_2_4_sparse_avx2",
    "StructuredSparse24Engine",
    "quantize_to_bitnet_ternary",
    "bitnet_ternary_gemm_avx2",
    "BitNetTernaryEngine",
]
