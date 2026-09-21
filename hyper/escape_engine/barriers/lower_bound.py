"""
hyper/escape_engine/barriers/lower_bound.py
==========================================
VAEE Section 18: Formal Mathematical & Information-Theoretic Lower Bounds.

Establishes mathematically proven barriers (e.g., Omega(N^2) for reading inputs,
Omega(N log N) for comparison-based sorting).
"""

from __future__ import annotations

import math
from typing import Optional, Tuple


class LowerBoundAnalyzer:
    """Computes established theoretical lower bounds."""

    @staticmethod
    def get_sorting_comparison_lower_bound(n: int) -> Tuple[int, str]:
        """Comparison sorting lower bound is ceil(log2(N!)) >= N log2(N) - 1.44 N."""
        if n <= 1:
            return 0, "Omega(1)"
        bound = int(math.ceil(math.lgamma(n + 1) / math.log(2)))
        return bound, "Omega(N log N) comparison bound"

    @staticmethod
    def get_matrix_mult_io_lower_bound(m: int, k: int, n: int) -> Tuple[int, str]:
        """Matrix multiplication trivial I/O lower bound is Omega(M*K + K*N + M*N)."""
        io_bound = m * k + k * n + m * n
        return io_bound, "Omega(Input + Output Size) I/O bound"
