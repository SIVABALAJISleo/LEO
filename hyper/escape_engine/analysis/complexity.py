"""
hyper/escape_engine/analysis/complexity.py
==========================================
VAEE Asymptotic Complexity & Scaling Analysis.
"""

from __future__ import annotations

import math
from typing import Dict, Tuple


class ComplexityAnalyzer:
    """Estimates and evaluates asymptotic complexity of candidate pathways."""

    @staticmethod
    def estimate_matrix_mult_complexity(M: int, K: int, N: int, algorithm: str = "CANONICAL") -> Tuple[str, int]:
        """Returns (asymptotic notation, approximate operation count)."""
        if algorithm == "STRASSEN" and M == N and M == K and (M & (M - 1) == 0):
            # 7^(log2(N)) ~ N^2.807
            ops = int(M ** (math.log(7, 2)))
            return "O(N^2.807)", ops
        elif algorithm == "SPARSE":
            # Assuming ~20% nonzeros
            nnz = int(0.2 * M * K)
            ops = 2 * nnz * N
            return "O(NNZ * N)", ops
        elif algorithm == "LOW_RANK":
            r = 16
            ops = 2 * M * r * K + 2 * r * K * N
            return "O((M + N) * r * K)", ops
        else:
            # Canonical standard GEMM
            ops = 2 * M * K * N
            return "O(M * K * N)", ops

    @staticmethod
    def estimate_sorting_complexity(N: int, algorithm: str = "COMPARATIVE") -> Tuple[str, int]:
        if algorithm == "LINEAR_RADIX":
            # O(N + K)
            return "O(N + K)", int(N + 256)
        return "O(N log N)", int(N * math.log2(max(2, N)))
