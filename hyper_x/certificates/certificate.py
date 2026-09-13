#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/certificates/certificate.py
===================================
Phase 23: Execution Certificate System.

Every optimized execution produces a tamper-evident cryptographic certificate.
Final Status Categories:
  - VERIFIED_EXACT
  - VERIFIED_NUMERICAL
  - VERIFIED_CONTRACT
  - VERIFIED_APPROXIMATE
  - VERIFIED_PREDICTIVE
  - VERIFIED_RECONSTRUCTED
  - FALLBACK
  - UNKNOWN
  - REJECTED
"""

from __future__ import annotations
import json
import time
import hashlib
import enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional


class CertificateFinalStatus(str, enum.Enum):
    VERIFIED_EXACT = "VERIFIED_EXACT"
    VERIFIED_NUMERICAL = "VERIFIED_NUMERICAL"
    VERIFIED_CONTRACT = "VERIFIED_CONTRACT"
    VERIFIED_APPROXIMATE = "VERIFIED_APPROXIMATE"
    VERIFIED_PREDICTIVE = "VERIFIED_PREDICTIVE"
    VERIFIED_RECONSTRUCTED = "VERIFIED_RECONSTRUCTED"
    FALLBACK = "FALLBACK"
    UNKNOWN = "UNKNOWN"
    REJECTED = "REJECTED"


@dataclass
class ExecutionCertificate:
    certificate_id: str
    timestamp: float
    workload_id: str
    contract_hash: str
    input_hash: str
    candidate_hash: str
    reference_hash: str
    hardware_fingerprint: str
    model_hash: str = "none"
    software_fingerprint: str = "HYPER-UltraSonic-v2.0-Win11"
    execution_path: str = "EXACT_REUSE"
    original_work: float = 0.0
    necessary_work: float = 0.0
    eliminated_work: float = 0.0
    reused_work: float = 0.0
    predicted_work: float = 0.0
    reconstructed_work: float = 0.0
    verification_work: float = 0.0
    latency: float = 0.0
    throughput: float = 0.0
    memory: float = 0.0
    correctness: str = "PASS"
    numerical_error: float = 0.0
    exact_status: str = "EXACT_MATCH"
    adversarial_status: str = "PASS"
    holdout_status: str = "PASS"
    provenance_status: str = "MEASURED"
    final_status: str = CertificateFinalStatus.VERIFIED_CONTRACT.value
    # Project Omega: Software-Defined Compute Fabric metrics
    virtual_work_units: int = 0
    physical_execution_units: int = 56
    software_parallel_worker_equivalence: float = 0.0
    computational_compression_ratio: float = 1.0
    gap_root_cause: str = "NONE"
    # Backward compatibility fields
    output_hash: str = ""
    exactness_class: str = "NUMERICALLY_EQUIVALENT"
    correctness_result: str = "PASS"
    numerical_metrics: Dict[str, Any] = field(default_factory=dict)
    adversarial_result: Dict[str, Any] = field(default_factory=dict)
    holdout_result: Dict[str, Any] = field(default_factory=dict)
    latency_samples_ms: List[float] = field(default_factory=list)
    throughput_ops_per_sec: float = 0.0
    memory_rss_mb: float = 0.0
    work_reference_flops: float = 0.0
    work_necessary_flops: float = 0.0
    work_eliminated_ratio: float = 0.0
    cache_state: str = "WARM"
    provenance: str = "MEASURED"
    fallback_status: str = "NONE"
    verifier_version: str = "vNext-2.0"
    certificate_signature: str = ""

    def __post_init__(self):
        # Sync backward compatibility fields if not explicitly provided
        if not self.work_reference_flops and self.original_work:
            self.work_reference_flops = self.original_work
        elif not self.original_work and self.work_reference_flops:
            self.original_work = self.work_reference_flops

        if not self.work_necessary_flops and self.necessary_work:
            self.work_necessary_flops = self.necessary_work
        elif not self.necessary_work and self.work_necessary_flops:
            self.necessary_work = self.work_necessary_flops

        if not self.latency and self.latency_samples_ms:
            self.latency = self.latency_samples_ms[0]
        elif not self.latency_samples_ms and self.latency:
            self.latency_samples_ms = [self.latency]

        if not self.throughput and self.throughput_ops_per_sec:
            self.throughput = self.throughput_ops_per_sec
        elif not self.throughput_ops_per_sec and self.throughput:
            self.throughput_ops_per_sec = self.throughput

        if not self.memory and self.memory_rss_mb:
            self.memory = self.memory_rss_mb
        elif not self.memory_rss_mb and self.memory:
            self.memory_rss_mb = self.memory

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

    def save_json(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, filepath: str) -> ExecutionCertificate:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
