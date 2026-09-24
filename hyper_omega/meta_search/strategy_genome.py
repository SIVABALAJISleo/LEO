"""
Search Strategy Genome: Encodes hyper-parameters of the search strategy itself.
"""
from dataclasses import dataclass, field
import random
from typing import Any, Dict, List, Optional


@dataclass
class SearchStrategyGenome:
    """Encodes a meta-search strategy configuration."""
    strategy_id: str
    algorithm: str = "beam_search"  # beam_search, mcts, genetic, alphatensor, alphadev
    candidate_budget: int = 100
    mutation_rate: float = 0.2
    exploration_rate: float = 0.3
    exploitation_rate: float = 0.7
    novelty_weight: float = 0.5
    verification_frequency: int = 1
    selection_policy: str = "pareto_tournament"  # pareto_tournament, roulette, elitist
    representation_policy: str = "mixed_sparse_dense"
    generation: int = 0
    yield_score: float = 0.0  # Measured discovery yield

    def mutate_meta_strategy(self) -> 'SearchStrategyGenome':
        """Mutate meta-parameters based on evolutionary exploration."""
        child = SearchStrategyGenome(
            strategy_id=f"meta_{self.generation + 1}_{random.randint(100, 999)}",
            algorithm=self.algorithm,
            candidate_budget=max(10, int(self.candidate_budget * random.choice([0.8, 1.0, 1.25]))),
            mutation_rate=min(0.9, max(0.05, self.mutation_rate + random.uniform(-0.05, 0.05))),
            exploration_rate=min(0.9, max(0.05, self.exploration_rate + random.uniform(-0.05, 0.05))),
            exploitation_rate=min(0.9, max(0.05, self.exploitation_rate + random.uniform(-0.05, 0.05))),
            novelty_weight=min(1.0, max(0.0, self.novelty_weight + random.uniform(-0.1, 0.1))),
            verification_frequency=self.verification_frequency,
            selection_policy=self.selection_policy,
            representation_policy=self.representation_policy,
            generation=self.generation + 1,
            yield_score=0.0
        )
        return child
