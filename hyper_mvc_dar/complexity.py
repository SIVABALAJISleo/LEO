"""
hyper_mvc_dar/complexity.py
Complexity Replacement Engine: Discovers lower-complexity algorithmic substitutions
(e.g., O(N^2) all-pairs to O(N) multipole; full transform to sparse sublinear transform).
"""

import math
from typing import Dict, Any, Tuple
from .contract import ExecutionContract


class ComplexityReplacementEngine:
    """Evaluates asymptotic scaling and break-even thresholds for algorithmic replacements."""

    @staticmethod
    def evaluate_n_body_replacement(n: int, contract: ExecutionContract) -> Dict[str, Any]:
        """Compares direct all-pairs O(N^2) against Fast Multipole Method O(N)."""
        direct_flops = 20 * n * n
        fmm_flops = int(120 * n * math.log2(max(2, n)))

        # Break-even point is typically N ~ 256 to 512
        should_replace = fmm_flops < direct_flops and not contract.is_exact()
        speedup = round(direct_flops / max(1, fmm_flops), 2)

        return {
            "n": n,
            "direct_flops": direct_flops,
            "fmm_flops": fmm_flops,
            "should_replace": should_replace,
            "asymptotic_speedup": speedup,
            "algorithm": "FastMultipoleMethod_Octree" if should_replace else "Direct_AllPairs"
        }

    @staticmethod
    def evaluate_fft_replacement(n: int, k_sparse: int, contract: ExecutionContract) -> Dict[str, Any]:
        """Compares dense FFT O(N log N) against MIT Sparse FFT O(k log(N/delta))."""
        dense_flops = int(5 * n * math.log2(n))
        sfft_flops = int(18 * k_sparse * math.log2(n))

        should_replace = sfft_flops < dense_flops and contract.allows_low_rank()
        return {
            "n": n,
            "k_sparse": k_sparse,
            "dense_flops": dense_flops,
            "sfft_flops": sfft_flops,
            "should_replace": should_replace,
            "speedup": round(dense_flops / max(1, sfft_flops), 2),
            "algorithm": "Sublinear_Sparse_FFT" if should_replace else "Dense_CooleyTukey"
        }
