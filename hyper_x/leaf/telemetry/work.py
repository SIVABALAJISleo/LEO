"""
hyper_x/leaf/telemetry/work.py
==============================
Work accounting and Computational Compression Ratio (CCR) tracking for LEAF.

Phase 30 Definition:
    CCR = reference necessary work / candidate necessary work
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ComputationalCompressionLedger:
    reference_necessary_flops: int
    candidate_necessary_flops: int
    eliminated_flops: int
    computational_compression_ratio: float
    work_reduction_percentage: float

    @classmethod
    def calculate(cls, ref_flops: int, cand_flops: int) -> "ComputationalCompressionLedger":
        elim = max(0, ref_flops - cand_flops)
        ccr = float(ref_flops) / max(1, cand_flops)
        pct = (float(elim) / max(1, ref_flops)) * 100.0
        return cls(
            reference_necessary_flops=ref_flops,
            candidate_necessary_flops=cand_flops,
            eliminated_flops=elim,
            computational_compression_ratio=ccr,
            work_reduction_percentage=pct,
        )
