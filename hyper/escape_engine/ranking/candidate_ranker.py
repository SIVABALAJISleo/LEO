"""
hyper/escape_engine/ranking/candidate_ranker.py
===============================================
VAEE Candidate Ranking Engine.
Performs fast non-dominated sorting and rank assignments across multiple metrics.
"""

from __future__ import annotations

from typing import List
from .pareto import ParetoFrontier, ParetoPoint


class CandidateRanker:
    """Ranks and manages Pareto dominance fronts."""

    @staticmethod
    def build_frontier(points: List[ParetoPoint]) -> ParetoFrontier:
        frontier = ParetoFrontier()
        for p in points:
            frontier.update(p)
        return frontier
