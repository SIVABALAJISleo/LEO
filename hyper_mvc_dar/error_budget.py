"""
hyper_mvc_dar/error_budget.py
Error-Budget Engine: Tracks cumulative approximation and quantization error across multi-stage pipelines.
"""

from typing import Dict, Any, List


class ErrorBudgetTracker:
    """Manages remaining allowable error budget epsilon across sequential stages."""

    def __init__(self, total_budget: float = 0.01):
        self.total_budget = total_budget
        self.consumed_budget = 0.0
        self.stage_allocations: List[Dict[str, Any]] = []

    def allocate_stage(self, stage_name: str, error_incurred: float) -> bool:
        """Records error incurred by a stage; returns False if budget is exceeded."""
        # Simple worst-case triangular inequality bound: sum(errors) <= epsilon
        self.stage_allocations.append({
            "stage_name": stage_name,
            "error_incurred": error_incurred,
            "remaining_before": self.total_budget - self.consumed_budget
        })
        self.consumed_budget += error_incurred
        return self.consumed_budget <= self.total_budget

    @property
    def remaining_budget(self) -> float:
        return max(0.0, self.total_budget - self.consumed_budget)

    @property
    def is_valid(self) -> bool:
        return self.consumed_budget <= self.total_budget
