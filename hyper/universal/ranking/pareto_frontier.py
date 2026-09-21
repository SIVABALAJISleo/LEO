"""
hyper/universal/ranking/pareto_frontier.py
==========================================
Multi-Objective Pareto Frontier Engine.
Maintains the non-dominated candidate set across:
- Latency (minimize)
- Memory peak (minimize)
- Energy (minimize)
- Confidence (maximize)
- Speedup vs Baseline (maximize)
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional
import numpy as np

from ..pathways.schema import UniversalPathway


@dataclasses.dataclass
class UniversalParetoPoint:
    pathway: UniversalPathway
    latency_ms: float
    memory_mb: float
    energy_mj: float
    confidence: float
    speedup: float

    def dominates(self, other: UniversalParetoPoint) -> bool:
        """True if self is better or equal in all objectives and strictly better in at least one."""
        not_worse = (
            self.latency_ms <= other.latency_ms
            and self.memory_mb <= other.memory_mb
            and self.energy_mj <= other.energy_mj
            and self.confidence >= other.confidence
        )
        strictly_better = (
            self.latency_ms < other.latency_ms
            or self.memory_mb < other.memory_mb
            or self.energy_mj < other.energy_mj
            or self.confidence > other.confidence
        )
        return not_worse and strictly_better

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pathway": self.pathway.to_dict(),
            "latency_ms": round(self.latency_ms, 4),
            "memory_mb": round(self.memory_mb, 2),
            "energy_mj": round(self.energy_mj, 2),
            "confidence": round(self.confidence, 4),
            "speedup": round(self.speedup, 2),
        }


class UniversalParetoFrontier:
    """Manages the set of non-dominated Pareto candidate pathways."""

    def __init__(self) -> None:
        self.points: List[UniversalParetoPoint] = []

    def update(self, new_point: UniversalParetoPoint) -> bool:
        # If any existing point dominates new_point, discard it
        for pt in self.points:
            if pt.dominates(new_point):
                return False

        # Remove existing points that new_point dominates
        self.points = [pt for pt in self.points if not new_point.dominates(pt)]
        self.points.append(new_point)
        return True

    def get_best_latency(self) -> Optional[UniversalParetoPoint]:
        if not self.points:
            return None
        return min(self.points, key=lambda p: p.latency_ms)

    def to_list(self) -> List[Dict[str, Any]]:
        return [pt.to_dict() for pt in sorted(self.points, key=lambda p: p.latency_ms)]
