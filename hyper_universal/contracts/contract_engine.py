"""
hyper_universal/contracts/contract_engine.py
Formal workload contract engine defining immutable specifications, exactness classes,
numerical tolerances, resource budgets, and verification criteria.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np


class ExactnessRequirement(str, Enum):
    BITWISE_EXACT = "BITWISE_EXACT"
    EXACT_INTEGER_SYMBOLIC = "EXACT_INTEGER_SYMBOLIC"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    APPROXIMATE_BOUNDED = "APPROXIMATE_BOUNDED"
    APPROXIMATE_WITH_TOLERANCE = "APPROXIMATE_BOUNDED"
    APPLICATION_CONTRACT_EQUIVALENT = "APPLICATION_CONTRACT_EQUIVALENT"
    PROBABILISTIC_BOUNDED = "PROBABILISTIC_BOUNDED"


class BackendTarget(str, Enum):
    CPU_AVX2 = "CPU_AVX2"
    INTEL_UHD_IGPU_OPENCL = "INTEL_UHD_IGPU_OPENCL"
    INTEL_UHD_IGPU_VULKAN = "INTEL_UHD_IGPU_VULKAN"
    HYBRID_CPU_IGPU = "HYBRID_CPU_IGPU"
    CPU_STREAMING = "CPU_STREAMING"
    CPU_FALLBACK = "CPU_FALLBACK"


@dataclass(frozen=True)
class NumericalTolerance:
    max_relative_error: float = 1e-5
    max_absolute_error: float = 1e-5
    min_snr_db: float = 60.0
    min_ssim: float = 0.98
    confidence_level: float = 0.99  # For probabilistic verification

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_relative_error": self.max_relative_error,
            "max_absolute_error": self.max_absolute_error,
            "min_snr_db": self.min_snr_db,
            "min_ssim": self.min_ssim,
            "confidence_level": self.confidence_level,
        }


@dataclass(frozen=True)
class ResourceBudget:
    max_ram_bytes: int = 4 * 1024 * 1024 * 1024  # 4 GB max default budget
    max_latency_ms: Optional[float] = 5000.0     # 5 second SLA
    max_disk_spill_bytes: int = 16 * 1024 * 1024 * 1024  # 16 GB SSD spill budget
    max_candidates_to_evaluate: int = 10
    max_memory_mb: Optional[float] = None
    latency_deadline_ms: Optional[float] = None

    def __post_init__(self):
        if self.max_memory_mb is not None:
            object.__setattr__(self, "max_ram_bytes", int(self.max_memory_mb * 1024 * 1024))
        if self.latency_deadline_ms is not None:
            object.__setattr__(self, "max_latency_ms", self.latency_deadline_ms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_ram_bytes": self.max_ram_bytes,
            "max_memory_mb": round(self.max_ram_bytes / (1024 * 1024), 2),
            "max_latency_ms": self.max_latency_ms,
            "max_disk_spill_bytes": self.max_disk_spill_bytes,
            "max_candidates_to_evaluate": self.max_candidates_to_evaluate,
        }


@dataclass
class UniversalContract:
    workload_id: str
    version: str = "1.0.0"
    workload_name: str = ""
    family: str = "GENERAL"
    category: str = "GENERAL"
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    exactness: ExactnessRequirement = ExactnessRequirement.NUMERICALLY_EQUIVALENT
    tolerances: NumericalTolerance = field(default_factory=NumericalTolerance)
    budget: ResourceBudget = field(default_factory=ResourceBudget)
    allowed_backends: Tuple[BackendTarget, ...] = (BackendTarget.CPU_AVX2, BackendTarget.CPU_FALLBACK)
    verification_strategy: str = "differential_reference"
    fallback_backend: str = "CPU_AVX2"
    allow_out_of_core_streaming: bool = True
    allow_quantization: bool = False
    allow_lossy_compression: bool = False
    contract_hash: str = field(default="", init=False)

    # Aliases for flexible constructor kwargs
    exactness_requirement: Optional[ExactnessRequirement] = None
    tolerance: Optional[NumericalTolerance] = None
    resource_budget: Optional[ResourceBudget] = None

    def __post_init__(self):
        if self.exactness_requirement is not None:
            self.exactness = self.exactness_requirement
        else:
            self.exactness_requirement = self.exactness

        if self.tolerance is not None:
            self.tolerances = self.tolerance
        else:
            self.tolerance = self.tolerances

        if self.resource_budget is not None:
            self.budget = self.resource_budget
        else:
            self.resource_budget = self.budget

        payload = {
            "workload_id": self.workload_id,
            "version": self.version,
            "exactness": self.exactness.value,
            "rel_err": self.tolerances.max_relative_error,
            "abs_err": self.tolerances.max_absolute_error,
            "min_ssim": self.tolerances.min_ssim,
            "max_ram_bytes": self.budget.max_ram_bytes,
            "max_latency_ms": self.budget.max_latency_ms,
        }
        h = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        self.contract_hash = h

    def validate_candidate_output(
        self, reference: Any, candidate: Any
    ) -> Tuple[bool, float, float, str]:
        """
        Validates candidate output strictly against reference under this immutable contract.
        Returns: (is_valid, max_relative_error, max_absolute_error, reason)
        """
        if candidate is None:
            return False, float("inf"), float("inf"), "Candidate produced None output"

        # Check for NaN / Inf
        if isinstance(candidate, np.ndarray):
            if np.isnan(candidate).any() or np.isinf(candidate).any():
                return False, float("inf"), float("inf"), "Candidate output contains NaN or Inf"

        # 1. Bitwise Exact Mode
        if self.exactness == ExactnessRequirement.BITWISE_EXACT:
            if isinstance(reference, np.ndarray) and isinstance(candidate, np.ndarray):
                if reference.shape != candidate.shape:
                    return False, float("inf"), float("inf"), f"Shape mismatch: {reference.shape} vs {candidate.shape}"
                is_equal = np.array_equal(reference, candidate)
                diff = float(np.max(np.abs(reference - candidate))) if is_equal or reference.shape == candidate.shape else float("inf")
                return is_equal, diff, diff, "Bitwise identical" if is_equal else f"Bitwise mismatch (diff={diff:.6e})"
            is_equal = (reference == candidate)
            return is_equal, 0.0 if is_equal else 1.0, 0.0 if is_equal else 1.0, "Bitwise identical" if is_equal else "Bitwise mismatch"

        # 2. Exact Integer / Symbolic Mode
        if self.exactness == ExactnessRequirement.EXACT_INTEGER_SYMBOLIC:
            if isinstance(reference, np.ndarray) and isinstance(candidate, np.ndarray):
                if reference.shape != candidate.shape:
                    return False, 1.0, 1.0, f"Shape mismatch: {reference.shape} vs {candidate.shape}"
                is_equal = np.array_equal(reference, candidate)
                return is_equal, 0.0 if is_equal else 1.0, 0.0 if is_equal else 1.0, "Symbolic match" if is_equal else "Symbolic mismatch"
            is_equal = (reference == candidate)
            return is_equal, 0.0 if is_equal else 1.0, 0.0 if is_equal else 1.0, "Symbolic match" if is_equal else "Symbolic mismatch"

        # 3. Numerical Equivalence & Bounded Modes
        if isinstance(reference, np.ndarray) and isinstance(candidate, np.ndarray):
            if reference.shape != candidate.shape:
                return False, 1.0, 1.0, f"Shape mismatch: {reference.shape} vs {candidate.shape}"

            abs_err = np.abs(reference - candidate)
            max_abs = float(np.max(abs_err))
            ref_max = float(np.max(np.abs(reference)))
            scale = ref_max if ref_max > 0.0 else 1.0
            max_rel = float(max_abs / scale)

            passed_rel = max_rel <= self.tolerances.max_relative_error
            passed_abs = max_abs <= self.tolerances.max_absolute_error

            if self.exactness in [ExactnessRequirement.NUMERICALLY_EQUIVALENT, ExactnessRequirement.APPLICATION_CONTRACT_EQUIVALENT]:
                is_valid = bool(passed_rel and passed_abs)
                reason = "Numerically equivalent within declared bounds" if is_valid else (
                    f"Output exceeds contract tolerance: rel={max_rel:.5e} (limit {self.tolerances.max_relative_error:.5e}), "
                    f"abs={max_abs:.5e} (limit {self.tolerances.max_absolute_error:.5e})"
                )
                return is_valid, max_rel, max_abs, reason

            if self.exactness in [ExactnessRequirement.APPROXIMATE_BOUNDED, ExactnessRequirement.APPROXIMATE_WITH_TOLERANCE]:
                is_valid = bool(passed_rel and passed_abs)
                reason = "Within approximation budget" if is_valid else (
                    f"Output exceeds contract tolerance: rel={max_rel:.4f} (limit {self.tolerances.max_relative_error:.4f}), "
                    f"abs={max_abs:.4f} (limit {self.tolerances.max_absolute_error:.4f})"
                )
                return is_valid, max_rel, max_abs, reason

        # Scalar numerical comparison
        try:
            diff = abs(float(reference) - float(candidate))
            ref_val = abs(float(reference))
            scale = ref_val if ref_val > 0.0 else 1.0
            rel_err = diff / scale
            is_valid = bool(rel_err <= self.tolerances.max_relative_error and diff <= self.tolerances.max_absolute_error)
            return is_valid, rel_err, diff, "Scalar verified" if is_valid else f"Output exceeds contract tolerance: rel={rel_err:.4e}"
        except Exception as e:
            if isinstance(reference, np.ndarray) or isinstance(candidate, np.ndarray):
                return False, 1.0, 1.0, f"Comparison error: {e}"
            is_equal = bool(reference == candidate)
            return is_equal, 0.0 if is_equal else 1.0, 0.0 if is_equal else 1.0, str(e)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "version": self.version,
            "category": self.category,
            "description": self.description,
            "exactness": self.exactness.value,
            "exactness_requirement": self.exactness.value,
            "tolerances": self.tolerances.to_dict(),
            "budget": self.budget.to_dict(),
            "contract_hash": self.contract_hash,
            "verification_strategy": self.verification_strategy,
            "fallback_backend": self.fallback_backend,
        }


def differential_contract_verify(
    contract: UniversalContract, candidate: Any, reference: Any
) -> Tuple[bool, float, float, str]:
    """Top-level helper for contract validation (candidate against reference)."""
    return contract.validate_candidate_output(reference=reference, candidate=candidate)


class ContractRegistry:
    """Central store for formally registered workload contracts."""

    def __init__(self):
        self._contracts: Dict[str, UniversalContract] = {}
        self._register_default_contracts()

    def register(self, contract: UniversalContract) -> None:
        self._contracts[contract.workload_id] = contract

    def get(self, workload_id: str) -> Optional[UniversalContract]:
        return self._contracts.get(workload_id)

    def list_contracts(self) -> List[UniversalContract]:
        return list(self._contracts.values())

    def _register_default_contracts(self) -> None:
        defaults = [
            UniversalContract(
                workload_id="dense_gemm_512x512",
                category="linear_algebra",
                description="Dense Matrix Multiplication FP32 (512x512)",
                input_schema={"shape": [512, 512], "dtype": "float32"},
                output_schema={"shape": [512, 512], "dtype": "float32"},
                exactness=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
                tolerances=NumericalTolerance(max_relative_error=1e-4, max_absolute_error=1e-4),
                budget=ResourceBudget(max_ram_bytes=512 * 1024 * 1024, max_latency_ms=2000.0),
            ),
            UniversalContract(
                workload_id="fft_spectral_1024",
                category="signal_processing",
                description="1D Spectral FFT 1024-point complex",
                input_schema={"shape": [1024], "dtype": "complex64"},
                output_schema={"shape": [1024], "dtype": "complex64"},
                exactness=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
                tolerances=NumericalTolerance(max_relative_error=1e-5, max_absolute_error=1e-5),
                budget=ResourceBudget(max_ram_bytes=128 * 1024 * 1024, max_latency_ms=500.0),
            ),
            UniversalContract(
                workload_id="sorting_keys_1m",
                category="algorithms",
                description="Bitwise exact key sort",
                input_schema={"shape": [1_000_000], "dtype": "int32"},
                output_schema={"shape": [1_000_000], "dtype": "int32"},
                exactness=ExactnessRequirement.BITWISE_EXACT,
                tolerances=NumericalTolerance(max_relative_error=0.0, max_absolute_error=0.0),
                budget=ResourceBudget(max_ram_bytes=256 * 1024 * 1024, max_latency_ms=1000.0),
            ),
            UniversalContract(
                workload_id="sparse_spmv_1000",
                category="linear_algebra",
                description="Sparse Matrix Vector Multiplication (1000x1000, 95% sparse)",
                input_schema={"shape": [1000, 1000], "dtype": "float32"},
                output_schema={"shape": [1000], "dtype": "float32"},
                exactness=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
                tolerances=NumericalTolerance(max_relative_error=1e-5, max_absolute_error=1e-5),
                budget=ResourceBudget(max_ram_bytes=64 * 1024 * 1024, max_latency_ms=500.0),
            ),
        ]
        for c in defaults:
            self.register(c)
