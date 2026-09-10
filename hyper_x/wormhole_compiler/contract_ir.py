"""
hyper_x/wormhole_compiler/contract_ir.py
=============================================================================
Universal Contract IR (Section 2)
=============================================================================
Defines the authoritative, immutable specification of workload constraints,
observables, invariant assertions, and tolerances.

The engine searches for G' such that:
    O(G'(X)) == O(G(X))
under the declared correctness contract.

Supported Correctness Modes:
    1. EXACT: Identical mathematical output (zero tolerance, preserves shape & dtype)
    2. EXACT_REFORMULATION: Mathematically equivalent representation (e.g., A @ (B @ x))
    3. NUMERICALLY_EQUIVALENT: Bound by strict floating-point numerical error (eps)
    4. BOUNDED_APPROXIMATION: Bounded approximation within declared tolerance (e.g. low-rank, SVD)
    5. PERCEPTUAL_APPROXIMATION: Bound by perceptual metrics (SSIM >= min_ssim, PSNR >= min_psnr)
    6. PREDICTIVE: Speculative computation with verified residual guard and exact fallback
    7. CONTRACT: General contract-level satisfaction over specified observables

RULE: Never automatically downgrade EXACT -> APPROXIMATE without explicit contract permission.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set


class CorrectnessMode(str, enum.Enum):
    EXACT = "EXACT"
    EXACT_REFORMULATION = "EXACT_REFORMULATION"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    BOUNDED_APPROXIMATION = "BOUNDED_APPROXIMATION"
    PERCEPTUAL_APPROXIMATION = "PERCEPTUAL_APPROXIMATION"
    PREDICTIVE = "PREDICTIVE"
    CONTRACT = "CONTRACT"


class CachePolicy(str, enum.Enum):
    COLD = "COLD"
    WARM = "WARM"
    PERSISTENT = "PERSISTENT"


class ExecutionTrack(str, enum.Enum):
    EXACT = "EXACT"
    NUMERICALLY_APPROXIMATE = "NUMERICALLY_APPROXIMATE"
    APPLICATION_CONTRACT = "APPLICATION_CONTRACT"


@dataclass(frozen=True)
class InvariantRule:
    """Formal mathematical invariant that candidate transformations must preserve."""
    name: str
    description: str
    assertion_type: str  # "SHAPE_EQUAL", "FINITE_VALUES", "NORM_BOUND", "ENERGY_CONSERVATION", "RANK_BOUND"
    threshold: float = 0.0


@dataclass
class UniversalWorkloadContract:
    """
    Universal Contract IR encapsulating all execution, numerical, perceptual,
    and provenance constraints for a workload.
    """
    workload_id: str
    operation: str
    correctness_mode: CorrectnessMode
    observable: str = "output_tensor"
    tolerance: float = 0.0
    deterministic: bool = True
    preserve_shape: bool = True
    preserve_dtype: bool = True
    preserve_semantics: bool = True

    # Multi-dimensional resource requirements
    latency_slo_ms: float = 100.0
    throughput_slo: float = 10.0
    memory_limit_mb: float = 4096.0
    energy_budget_joules: Optional[float] = None
    power_limit_watts: Optional[float] = None

    # Perceptual requirements (for PERCEPTUAL_APPROXIMATION mode)
    min_ssim: float = 0.92
    min_psnr_db: float = 28.0

    # Invariants & Permissions
    invariants: List[InvariantRule] = field(default_factory=list)
    acceptable_approximations: List[str] = field(default_factory=list)
    forbidden_approximations: List[str] = field(default_factory=lambda: ["unverified_zeroing", "silent_truncation"])

    # Execution & Reproducibility policy
    cache_policy: CachePolicy = CachePolicy.COLD
    execution_track: ExecutionTrack = ExecutionTrack.APPLICATION_CONTRACT
    require_reproducibility: bool = True
    require_real_hardware: bool = True
    require_provenance: bool = True

    # Hardware target lock
    target_hardware: Dict[str, Any] = field(default_factory=lambda: {
        "cpu": "Intel Core i5-12450H",
        "gpu": "Intel UHD Graphics",
        "ram_gb": 16,
        "isa": ["AVX2", "FMA"]
    })

    def is_exact(self) -> bool:
        return self.correctness_mode in (CorrectnessMode.EXACT, CorrectnessMode.EXACT_REFORMULATION)

    def allows_approximation(self) -> bool:
        return self.correctness_mode in (
            CorrectnessMode.BOUNDED_APPROXIMATION,
            CorrectnessMode.PERCEPTUAL_APPROXIMATION,
            CorrectnessMode.PREDICTIVE,
            CorrectnessMode.CONTRACT
        )

    def validate_transformation(self, proposed_mode: CorrectnessMode) -> bool:
        """
        Enforces: Never downgrade EXACT -> APPROXIMATE without explicit contract permission.
        """
        if self.is_exact() and proposed_mode not in (CorrectnessMode.EXACT, CorrectnessMode.EXACT_REFORMULATION):
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "operation": self.operation,
            "correctness_mode": self.correctness_mode.value,
            "observable": self.observable,
            "tolerance": self.tolerance,
            "deterministic": self.deterministic,
            "preserve_shape": self.preserve_shape,
            "preserve_dtype": self.preserve_dtype,
            "preserve_semantics": self.preserve_semantics,
            "latency_slo_ms": self.latency_slo_ms,
            "memory_limit_mb": self.memory_limit_mb,
            "min_ssim": self.min_ssim,
            "min_psnr_db": self.min_psnr_db,
            "cache_policy": self.cache_policy.value,
            "execution_track": self.execution_track.value,
            "acceptable_approximations": self.acceptable_approximations,
            "forbidden_approximations": self.forbidden_approximations,
        }
