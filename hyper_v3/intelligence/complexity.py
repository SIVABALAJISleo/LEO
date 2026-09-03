"""
hyper_v3/intelligence/complexity.py
Estimates theoretical algorithmic complexity and scaling bounds.
"""

from typing import Dict, Any
import math


class ComplexityAnalyzer:
    """Calculates asymptotic complexity and FLOP scaling for operations."""

    @staticmethod
    def estimate_gemm_complexity(m: int, n: int, k: int, algorithm: str = "standard") -> Dict[str, Any]:
        if algorithm == "strassen":
            # O(N^2.807)
            flops = int(7 * (max(m, n, k)**2.807))
            complexity_class = "O(N^2.807)"
        elif algorithm == "low_rank_r":
            # O(r*(m+n)*k)
            r = min(m, n, k) // 4
            flops = int(r * (m * k + k * n))
            complexity_class = "O(r*N^2)"
        else:
            flops = 2 * m * n * k
            complexity_class = "O(N^3)"

        return {
            "algorithm": algorithm,
            "complexity_class": complexity_class,
            "estimated_flops": flops,
            "memory_footprint_bytes": (m * k + k * n + m * n) * 4
        }

    @staticmethod
    def estimate_nbody_complexity(n: int, algorithm: str = "direct") -> Dict[str, Any]:
        if algorithm == "barnes_hut":
            flops = int(n * math.log2(max(n, 2)) * 20)
            complexity_class = "O(N log N)"
        else:
            flops = int(n * n * 20)
            complexity_class = "O(N^2)"

        return {
            "n": n,
            "algorithm": algorithm,
            "complexity_class": complexity_class,
            "estimated_flops": flops
        }
