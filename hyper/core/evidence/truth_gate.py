"""
hyper/core/evidence/truth_gate.py
Fail-Closed Truth Gate and 100% Contract Closure Validator (Prompt Section 30 & 33).
A candidate passes ONLY when ALL mandatory predicates pass without exception.
No weighted score may convert failures into a PASS.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from hyper.core.evidence.models import EvidenceGrade, EvidenceObject


class GateDecision(str, Enum):
    PASS = "PASS"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"


class TruthGateChecklist(BaseModel):
    contract_pass: bool = False
    proof_pass: bool = False
    verification_pass: bool = False
    provenance_pass: bool = False
    measurement_pass: bool = False
    reproducibility_pass: bool = False
    discrepancy_details: List[str] = Field(default_factory=list)


class TruthGate:
    """
    Final Scientific Truth Gate.
    Requires:
    contract_pass AND proof_pass AND verification_pass AND provenance_pass AND measurement_pass AND reproducibility_pass.
    If ANY condition fails, the verdict is UNKNOWN or REJECTED, NEVER PASS.
    """

    @classmethod
    def evaluate(cls, checklist: TruthGateChecklist, evidence: EvidenceObject) -> Tuple[GateDecision, str]:
        reasons = []

        if not checklist.contract_pass:
            reasons.append("Contract validation failed (output discrepancy or tolerance exceeded)")
        if not checklist.proof_pass:
            reasons.append("Formal / symbolic proof verification failed")
        if not checklist.verification_pass:
            reasons.append("Independent differential verification failed")
        if not checklist.provenance_pass:
            reasons.append("Provenance validation failed (missing hardware/code fingerprint)")
        if not checklist.measurement_pass:
            reasons.append("Real measurement pass failed (synthetic or simulated data rejected)")
        if not checklist.reproducibility_pass:
            reasons.append("Multi-run reproducibility check failed")

        if checklist.discrepancy_details:
            reasons.extend(checklist.discrepancy_details)

        # Integrity rule: If evidence is marked PREDICTED or SIMULATED, it CANNOT be accepted as REAL_VERIFIED
        if evidence.evidence_status in [EvidenceGrade.PREDICTED, EvidenceGrade.SIMULATED, EvidenceGrade.INVALID]:
            reasons.append(f"Evidence status {evidence.evidence_status.value} is unacceptable for TruthGate PASS")

        if not reasons:
            return GateDecision.PASS, "100% Contract closure verified across all formal predicates."
        
        return GateDecision.UNKNOWN, f"TruthGate UNKNOWN / REJECTED: {'; '.join(reasons)}"
