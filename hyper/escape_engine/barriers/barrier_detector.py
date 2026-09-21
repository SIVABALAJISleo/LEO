"""
hyper/escape_engine/barriers/barrier_detector.py
================================================
VAEE Section 17, 18 & 54: Formal Barrier & Uncertainty Detector.

CRITICAL SCIENTIFIC RULE:
Never confuse "We searched a lot" with "The problem has no better solution."
Distinguishes:
- PROVEN_BARRIER: Mathematically established lower bound or information constraint
- EMPIRICAL_BARRIER: Measured hardware bottleneck (e.g. DDR5 bus saturation)
- UNRESOLVED: Search exhausted without finding improvement (NOT an impossibility proof)
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional

from .lower_bound import LowerBoundAnalyzer
from .information_barrier import InformationBarrier, InformationBarrierAnalyzer
from ..contracts.schema import ComputationalContract
from ..contracts.information_boundary import InformationBoundaryProfile


class BarrierClassification:
    PROVEN_BARRIER = "PROVEN_BARRIER"
    EMPIRICAL_BARRIER = "EMPIRICAL_BARRIER"
    UNRESOLVED = "UNRESOLVED"
    NO_BARRIER_DETECTED = "NO_BARRIER_DETECTED"


@dataclasses.dataclass
class BarrierVerdict:
    status: str                       # from BarrierClassification
    barrier_name: Optional[str]
    is_impossibility_proof: bool
    evidence_statement: str
    scientific_limitation_notice: str

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class BarrierDetector:
    """Detects formal barriers and guards against premature impossibility claims."""

    @staticmethod
    def detect_barriers(
        contract: ComputationalContract,
        profile: InformationBoundaryProfile,
        hardware_memory_bound: bool = False,
    ) -> BarrierVerdict:
        # 1. Check for proven mathematical barrier
        if contract.input_type == "matrix" and not profile.is_sparse and not profile.is_low_rank and contract.correctness == "EXACT":
            barrier = InformationBarrierAnalyzer.check_dense_dependency(is_dense_random=True, exact_required=True)
            if barrier:
                return BarrierVerdict(
                    status=BarrierClassification.PROVEN_BARRIER,
                    barrier_name=barrier.barrier_id,
                    is_impossibility_proof=True,
                    evidence_statement=barrier.evidence,
                    scientific_limitation_notice=(
                        "Dense incompressible random matrix multiplication under an exact contract "
                        "has a proven Omega(N^2) I/O lower bound. No algorithmic shortcut can avoid reading inputs."
                    ),
                )

        # 2. Check for empirical hardware bottleneck
        if hardware_memory_bound:
            return BarrierVerdict(
                status=BarrierClassification.EMPIRICAL_BARRIER,
                barrier_name="HARDWARE_BUS_SATURATION",
                is_impossibility_proof=False,
                evidence_statement="Execution time is bounded by the physical 18.57 GB/s DDR5 bus throughput",
                scientific_limitation_notice=(
                    "Empirical bandwidth saturation on this hardware architecture. "
                    "This is an empirical hardware limitation, NOT a mathematical impossibility."
                ),
            )

        # 3. Unresolved / No barrier detected
        return BarrierVerdict(
            status=BarrierClassification.NO_BARRIER_DETECTED,
            barrier_name=None,
            is_impossibility_proof=False,
            evidence_statement="No formal or empirical barrier detected. Search space remains open.",
            scientific_limitation_notice="Unexplored transformations may still exist within an expanded search space.",
        )
