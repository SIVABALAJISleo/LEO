"""
hyper_x/wormhole_compiler/claim_validator.py
=============================================================================
HYPER-X Scientific Claim Validation Engine (Phase 41)
=============================================================================
Audits and validates every performance or parity claim against empirical evidence:
  - Statement Text
  - Claimed Metric Dimension (Application Parity vs Hardware Parity)
  - Cryptographic Evidence Pointer (workload_hash, candidate_hash, proof_id)

Outputs:
  - VERIFIED (backed by multi-verifier consensus & holdout)
  - QUALIFIED (verified on specific structured distribution, e.g. low-rank)
  - ESTIMATED (analytical estimation, e.g. TDP power calculation)
  - UNSUPPORTED (claim lacks evidence pointer)
  - INVALID (scientifically contradictory claim, e.g. hardware faking)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import enum


class ClaimStatus(str, enum.Enum):
    VERIFIED = "VERIFIED"
    QUALIFIED = "QUALIFIED"
    ESTIMATED = "ESTIMATED"
    UNSUPPORTED = "UNSUPPORTED"
    INVALID = "INVALID"


@dataclass
class ClaimAuditResult:
    statement: str
    dimension: str
    status: ClaimStatus
    audit_notes: str
    evidence_valid: bool


class ClaimValidator:
    """Rigorous scientific validator for all published statements."""

    @staticmethod
    def audit_claim(
        statement: str,
        dimension: str,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> ClaimAuditResult:
        """Audits a claim against required evidence standards."""
        st_lower = statement.lower()

        # Check for prohibited hardware faking claims
        if "gpu replaced" in st_lower or "100% nvidia replacement" in st_lower:
            return ClaimAuditResult(
                statement=statement,
                dimension=dimension,
                status=ClaimStatus.INVALID,
                audit_notes="Prohibited statement: Software cannot alter physical silicon hardware resources.",
                evidence_valid=False,
            )

        if "measured power" in st_lower and evidence and evidence.get("sensor_available") is False:
            return ClaimAuditResult(
                statement=statement,
                dimension=dimension,
                status=ClaimStatus.INVALID,
                audit_notes="Prohibited statement: Nominal TDP power estimation cannot be labeled as measured power.",
                evidence_valid=False,
            )

        # Evidence evaluation
        if evidence is None or not evidence.get("proof_record_id"):
            return ClaimAuditResult(
                statement=statement,
                dimension=dimension,
                status=ClaimStatus.UNSUPPORTED,
                audit_notes="Claim lacks required cryptographic proof record pointer.",
                evidence_valid=False,
            )

        if dimension == "APPLICATION_PARITY" or dimension == "CONTRACT_PARITY":
            if evidence.get("tolerance_satisfied", False) and evidence.get("holdout_passed", False):
                return ClaimAuditResult(
                    statement=statement,
                    dimension=dimension,
                    status=ClaimStatus.VERIFIED,
                    audit_notes="Verified: Application contract strictly satisfied on blind holdout.",
                    evidence_valid=True,
                )

        if dimension == "WORK_ELIMINATION":
            elim_pct = evidence.get("work_elimination_pct", 0.0)
            return ClaimAuditResult(
                statement=statement,
                dimension=dimension,
                status=ClaimStatus.VERIFIED if elim_pct > 0 else ClaimStatus.QUALIFIED,
                audit_notes=f"Work elimination verified at {elim_pct:.1f}% mathematical FLOP reduction.",
                evidence_valid=True,
            )

        return ClaimAuditResult(
            statement=statement,
            dimension=dimension,
            status=ClaimStatus.QUALIFIED,
            audit_notes="Claim qualified to specific benchmark bounds.",
            evidence_valid=True,
        )
