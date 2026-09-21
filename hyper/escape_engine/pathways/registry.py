"""
hyper/escape_engine/pathways/registry.py
========================================
VAEE Section 9 & 10: Deduplicating Pathway Registry & Diversity Engine.

Prevents counting superficial parameter variations as independent discoveries:
- Enforces structural uniqueness via structural_hash
- Computes diversity metrics D = unique_pathways / total_candidates
- Tracks unique algorithm families, representations, and execution strategies
"""

from __future__ import annotations

import collections
from typing import Any, Dict, List, Optional, Set, Tuple

from .schema import ComputationalPathway


class PathwayRegistry:
    """Central registry for computational pathways with structural deduplication."""

    def __init__(self) -> None:
        self._pathways_by_id: Dict[str, ComputationalPathway] = {}
        self._pathways_by_structural_hash: Dict[str, ComputationalPathway] = {}
        self._algorithm_families: Set[str] = set()
        self._transformation_chains: Set[str] = set()
        self._representations: Set[str] = set()
        self._execution_strategies: Set[str] = set()
        self._total_registered_attempts: int = 0

    def register(self, pathway: ComputationalPathway) -> Tuple[bool, ComputationalPathway]:
        """
        Register a candidate pathway.
        Returns (is_structurally_unique, registered_or_existing_pathway).
        """
        self._total_registered_attempts += 1
        s_hash = pathway.structural_hash

        if s_hash in self._pathways_by_structural_hash:
            # Duplicate structural pathway detected
            return False, self._pathways_by_structural_hash[s_hash]

        # Truly structurally unique
        self._pathways_by_id[pathway.pathway_id] = pathway
        self._pathways_by_structural_hash[s_hash] = pathway
        self._algorithm_families.add(pathway.algorithm_family)
        self._transformation_chains.add(pathway.transformation_hash)
        self._representations.add(pathway.representation)
        self._execution_strategies.add(pathway.execution_strategy)

        return True, pathway

    def get_by_id(self, pathway_id: str) -> Optional[ComputationalPathway]:
        return self._pathways_by_id.get(pathway_id)

    def get_by_hash(self, structural_hash: str) -> Optional[ComputationalPathway]:
        return self._pathways_by_structural_hash.get(structural_hash)

    def list_pathways(self) -> List[ComputationalPathway]:
        return list(self._pathways_by_id.values())

    @property
    def total_attempts(self) -> int:
        return self._total_registered_attempts

    @property
    def structurally_unique_count(self) -> int:
        return len(self._pathways_by_structural_hash)

    @property
    def diversity_ratio(self) -> float:
        """Diversity D = structurally_unique / total_attempts"""
        if self._total_registered_attempts == 0:
            return 1.0
        return self.structurally_unique_count / self._total_registered_attempts

    def get_diversity_stats(self) -> Dict[str, Any]:
        return {
            "total_candidates": self._total_registered_attempts,
            "structurally_unique": self.structurally_unique_count,
            "diversity_ratio": round(self.diversity_ratio, 4),
            "unique_algorithm_families": len(self._algorithm_families),
            "unique_transformation_chains": len(self._transformation_chains),
            "unique_representations": len(self._representations),
            "unique_execution_strategies": len(self._execution_strategies),
            "algorithm_families_list": sorted(list(self._algorithm_families)),
            "representations_list": sorted(list(self._representations)),
            "execution_strategies_list": sorted(list(self._execution_strategies)),
        }
