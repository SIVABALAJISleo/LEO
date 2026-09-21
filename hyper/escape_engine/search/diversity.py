"""
hyper/escape_engine/search/diversity.py
=======================================
VAEE Section 10: Pathway Diversity Metric & Similarity Engine.

Calculates pathway similarity and enforces structural diversity so that 1000 minor parameter
tweaks are not counted as 1000 genuinely different computational formulations.
"""

from __future__ import annotations

import difflib
from typing import List, Set

from ..pathways.schema import ComputationalPathway


class DiversityEngine:
    """Evaluates structural divergence and enforces minimum distance between candidates."""

    @staticmethod
    def calculate_pathway_similarity(p1: ComputationalPathway, p2: ComputationalPathway) -> float:
        """
        Compute similarity score in [0.0, 1.0] based on:
        - Algorithm family match (weight 0.40)
        - Representation match (weight 0.25)
        - Transformation sequence edit distance (weight 0.25)
        - Execution strategy match (weight 0.10)
        """
        sim = 0.0
        if p1.algorithm_family == p2.algorithm_family:
            sim += 0.40

        if p1.representation == p2.representation:
            sim += 0.25

        chain1 = " ".join(p1.transformation_chain)
        chain2 = " ".join(p2.transformation_chain)
        seq_ratio = difflib.SequenceMatcher(None, chain1, chain2).ratio()
        sim += 0.25 * seq_ratio

        if p1.execution_strategy == p2.execution_strategy:
            sim += 0.10

        return round(sim, 4)

    @staticmethod
    def is_sufficiently_novel(
        candidate: ComputationalPathway,
        existing_population: List[ComputationalPathway],
        max_similarity_threshold: float = 0.85,
    ) -> bool:
        """Reject candidates that are too similar to already evaluated pathways."""
        if not existing_population:
            return True

        for existing in existing_population:
            if DiversityEngine.calculate_pathway_similarity(candidate, existing) >= max_similarity_threshold:
                return False
        return True
