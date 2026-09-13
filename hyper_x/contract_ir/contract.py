#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/contract_ir/contract.py
===============================
Phase 2: Formal Machine-Readable Contract IR Representation for HYPER / LEO.

Declares non-negotiable invariants, exactness modes, tolerances, observables, and policies.
"""

from __future__ import annotations
import enum
import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List


class CorrectnessMode(str, enum.Enum):
    """The 7 strict non-overlapping correctness modes specified by the protocol."""
    EXACT_BITWISE = "EXACT_BITWISE"
    EXACT = "EXACT_BITWISE"
    EXACT_SEMANTIC = "EXACT_SEMANTIC"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    BOUNDED_APPROXIMATION = "BOUNDED_APPROXIMATION"
    PERCEPTUAL = "PERCEPTUAL"
    PERCEPTUAL_APPROXIMATION = "PERCEPTUAL"
    PREDICTIVE = "PREDICTIVE"
    CONTRACT_DEFINED = "CONTRACT_DEFINED"


# Backward compatibility alias
ExactnessClass = CorrectnessMode


@dataclass
class ContractIR:
    """Formal machine-readable workload computation contract IR."""
    workload_id: str
    application: str                                        # e.g., "LINEAR_ALGEBRA", "LLM_INFERENCE", "GRAPHICS"
    observable: str                                         # Declared observable output (e.g., "OUTPUT_MATRIX", "NEXT_TOKENS", "FRAME_RGB")
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    exactness_mode: CorrectnessMode = CorrectnessMode.NUMERICALLY_EQUIVALENT
    numerical_tolerance: float = 1e-4                       # General numerical threshold
    absolute_tolerance: float = 1e-5                        # Maximum entrywise error |y - y_ref|
    relative_tolerance: float = 1e-3                        # Maximum relative norm error ||y - y_ref|| / ||y_ref||
    perceptual_tolerance: float = 0.95                      # Minimum SSIM/PSNR bound
    latency_slo: float = 100.0                              # Latency SLO in milliseconds
    throughput_slo: float = 10.0                            # Throughput SLO (ops/s, tokens/s, FPS)
    memory_limit: float = 2048.0                            # Memory limit in MB (16GB max system constraint)
    determinism_requirement: bool = True
    reproducibility_requirement: bool = True
    allowed_approximations: List[str] = field(default_factory=lambda: ["low_rank", "sparsity"])
    forbidden_transformations: List[str] = field(default_factory=list)
    cache_policy: str = "EXACT_ONLY"                        # "EXACT_ONLY", "SEMANTIC_ISOLATED", "NO_CACHE"
    prediction_policy: str = "VERIFIED_TARGET_ONLY"         # "VERIFIED_TARGET_ONLY", "DISALLOWED"
    reconstruction_policy: str = "PERCEPTUAL_BOUNDED"       # "PERCEPTUAL_BOUNDED", "DISALLOWED"
    fallback_policy: str = "DETERMINISTIC_LADDER"           # "DETERMINISTIC_LADDER", "EXACT_REFERENCE"
    verification_policy: str = "FAIL_CLOSED"                # "FAIL_CLOSED"
    provenance_policy: str = "CRYPTOGRAPHIC_MEASURED"       # "CRYPTOGRAPHIC_MEASURED"
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Backward compatibility properties
    @property
    def exactness_class(self) -> CorrectnessMode:
        return self.exactness_mode

    @property
    def workload_family(self) -> str:
        return self.application

    @property
    def allowed_approximation(self) -> bool:
        return len(self.allowed_approximations) > 0

    @property
    def latency_slo_ms(self) -> float:
        return self.latency_slo

    @property
    def memory_budget_mb(self) -> float:
        return self.memory_limit

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["exactness_mode"] = self.exactness_mode.value
        # For backward compatibility with older readers expecting exactness_class
        d["exactness_class"] = self.exactness_mode.value
        return d

    def compute_contract_hash(self) -> str:
        """Returns deterministic SHA-256 digest of contract parameters."""
        d = self.to_dict()
        serialized = json.dumps(d, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContractIR:
        data_copy = dict(data)
        # Normalize exactness mode
        mode_val = data_copy.pop("exactness_mode", data_copy.pop("exactness_class", None))
        if mode_val:
            # Handle mapping from legacy strings
            if isinstance(mode_val, str):
                try:
                    mode = CorrectnessMode(mode_val)
                except ValueError:
                    if "EXACT" in mode_val:
                        mode = CorrectnessMode.EXACT_BITWISE
                    elif "PERCEPTUAL" in mode_val:
                        mode = CorrectnessMode.PERCEPTUAL
                    elif "PREDICT" in mode_val:
                        mode = CorrectnessMode.PREDICTIVE
                    else:
                        mode = CorrectnessMode.NUMERICALLY_EQUIVALENT
                data_copy["exactness_mode"] = mode

        # Normalize legacy field names if present
        if "workload_family" in data_copy and "application" not in data_copy:
            data_copy["application"] = data_copy.pop("workload_family")
        if "latency_slo_ms" in data_copy and "latency_slo" not in data_copy:
            data_copy["latency_slo"] = data_copy.pop("latency_slo_ms")
        if "memory_budget_mb" in data_copy and "memory_limit" not in data_copy:
            data_copy["memory_limit"] = data_copy.pop("memory_budget_mb")
        if "observable" not in data_copy:
            data_copy["observable"] = "OUTPUT_TENSOR"

        # Remove extra keys that don't belong to the dataclass
        valid_fields = {f for f in cls.__dataclass_fields__}
        filtered = {k: v for k, v in data_copy.items() if k in valid_fields}
        return cls(**filtered)
