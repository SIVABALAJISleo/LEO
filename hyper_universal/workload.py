"""
hyper_universal/workload.py
===========================
Universal Workload Schema & Domain Registry.

Implements Section 7 of the Master Specification:
- Represents arbitrary computational workloads symbolically.
- Supports 24 Workload Families (Linear Algebra, Deep Learning, Graphics, Physics, etc.)
  as well as CUSTOM, UNKNOWN, COMPOSITE, and GENERATED.
- Tracks input/output specifications, contracts, targets, and proof obligations.
"""

from __future__ import annotations
import hashlib
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper_universal.contract_ir import ContractIR, ContractType


class WorkloadFamily(str, Enum):
    LINEAR_ALGEBRA = "LINEAR_ALGEBRA"
    DEEP_LEARNING = "DEEP_LEARNING"
    GRAPHICS = "GRAPHICS"
    RENDERING = "RENDERING"
    SIMULATION = "SIMULATION"
    CRYPTOGRAPHY = "CRYPTOGRAPHY"
    COMPRESSION = "COMPRESSION"
    SEARCH = "SEARCH"
    SORTING = "SORTING"
    GRAPH_ALGORITHMS = "GRAPH_ALGORITHMS"
    SIGNAL_PROCESSING = "SIGNAL_PROCESSING"
    IMAGE_PROCESSING = "IMAGE_PROCESSING"
    VIDEO_PROCESSING = "VIDEO_PROCESSING"
    SCIENTIFIC_COMPUTING = "SCIENTIFIC_COMPUTING"
    OPTIMIZATION = "OPTIMIZATION"
    DATABASE_OPERATIONS = "DATABASE_OPERATIONS"
    NUMERICAL_PDE = "NUMERICAL_PDE"
    SYMBOLIC_COMPUTATION = "SYMBOLIC_COMPUTATION"
    DYNAMIC_PROGRAMMING = "DYNAMIC_PROGRAMMING"
    PHYSICS_SIMULATION = "PHYSICS_SIMULATION"
    GENERAL_PURPOSE = "GENERAL_PURPOSE"
    CUSTOM = "CUSTOM"
    UNKNOWN = "UNKNOWN"
    COMPOSITE = "COMPOSITE"
    GENERATED = "GENERATED"


class UniversalWorkload(BaseModel):
    workload_id: str
    name: str
    workload_family: WorkloadFamily = WorkloadFamily.GENERAL_PURPOSE
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    input_domain: str = "ℝ^N"
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    contract: ContractIR
    reference_algorithm: str = "CANONICAL_NAIVE"
    allowed_transformations: List[str] = Field(
        default_factory=lambda: [
            "TILING", "SPARSIFICATION", "LOW_RANK", "ALGEBRAIC_REFORMULATION",
            "MEMOIZATION", "INCREMENTALIZATION", "BITNET_TERNARY", "FUSION"
        ]
    )
    forbidden_shortcuts: List[str] = Field(
        default_factory=lambda: [
            "DELEGATE_TO_REFERENCE", "UNREPORTED_PRECOMPUTATION",
            "REDUCE_PRECISION_WITHOUT_DECLARATION"
        ]
    )
    resource_targets: Dict[str, float] = Field(default_factory=dict)
    performance_targets: Dict[str, float] = Field(default_factory=dict)
    proof_obligations: List[str] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

    def get_canonical_hash(self) -> str:
        content = f"{self.workload_id}:{self.workload_family.value}:{self.name}:{self.contract.contract_type.value}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
