"""
hyper/discovery/pathway_ir.py
==============================
Pathway Intermediate Representation (Pathway IR) for HYPER.

A Pathway in HYPER is a complete holistic execution specification:
  Algorithm
  + Data Representation
  + Memory Strategy
  + Scheduling
  + Reuse
  + Incrementality
  + Execution Placement
  + Verification
  + Fallback Plan
"""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.discovery.capability_decomposer import CapabilityFamily
from hyper.universal.contracts.universal_contract import UniversalContract, ContractCorrectness


class ExecutionDevice(str, Enum):
    CPU_AVX2 = "CPU_AVX2"
    IGPU_VULKAN = "IGPU_VULKAN"
    IGPU_DIRECTML = "IGPU_DIRECTML"
    HYBRID_CPU_IGPU = "HYBRID_CPU_IGPU"
    CPU_SCALAR_FALLBACK = "CPU_SCALAR_FALLBACK"


class MemoryStrategy(str, Enum):
    ZERO_COPY_UNIFIED = "ZERO_COPY_UNIFIED"
    BLOCKED_CACHE_TILING = "BLOCKED_CACHE_TILING"
    COMPRESSED_LAYOUT = "COMPRESSED_LAYOUT"
    TRANSIENT_STREAMING = "TRANSIENT_STREAMING"
    SHARED_MEMORY_BANKED = "SHARED_MEMORY_BANKED"


class SchedulingStrategy(str, Enum):
    SYNCHRONOUS = "SYNCHRONOUS"
    ASYNC_PIPELINED = "ASYNC_PIPELINED"
    WORK_STEALING = "WORK_STEALING"
    DOUBLE_BUFFERED = "DOUBLE_BUFFERED"


class TransformationStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step-{uuid.uuid4().hex[:6]}")
    name: str
    category: str  # MATHEMATICAL, COMPILER, RUNTIME, MEMORY, TEMPORAL, GRAPHICS, AI
    description: str
    estimated_work_reduction_pct: float = 0.0
    preconditions: List[str] = Field(default_factory=list)
    postconditions: List[str] = Field(default_factory=list)


class ExecutionPlan(BaseModel):
    primary_device: ExecutionDevice = ExecutionDevice.CPU_AVX2
    offload_ratio_igpu: float = 0.0  # 0.0 = 100% CPU, 1.0 = 100% iGPU
    thread_count: int = 8
    vector_width_bits: int = 256  # AVX2 default


class MemoryPlan(BaseModel):
    strategy: MemoryStrategy = MemoryStrategy.BLOCKED_CACHE_TILING
    tile_size_bytes: int = 32768  # 32KB L1 cache tile
    use_unified_wormhole: bool = True
    compression_enabled: bool = False
    estimated_peak_memory_mb: float = 64.0


class SchedulingPlan(BaseModel):
    strategy: SchedulingStrategy = SchedulingStrategy.SYNCHRONOUS
    pipeline_stages: int = 1
    prefetch_distance: int = 2


class VerificationPlan(BaseModel):
    target_correctness: ContractCorrectness = ContractCorrectness.EXACT
    max_absolute_error_tolerance: float = 1e-6
    max_relative_error_tolerance: float = 1e-5
    run_adversarial_gauntlet: bool = True
    adversarial_sample_count: int = 50
    minimum_ssim_score: float = 0.95
    minimum_psnr_score: float = 35.0


class FallbackPlan(BaseModel):
    fallback_device: ExecutionDevice = ExecutionDevice.CPU_SCALAR_FALLBACK
    fallback_strategy: str = "CANONICAL_REFERENCE"
    trigger_conditions: List[str] = Field(
        default_factory=lambda: ["NUMERICAL_DIVERGENCE", "UNCAUGHT_EXCEPTION", "TIMEOUT_EXCEEDED"]
    )
    fallback_penalty_cost_ms: float = 10.0


class PathwayCostEstimate(BaseModel):
    estimated_latency_ms: float = 1.0
    estimated_throughput_ops_sec: float = 1000.0
    estimated_memory_bandwidth_gb_s: float = 5.0
    estimated_ram_mb: float = 64.0
    estimated_power_watts: float = 15.0
    fallback_probability: float = 0.001


class PathwayIR(BaseModel):
    """
    Holistic intermediate representation of an algorithmic and execution pathway.
    """
    pathway_id: str = Field(default_factory=lambda: f"pw-{uuid.uuid4().hex[:8]}")
    workload_id: str
    capability_family: CapabilityFamily = CapabilityFamily.GENERAL_COMPUTE
    contract: UniversalContract
    transformations: List[TransformationStep] = Field(default_factory=list)
    execution_plan: ExecutionPlan = Field(default_factory=ExecutionPlan)
    memory_plan: MemoryPlan = Field(default_factory=MemoryPlan)
    scheduling_plan: SchedulingPlan = Field(default_factory=SchedulingPlan)
    verification_plan: VerificationPlan = Field(default_factory=VerificationPlan)
    fallback_plan: FallbackPlan = Field(default_factory=FallbackPlan)
    cost_estimate: PathwayCostEstimate = Field(default_factory=PathwayCostEstimate)

    is_verified: bool = False
    verification_status: str = "UNVERIFIED"
    certificate_id: Optional[str] = None
    created_at: float = Field(default_factory=time.time)

    def summary(self) -> Dict[str, Any]:
        return {
            "pathway_id": self.pathway_id,
            "workload_id": self.workload_id,
            "family": self.capability_family.value,
            "transformations": [t.name for t in self.transformations],
            "device": self.execution_plan.primary_device.value,
            "memory_strategy": self.memory_plan.strategy.value,
            "scheduling": self.scheduling_plan.strategy.value,
            "cost_latency_ms": self.cost_estimate.estimated_latency_ms,
            "verified": self.is_verified,
        }
