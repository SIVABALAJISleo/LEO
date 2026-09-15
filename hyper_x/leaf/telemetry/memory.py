"""
hyper_x/leaf/telemetry/memory.py
================================
Memory working set and L3-cache telemetry for LEAF.

Rule (Phase 12):
    Do not claim "entire model fits in L3" unless actual model/representation size
    and cache behavior are measured.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


L3_TOTAL_CAPACITY_BYTES: int = 12 * 1024 * 1024        # 12 MB
L3_SAFE_BUDGET_BYTES: int = int(9.6 * 1024 * 1024)     # 9.6 MB


@dataclass(frozen=True)
class MemoryWorkingSetReport:
    working_set_bytes: int
    l3_budget_bytes: int
    is_l3_resident: bool
    l3_utilization_percentage: float
    memory_compression_ratio: float

    @classmethod
    def analyze(cls, original_bytes: int, candidate_bytes: int) -> "MemoryWorkingSetReport":
        is_res = candidate_bytes <= L3_SAFE_BUDGET_BYTES
        util_pct = (float(candidate_bytes) / L3_TOTAL_CAPACITY_BYTES) * 100.0
        comp_ratio = float(original_bytes) / max(1, candidate_bytes)
        return cls(
            working_set_bytes=candidate_bytes,
            l3_budget_bytes=L3_SAFE_BUDGET_BYTES,
            is_l3_resident=is_res,
            l3_utilization_percentage=util_pct,
            memory_compression_ratio=comp_ratio,
        )
