"""
hyper_v3/search/beam_search.py
Multi-objective beam search optimizer navigating the strategy space subject to a search budget.
"""

from typing import List, Dict, Any
from hyper_v3.frontend.contract_parser import ExecutionContract, ExecutionTrack
from hyper_v3.search.candidate_generator import CandidateGenerator, StrategyCandidate
from hyper_v3.search.cost_model import HardwareCostModel


class BeamSearchOptimizer:
    """Explores and ranks execution strategies with beam width and timeout constraints."""

    def __init__(self, cost_model: HardwareCostModel, beam_width: int = 3, max_budget_ms: float = 50.0):
        self.cost_model = cost_model
        self.beam_width = beam_width
        self.max_budget_ms = max_budget_ms

    def search(self, workload_name: str, contract: ExecutionContract, approx_flops: int = 1000000) -> StrategyCandidate:
        candidates = CandidateGenerator.generate_candidates(workload_name, contract)

        # Score candidates based on cost model + VWA
        scored: List[tuple] = []
        for cand in candidates:
            # Estimate cost
            read_bytes = 4096 * 4
            write_bytes = 2048 * 4
            est = self.cost_model.estimate_cost(
                flops=int(approx_flops * (1.0 - cand.predicted_vwa)),
                read_bytes=read_bytes,
                write_bytes=write_bytes,
                device=cand.target_device,
                requires_transfer=(cand.target_device.value in ["iGPU", "HYBRID"]),
                requires_verification=(contract.track == ExecutionTrack.CONTRACT_AWARE)
            )
            cand.predicted_latency_us = est.total_time_us

            # Objective: Minimize latency, maximize VWA
            score = est.total_time_us * (1.0 - cand.predicted_vwa * 0.5)
            scored.append((score, cand))

        scored.sort(key=lambda x: x[0])
        best_candidate = scored[0][1]
        return best_candidate
