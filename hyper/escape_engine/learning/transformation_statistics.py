"""
hyper/escape_engine/learning/transformation_statistics.py
=========================================================
VAEE Section 20: Transformation Probability Estimator.

Calculates P(success | transformation, workload) based on cumulative history.
"""

from __future__ import annotations

import collections
from typing import Dict, List, Tuple

from .pathway_history import PathwayHistoryRecord


class TransformationStatistics:
    """Estimates empirical success probabilities for transformation operators."""

    def __init__(self) -> None:
        # Map: (workload_type, transformation_id) -> [success_count, total_count]
        self._counts: Dict[Tuple[str, str], List[int]] = collections.defaultdict(lambda: [0, 0])

    def update_from_records(self, records: List[PathwayHistoryRecord]) -> None:
        for r in records:
            is_success = 1 if r.outcome == "SUCCESS" else 0
            for op in r.transformation_chain:
                key = (r.workload_type, op)
                self._counts[key][0] += is_success
                self._counts[key][1] += 1

    def get_success_probability(self, workload_type: str, transformation_id: str, prior_alpha: float = 1.0, prior_beta: float = 1.0) -> float:
        """Bayesian smoothed estimate of success probability."""
        key = (workload_type, transformation_id)
        successes, total = self._counts[key]
        return (successes + prior_alpha) / (total + prior_alpha + prior_beta)

    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        stats: Dict[str, Dict[str, float]] = collections.defaultdict(dict)
        for (wl, op), (s, tot) in self._counts.items():
            prob = s / max(1, tot)
            stats[wl][op] = round(prob, 3)
        return dict(stats)
