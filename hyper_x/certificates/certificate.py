#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/certificates/certificate.py
===================================
Phase 8: Cryptographic Execution Certificate System.
Guarantees tamper-evident verification. No certificate = No verified percentage.
"""

from __future__ import annotations
import json
import time
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


@dataclass
class ExecutionCertificate:
    certificate_id: str
    timestamp: float
    workload_id: str
    contract_hash: str
    hardware_fingerprint: str
    candidate_hash: str
    reference_hash: str
    input_hash: str
    output_hash: str
    exactness_class: str
    correctness_result: str                     # PASS, FAIL, UNKNOWN
    numerical_metrics: Dict[str, Any]
    adversarial_result: Dict[str, Any]
    holdout_result: Dict[str, Any]
    latency_samples_ms: List[float]
    throughput_ops_per_sec: float
    memory_rss_mb: float
    work_reference_flops: float
    work_necessary_flops: float
    work_eliminated_ratio: float
    cache_state: str                            # COLD, WARM, CACHE_HIT, CACHE_MISS
    provenance: str                             # MEASURED, REFERENCE, ESTIMATED, CACHED
    fallback_status: str                        # NONE, FALLBACK_EXECUTED
    verifier_version: str = "vNext-1.0"
    certificate_signature: str = ""

    def __post_init__(self):
        if not self.certificate_signature:
            self.certificate_signature = self.compute_signature()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def compute_signature(self) -> str:
        d = asdict(self)
        d.pop("certificate_signature", None)
        serialized = json.dumps(d, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_tamper_evident(self) -> bool:
        return self.compute_signature() == self.certificate_signature

    def save_json(self, filepath: str = "execution_certificate.json"):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
