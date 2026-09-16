"""
hyper_x/contract.py
===================
Phase 2: Formal Computational Contract.
Defines the immutable specification that governs execution, verification, and certification.
A candidate may NEVER modify its own contract during execution.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class WorkloadContract:
    workload_id: str
    workload_domain: str
    input_schema: Dict[str, Any]
    input_hash: str
    output_schema: Dict[str, Any]
    output_observable: str
    correctness_class: str
    numerical_tolerance: float = 1e-4
    bit_exact_required: bool = False
    latency_deadline_ms: float = 100.0
    throughput_requirement: float = 10.0
    quality_requirement: float = 40.0  # e.g., PSNR dB or metric threshold
    memory_limit_mb: float = 2048.0
    external_compute_allowed: bool = False
    cache_allowed: bool = False
    precomputation_allowed: bool = False
    approximation_allowed: bool = False
    temporal_reuse_allowed: bool = False
    prediction_allowed: bool = False
    reconstruction_allowed: bool = False
    reference_backend: str = "NVIDIA RTX 5090 Reference"
    candidate_backend: str = "Intel Core i5 + Intel UHD"
    reproducibility_requirements: Dict[str, Any] = field(default_factory=dict)

    def compute_contract_hash(self) -> str:
        serialized = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
