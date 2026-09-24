"""
hyper_universal/contract_ir.py
==============================
Contract IR: Rigorous Mathematical Specification of Computational Obligations.

Implements Section 8 of the Master Specification:
- Supports 12 Contract Types:
    EXACT, NUMERICAL, TOLERANCE, SYMBOLIC, STRUCTURAL, SEMANTIC,
    PERCEPTUAL, PROBABILISTIC, RESOURCE, LATENCY, THROUGHPUT, COMPOSITE.
- Every contract explicitly declares:
    * what must match
    * what may differ
    * allowed numerical tolerance
    * allowed representation differences
    * allowed timing variation
    * forbidden shortcuts
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field


class ContractType(str, Enum):
    EXACT = "EXACT"
    NUMERICAL = "NUMERICAL"
    TOLERANCE = "TOLERANCE"
    SYMBOLIC = "SYMBOLIC"
    STRUCTURAL = "STRUCTURAL"
    SEMANTIC = "SEMANTIC"
    PERCEPTUAL = "PERCEPTUAL"
    PROBABILISTIC = "PROBABILISTIC"
    RESOURCE = "RESOURCE"
    LATENCY = "LATENCY"
    THROUGHPUT = "THROUGHPUT"
    COMPOSITE = "COMPOSITE"


class NumericalTolerance(BaseModel):
    absolute_tolerance: float = 1e-5
    relative_tolerance: float = 1e-4
    max_divergent_elements: int = 0
    divergence_metric: str = "L_INFINITY"


class ResourceLimits(BaseModel):
    max_latency_ms: Optional[float] = None
    min_throughput_ops: Optional[float] = None
    max_memory_mb: float = 4096.0
    max_bandwidth_gbps: float = 18.57
    max_power_watts: float = 45.0


class ContractIR(BaseModel):
    contract_id: str
    workload_id: str
    contract_type: ContractType = ContractType.EXACT
    mandatory_outputs: List[str] = Field(default_factory=lambda: ["output"])
    tolerance: NumericalTolerance = Field(default_factory=NumericalTolerance)
    resource_limits: ResourceLimits = Field(default_factory=ResourceLimits)
    allows_approximation: bool = False
    preserves_ordering: bool = True
    is_deterministic: bool = True
    allowed_representation_changes: List[str] = Field(
        default_factory=lambda: ["DENSE", "SPARSE", "LOW_RANK", "TILED", "TERNARY"]
    )
    forbidden_shortcuts: List[str] = Field(
        default_factory=lambda: [
            "DELEGATE_TO_REFERENCE",
            "UNREPORTED_PRECOMPUTATION",
            "REDUCE_PRECISION_WITHOUT_DECLARATION",
            "HARDCODE_BENCHMARK_ANSWER",
            "OMIT_REQUIRED_COMPUTATION",
        ]
    )
    what_must_match: str = "Values must strictly equal ground truth within contract tolerance."
    what_may_differ: str = "Internal memory layout, loop ordering, and intermediate representations."
    created_at: float = Field(default_factory=time.time)

    def is_exact(self) -> bool:
        return self.contract_type in (ContractType.EXACT, ContractType.SYMBOLIC)
