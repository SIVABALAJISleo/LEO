"""
hyper/escape_engine/search/novelty.py
====================================
VAEE Novelty Search Archive.
Maintains a behavioral archive of computational strategies to prevent search collapse.
"""

from __future__ import annotations

from typing import List, Tuple

from ..pathways.schema import ComputationalPathway
from .diversity import DiversityEngine


class NoveltyArchive:
    """Stores behaviorally distinct computational pathways to drive novelty search."""

    def __init__(self, capacity: int = 50) -> None:
        self.capacity = capacity
        self.archive: List[ComputationalPathway] = []

    def compute_novelty_score(self, candidate: ComputationalPathway, k_nearest: int = 5) -> float:
        """Calculates sparseness / distance to k-nearest neighbors in archive."""
        if not self.archive:
            return 1.0

        distances = [
            1.0 - DiversityEngine.calculate_pathway_similarity(candidate, arch)
            for arch in self.archive
        ]
        distances.sort()
        k = min(k_nearest, len(distances))
        return float(sum(distances[:k]) / k)

    def consider_add(self, candidate: ComputationalPathway, novelty_threshold: float = 0.3) -> bool:
        score = self.compute_novelty_score(candidate)
        if score >= novelty_threshold:
            if len(self.archive) >= self.capacity:
                self.archive.pop(0)
            self.archive.append(candidate)
            return True
        return False
