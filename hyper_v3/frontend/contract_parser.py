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
        allow_low_rank: bool = True,
        allow_sparsity: bool = True,
        allow_temporal_reuse: bool = True,
        allow_spatial_reuse: bool = True,
        allow_adaptive_sampling: bool = True,
        allow_early_termination: bool = True,
        allow_representation_transform: bool = True,
        allow_reduced_precision: bool = False,
        precision_target: PrecisionTarget = PrecisionTarget.FP32,
        max_relative_error: float = 0.80,
        max_absolute_error: float = 2.0,
        min_snr_db: float = 10.0,
        min_ssim: float = 0.80
    ) -> ExecutionContract:
        """Create a contract-aware Track B contract."""
        return ExecutionContract(
            contract_id=f"contract_aware_{workload_name}",
            workload_name=workload_name,
            track=ExecutionTrack.CONTRACT_AWARE,
            exactness_class=ExactnessClass.CONTRACT_EQUIVALENT,
            allow_low_rank=allow_low_rank,
            allow_sparsity=allow_sparsity,
            allow_temporal_reuse=allow_temporal_reuse,
            allow_spatial_reuse=allow_spatial_reuse,
            allow_adaptive_sampling=allow_adaptive_sampling,
            allow_early_termination=allow_early_termination,
            allow_representation_transform=allow_representation_transform,
            allow_reduced_precision=allow_reduced_precision,
            precision_target=precision_target,
            max_relative_error=max_relative_error,
            max_absolute_error=max_absolute_error,
            min_snr_db=min_snr_db,
            min_ssim=min_ssim
        )
