#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/contract_ir/contract.py
===============================
Phase 2: Formal Contract IR Representation for HYPER / LEO.

Declares non-negotiable invariants, exactness classes, tolerances, and policies.
"""

from __future__ import annotations
import enum
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List


class ExactnessClass(str, enum.Enum):
    """Formal correctness classes separating exact math, approximations, and predictions."""
    EXACT = "EXACT"
    EXACT_REFORMULATION = "EXACT_REFORMULATION"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    BOUNDED_APPROXIMATION = "BOUNDED_APPROXIMATION"
    PERCEPTUAL_APPROXIMATION = "PERCEPTUAL_APPROXIMATION"
    PREDICTIVE = "PREDICTIVE"
    SPECULATIVE = "SPECULATIVE"
    CACHED_EXACT = "CACHED_EXACT"
    REUSED_EXACT = "REUSED_EXACT"
    REDUCED_WORK = "REDUCED_WORK"
    SIMULATED = "SIMULATED"
    UNKNOWN = "UNKNOWN"


@dataclass
class ContractIR:
    """Formal workload execution contract IR."""
    workload_id: str
    workload_family: str                          # DENSE_LINEAR_ALGEBRA, LLM_INFERENCE, GRAPHICS_TEMPORAL, etc.
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    exactness_class: ExactnessClass = ExactnessClass.NUMERICALLY_EQUIVALENT
    numerical_tolerance: float = 1e-4             # Relative Frobenius norm bound
    absolute_tolerance: float = 1e-5              # Absolute entrywise threshold
    perceptual_tolerance: float = 0.95            # Minimum SSIM threshold for vision
    latency_slo_ms: float = 100.0                 # Latency budget in milliseconds
    throughput_slo: float = 10.0                  # Minimum throughput (ops/sec or tokens/sec)
    memory_budget_mb: float = 2048.0              # Maximum memory footprint
    energy_budget_joules: Optional[float] = None
    determinism_requirement: bool = True
    reproducibility_requirement: bool = True
    allowed_approximation: bool = False
    allowed_prediction: bool = False
    allowed_reconstruction: bool = False
    cache_policy: str = "EXACT_ONLY"              # EXACT_ONLY, SEMANTIC_ALLOWED, NO_CACHE
    fallback_policy: str = "EXACT_REFERENCE"      # EXACT_REFERENCE, CONSERVATIVE_APPROX, FAIL_FAST
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["exactness_class"] = self.exactness_class.value
        return d

    def compute_contract_hash(self) -> str:
        """Returns deterministic SHA-256 digest of contract parameters."""
        serialized = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContractIR:
        data_copy = dict(data)
        if "exactness_class" in data_copy:
            data_copy["exactness_class"] = ExactnessClass(data_copy["exactness_class"])
        return cls(**data_copy)
