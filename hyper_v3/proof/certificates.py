"""
hyper_v3/proof/certificates.py
Generates formal, tamper-evident exactness certificates for mathematical transformations.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import hashlib
import json
import time

from hyper_v3.frontend.contract_parser import ExactnessClass


@dataclass
class ExactnessCertificate:
    """Tamper-evident certificate verifying correctness of a computational transformation."""
    certificate_id: str
    transformation_name: str
    source_operation: str
    target_operation: str
    equivalence_class: ExactnessClass
    proof_method: str
    max_relative_error_observed: float
    max_absolute_error_observed: float
    verification_status: str  # PASS, FAIL
    timestamp: float = field(default_factory=time.time)
    certificate_hash: str = field(default="", init=False)

    def __post_init__(self):
        data = {
            "id": self.certificate_id,
            "trans": self.transformation_name,
            "src": self.source_operation,
            "tgt": self.target_operation,
            "equiv": self.equivalence_class.value,
            "proof": self.proof_method,
            "rel_err": self.max_relative_error_observed,
            "abs_err": self.max_absolute_error_observed,
            "status": self.verification_status,
            "ts": self.timestamp
        }
        h = hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
        object.__setattr__(self, "certificate_hash", h)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "certificate_id": self.certificate_id,
            "transformation": self.transformation_name,
            "source_operation": self.source_operation,
            "target_operation": self.target_operation,
            "equivalence_class": self.equivalence_class.value,
            "proof_method": self.proof_method,
            "max_relative_error": self.max_relative_error_observed,
            "max_absolute_error": self.max_absolute_error_observed,
            "verification": self.verification_status,
            "timestamp": self.timestamp,
            "certificate_hash": self.certificate_hash
        }
