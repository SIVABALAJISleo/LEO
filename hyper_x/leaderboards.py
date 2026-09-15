"""
hyper_x/leaderboards.py
=======================
The Four Core Independent Leaderboards for LEO / HYPER (Part 54).

Absolute Rule (Part 54):
"Do not combine these into one misleading percentage."

Leaderboards:
- Leaderboard A: SAME_COMPUTATION
  Compares identical mathematical operations (FLOP for FLOP, zero shortcuts).
- Leaderboard B: EXACT_REDUCED_COMPUTATION
  Compares mathematically identical outputs produced through reduced computation.
- Leaderboard C: CONTRACT_EQUIVALENCE
  Compares outputs that strictly satisfy the application contract (e.g. bounded approximation, PSNR, perceptual).
- Leaderboard D: APPLICATION_PERFORMANCE
  Compares end-to-end task completion (wall-clock latency, user-observed FPS/TPS).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List
from enum import Enum


class LeaderboardCategory(str, Enum):
    A_SAME_COMPUTATION = "SAME_COMPUTATION"
    B_EXACT_REDUCED_COMPUTATION = "EXACT_REDUCED_COMPUTATION"
    C_CONTRACT_EQUIVALENCE = "CONTRACT_EQUIVALENCE"
    D_APPLICATION_PERFORMANCE = "APPLICATION_PERFORMANCE"


@dataclass
class LeaderboardEntry:
    workload_id: str
    category: LeaderboardCategory
    target_hardware: str
    reference_hardware: str
    target_metric_val: float
    reference_metric_val: float
    metric_unit: str
    ratio: float  # target / reference
    parity_achieved: bool
    evidence_class: str  # MEASURED, REFERENCE, etc.
    notes: str = ""


class FourCoreLeaderboards:
    """Manages the four disjoint scoreboards without blending."""

    def __init__(self):
        self.scoreboard_a: List[LeaderboardEntry] = []
        self.scoreboard_b: List[LeaderboardEntry] = []
        self.scoreboard_c: List[LeaderboardEntry] = []
        self.scoreboard_d: List[LeaderboardEntry] = []

    def add_entry(self, entry: LeaderboardEntry) -> None:
        if entry.category == LeaderboardCategory.A_SAME_COMPUTATION:
            self.scoreboard_a.append(entry)
        elif entry.category == LeaderboardCategory.B_EXACT_REDUCED_COMPUTATION:
            self.scoreboard_b.append(entry)
        elif entry.category == LeaderboardCategory.C_CONTRACT_EQUIVALENCE:
            self.scoreboard_c.append(entry)
        elif entry.category == LeaderboardCategory.D_APPLICATION_PERFORMANCE:
            self.scoreboard_d.append(entry)

    def summary(self) -> Dict[str, Any]:
        def summarize_board(board: List[LeaderboardEntry]) -> Dict[str, Any]:
            total = len(board)
            passed = sum(1 for e in board if e.parity_achieved)
            return {
                "total_workloads": total,
                "parity_achieved_count": passed,
                "parity_percentage": round((passed / max(1, total)) * 100.0, 1),
                "entries": [asdict(e) for e in board]
            }

        return {
            "LEADERBOARD_A_SAME_COMPUTATION": summarize_board(self.scoreboard_a),
            "LEADERBOARD_B_EXACT_REDUCED_COMPUTATION": summarize_board(self.scoreboard_b),
            "LEADERBOARD_C_CONTRACT_EQUIVALENCE": summarize_board(self.scoreboard_c),
            "LEADERBOARD_D_APPLICATION_PERFORMANCE": summarize_board(self.scoreboard_d),
            "warning": "DO NOT BLEND THESE FOUR METRICS INTO A SINGLE AGGREGATE PERCENTAGE."
        }
