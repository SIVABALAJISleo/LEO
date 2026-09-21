"""
hyper/escape_engine/learning/strategy_selector.py
=================================================
VAEE Adaptive Strategy Selector.
Balances exploration of novel transformations with exploitation of proven high-probability pathways.
"""

from __future__ import annotations

import random
from typing import List

from .transformation_statistics import TransformationStatistics


class StrategySelector:
    """Balances exploration and exploitation across transformation operators."""

    def __init__(self, stats: TransformationStatistics, epsilon: float = 0.2, seed: int = 42) -> None:
        self.stats = stats
        self.epsilon = epsilon
        self.rng = random.Random(seed)

    def prioritize_transformations(self, workload_type: str, candidate_ops: List[str]) -> List[str]:
        """Orders transformations by combining exploitation probabilities with epsilon exploration."""
        if self.rng.random() < self.epsilon:
            # Exploration: shuffle randomly
            shuffled = list(candidate_ops)
            self.rng.shuffle(shuffled)
            return shuffled

        # Exploitation: rank by empirical P(success)
        return sorted(
            candidate_ops,
            key=lambda op: self.stats.get_success_probability(workload_type, op),
            reverse=True,
        )
