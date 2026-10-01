"""
hyper/verifier/__init__.py
==========================
Authoritative Verification and Truth Gate Package for LEO/HYPER.
"""

from hyper.verifier.differential_verifier import (
    DifferentialVerifier,
    DifferentialReport,
    ExactnessLevel,
    VerificationVerdict,
)
from hyper.verifier.truth_gate import (
    UniversalTruthGate,
    TruthGateResult,
    ProofStatus,
)

__all__ = [
    "DifferentialVerifier",
    "DifferentialReport",
    "ExactnessLevel",
    "VerificationVerdict",
    "UniversalTruthGate",
    "TruthGateResult",
    "ProofStatus",
]
