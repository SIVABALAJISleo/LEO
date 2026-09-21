"""
hyper/escape_engine/ranking/pareto.py
=====================================
VAEE Section 19: Multi-Objective Pareto Frontier Engine.

Maintains non-dominated candidate frontier across:
(latency_ms, peak_memory_mb, energy_mj, verification_confidence)
Never forces an arbitrary single winner when trade-offs exist.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Tuple

from ..pathways.schema import ComputationalPathway


@dataclasses.dataclass
class ParetoPoint:
    pathway: ComputationalPathway
    latency_ms: float
    memory_mb: float
    energy_mj: float
    confidence: float
    speedup_vs_baseline: float

    def dominates(self, other: ParetoPoint) -> bool:
        """
        Returns True if self dominates other:
        - self is <= other in all costs (latency, memory, energy)
        - self is >= other in confidence
        - self is strictly better in at least one objective
        """
        not_worse = (
            self.latency_ms <= other.latency_ms and
            self.memory_mb <= other.memory_mb and
            self.energy_mj <= other.energy_mj and
            self.confidence >= other.confidence
        )
        strictly_better = (
            self.latency_ms < other.latency_ms or
            self.memory_mb < other.memory_mb or
            self.energy_mj < other.energy_mj or
            self.confidence > other.confidence
        )
        return not_worse and strictly_better

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pathway_id": self.pathway.pathway_id,
            "algorithm_family": self.pathway.algorithm_family,
            "representation": self.pathway.representation,
            "transformation_chain": self.pathway.transformation_chain,
            "latency_ms": round(self.latency_ms, 4),
            "memory_mb": round(self.memory_mb, 3),
            "energy_mj": round(self.energy_mj, 3),
            "confidence": round(self.confidence, 4),
            "speedup": round(self.speedup_vs_baseline, 2),
        }


class ParetoFrontier:
    """Manages the non-dominated Pareto frontier for evaluated pathways."""

    def __init__(self) -> None:
        self.points: List[ParetoPoint] = []

    def update(self, point: ParetoPoint) -> bool:
        """
        Attempt to add point to frontier.
        Prunes existing points dominated by the new point.
        Returns True if point was added to frontier.
        """
        # Check if dominated by any existing point
        for existing in self.points:
            if existing.dominates(point):
                return False

        # Remove points dominated by new point
        self.points = [p for p in self.points if not point.dominates(p)]
        self.points.append(point)
        return True

    def get_frontier(self) -> List[ParetoPoint]:
        # Sort primarily by latency
        return sorted(self.points, key=lambda p: p.latency_ms)

    def to_list(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in self.get_frontier()]
