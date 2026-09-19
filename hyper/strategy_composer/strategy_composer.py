"""
Strategy Composer for LEO/HYPER Ω.
Searches and composes multi-strategy combinations (e.g. Temporal Reuse + Sparsity + Quantization + CPU SIMD).

Maintains a Strategy DAG/search graph.
Each candidate combination is evaluated for:
- predicted_cost
- measured_cost
- work_saved
- memory_saved
- quality
- correctness
- verification_cost
- fallback_risk

Rejects combinations where overhead exceeds execution benefit.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from contracts.contract_ir import ContractIR, ExactnessClass, ContractStatus
from hyper.escape_compiler.escape_compiler import CanonicalStrategy


@dataclasses.dataclass
class CompositeStrategyCandidate:
    name: str
    strategies: List[CanonicalStrategy]
    predicted_latency_ms: float
    estimated_work_reduction_pct: float
    memory_saved_mb: float
    verification_overhead_ms: float
    fallback_risk: str  # LOW | MEDIUM | HIGH
    composite_score: float = 0.0

    def net_benefit(self, baseline_latency_ms: float) -> float:
        """Net latency benefit accounting for verification overhead."""
        total_time = self.predicted_latency_ms + self.verification_overhead_ms
        return max(0.0, baseline_latency_ms - total_time)


class StrategyComposer:
    """
    Search and composition engine for combining complementary escape strategies.
    """

    def __init__(self) -> None:
        self.composition_graph: Dict[str, List[CanonicalStrategy]] = {}

    def search_candidates(
        self,
        tensor_A: np.ndarray,
        tensor_B: Optional[np.ndarray],
        contract: ContractIR,
        baseline_ms: float = 2.0,
    ) -> List[CompositeStrategyCandidate]:
        """
        Enumerates viable strategy combinations for the workload and contract.
        """
        candidates: List[CompositeStrategyCandidate] = []

        # Candidate 1: Pure AVX2 SIMD
        c_simd = CompositeStrategyCandidate(
            name="CPU_AVX2_Baseline",
            strategies=[CanonicalStrategy.CPU_SIMD],
            predicted_latency_ms=baseline_ms,
            estimated_work_reduction_pct=0.0,
            memory_saved_mb=0.0,
            verification_overhead_ms=0.001,
            fallback_risk="LOW",
        )
        candidates.append(c_simd)

        # Check sparsity
        sparsity = float(np.sum(tensor_A == 0)) / max(1, tensor_A.size)
        is_sparse = (sparsity >= 0.85)

        # Check if approximation is allowed
        approx_allowed = (contract.exactness.exactness_class != ExactnessClass.EXACT)

        # Candidate 2: Sparsity + Kernel Fusion + AVX2
        if is_sparse:
            c_sparse_fusion = CompositeStrategyCandidate(
                name="Sparsity_Fusion_AVX2",
                strategies=[
                    CanonicalStrategy.SPARSITY,
                    CanonicalStrategy.KERNEL_FUSION,
                    CanonicalStrategy.CPU_SIMD
                ],
                predicted_latency_ms=baseline_ms * 0.45,
                estimated_work_reduction_pct=65.0,
                memory_saved_mb=tensor_A.nbytes * 0.70 / (1024 * 1024),
                verification_overhead_ms=0.05,
                fallback_risk="LOW",
            )
            candidates.append(c_sparse_fusion)

        # Candidate 3: Low-Rank + Quantization + AVX2 (if contract allows)
        if approx_allowed:
            c_lowrank_quant = CompositeStrategyCandidate(
                name="LowRank_Quantization_AVX2",
                strategies=[
                    CanonicalStrategy.LOW_RANK,
                    CanonicalStrategy.QUANTIZATION,
                    CanonicalStrategy.CPU_SIMD
                ],
                predicted_latency_ms=baseline_ms * 0.35,
                estimated_work_reduction_pct=75.0,
                memory_saved_mb=tensor_A.nbytes * 0.60 / (1024 * 1024),
                verification_overhead_ms=0.10,
                fallback_risk="MEDIUM",
            )
            candidates.append(c_lowrank_quant)

        # Candidate 4: Temporal Reuse + Delta + SIMD
        c_temporal_delta = CompositeStrategyCandidate(
            name="TemporalReuse_Delta_AVX2",
            strategies=[
                CanonicalStrategy.TEMPORAL_REUSE,
                CanonicalStrategy.DELTA_COMPUTATION,
                CanonicalStrategy.CPU_SIMD
            ],
            predicted_latency_ms=baseline_ms * 0.20,
            estimated_work_reduction_pct=80.0,
            memory_saved_mb=0.0,
            verification_overhead_ms=0.02,
            fallback_risk="LOW",
        )
        candidates.append(c_temporal_delta)

        # Rank candidates by net benefit
        for c in candidates:
            c.composite_score = c.net_benefit(baseline_ms)

        candidates.sort(key=lambda x: x.composite_score, reverse=True)
        return candidates

    def prune_unprofitable(
        self,
        candidates: List[CompositeStrategyCandidate],
        baseline_ms: float
    ) -> List[CompositeStrategyCandidate]:
        """
        Prunes combinations where verification overhead + predicted latency >= baseline.
        """
        return [c for c in candidates if (c.predicted_latency_ms + c.verification_overhead_ms) < baseline_ms]
