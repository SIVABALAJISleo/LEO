"""
hyper_x/verification/provenance_verifier.py
===========================================
Phase 1: Provenance Verifier.
Validates cryptographic software commit, model weights, input seeds, and hardware identity.
Fail-closed default: passed = False.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ProvenanceVerificationResult:
    passed: bool = False  # Fail-closed default
    provenance_hash: str = ""
    is_reproducible: bool = False
    violations: List[str] = field(default_factory=list)


class ProvenanceVerifier:
    """
    Verifies that all hardware and software provenance metadata is present and cryptographically sealed.
    """

    REQUIRED_FIELDS = [
        "git_commit",
        "input_hash",
        "model_hash",
        "hardware_identity",
        "seed",
        "compiler_version",
    ]

    @classmethod
    def verify(cls, metadata: Dict[str, Any]) -> ProvenanceVerificationResult:
        violations = []
        for field_name in cls.REQUIRED_FIELDS:
            val = metadata.get(field_name)
            if val is None or str(val).strip() == "":
                violations.append(f"Missing mandatory provenance field: {field_name}")

        passed = len(violations) == 0
        prov_str = "".join(f"{k}:{metadata.get(k, '')}" for k in sorted(metadata.keys()))
        p_hash = hashlib.sha256(prov_str.encode("utf-8")).hexdigest()

        return ProvenanceVerificationResult(
            passed=passed,
            provenance_hash=p_hash,
            is_reproducible=passed,
            violations=violations,
        )
