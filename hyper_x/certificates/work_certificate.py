"""
hyper_x/certificates/work_certificate.py
========================================
HYPER-Ω External-Equivalence Work Certificate:
Formal cryptographic record certifying verified work elimination and reference equivalence.
"""

from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional


@dataclass
class ExternalEquivalenceWorkCertificate:
    experiment_id: str
    workload_id: str
    hardware_identity: str
    reference_identity: str
    candidate_identity: str
    input_hash: str
    reference_output_hash: str
    candidate_output_hash: str
    contract_hash: str
    equivalence_mode: str
    reference_algorithm: str
    candidate_algorithm: str
    reference_operation_count: float
    candidate_operation_count: float
    verified_work_elimination: float
    reference_memory_bytes: float
    candidate_memory_bytes: float
    reference_latency_ms: float
    candidate_latency_ms: float
    speedup_ratio: float
    cpu_time_ms: float
    igpu_time_ms: float
    cache_state: str                       # e.g., "COLD_START_EXACT"
    precomputation_state: str              # "ZERO_PRECOMPUTATION"
    external_compute_state: str            # "STRICTLY_LOCAL"
    verification_method: str
    verification_result: str               # "PASS", "FAIL", "UNKNOWN"
    adversarial_result: str                # "PASS", "FAIL", "UNKNOWN"
    holdout_result: str                    # "PASS", "FAIL", "UNKNOWN"
    reproducibility_command: str
    status: str                            # "VERIFIED", "VERIFIED_EXACT", "VERIFIED_CONTRACT", "FAILED", "UNKNOWN", "INVALID"
    certificate_hash: str = ""
    timestamp: float = field(default_factory=time.time)

    def seal(self) -> str:
        """Computes cryptographic SHA-256 seal of certificate fields."""
        data_str = json.dumps(asdict(self), sort_keys=True)
        self.certificate_hash = hashlib.sha256(data_str.encode("utf-8")).hexdigest()
        return self.certificate_hash

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
