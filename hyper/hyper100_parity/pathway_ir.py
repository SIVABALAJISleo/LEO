"""
hyper/hyper100_parity/pathway_ir.py
====================================
Pathway Intermediate Representation (Pathway IR) for HYPER (Section 8).

A Pathway in HYPER is a complete, holistic software execution specification:
  Algorithm
  + Data Representation
  + Memory Strategy
  + Scheduling Strategy
  + Reuse Strategy
  + Incrementality Plan
  + Reconstruction Plan
  + CPU/iGPU Placement Plan
  + Verification Plan
  + Fallback Plan
  + Certificates
  + Estimated Cost Model
"""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .taxonomy import CapabilityFamily, EquivalenceClass, EvidenceLevel
from .contract_engine import PerformanceContract


class DevicePlacement(str, Enum):
    CPU_AVX2 = "CPU_AVX2"
    IGPU_OPENCL_VULKAN = "IGPU_OPENCL_VULKAN"
    CPU_IGPU_COOPERATIVE = "CPU_IGPU_COOPERATIVE"
    CPU_SCALAR_FALLBACK = "CPU_SCALAR_FALLBACK"


class DataRepresentation(str, Enum):
    DENSE_FP32 = "DENSE_FP32"
    DENSE_FP16 = "DENSE_FP16"
    INT8_SYMMETRIC = "INT8_SYMMETRIC"
    TERNARY_BITNET = "TERNARY_BITNET"
    CSR_SPARSE = "CSR_SPARSE"
    LOW_RANK_FACTORED = "LOW_RANK_FACTORED"
    COMPRESSED_DELTA = "COMPRESSED_DELTA"
    FOURIER_SPECTRAL = "FOURIER_SPECTRAL"


class MemoryStrategy(str, Enum):
    CACHE_TILED_L1_L2 = "CACHE_TILED_L1_L2"
    ZERO_COPY_UMA_BRIDGE = "ZERO_COPY_UMA_BRIDGE"
    STREAMING_CONTIGUOUS = "STREAMING_CONTIGUOUS"
    DOUBLE_BUFFERED_PINNED = "DOUBLE_BUFFERED_PINNED"
    DELTA_RESIDUAL_BUFFER = "DELTA_RESIDUAL_BUFFER"


class SchedulingStrategy(str, Enum):
    SYNCHRONOUS_AFFINITY_PINNED = "SYNCHRONOUS_AFFINITY_PINNED"
    ASYNC_PIPELINED = "ASYNC_PIPELINED"
    WORK_STEALING_PARALLEL = "WORK_STEALING_PARALLEL"
    INTERLEAVED_CPU_IGPU = "INTERLEAVED_CPU_IGPU"


class TransformationRecord(BaseModel):
    step_id: str = Field(default_factory=lambda: f"xf-{uuid.uuid4().hex[:6]}")
    name: str
    category: str  # MATHEMATICAL, SPARSITY, TEMPORAL, MEMORY, HARDWARE, RECONSTRUCTION
    mathematical_basis: str
    work_eliminated_ratio: float = 0.0
    preconditions: List[str] = Field(default_factory=list)
    postconditions: List[str] = Field(default_factory=list)


class EstimatedCost(BaseModel):
    latency_ms: float = 1.0
    throughput_ops_sec: float = 1000.0
    memory_peak_mb: float = 16.0
    memory_bandwidth_gb_s: float = 4.0
    power_watts: float = 25.0
    cpu_utilization_pct: float = 50.0
    igpu_utilization_pct: float = 0.0
    fallback_risk: float = 0.01


class PathwayIR(BaseModel):
    """
    Formal, proof-carrying Pathway IR representing a searched alternative pathway.
    """
    pathway_id: str = Field(default_factory=lambda: f"pw-{uuid.uuid4().hex[:8]}")
    workload_id: str
    capability_family: CapabilityFamily
    contract: PerformanceContract

    # Core 10 Pathway Pillars
    algorithm_name: str
    representation: DataRepresentation = DataRepresentation.DENSE_FP32
    memory_strategy: MemoryStrategy = MemoryStrategy.CACHE_TILED_L1_L2
    scheduling_strategy: SchedulingStrategy = SchedulingStrategy.SYNCHRONOUS_AFFINITY_PINNED
    reuse_strategy: str = "EXACT_HASH_MEMOIZATION"
    incrementality_plan: str = "STATE_DELTA_TRACKING"
    reconstruction_plan: str = "DIRECT_EVALUATION"
    placement: DevicePlacement = DevicePlacement.CPU_AVX2
    verification_method: str = "DOUBLE_EXECUTION_STOCHASTIC"
    fallback_strategy: str = "CANONICAL_REFERENCE"

    transformations: List[TransformationRecord] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    certificate_ids: List[str] = Field(default_factory=list)
    estimated_cost: EstimatedCost = Field(default_factory=EstimatedCost)

    # Verification State
    is_verified: bool = False
    evidence_level: EvidenceLevel = EvidenceLevel.HYPOTHESIS
    created_at: float = Field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
