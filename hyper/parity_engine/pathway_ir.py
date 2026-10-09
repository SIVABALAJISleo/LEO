"""
hyper/parity_engine/pathway_ir.py
=================================
Formal Computational Pathway Intermediate Representation (Pathway IR).
Implements Section 8 of the HYPER 100% Master Mission.

A Pathway consists of:
- algorithm
- representation
- memory strategy
- scheduling
- reuse
- incrementality
- reconstruction
- CPU/iGPU placement
- verification
- fallback
"""

from __future__ import annotations
import enum
import json
import uuid
import time
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from .contract_engine import EquivalenceClass, WorkloadContract


class TargetDevicePlacement(str, enum.Enum):
    CPU_ONLY = "CPU_ONLY"
    IGPU_ONLY = "IGPU_ONLY"
    CPU_IGPU_HETEROGENEOUS = "CPU_IGPU_HETEROGENEOUS"
    DYNAMIC_ADAPTIVE = "DYNAMIC_ADAPTIVE"


class TransformationType(str, enum.Enum):
    EXACT_ALGEBRAIC = "EXACT_ALGEBRAIC"
    FACTORIZATION = "FACTORIZATION"
    COMMON_SUBEXPRESSION = "COMMON_SUBEXPRESSION"
    SPARSIFICATION = "SPARSIFICATION"
    LOW_RANK_DECOMPOSITION = "LOW_RANK_DECOMPOSITION"
    TEMPORAL_REUSE = "TEMPORAL_REUSE"
    SPATIAL_RECONSTRUCTION = "SPATIAL_RECONSTRUCTION"
    INCREMENTAL_UPDATE = "INCREMENTAL_UPDATE"
    DIRTY_REGION_COMPACT = "DIRTY_REGION_COMPACT"
    OPERATOR_FUSION = "OPERATOR_FUSION"
    TILING_CACHE_BLOCK = "TILING_CACHE_BLOCK"
    PRECISION_QUANTIZATION = "PRECISION_QUANTIZATION"
    SPECULATIVE_PREDICTION = "SPECULATIVE_PREDICTION"
    WORK_ELIMINATION = "WORK_ELIMINATION"


class TransformationRecord(BaseModel):
    transformation_id: str = Field(default_factory=lambda: f"TX_{uuid.uuid4().hex[:8]}")
    type: TransformationType
    description: str
    assumptions: List[str] = Field(default_factory=list)
    theoretical_speedup: float = 1.0
    information_loss_bound: float = 0.0


class MemoryPlan(BaseModel):
    strategy: str = "ZERO_COPY_UMA"  # UMA unified memory, streaming tiling, compressed cache
    estimated_bytes_allocated: int = 0
    estimated_bytes_transferred: int = 0
    cache_locality_score: float = 1.0
    tiling_block_size: Optional[List[int]] = None
    hot_cold_separation: bool = True


class SchedulerPlan(BaseModel):
    placement: TargetDevicePlacement = TargetDevicePlacement.CPU_ONLY
    num_threads: int = 8
    workload_split_ratio: float = 1.0  # 1.0 = 100% CPU, 0.0 = 100% iGPU
    priority_level: int = 1
    synchronization_frequency: str = "END_OF_TASK"


class VerificationPlan(BaseModel):
    verification_mode: str = "DOUBLE_EXECUTION_AND_FREIVALDS"
    sample_eval_count: int = 5
    adversarial_test_cases: int = 10
    trusted_reference_check: bool = True
    evidence_level_target: str = "VERIFIED"


class FallbackPlan(BaseModel):
    fallback_algorithm: str = "TRUSTED_REFERENCE_BASELINE"
    trigger_conditions: List[str] = Field(
        default_factory=lambda: ["ERROR_BOUND_EXCEEDED", "TIMEOUT_EXCEEDED", "NUMERICAL_INSTABILITY"]
    )
    fallback_cost_multiplier: float = 1.0


class PathwayIR(BaseModel):
    """
    Formal specification of an alternative computational pathway.
    """
    pathway_id: str = Field(default_factory=lambda: f"PTH_{uuid.uuid4().hex[:10]}")
    workload_id: str
    capability_id: str
    contract_id: str
    representation: str = "CIR_GRAPH_DAG"
    algorithm_name: str
    mathematical_basis: str
    equivalence_class: EquivalenceClass = EquivalenceClass.NUMERICALLY_EQUIVALENT

    transformations: List[TransformationRecord] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)

    execution_plan: Dict[str, Any] = Field(default_factory=dict)
    memory_plan: MemoryPlan = Field(default_factory=MemoryPlan)
    scheduler_plan: SchedulerPlan = Field(default_factory=SchedulerPlan)
    verification_plan: VerificationPlan = Field(default_factory=VerificationPlan)
    fallback_plan: FallbackPlan = Field(default_factory=FallbackPlan)

    certificates: List[str] = Field(default_factory=list)  # Certificate IDs
    estimated_cost_ms: float = 1.0
    estimated_work_reduction: float = 0.0  # Fraction [0.0, 1.0]
    estimated_speedup: float = 1.0

    created_at: float = Field(default_factory=time.time)

    def to_yaml_dict(self) -> Dict[str, Any]:
        return {
            "pathway": {
                "id": self.pathway_id,
                "workload": self.workload_id,
                "capability": self.capability_id,
                "contract": self.contract_id,
                "representation": self.representation,
                "algorithm": self.algorithm_name,
                "mathematical_basis": self.mathematical_basis,
                "transformations": [t.model_dump() for t in self.transformations],
                "dependencies": self.dependencies,
                "execution_plan": self.execution_plan,
                "memory_plan": self.memory_plan.model_dump(),
                "scheduler_plan": self.scheduler_plan.model_dump(),
                "verification_plan": self.verification_plan.model_dump(),
                "fallback_plan": self.fallback_plan.model_dump(),
                "certificates": self.certificates,
                "estimated_cost": self.estimated_cost_ms,
                "estimated_work_reduction": self.estimated_work_reduction,
                "estimated_speedup": self.estimated_speedup,
            }
        }
