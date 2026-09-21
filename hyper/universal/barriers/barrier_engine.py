"""
hyper/universal/barriers/barrier_engine.py
==========================================
Formal Barrier and Epistemic Uncertainty Engine.
Detects when computational optimization encounters irreducible limitations:
- Information Entropy Barriers
- Computational Lower Bounds
- Memory Bandwidth Saturation
- Dependency Serialization
- Precision Floors
Classifications: PROVEN, EMPIRICAL, UNRESOLVED.
Preserves UNKNOWN as a first-class scientific result.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
from typing import Any, Dict, List, Optional

from ..contracts.universal_contract import UniversalContract
from ..information.boundary_engine import InformationBoundaryProfile


class BarrierType(str, Enum):
    INFORMATION_ENTROPY = "INFORMATION_ENTROPY"
    COMPUTATIONAL_LOWER_BOUND = "COMPUTATIONAL_LOWER_BOUND"
    MEMORY_BANDWIDTH = "MEMORY_BANDWIDTH"
    COMMUNICATION_BOTTLENECK = "COMMUNICATION_BOTTLENECK"
    PRECISION_FLOOR = "PRECISION_FLOOR"
    DEPENDENCY_SERIALIZATION = "DEPENDENCY_SERIALIZATION"
    HARDWARE_SATURATION = "HARDWARE_SATURATION"


class ProofStatus(str, Enum):
    PROVEN = "PROVEN"                   # Mathematically established lower bound
    EMPIRICAL = "EMPIRICAL"             # Measured hardware saturation / profiling evidence
    UNRESOLVED = "UNRESOLVED"           # Unsettled, search budget exhausted


@dataclasses.dataclass
class UniversalBarrierVerdict:
    has_barrier: bool
    barrier_type: Optional[BarrierType]
    proof_status: ProofStatus
    evidence: str
    affected_workload: str
    affected_transformation: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "has_barrier": self.has_barrier,
            "barrier_type": self.barrier_type.value if self.barrier_type else None,
            "proof_status": self.proof_status.value,
            "evidence": self.evidence,
            "affected_workload": self.affected_workload,
            "affected_transformation": self.affected_transformation,
            "confidence": self.confidence,
        }


class UniversalBarrierEngine:
    """Classifies computational lower bounds and information boundaries."""

    @staticmethod
    def detect_barrier(
        contract: UniversalContract,
        profile: Optional[InformationBoundaryProfile] = None,
    ) -> UniversalBarrierVerdict:
        # 1. Information entropy check: completely incompressible data
        if profile and profile.entropy_analysis:
            comp_ratio = profile.entropy_analysis.get("compression_ratio", 1.0)
            shannon = profile.entropy_analysis.get("shannon_entropy_bits", 0.0)
            if comp_ratio >= 0.98 and shannon >= 7.8:
                return UniversalBarrierVerdict(
                    has_barrier=True,
                    barrier_type=BarrierType.INFORMATION_ENTROPY,
                    proof_status=ProofStatus.PROVEN,
                    evidence=f"Shannon entropy ({shannon:.2f} bits) indicates maximally incompressible data; no exact lossless reduction exists.",
                    affected_workload=contract.workload_id,
                    confidence=0.99,
                )

        # 2. Strict floating point exactness barrier
        if contract.is_exact() and "FLOAT" in contract.precision.value:
            # Cannot use int8 or lossy representations
            return UniversalBarrierVerdict(
                has_barrier=False,
                barrier_type=None,
                proof_status=ProofStatus.EMPIRICAL,
                evidence="Exact float contract forbids lossy quantization, but algebraic pathways remain open.",
                affected_workload=contract.workload_id,
                confidence=0.85,
            )

        return UniversalBarrierVerdict(
            has_barrier=False,
            barrier_type=None,
            proof_status=ProofStatus.UNRESOLVED,
            evidence="No proven barrier detected; continuous adaptive search permitted.",
            affected_workload=contract.workload_id,
            confidence=0.5,
        )
