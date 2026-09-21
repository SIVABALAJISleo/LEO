"""
hyper/escape_engine/workloads/dynamic_programming.py
====================================================
VAEE Initial Research Workload: Dynamic Programming (0/1 Knapsack & Edit Distance).

Compares:
- Full 2D matrix allocation: O(N * W) space
- Space-optimized 1D rolling array: O(W) space
- Verifies exact solution equivalence
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, List, Tuple

from ..contracts.schema import ComputationalContract
from ..verification.verifier import MasterVerifier
from ..analysis.cost_model import CostAnalyzer


class DynamicProgrammingResearchWorkload:
    """Workload evaluating memory representation reduction in Dynamic Programming."""

    def __init__(self, N: int = 200, W: int = 2000, seed: int = 42) -> None:
        self.N, self.W = N, W
        rng = np.random.default_rng(seed)
        self.weights = rng.integers(1, 50, size=N, dtype=np.int32)
        self.values = rng.integers(10, 200, size=N, dtype=np.int32)

        # Ground truth using 2D table
        self.ref_val = self.full_table_knapsack()

        self.contract = ComputationalContract(
            contract_id=f"knapsack_n{N}_w{W}",
            input_type="sequence",
            output_type="scalar",
            input_shape=(N,),
            output_shape=(1,),
            dtype="int32",
            correctness="EXACT",
            numeric_tolerance=0.0,
            verification_method="EXACT",
        )

    def full_table_knapsack(self) -> int:
        """Full 2D DP matrix O(N * W) space."""
        dp = np.zeros((self.N + 1, self.W + 1), dtype=np.int32)
        for i in range(1, self.N + 1):
            wt = self.weights[i - 1]
            val = self.values[i - 1]
            dp[i, :] = dp[i - 1, :]
            if wt <= self.W:
                dp[i, wt:] = np.maximum(dp[i, wt:], dp[i - 1, :-wt] + val)
        return int(dp[self.N, self.W])

    def space_optimized_knapsack(self) -> int:
        """1D rolling array O(W) space."""
        dp = np.zeros(self.W + 1, dtype=np.int32)
        for i in range(self.N):
            wt = self.weights[i]
            val = self.values[i]
            if wt <= self.W:
                dp[wt:] = np.maximum(dp[wt:], dp[:-wt] + val)
        return int(dp[self.W])

    def run_benchmark(self) -> Dict[str, Any]:
        _, cost_2d = CostAnalyzer.measure_execution(self.full_table_knapsack, trials=5)
        _, cost_1d = CostAnalyzer.measure_execution(self.space_optimized_knapsack, trials=5)

        val_1d = self.space_optimized_knapsack()
        verifier = MasterVerifier()
        v_res = verifier.verify_candidate(val_1d, self.ref_val, self.contract)

        speedup = cost_2d.wall_clock_ms / max(1e-6, cost_1d.wall_clock_ms)
        mem_reduction = 1.0 - (cost_1d.peak_memory_mb / max(1e-6, cost_2d.peak_memory_mb))

        return {
            "workload": f"Knapsack_N_{self.N}_Capacity_{self.W}",
            "contract": self.contract.to_dict(),
            "2d_table_ms": cost_2d.wall_clock_ms,
            "1d_rolling_ms": cost_1d.wall_clock_ms,
            "verified_speedup": round(speedup, 2),
            "is_exact": v_res.is_valid,
            "verification_status": v_res.trust_level,
        }
