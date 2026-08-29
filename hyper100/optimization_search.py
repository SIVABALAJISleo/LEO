"""
hyper100/optimization_search.py
===============================
HYPER Optimization Search Engine.
Explores the Pareto frontier of candidate execution strategies, solving:
  argmin_{s in S} (Estimated Execution Cost(s))
  subject to: Error(s) <= epsilon, Latency(s) <= max_latency, Memory(s) <= max_memory.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import numpy as np

from .contract_engine import ExecutionContract, ContractExactness
from .workload_analyzer import ComputationGraph, WorkloadProfile
from .redundancy_discovery import RedundancyReport


@dataclass
class OptimizationStrategy:
    """A concrete plan combining elimination, compression, precision, and hardware placement."""
    strategy_id: str
    use_cache: bool = True
    use_sparsity: bool = False
    sparsity_threshold: float = 1e-4
    use_low_rank: bool = False
    target_rank: Optional[int] = None
    precision: str = "FP32"             # 'FP32', 'FP16', 'INT8', 'TERNARY'
    use_prediction: bool = False
    device_target: str = "CPU_AVX2"     # 'CPU_AVX2', 'INTEL_UHD', 'HETEROGENEOUS_PIPELINED'
    estimated_speedup: float = 1.0
    estimated_memory_reduction: float = 1.0


class OptimizationSearchEngine:
    """Searches optimal optimization combinations and caches decisions per graph signature."""

    def __init__(self):
        self._strategy_cache: Dict[str, OptimizationStrategy] = {}

    def search_optimal_strategy(
        self,
        profile: WorkloadProfile,
        redundancy: RedundancyReport,
        contract: ExecutionContract
    ) -> OptimizationStrategy:
        """
        Solves constrained optimization problem for the workload.
        """
        sig_key = f"{profile.graph_signature}_{contract.exactness.value}_{contract.max_error}"
        if sig_key in self._strategy_cache:
            return self._strategy_cache[sig_key]

        # 1. Exact contract requirements
        if contract.is_exact_required():
            strategy = OptimizationStrategy(
                strategy_id="EXACT_SAFE_STRATEGY",
                use_cache=contract.allow_caching,
                use_sparsity=False,
                use_low_rank=False,
                precision="FP32",
                use_prediction=False,
                device_target=profile.recommended_primary_device,
                estimated_speedup=1.0,
                estimated_memory_reduction=1.0
            )
            self._strategy_cache[sig_key] = strategy
            return strategy

        # 2. Heuristic Pareto search
        use_sparse = (redundancy.sparsity_ratio >= 0.40 and contract.allow_approximation)
        use_lowrank = (redundancy.effective_compression_ratio >= 2.0 and redundancy.rank_estimate < 128 and contract.allow_approximation)
        use_pred = (redundancy.temporal_delta_ratio < 0.20 and contract.allow_prediction)

        # Precision selection
        prec = "FP32"
        if contract.max_error >= 0.05:
            prec = "INT8"
        elif contract.max_error >= 1e-3:
            prec = "FP16"

        device = profile.recommended_primary_device
        if use_sparse and device == "INTEL_UHD":
            device = "CPU_AVX2"  # Sparse indexing overhead on iGPU often slower than AVX2 vector SIMD

        speedup_est = 1.0
        if use_sparse:
            speedup_est *= 1.8
        if use_lowrank:
            speedup_est *= 2.2
        if prec == "INT8":
            speedup_est *= 2.5
        elif prec == "FP16":
            speedup_est *= 1.5
        if use_pred:
            speedup_est *= 3.0

        strategy = OptimizationStrategy(
            strategy_id=f"OPT_{prec}_{device}_{'SPARSE_' if use_sparse else ''}{'LOWRANK_' if use_lowrank else ''}",
            use_cache=contract.allow_caching,
            use_sparsity=use_sparse,
            sparsity_threshold=1e-4,
            use_low_rank=use_lowrank,
            target_rank=redundancy.rank_estimate,
            precision=prec,
            use_prediction=use_pred,
            device_target=device,
            estimated_speedup=speedup_est,
            estimated_memory_reduction=redundancy.effective_compression_ratio if use_lowrank else 1.0
        )
        self._strategy_cache[sig_key] = strategy
        return strategy
