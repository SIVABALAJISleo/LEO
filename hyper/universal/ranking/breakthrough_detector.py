"""
hyper/universal/ranking/breakthrough_detector.py
================================================
Section 34: Breakthrough Detector.
Identifies genuine, verified algorithmic improvements.
Labels: VERIFIED_ALGORITHMIC_IMPROVEMENT.
Never claims impossible scientific breakthroughs without full falsification proof.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional

from ..pathways.schema import UniversalPathway
from ..verification.schema import UniversalVerificationResult, VerificationState


@dataclasses.dataclass
class BreakthroughRecord:
    is_improvement: bool
    label: str                          # "VERIFIED_ALGORITHMIC_IMPROVEMENT" | "INCREMENTAL_OPTIMIZATION" | "NONE"
    workload_id: str
    baseline_latency_ms: float
    candidate_latency_ms: float
    work_reduction_pct: float
    speedup: float
    verification_state: str
    transformation_chain: list[str]

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class BreakthroughDetector:
    """Detects and registers verified algorithmic breakthroughs with audit traceability."""

    @staticmethod
    def evaluate(
        workload_id: str,
        pathway: UniversalPathway,
        v_res: UniversalVerificationResult,
        baseline_latency_ms: float,
        candidate_latency_ms: float,
    ) -> BreakthroughRecord:
        if not v_res.is_valid or candidate_latency_ms >= baseline_latency_ms:
            return BreakthroughRecord(
                is_improvement=False,
                label="NONE",
                workload_id=workload_id,
                baseline_latency_ms=baseline_latency_ms,
                candidate_latency_ms=candidate_latency_ms,
                work_reduction_pct=0.0,
                speedup=1.0,
                verification_state=v_res.state.value,
                transformation_chain=pathway.transformation_chain,
            )

        speedup = baseline_latency_ms / max(1e-6, candidate_latency_ms)
        work_red = max(0.0, (1.0 - (candidate_latency_ms / baseline_latency_ms)) * 100.0)

        # Significant algorithmic improvement threshold: >= 2.0x verified exact speedup
        is_breakthrough = speedup >= 2.0 and v_res.state in (VerificationState.EXACT_VERIFIED, VerificationState.NUMERICALLY_VERIFIED)

        label = "VERIFIED_ALGORITHMIC_IMPROVEMENT" if is_breakthrough else "INCREMENTAL_OPTIMIZATION"

        return BreakthroughRecord(
            is_improvement=True,
            label=label,
            workload_id=workload_id,
            baseline_latency_ms=round(baseline_latency_ms, 4),
            candidate_latency_ms=round(candidate_latency_ms, 4),
            work_reduction_pct=round(work_red, 2),
            speedup=round(speedup, 2),
            verification_state=v_res.state.value,
            transformation_chain=pathway.transformation_chain,
        )
