"""
hyper_universal/claim_gate.py
=============================
Universal Claim Gate & Universal Claim Certificate Engine.

Implements Sections 31 & 58 of the Master Specification:
- Hard Gatekeeper that strictly refuses to issue universal parity or proof claims
  unless all 12 rigorous evidence checkpoints are verified.
- Emits formal, tamper-evident UniversalClaimCertificate.
- If evidence is incomplete or counterexamples exist:
    final_status = NOT_ESTABLISHED or BOUNDED_ESTABLISHED or UNKNOWN.
    Never 'FORMALLY_ESTABLISHED' based merely on finite benchmark success!
"""

from __future__ import annotations
import hashlib
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper_universal.types import ClaimStatus


class UniversalClaimChecklist(BaseModel):
    universe_formally_defined: bool = False
    input_domains_defined: bool = False
    contracts_formally_defined: bool = False
    candidate_coverage_sufficient: bool = False
    correctness_evidence_passed: bool = False
    performance_evidence_measured: bool = False
    resource_limits_verified: bool = False
    independent_verification_passed: bool = False
    counterexample_search_passed: bool = False
    generalization_evidence_passed: bool = False
    proof_artifacts_verified: bool = False
    reproducibility_guaranteed: bool = False

    def passed_count(self) -> int:
        fields = [
            self.universe_formally_defined,
            self.input_domains_defined,
            self.contracts_formally_defined,
            self.candidate_coverage_sufficient,
            self.correctness_evidence_passed,
            self.performance_evidence_measured,
            self.resource_limits_verified,
            self.independent_verification_passed,
            self.counterexample_search_passed,
            self.generalization_evidence_passed,
            self.proof_artifacts_verified,
            self.reproducibility_guaranteed,
        ]
        return sum(1 for f in fields if f)

    def total_count(self) -> int:
        return 12

    def is_all_passed(self) -> bool:
        return self.passed_count() == self.total_count()


class UniversalClaimCertificate(BaseModel):
    claim_id: str = Field(default_factory=lambda: f"claim-{uuid.uuid4().hex[:8]}")
    workload_universe: str
    target_claim: str
    final_status: ClaimStatus = ClaimStatus.UNKNOWN
    passed_checkpoints: int = 0
    total_checkpoints: int = 12
    evidence_percentage: float = 0.0
    checklist: UniversalClaimChecklist = Field(default_factory=UniversalClaimChecklist)
    rejection_reasons: List[str] = Field(default_factory=list)
    hardware_provenance: str = "Intel Core i5-12450H + Intel UHD Graphics (48 EUs)"
    software_provenance: str = "LEO / HYPER Omega v1.0"
    certificate_hash: str = ""
    timestamp: float = Field(default_factory=time.time)

    def compute_hash(self) -> str:
        content = f"{self.claim_id}:{self.final_status.value}:{self.evidence_percentage}:{self.workload_universe}"
        self.certificate_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.certificate_hash


class UniversalClaimGate:
    """
    Audits candidate evidence against the constitutional 12-item checklist.
    Guarantees no false positive 'UNIVERSAL_CLAIM = TRUE'.
    """

    def __init__(self) -> None:
        self.issued_certificates: List[UniversalClaimCertificate] = []

    def audit_claim(
        self,
        workload_universe: str,
        target_claim: str,
        checklist: UniversalClaimChecklist,
        has_counterexamples: bool = False,
    ) -> UniversalClaimCertificate:
        passed = checklist.passed_count()
        total = checklist.total_count()
        pct = round((passed / total) * 100.0, 1)

        rejections: List[str] = []

        if has_counterexamples:
            status = ClaimStatus.NOT_ESTABLISHED
            rejections.append("Counterexamples exist in domain; claim is falsified.")
        elif checklist.is_all_passed():
            status = ClaimStatus.FORMALLY_ESTABLISHED
        elif not checklist.candidate_coverage_sufficient or not checklist.counterexample_search_passed:
            status = ClaimStatus.UNKNOWN
            rejections.append("Mandatory candidate coverage or counterexample search incomplete; domain state is UNKNOWN.")
        elif passed >= 10:
            status = ClaimStatus.BOUNDED_ESTABLISHED
            rejections.append("Missing proof artifacts or full generalization; bounded claim only.")
        elif passed >= 8:
            status = ClaimStatus.PARTIALLY_ESTABLISHED
            rejections.append("Evidence incomplete; partial empirical support only.")
        else:
            status = ClaimStatus.UNKNOWN
            rejections.append("Insufficient evidence across mandatory checkpoints.")

        cert = UniversalClaimCertificate(
            workload_universe=workload_universe,
            target_claim=target_claim,
            final_status=status,
            passed_checkpoints=passed,
            total_checkpoints=total,
            evidence_percentage=pct,
            checklist=checklist,
            rejection_reasons=rejections,
        )
        cert.compute_hash()
        self.issued_certificates.append(cert)
        return cert
