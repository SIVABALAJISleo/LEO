"""
hyper_v3/proof/invariants.py
Tracks system and mathematical invariants (Energy conservation, Error budget propagation).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class ErrorBudget:
    """Propagates error budgets across multi-stage computation graphs."""
    total_budget: float
    allocated: Dict[str, float] = field(default_factory=dict)

    def allocate(self, stage_name: str, amount: float) -> bool:
        current_sum = sum(self.allocated.values())
        if current_sum + amount > self.total_budget:
            return False
        self.allocated[stage_name] = amount
        return True

    def remaining(self) -> float:
        return max(0.0, self.total_budget - sum(self.allocated.values()))
