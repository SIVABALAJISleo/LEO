"""
cbe/controller/compute_budget.py
Formal compute budget allocator and enforcer.
Ensures total frame latency stays within target millisecond budgets.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class StageBudget:
    stage_name: str
    allocated_ms: float
    spent_ms: float = 0.0
    start_timestamp: float = 0.0


class ComputeBudget:
    """
    Allocates and monitors microsecond budgets across execution stages:
    State Understanding -> Prediction -> Temporal Reprojection -> Residual Classification ->
    Rendering -> Reconstruction -> Quality Verification.
    """
    def __init__(self, target_fps: float = 60.0):
        self.target_fps = target_fps
        self.total_budget_ms = 1000.0 / target_fps
        self.stages: Dict[str, StageBudget] = {
            "state": StageBudget("state", allocated_ms=self.total_budget_ms * 0.05),
            "prediction": StageBudget("prediction", allocated_ms=self.total_budget_ms * 0.10),
            "temporal_reprojection": StageBudget("temporal_reprojection", allocated_ms=self.total_budget_ms * 0.10),
            "residual_classify": StageBudget("residual_classify", allocated_ms=self.total_budget_ms * 0.05),
            "render": StageBudget("render", allocated_ms=self.total_budget_ms * 0.45),
            "reconstruction": StageBudget("reconstruction", allocated_ms=self.total_budget_ms * 0.20),
            "quality_check": StageBudget("quality_check", allocated_ms=self.total_budget_ms * 0.05),
        }
        self.frame_start_time = 0.0

    def start_frame(self):
        self.frame_start_time = time.perf_counter()
        for s in self.stages.values():
            s.spent_ms = 0.0

    def begin_stage(self, stage_name: str):
        if stage_name in self.stages:
            self.stages[stage_name].start_timestamp = time.perf_counter()

    def end_stage(self, stage_name: str) -> float:
        if stage_name in self.stages:
            s = self.stages[stage_name]
            elapsed = (time.perf_counter() - s.start_timestamp) * 1000.0
            s.spent_ms += elapsed
            return elapsed
        return 0.0

    def get_total_elapsed_ms(self) -> float:
        if self.frame_start_time <= 0:
            return 0.0
        return (time.perf_counter() - self.frame_start_time) * 1000.0

    def is_budget_exceeded(self) -> bool:
        return self.get_total_elapsed_ms() > self.total_budget_ms

    def get_summary(self) -> Dict[str, Any]:
        total_spent = self.get_total_elapsed_ms()
        return {
            "target_budget_ms": round(self.total_budget_ms, 2),
            "total_spent_ms": round(total_spent, 2),
            "budget_headroom_ms": round(self.total_budget_ms - total_spent, 2),
            "stage_breakdown": {
                name: round(s.spent_ms, 3) for name, s in self.stages.items()
            }
        }
