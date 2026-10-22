"""
hyper_x/cpce/result_schema.py
=============================
Unified Result Schema for CPCE.
Implements typed result records carrying fail-closed execution status,
complete measurement provenance, verified resource metrics, and cryptographic seals.
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class ExecutionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"


class ProvenanceLabel(str, Enum):
    MEASURED = "MEASURED"
    DERIVED = "DERIVED"
    CONFIGURED = "CONFIGURED"
    SIMULATED_REFERENCE = "SIMULATED_REFERENCE"
    UNAVAILABLE = "UNAVAILABLE"


@dataclasses.dataclass
class CPCEResult:
    """Authoritative result record for a CPCE workload execution."""
    status: ExecutionStatus
    contract_id: str
    contract_version: str
    backend_requested: str
    backend_used: str
    device_identity: str
    output: Any
    verification_status: str
    verification_evidence: Dict[str, Any]
    timings_ms: Dict[str, float]
    resource_metrics: Dict[str, Any]
    optimizations_applied: List[str]
    provenance: Dict[str, str]
    warnings: List[str] = dataclasses.field(default_factory=list)
    error_details: Optional[str] = None
    certificate_hash: str = ""
    timestamp: float = dataclasses.field(default_factory=time.time)

    def seal(self) -> str:
        """Generates SHA-256 seal of the execution result."""
        seal_dict = {
            "status": self.status.value,
            "contract_id": self.contract_id,
            "backend_used": self.backend_used,
            "device_identity": self.device_identity,
            "timings_ms": self.timings_ms,
            "optimizations_applied": self.optimizations_applied,
            "timestamp": self.timestamp,
        }
        data_str = json.dumps(seal_dict, sort_keys=True)
        self.certificate_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        return self.certificate_hash

    def to_dict(self) -> Dict[str, Any]:
        """Serializes result into dictionary without raw tensor dumping."""
        out_summary = f"<Array shape={self.output.shape} dtype={self.output.dtype}>" if hasattr(self.output, "shape") else str(self.output)[:128]
        return {
            "status": self.status.value,
            "contract_id": self.contract_id,
            "contract_version": self.contract_version,
            "backend_requested": self.backend_requested,
            "backend_used": self.backend_used,
            "device_identity": self.device_identity,
            "output_summary": out_summary,
            "verification_status": self.verification_status,
            "verification_evidence": self.verification_evidence,
            "timings_ms": self.timings_ms,
            "resource_metrics": self.resource_metrics,
            "optimizations_applied": self.optimizations_applied,
            "provenance": self.provenance,
            "warnings": self.warnings,
            "error_details": self.error_details,
            "certificate_hash": self.certificate_hash,
            "timestamp": self.timestamp,
        }
