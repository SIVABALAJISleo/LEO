"""
hyper/escape_engine/search/search_budget.py
===========================================
VAEE Section 11 & 29: Search Budget & Resource Bounds Controller.

Guarantees search terminates within bounded time, candidate counts, and memory thresholds.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Optional


@dataclasses.dataclass
class SearchBudget:
    max_candidates: int = 100
    max_time_seconds: float = 30.0
    max_memory_mb: float = 2048.0
    target_improvement_ratio: float = 1.2  # Stop early if >= 1.2x verified improvement achieved
    patience_without_improvement: int = 25 # Candidates before declaring saturation

    start_time: float = dataclasses.field(default_factory=time.time)
    candidates_evaluated: int = 0

    def is_exhausted(self, current_memory_mb: Optional[float] = None) -> bool:
        """Check if any search constraint has been exceeded."""
        elapsed = time.time() - self.start_time
        if elapsed >= self.max_time_seconds:
            return True
        if self.candidates_evaluated >= self.max_candidates:
            return True
        if current_memory_mb is not None and current_memory_mb >= self.max_memory_mb:
            return True
        return False

    def remaining_time(self) -> float:
        return max(0.0, self.max_time_seconds - (time.time() - self.start_time))

    def increment(self) -> None:
        self.candidates_evaluated += 1
