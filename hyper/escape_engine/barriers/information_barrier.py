"""
hyper/escape_engine/barriers/information_barrier.py
==================================================
VAEE Section 18: Information & Dependency Barriers.
Detects when every output element strictly depends on every input element (no shortcut possible).
"""

from __future__ import annotations

import dataclasses
from typing import List, Optional


@dataclasses.dataclass
class InformationBarrier:
    barrier_id: str
    barrier_type: str                 # "INPUT_DEPENDENCY" | "MEMORY_BOUND" | "LOWER_BOUND"
    description: str
    is_mathematically_proven: bool    # True = proven mathematical limit; False = empirical boundary
    evidence: str


class InformationBarrierAnalyzer:
    """Analyzes whether an information barrier exists for a given contract."""

    @staticmethod
    def check_dense_dependency(is_dense_random: bool, exact_required: bool) -> Optional[InformationBarrier]:
        if is_dense_random and exact_required:
            return InformationBarrier(
                barrier_id="BARRIER_INCOMPRESSIBLE_DENSE",
                barrier_type="INPUT_DEPENDENCY",
                description="Dense incompressible random matrix with exact contract requires reading all M*K entries",
                is_mathematically_proven=True,
                evidence="Full rank and non-zero entries mandate Omega(N^2) memory reads",
            )
        return None
