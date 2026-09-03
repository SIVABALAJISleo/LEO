"""
hyper_v3/search/evolutionary.py
Genetic / evolutionary strategy tuner mutating tiling and partition parameters.
"""

from typing import List
import random
from hyper_v3.search.candidate_generator import StrategyCandidate


class EvolutionarySearch:
    """Mutates and evolves parameter configurations across generations."""

    @staticmethod
    def mutate(candidate: StrategyCandidate) -> StrategyCandidate:
        new_tile = random.choice([16, 32, 64, 128])
        new_cand = StrategyCandidate(
            candidate_id=f"{candidate.candidate_id}_mut_{new_tile}",
            strategy_name=candidate.strategy_name,
            target_device=candidate.target_device,
            use_low_rank=candidate.use_low_rank,
            use_sparsity=candidate.use_sparsity,
            use_memoization=candidate.use_memoization,
            use_fusion=candidate.use_fusion,
            tile_size=new_tile,
            predicted_latency_us=candidate.predicted_latency_us,
            predicted_vwa=candidate.predicted_vwa,
            transformations=list(candidate.transformations)
        )
        return new_cand
