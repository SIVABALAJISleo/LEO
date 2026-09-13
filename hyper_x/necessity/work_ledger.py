#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/necessity/work_ledger.py
================================
Phase 4: Formal Work Ledger and Arithmetic Accounting.
Tracks FLOPs and memory movement across all operational categories.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any, List


@dataclass
class WorkBreakdown:
    original_flops: float
    necessary_flops: float
    eliminable_flops: float
    reused_flops: float = 0.0
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
        d = asdict(self)
        d["work_elimination_ratio"] = round(self.work_elimination_ratio, 4)
        d["work_elimination_pct"] = round(self.work_elimination_ratio * 100.0, 2)
        return d


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
