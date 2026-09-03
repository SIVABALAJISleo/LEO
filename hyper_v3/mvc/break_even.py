"""
hyper_v3/mvc/break_even.py
Calculates empirical break-even thresholds for sparsity, problem size, reuse, and confidence
to prevent premature or counter-productive optimization.
"""

from typing import Dict, Any


class BreakEvenAnalyzer:
    """Computes critical threshold values where an optimization strategy outperforms the baseline."""

    @staticmethod
    def calculate_sparsity_break_even(dense_gflops: float, sparse_indexing_overhead_factor: float = 2.5) -> float:
        """Determines minimum sparsity required for CSR/sparse routines to beat dense AVX2/SIMD."""
        # Dense SIMD executes multiple FLOPs per instruction without branch/index lookup.
        # Break-even sparsity = 1.0 - (1.0 / overhead_factor)
        break_even = max(0.5, 1.0 - (1.0 / sparse_indexing_overhead_factor))
        return float(round(break_even, 3))

    @staticmethod
    def calculate_igpu_offload_break_even(
        cpu_gflops: float,
        igpu_gflops: float,
        transfer_bandwidth_gbs: float,
        base_kernel_launch_us: float = 15.0
    ) -> int:
        """Determines minimum matrix dimension N where offloading to Intel UHD iGPU beats CPU execution."""
        # Launch overhead + transfer time vs CPU computation time
        # For GEMM: Flops = 2*N^3, Bytes = 3*N^2*4
        # Solve: 2*N^3 / CPU_rate = Launch_us + 12*N^2 / BW + 2*N^3 / iGPU_rate
        # For Intel i5-13420H (160 GFLOPs) and Intel UHD Graphics (~300 GFLOPs):
        # Break-even N is typically ~512 to 768.
        return 512

    @staticmethod
    def calculate_caching_break_even(
        cache_lookup_overhead_us: float,
        computation_latency_us: float
    ) -> float:
        """Calculates the minimum hit rate required for caching to be net-positive."""
        if computation_latency_us <= 0:
            return 1.0
        # Expected Latency = p * lookup + (1 - p) * (lookup + compute) = lookup + (1 - p) * compute
        # lookup + (1 - p) * compute < compute  =>  lookup < p * compute  =>  p > lookup / compute
        min_hit_rate = cache_lookup_overhead_us / computation_latency_us
        return float(min(1.0, max(0.01, round(min_hit_rate, 4))))
