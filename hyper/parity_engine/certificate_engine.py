"""
hyper/parity_engine/certificate_engine.py
=========================================
Formal Mathematical & Empirical Certificate Engine.
Implements Section 25 of the HYPER 100% Master Mission.

Certificate Types (Section 25):
1.  EXACT_EQUIVALENCE
2.  NUMERICAL_EQUIVALENCE
3.  DEPENDENCY_ELIMINATION
4.  REUSE_VALIDITY
5.  INCREMENTAL_VALIDITY
6.  ALGEBRAIC_EQUIVALENCE
7.  VISIBILITY
8.  TEMPORAL_REUSE
9.  SPARSITY
10. BOUNDS
11. ERROR_BOUND
12. CONTRACT_EQUIVALENCE

Schema:
certificate:
  id: str
  type: CertificateType
  original: str
  replacement: str
  assumptions: List[str]
  proof: str
  tests: int
  adversarial_tests: int
  numerical_error: float
  status: CertificateStatus
"""

from __future__ import annotations
import enum
import hashlib
import json
import os
import uuid
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CertificateType(str, enum.Enum):
    EXACT_EQUIVALENCE = "EXACT_EQUIVALENCE"
    NUMERICAL_EQUIVALENCE = "NUMERICAL_EQUIVALENCE"
    DEPENDENCY_ELIMINATION = "DEPENDENCY_ELIMINATION"
    REUSE_VALIDITY = "REUSE_VALIDITY"
    INCREMENTAL_VALIDITY = "INCREMENTAL_VALIDITY"
    ALGEBRAIC_EQUIVALENCE = "ALGEBRAIC_EQUIVALENCE"
    VISIBILITY = "VISIBILITY"
    TEMPORAL_REUSE = "TEMPORAL_REUSE"
    SPARSITY = "SPARSITY"
    BOUNDS = "BOUNDS"
    ERROR_BOUND = "ERROR_BOUND"
    CONTRACT_EQUIVALENCE = "CONTRACT_EQUIVALENCE"


class CertificateStatus(str, enum.Enum):
    VALIDATED = "VALIDATED"
    PROVISIONALLY_HELD = "PROVISIONALLY_HELD"
    REFUTED = "REFUTED"
    EXPIRED = "EXPIRED"


class Certificate(BaseModel):
    id: str = Field(default_factory=lambda: f"CERT_{uuid.uuid4().hex[:10]}")
    type: CertificateType
    original: str
    replacement: str
    assumptions: List[str] = Field(default_factory=list)
    proof: str
    tests: int = 0
    adversarial_tests: int = 0
    numerical_error: float = 0.0
    status: CertificateStatus = CertificateStatus.VALIDATED
    sha256_fingerprint: str = ""
    timestamp: float = Field(default_factory=time.time)

    def model_post_init(self, __context: Any) -> None:
        if not self.sha256_fingerprint:
            content = f"{self.id}:{self.type.value}:{self.original}:{self.replacement}:{self.numerical_error}:{self.status.value}"
            self.sha256_fingerprint = hashlib.sha256(content.encode("utf-8")).hexdigest()

    def to_yaml_dict(self) -> Dict[str, Any]:
        return {
            "certificate": {
                "id": self.id,
                "type": self.type.value,
                "original": self.original,
                "replacement": self.replacement,
                "assumptions": self.assumptions,
                "proof": self.proof,
                "tests": self.tests,
                "adversarial_tests": self.adversarial_tests,
                "numerical_error": self.numerical_error,
                "status": self.status.value,
                "sha256_fingerprint": self.sha256_fingerprint,
                "timestamp": self.timestamp,
            }
        }


class CertificateEngine:
    """
    Issues, validates, stores, and audits certificates for all verified transformations.
    """

    def __init__(self, ledger_file: str = "reports/certificates_ledger.json") -> None:
        self.ledger_file = ledger_file
        self.certificates: Dict[str, Certificate] = {}
        self._load_ledger()

    def _load_ledger(self) -> None:
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("certificates", []):
                        cert = Certificate(**item)
                        self.certificates[cert.id] = cert
            except Exception:
                pass

    def save_ledger(self) -> None:
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
        payload = {
            "total_certificates": len(self.certificates),
            "updated_at": time.time(),
            "certificates": [c.model_dump() for c in self.certificates.values()],
        }
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def issue_certificate(
        self,
        cert_type: CertificateType,
        original: str,
        replacement: str,
        assumptions: List[str],
        proof: str,
        tests: int,
        adversarial_tests: int,
        numerical_error: float,
        status: CertificateStatus = CertificateStatus.VALIDATED,
    ) -> Certificate:
        cert = Certificate(
            type=cert_type,
            original=original,
            replacement=replacement,
            assumptions=assumptions,
            proof=proof,
            tests=tests,
            adversarial_tests=adversarial_tests,
            numerical_error=numerical_error,
            status=status,
        )
        self.certificates[cert.id] = cert
        self.save_ledger()
        return cert

    def verify_certificate_integrity(self, cert_id: str) -> bool:
        if cert_id not in self.certificates:
            return False
        cert = self.certificates[cert_id]
        content = f"{cert.id}:{cert.type.value}:{cert.original}:{cert.replacement}:{cert.numerical_error}:{cert.status.value}"
        expected = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return cert.sha256_fingerprint == expected
