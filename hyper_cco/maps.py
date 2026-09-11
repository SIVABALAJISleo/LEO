"""
hyper_cco/maps.py
=============================================================================
Computational Maps & Frontiers (Sections 62, 63, 64)
=============================================================================
Provides structured visualization schemas for:
  1. NecessityMap (Section 62): Breaks down Original, Necessary, Eliminated, Reused, Predicted, Approximate, and Unknown work.
  2. WormholeMap (Section 63): Contrasts the Original baseline path against the Discovered shortcut path.
  3. FrontierMap (Section 64): Tracks the state of the scientific discovery frontier (Solved, Optimized, Necessary, Unknown).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class NecessityMapRecord:
    workload_id: str
    original_flops: float
    necessary_flops: float
    eliminated_flops: float
    reused_flops: float
    predicted_flops: float
    approximate_flops: float
    unknown_flops: float

    def to_ascii_diagram(self) -> str:
        orig = max(1.0, self.original_flops)
        nec_pct = (self.necessary_flops / orig) * 100.0
        elim_pct = (self.eliminated_flops / orig) * 100.0
        reu_pct = (self.reused_flops / orig) * 100.0
        app_pct = (self.approximate_flops / orig) * 100.0

        bar_len = 30
        nec_bars = int(round((nec_pct / 100.0) * bar_len))
        elim_bars = int(round((elim_pct / 100.0) * bar_len))
        reu_bars = int(round((reu_pct / 100.0) * bar_len))
        app_bars = max(0, bar_len - nec_bars - elim_bars - reu_bars)

        bar_repr = "#" * nec_bars + "." * elim_bars + "=" * reu_bars + "~" * app_bars

        return (
            f"=== Necessity Map: {self.workload_id} ===\n"
            f"Original FLOPs:    {self.original_flops:,.0f}\n"
            f"Work Breakdown:    [{bar_repr}]\n"
            f"  [#] Necessary:   {self.necessary_flops:,.0f} ({nec_pct:.1f}%)\n"
            f"  [.] Eliminated:  {self.eliminated_flops:,.0f} ({elim_pct:.1f}%)\n"
            f"  [=] Reused:      {self.reused_flops:,.0f} ({reu_pct:.1f}%)\n"
            f"  [~] Approximate: {self.approximate_flops:,.0f} ({app_pct:.1f}%)\n"
        )


@dataclass
class WormholeMapRecord:
    workload_id: str
    original_path: List[str]
    discovered_path: List[str]
    work_elimination_ratio: float
    speedup: float
    observable_preserved: str

    def to_ascii_diagram(self) -> str:
        orig_str = " -> ".join(self.original_path)
        disc_str = " -> ".join(self.discovered_path)
        return (
            f"=== Wormhole Map: {self.workload_id} ===\n"
            f"Original Path:   {orig_str}\n"
            f"Discovered Path: {disc_str}\n"
            f"Preserved:       {self.observable_preserved}\n"
            f"Work Reduction:  {self.work_elimination_ratio * 100.0:.1f}%\n"
            f"Speedup:         {self.speedup:.2f}x\n"
        )


@dataclass
class FrontierMapRecord:
    solved_workloads: List[str]
    optimized_workloads: List[str]
    necessary_proven_workloads: List[str]
    unknown_frontier_workloads: List[str]

    def to_ascii_dashboard(self) -> str:
        return (
            f"+--------------------------------------------------------------+\n"
            f"|              LEO / HYPER RESEARCH FRONTIER MAP               |\n"
            f"+--------------------------------------------------------------+\n"
            f"| 1. SOLVED (100% Workload Closure):                          |\n"
            f"|    {', '.join(self.solved_workloads) or 'None':<58} |\n"
            f"| 2. OPTIMIZED (Cheaper Valid Path Found):                    |\n"
            f"|    {', '.join(self.optimized_workloads) or 'None':<58} |\n"
            f"| 3. NECESSARY PROVEN (Indispensable Work Formally Verified):  |\n"
            f"|    {', '.join(self.necessary_proven_workloads) or 'None':<58} |\n"
            f"| 4. UNKNOWN FRONTIER (Active Open Research Space):            |\n"
            f"|    {', '.join(self.unknown_frontier_workloads) or 'None':<58} |\n"
            f"+--------------------------------------------------------------+\n"
        )
