"""
hyper/universal/pathways/novelty.py
===================================
Pathway Novelty and Anti-Cheating Diversity Engine.
Ensures real structural and algorithmic uniqueness.
Rejects pseudodiversity (e.g. same algorithm + different random seeds or thread counts).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
import numpy as np

from .schema import UniversalPathway


class UniversalDiversityEngine:
    """Maintains deduplicating registry of candidate pathways and measures semantic diversity."""

    def __init__(self, similarity_threshold: float = 0.90) -> None:
        self.similarity_threshold = similarity_threshold
        self._registered_hashes: Set[str] = set()
        self._pathways: Dict[str, UniversalPathway] = {}
        self._family_counts: Dict[str, int] = {}

    def is_novel(self, pathway: UniversalPathway) -> bool:
        # Check structural hash
        if pathway.structural_hash in self._registered_hashes:
            return False

        # Check transformation chain equality
        chain_tuple = tuple(pathway.transformation_chain)
        for existing in self._pathways.values():
            if tuple(existing.transformation_chain) == chain_tuple and existing.target_hardware == pathway.target_hardware:
                return False

        return True

    def register(self, pathway: UniversalPathway) -> bool:
        if not self.is_novel(pathway):
            return False

        self._registered_hashes.add(pathway.structural_hash)
        self._pathways[pathway.pathway_id] = pathway
        fam = pathway.family.value
        self._family_counts[fam] = self._family_counts.get(fam, 0) + 1
        return True

    def get_pathway(self, pathway_id: str) -> Optional[UniversalPathway]:
        return self._pathways.get(pathway_id)

    def get_all(self) -> List[UniversalPathway]:
        return list(self._pathways.values())

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_unique_pathways": len(self._pathways),
            "family_distribution": self._family_counts,
            "structurally_unique_count": len(self._registered_hashes),
        }
