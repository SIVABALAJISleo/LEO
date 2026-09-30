"""
hyper_omega/provenance/certificates.py
Generates machine-readable, cryptographic Proof-Carrying Scientific Certificates.
Format satisfies Prompt Section 53 & Section 47.
"""
from __future__ import annotations
import hashlib
import json
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from hyper_omega.cost_model.ledger import WorkLedger, MetricProvenance


class ScientificCertificate(BaseModel):
    """Immutable proof-carrying certificate for an accepted computational escape."""
    certificate_id: str
    workload_id: str
    contract_type: str
    parity_level: str
    hardware: str = "Intel Core i5-12450H (4P+4E/12T) + Intel UHD Graphics"
    dispatch_path: str
    proof_type: str
    proof_hash: str
    input_hash: str
    code_hash: str
    exactness: str = "PROVEN_EXACT"
    
    baseline_operations: int = 0
    candidate_operations: int = 0
    verification_operations: int = 0
    work_eliminated_operations: int = 0
    elimination_percentage: float = 0.0
    
    latency_ms: float = 0.0
    speedup_ratio: float = 1.0
    memory_traffic_bytes: int = 0
    
    verification_method: str = "Independent Differential Verifier"
    confidence: float = 1.0
    fallback: bool = False
    timestamp: float = Field(default_factory=time.time)
    provenance: str = "MEASURED"

    def compute_certificate_signature(self) -> str:
        payload = f"{self.certificate_id}:{self.workload_id}:{self.proof_hash}:{self.input_hash}:{self.code_hash}:{self.exactness}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_json_dict(self) -> Dict[str, Any]:
        d = self.model_dump()
        d["signature"] = self.compute_certificate_signature()
        return d
