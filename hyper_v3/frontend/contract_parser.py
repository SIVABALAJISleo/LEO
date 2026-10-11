"""
hyper_v3/frontend/contract_parser.py
Formal immutable contract specification, parser, and validator for HYPER 3.0.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import hashlib
import json


class ExecutionTrack(Enum):
    EXACT = "track_a_exact"
    CONTRACT_AWARE = "track_b_contract_aware"


class ExactnessClass(Enum):
    BITWISE_EXACT = "BITWISE_EXACT"
    NUMERICALLY_EXACT_UNDER_DEFINED_MODEL = "NUMERICALLY_EXACT_UNDER_DEFINED_MODEL"
    MATHEMATICALLY_EQUIVALENT = "MATHEMATICALLY_EQUIVALENT"
    CONTRACT_EQUIVALENT = "CONTRACT_EQUIVALENT"
    APPROXIMATE = "APPROXIMATE"
    PREDICTIVE = "PREDICTIVE"


class PrecisionTarget(Enum):
    FP64 = "FP64"
    FP32 = "FP32"
    FP16 = "FP16"
    BF16 = "BF16"
    INT8 = "INT8"
    TERNARY = "TERNARY"


@dataclass(frozen=True)
class ExecutionContract:
    """Immutable execution contract defining exact mathematical bounds and permissions."""
    contract_id: str
    workload_name: str
    track: ExecutionTrack
    exactness_class: ExactnessClass = ExactnessClass.BITWISE_EXACT
    allow_low_rank: bool = False
    allow_sparsity: bool = False
    allow_temporal_reuse: bool = False
    allow_spatial_reuse: bool = False
    allow_adaptive_sampling: bool = False
    allow_early_termination: bool = False
    allow_representation_transform: bool = False
    allow_reduced_precision: bool = False
    precision_target: PrecisionTarget = PrecisionTarget.FP32
    max_relative_error: float = 0.0
    max_absolute_error: float = 0.0
    min_snr_db: float = 100.0
    min_ssim: float = 1.0
    max_latency_ms: Optional[float] = None
    target_devices: List[str] = field(default_factory=lambda: ["CPU", "iGPU"])
    contract_hash: str = field(default="", init=False)

    def __post_init__(self):
        data = {
            "id": self.contract_id,
            "workload": self.workload_name,
            "track": self.track.value,
            "exactness": self.exactness_class.value,
            "low_rank": self.allow_low_rank,
            "sparsity": self.allow_sparsity,
            "temporal": self.allow_temporal_reuse,
            "spatial": self.allow_spatial_reuse,
            "adaptive": self.allow_adaptive_sampling,
            "early_term": self.allow_early_termination,
            "rep_transform": self.allow_representation_transform,
            "red_prec": self.allow_reduced_precision,
            "prec": self.precision_target.value,
            "rel_err": self.max_relative_error,
            "abs_err": self.max_absolute_error,
            "snr": self.min_snr_db,
            "ssim": self.min_ssim
        }
        h = hashlib.sha256(json.dumps(data, sort_keys=True).encode("utf-8")).hexdigest()
        object.__setattr__(self, "contract_hash", h)


WORKLOAD_CONTRACT_PROFILES: Dict[str, Dict[str, Any]] = {
    "dense_gemm_fp32": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.NUMERICALLY_EXACT_UNDER_DEFINED_MODEL,
        "allow_low_rank": True,
        "allow_sparsity": False,
        "allow_representation_transform": False,
    },
    "dense_gemm_fp16": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.NUMERICALLY_EXACT_UNDER_DEFINED_MODEL,
        "allow_sparsity": True,
        "allow_low_rank": False,
        "allow_representation_transform": False,
    },
    "fft_1d": {
        "max_relative_error": 1e-4,
        "max_absolute_error": 1e-4,
        "min_snr_db": 60.0,
        "exactness_class": ExactnessClass.MATHEMATICALLY_EQUIVALENT,
        "allow_sparsity": True,
    },
    "vector_reduction": {
        "max_relative_error": 1e-5,
        "max_absolute_error": 1e-5,
        "exactness_class": ExactnessClass.NUMERICALLY_EXACT_UNDER_DEFINED_MODEL,
        "allow_spatial_reuse": True,
    },
    "batch1_ai": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_reduced_precision": True,
        "precision_target": PrecisionTarget.TERNARY,
    },
    "batched_ai": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_spatial_reuse": True,
    },
    "semantic_query": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.APPROXIMATE,
        "allow_adaptive_sampling": True,
    },
    "rasterization": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "min_ssim": 0.98,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_spatial_reuse": True,
    },
    "particle_physics": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_temporal_reuse": True,
    },
    "bvh_hierarchy": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_representation_transform": False,
    },
    "path_tracing": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "min_ssim": 0.95,
        "exactness_class": ExactnessClass.APPROXIMATE,
        "allow_adaptive_sampling": True,
    },
    "video_pipeline": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "min_ssim": 0.98,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_representation_transform": True,
    },
    "nbody_simulation": {
        "max_relative_error": 0.05,
        "max_absolute_error": 0.05,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_adaptive_sampling": True,
    },
    "monte_carlo": {
        "max_relative_error": 0.05,
        "max_absolute_error": 1.0,
        "exactness_class": ExactnessClass.PREDICTIVE,
        "allow_early_termination": True,
    },
    "viewport_transform": {
        "max_relative_error": 0.01,
        "max_absolute_error": 0.01,
        "exactness_class": ExactnessClass.CONTRACT_EQUIVALENT,
        "allow_spatial_reuse": True,
    },
}


class ContractParser:
    """Parses, freezes, and validates execution contracts."""

    @staticmethod
    def create_exact_contract(workload_name: str) -> ExecutionContract:
        """Create a strict bit-exact Track A contract."""
        return ExecutionContract(
            contract_id=f"exact_{workload_name}",
            workload_name=workload_name,
            track=ExecutionTrack.EXACT,
            exactness_class=ExactnessClass.BITWISE_EXACT,
            allow_low_rank=False,
            allow_sparsity=False,
            allow_temporal_reuse=False,
            allow_spatial_reuse=False,
            allow_adaptive_sampling=False,
            allow_early_termination=False,
            allow_representation_transform=False,
            allow_reduced_precision=False,
            precision_target=PrecisionTarget.FP32,
            max_relative_error=1e-5,
            max_absolute_error=1e-5,
            min_snr_db=120.0,
            min_ssim=1.0
        )

    @staticmethod
    def create_contract_aware_contract(
        workload_name: str,
        allow_low_rank: Optional[bool] = None,
        allow_sparsity: Optional[bool] = None,
        allow_temporal_reuse: Optional[bool] = None,
        allow_spatial_reuse: Optional[bool] = None,
        allow_adaptive_sampling: Optional[bool] = None,
        allow_early_termination: Optional[bool] = None,
        allow_representation_transform: Optional[bool] = None,
        allow_reduced_precision: Optional[bool] = None,
        precision_target: Optional[PrecisionTarget] = None,
        max_relative_error: Optional[float] = None,
        max_absolute_error: Optional[float] = None,
        min_snr_db: Optional[float] = None,
        min_ssim: Optional[float] = None,
        exactness_class: Optional[ExactnessClass] = None,
    ) -> ExecutionContract:
        """Create a contract-aware Track B contract with workload-specific bounds."""
        profile = WORKLOAD_CONTRACT_PROFILES.get(workload_name, {})

        return ExecutionContract(
            contract_id=f"contract_aware_{workload_name}",
            workload_name=workload_name,
            track=ExecutionTrack.CONTRACT_AWARE,
            exactness_class=exactness_class or profile.get("exactness_class", ExactnessClass.CONTRACT_EQUIVALENT),
            allow_low_rank=allow_low_rank if allow_low_rank is not None else profile.get("allow_low_rank", False),
            allow_sparsity=allow_sparsity if allow_sparsity is not None else profile.get("allow_sparsity", False),
            allow_temporal_reuse=allow_temporal_reuse if allow_temporal_reuse is not None else profile.get("allow_temporal_reuse", False),
            allow_spatial_reuse=allow_spatial_reuse if allow_spatial_reuse is not None else profile.get("allow_spatial_reuse", False),
            allow_adaptive_sampling=allow_adaptive_sampling if allow_adaptive_sampling is not None else profile.get("allow_adaptive_sampling", False),
            allow_early_termination=allow_early_termination if allow_early_termination is not None else profile.get("allow_early_termination", False),
            allow_representation_transform=allow_representation_transform if allow_representation_transform is not None else profile.get("allow_representation_transform", False),
            allow_reduced_precision=allow_reduced_precision if allow_reduced_precision is not None else profile.get("allow_reduced_precision", False),
            precision_target=precision_target or profile.get("precision_target", PrecisionTarget.FP32),
            max_relative_error=max_relative_error if max_relative_error is not None else profile.get("max_relative_error", 0.05),
            max_absolute_error=max_absolute_error if max_absolute_error is not None else profile.get("max_absolute_error", 0.05),
            min_snr_db=min_snr_db if min_snr_db is not None else profile.get("min_snr_db", 40.0),
            min_ssim=min_ssim if min_ssim is not None else profile.get("min_ssim", 0.98),
        )

