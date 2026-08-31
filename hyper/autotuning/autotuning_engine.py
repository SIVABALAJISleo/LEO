"""
hyper/autotuning/autotuning_engine.py
=====================================
Autotuning Engine (Section 36):
Automatically tunes tile size, thread count, vector width, precision,
and prediction thresholds via micro-benchmarks.
"""

import time
from typing import Dict, Any, List, Callable, Tuple
import numpy as np


class AutotuningEngine:
    """
    Finds optimal kernel configurations through benchmark sweeps.
    """
    def __init__(self):
        self._cache: Dict[str, Any] = {}

    def autotune_tile_size(
        self, workload_name: str, candidate_tiles: List[int], benchmark_fn: Callable[[int], float]
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Sweeps over candidate tile sizes and selects minimum-latency tile.
        """
        if workload_name in self._cache:
            return self._cache[workload_name], {"from_cache": True}

        best_tile = candidate_tiles[0]
        min_time = float("inf")
        trials = {}

        for tile in candidate_tiles:
            try:
                t = benchmark_fn(tile)
                trials[tile] = round(t, 3)
                if t < min_time:
                    min_time = t
                    best_tile = tile
            except Exception:
                continue

        self._cache[workload_name] = best_tile
        return best_tile, {
            "best_tile_size": best_tile,
            "min_time_ms": round(min_time, 3),
            "trials": trials
        }
