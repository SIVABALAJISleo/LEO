"""
hyper/escape_engine/workloads/sorting.py
=======================================
VAEE Initial Research Workload: Bounded Key Integer Sorting.

Compares:
- Comparison-based QuickSort / Timsort (O(N log N) comparison bound)
- Linear non-comparative Counting / Radix Sort (O(N + K) linear pathway)
- Verifies exact permutation and monotonicity invariant
"""

from __future__ import annotations

import numpy as np
from typing import Any, Dict, List

from ..contracts.schema import ComputationalContract
from ..verification.verifier import MasterVerifier
from ..analysis.cost_model import CostAnalyzer


try:
    import numba

    @numba.njit(fastmath=True)
    def _fast_counting_sort(arr: np.ndarray, key_max: int) -> np.ndarray:
        counts = np.zeros(key_max, dtype=np.int32)
        n = len(arr)
        for i in range(n):
            counts[arr[i]] += 1
        out = np.empty(n, dtype=np.int32)
        idx = 0
        for k in range(key_max):
            c = counts[k]
            for _ in range(c):
                out[idx] = k
                idx += 1
        return out

    _HAS_NUMBA = True
except Exception:
    _HAS_NUMBA = False
    _fast_counting_sort = None


class SortingResearchWorkload:
    """Workload evaluating non-comparative sorting for bounded integer keys."""

    def __init__(self, N: int = 50000, key_max: int = 1000, seed: int = 42) -> None:
        self.N = N
        self.key_max = key_max
        self.rng = np.random.default_rng(seed)
        self.data = self.rng.integers(0, key_max, size=N, dtype=np.int32)
        self.ref_sorted = np.sort(self.data)

        # Warm up JIT if available
        if _HAS_NUMBA and _fast_counting_sort is not None:
            _ = _fast_counting_sort(self.data[:10], key_max)

        self.contract = ComputationalContract(
            contract_id=f"sort_bounded_{N}",
            input_type="sequence",
            output_type="sequence",
            input_shape=(N,),
            output_shape=(N,),
            dtype="int32",
            correctness="EXACT",
            numeric_tolerance=0.0,
            verification_method="INVARIANT_SORTED",
        )

    def comparison_sort(self) -> np.ndarray:
        return np.sort(self.data.copy(), kind="quicksort")

    def counting_sort(self) -> np.ndarray:
        """Linear time counting sort for bounded keys."""
        if _HAS_NUMBA and _fast_counting_sort is not None:
            return _fast_counting_sort(self.data, self.key_max)
        counts = np.bincount(self.data, minlength=self.key_max)
        return np.repeat(np.arange(len(counts), dtype=np.int32), counts)

    def run_benchmark(self) -> Dict[str, Any]:
        _, comp_cost = CostAnalyzer.measure_execution(self.comparison_sort, trials=5)
        _, count_cost = CostAnalyzer.measure_execution(self.counting_sort, trials=5)

        res = self.counting_sort()
        verifier = MasterVerifier()
        # Verify both invariant (sorted order) and exact match with reference
        v_inv = verifier.verify_candidate(res, self.ref_sorted, self.contract)
        is_exact = np.array_equal(res, self.ref_sorted)

        speedup = comp_cost.wall_clock_ms / max(1e-6, count_cost.wall_clock_ms)

        return {
            "workload": f"Sorting_N_{self.N}_K_{self.key_max}",
            "contract": self.contract.to_dict(),
            "comparison_sort_ms": comp_cost.wall_clock_ms,
            "counting_sort_ms": count_cost.wall_clock_ms,
            "verified_speedup": round(speedup, 2),
            "invariant_passed": bool(v_inv.is_valid),
            "exact_match": bool(is_exact),
            "classification": "SUCCESS" if (v_inv.is_valid and is_exact) else "FAILURE",
        }
