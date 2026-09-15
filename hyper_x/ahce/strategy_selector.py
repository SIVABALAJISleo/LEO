"""
hyper_x/ahce/strategy_selector.py
=================================
Strategy ranking and candidate selection for AHCE (Section 10).
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
from .contract import AHCEContract, CorrectnessClass
from .workload_signature import WorkloadSignature
from .candidate import AHCECandidate
from .strategy_registry import AHCEStrategyRegistry, AHCEStrategy


class AHCEStrategySelector:
    """Ranks applicable strategies based on cost estimation and contract alignment."""

    def __init__(self, registry: AHCEStrategyRegistry):
        self.registry = registry

    def rank_candidates(
        self,
        signature: WorkloadSignature,
        contract: AHCEContract,
        hardware: Dict[str, Any]
    ) -> List[AHCECandidate]:
        applicable = self.registry.get_applicable(signature, contract)
        candidates: List[AHCECandidate] = []

        dims = signature.features.dimensions
        M = dims[0] if len(dims) > 0 else 1
        K = dims[1] if len(dims) > 1 else 1
        baseline_work = float(2 * M * K * K)

        for strat in applicable:
            est = strat.estimate(signature, hardware)
            pred_work = est.get("predicted_work_units", baseline_work)
            pred_lat = est.get("predicted_latency_ms", 1.0)
            trans_cost = est.get("transformation_cost_ms", 0.0)

            # Calculate work reduction
            work_red = max(0.0, 1.0 - (pred_work / max(1.0, baseline_work)))

            # Baseline confidence calculation
            confidence = 0.8 if strat.name == "dense_baseline" else 0.65
            if strat.name == "exact_cache":
                confidence = 0.95  # Fast test

            cand = AHCECandidate(
                candidate_id=f"cand_{strat.name}_{signature.workload_id}",
                strategy_name=strat.name,
                correctness_class=strat.declared_correctness,
                transformations=[strat.name],
                predicted_work_reduction=round(work_red, 4),
                predicted_latency_ms=round(pred_lat, 4),
                transformation_cost_ms=round(trans_cost, 4),
                confidence=confidence,
                executable_target="CPU_AVX2"
            )
            candidates.append(cand)

        # Sort candidates: Higher predicted work reduction and lower total latency preferred
        # Exact cache always tried first if allowed, then reduced work, then dense baseline
        def sort_key(c: AHCECandidate) -> float:
            if c.strategy_name == "exact_cache":
                return -100.0
            if c.strategy_name == "dense_baseline":
                return 1000.0  # Fallback
            # Total score
            return c.predicted_latency_ms + c.transformation_cost_ms

        candidates.sort(key=sort_key)
        return candidates
