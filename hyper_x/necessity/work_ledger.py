#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/necessity/work_ledger.py
================================
Phase 4: Formal Work Ledger and Arithmetic Accounting.
Tracks FLOPs and memory movement across all operational categories specified by the protocol.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, List, Optional


class OperationTransform(str, enum.Enum):
    """The 15 canonical transformation operators attempted by the compiler."""
    DELETE = "DELETE"
    REUSE = "REUSE"
    MERGE = "MERGE"
    FACTOR = "FACTOR"
    REORDER = "REORDER"
    SPARSE = "SPARSE"
    LOW_RANK = "LOW_RANK"
    COMPRESS = "COMPRESS"
    APPROXIMATE = "APPROXIMATE"
    PREDICT = "PREDICT"
    RECONSTRUCT = "RECONSTRUCT"
    TILE = "TILE"
    FUSE = "FUSE"
    STREAM = "STREAM"
    SPECIALIZE = "SPECIALIZE"


@dataclass
class DAGOperationNode:
    operation_id: str
    operation_type: str
    dependencies: List[str] = field(default_factory=list)
    estimated_cost: float = 0.0
    measured_cost: float = 0.0
    information_required: str = "ALL"
    observable_dependency: bool = True
    eliminability: bool = False
    reuseability: bool = False
    reformulation_options: List[str] = field(default_factory=list)
    approximation_options: List[str] = field(default_factory=list)
    verification_requirement: str = "EXACT"


@dataclass
class WorkBreakdown:
    original_flops: float
    necessary_flops: float
    eliminable_flops: float
    reused_flops: float = 0.0
    reformulated_flops: float = 0.0
    approximated_flops: float = 0.0
    predicted_flops: float = 0.0
    reconstructed_flops: float = 0.0
    verification_overhead_flops: float = 0.0
    fallback_flops: float = 0.0

    @property
    def work_elimination_ratio(self) -> float:
        """
        Calculates fraction of work eliminated:
        ratio = 1 - (necessary + verification) / original
        """
        if self.original_flops <= 0.0:
            return 0.0
        effective_work = self.necessary_flops + self.verification_overhead_flops
        return max(0.0, min(1.0, 1.0 - (effective_work / self.original_flops)))

    @property
    def work_elimination_pct(self) -> float:
        return round(self.work_elimination_ratio * 100.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ORIGINAL_WORK": self.original_flops,
            "NECESSARY_WORK": self.necessary_flops,
            "ELIMINABLE_WORK": self.eliminable_flops,
            "REUSED_WORK": self.reused_flops,
            "REFORMULATED_WORK": self.reformulated_flops,
            "APPROXIMATED_WORK": self.approximated_flops,
            "PREDICTED_WORK": self.predicted_flops,
            "RECONSTRUCTED_WORK": self.reconstructed_flops,
            "VERIFICATION_WORK": self.verification_overhead_flops,
            "FALLBACK_WORK": self.fallback_flops,
            "WORK_ELIMINATION": round(self.work_elimination_ratio, 4),
            "WORK_ELIMINATION_PCT": self.work_elimination_pct,
            # Backward compatibility aliases
            "original_flops": self.original_flops,
            "necessary_flops": self.necessary_flops,
            "eliminable_flops": self.eliminable_flops,
            "work_elimination_ratio": round(self.work_elimination_ratio, 4),
            "work_elimination_pct": self.work_elimination_pct
        }


class WorkLedger:
    """Records and aggregates mathematical work operations with zero hardcoded numbers."""

    def __init__(self):
        self.entries: List[WorkBreakdown] = []

    def record(self, breakdown: WorkBreakdown) -> WorkBreakdown:
        self.entries.append(breakdown)
        return breakdown

    def get_summary(self) -> Dict[str, Any]:
        if not self.entries:
            return {
                "total_entries": 0,
                "total_original_flops": 0.0,
                "total_necessary_flops": 0.0,
                "mean_elimination_pct": 0.0
            }
        orig = sum(e.original_flops for e in self.entries)
        nec = sum(e.necessary_flops + e.verification_overhead_flops for e in self.entries)
        net_ratio = max(0.0, 1.0 - (nec / max(orig, 1.0)))
        return {
            "total_entries": len(self.entries),
            "total_original_flops": orig,
            "total_necessary_flops": nec,
            "net_elimination_ratio": round(net_ratio, 4),
            "net_elimination_pct": round(net_ratio * 100.0, 2)
        }
