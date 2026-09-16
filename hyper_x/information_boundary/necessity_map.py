#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/necessity_map.py
=============================================
Phase 3: Necessity Map Engine.
Constructs dynamic operation necessity maps by classifying operations into:
  - ESSENTIAL: Irreducible operations directly determining contract output
  - REDUNDANT: Sub-threshold zeros / dead branches (pruned immediately)
  - PREDICTABLE: Replaced by cheap surrogate or speculative draft
  - CACHED: Pre-computed intermediate result with exact cryptographic fingerprint
  - APPROXIMATE: Computable in reduced precision without contract violation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np
from .influence_graph import InformationCategory


@dataclass
class NecessityEntry:
    node_id: str
    category: InformationCategory
    nominal_cost_flops: float
    realized_cost_flops: float
    elimination_ratio: float
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class NecessityMapEngine:
    """
    Constructs comprehensive necessity maps for computational graphs,
    calculating necessary work vs eliminated work.
    """

    def __init__(self, sparsity_threshold: float = 1e-4):
        self.sparsity_threshold = sparsity_threshold
        self.entries: Dict[str, NecessityEntry] = {}

    def classify_gemm(
        self,
        op_id: str,
        A: np.ndarray,
        B: np.ndarray,
        is_cached: bool = False,
        allow_approx: bool = False,
    ) -> NecessityEntry:
        m, k = A.shape
        _, n = B.shape
        nominal_flops = 2.0 * m * k * n

        if is_cached:
            entry = NecessityEntry(
                node_id=op_id,
                category=InformationCategory.REUSABLE_INFORMATION,
                nominal_cost_flops=nominal_flops,
                realized_cost_flops=0.0,
                elimination_ratio=1.0,
                reason="EXACT_CACHE_REUSE: Cryptographic hash match in exact memoization cache.",
            )
        else:
            # Check sparsity
            zeros = np.sum(np.abs(A) < self.sparsity_threshold)
            zero_ratio = float(zeros / max(A.size, 1))

            if zero_ratio > 0.50:
                realized = nominal_flops * (1.0 - zero_ratio)
                entry = NecessityEntry(
                    node_id=op_id,
                    category=InformationCategory.REDUNDANT_INFORMATION,
                    nominal_cost_flops=nominal_flops,
                    realized_cost_flops=realized,
                    elimination_ratio=zero_ratio,
                    reason=f"SPARSE_PRUNING: {zero_ratio*100:.1f}% structurally dead inputs.",
                )
            elif allow_approx:
                entry = NecessityEntry(
                    node_id=op_id,
                    category=InformationCategory.APPROXIMABLE_INFORMATION,
                    nominal_cost_flops=nominal_flops,
                    realized_cost_flops=nominal_flops * 0.25,  # INT8 / low-rank speedup
                    elimination_ratio=0.75,
                    reason="APPROXIMATION_PERMITTED: Reduced precision within contract epsilon.",
                )
            else:
                entry = NecessityEntry(
                    node_id=op_id,
                    category=InformationCategory.REQUIRED_INFORMATION,
                    nominal_cost_flops=nominal_flops,
                    realized_cost_flops=nominal_flops,
                    elimination_ratio=0.0,
                    reason="IRREDUCIBLE_COMPUTE: Exact full rank compute required by contract.",
                )

        self.entries[op_id] = entry
        return entry

    def summary(self) -> Dict[str, Any]:
        total_nominal = sum(e.nominal_cost_flops for e in self.entries.values())
        total_realized = sum(e.realized_cost_flops for e in self.entries.values())
        overall_reduction = (
            (total_nominal - total_realized) / max(total_nominal, 1.0)
            if total_nominal > 0
            else 0.0
        )
        return {
            "total_nodes": len(self.entries),
            "total_nominal_flops": total_nominal,
            "total_realized_flops": total_realized,
            "flops_eliminated": total_nominal - total_realized,
            "overall_elimination_ratio": float(overall_reduction),
            "breakdown_by_category": {
                cat.value: sum(1 for e in self.entries.values() if e.category == cat)
                for cat in InformationCategory
            },
        }
