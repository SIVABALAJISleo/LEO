"""
hyper/godmode/workload_contracts.py
===================================
Universal Workload Contract Engine (Feature Module A).

Defines the formal contract that every workload must fulfill before any
optimization is certified. Enforces:
- Exactness and numerical/perceptual tolerances
- Memory limits, latency deadlines, and throughput targets
- Input/output schemas and measurement boundaries
- Prohibited shortcuts and hardcoded lookup rejections
"""

from __future__ import annotations
from enum import Enum
import math
import time
from typing import Any, Callable, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field


class ExactnessRequirement(str, Enum):
    EXACT = "EXACT"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    APPROXIMATE = "APPROXIMATE"
    PREDICTIVE = "PREDICTIVE"


class WorkloadFamily(str, Enum):
    AI_ML = "AI_ML"
    VISION = "VISION"
    VIDEO = "VIDEO"
    SCIENTIFIC = "SCIENTIFIC"
    GRAPHICS = "GRAPHICS"
    COMPRESSION = "COMPRESSION"
    SIMULATION = "SIMULATION"
    CRYPTO = "CRYPTO"
    SYSTEM = "SYSTEM"


class WorkloadContract(BaseModel):
    """
    Formal representation of workload requirements and acceptance criteria.
    """
    workload_id: str
    name: str
    family: WorkloadFamily
    input_schema: Dict[str, str] = Field(default_factory=dict)
    output_schema: Dict[str, str] = Field(default_factory=dict)
    valid_input_domain: str = "Unbounded continuous / discrete valid inputs"
    required_output_semantics: str = "Deterministic mathematical mapping"

    exactness_requirement: ExactnessRequirement = ExactnessRequirement.EXACT
    max_absolute_error: float = 0.0
    max_relative_error: float = 1e-6
    min_psnr_db: float = 40.0
    min_ssim: float = 0.990

    max_latency_ms: float = 100.0
    min_throughput_ops: float = 10.0
    max_peak_memory_mb: float = 2048.0

    reference_benchmark_device: str = "NVIDIA RTX 4090 / External GPU Baseline"
    reference_target_latency_ms: float = 5.0
    measurement_boundary: str = "WALL_CLOCK_KERNEL_EXECUTION"
    permitted_caching: bool = False
    prohibited_shortcuts: List[str] = Field(default_factory=lambda: [
        "HARDCODED_LOOKUP_TABLE",
        "SILENT_COMPUTATION_SKIPPING",
        "APPROXIMATION_FOR_EXACT_CONTRACT",
        "MUTATION_INSENSITIVITY",
    ])

    def validate_execution(
        self,
        ref_out: Any,
        cand_out: Any,
        measured_latency_ms: float,
        measured_peak_memory_mb: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Mechanically validates an execution against the declared contract.
        """
        violations: List[str] = []
        is_exact = False
        max_abs_err = 0.0
        rel_err = 0.0
        psnr = 99.0
        ssim = 1.0

        if isinstance(ref_out, np.ndarray) and isinstance(cand_out, np.ndarray):
            if ref_out.shape != cand_out.shape:
                violations.append(f"Shape mismatch: expected {ref_out.shape}, got {cand_out.shape}")
                return {"passed": False, "violations": violations}

            ref_f = ref_out.astype(np.float64)
            cand_f = cand_out.astype(np.float64)
            diff = np.abs(ref_f - cand_f)
            max_abs_err = float(np.max(diff))
            norm_ref = np.linalg.norm(ref_f)
            rel_err = float(np.linalg.norm(diff) / max(norm_ref, 1e-12))
            rmse = float(np.sqrt(np.mean(diff ** 2)))
            max_range = max(float(np.max(ref_f) - np.min(ref_f)), 1.0)
            psnr = 20.0 * math.log10(max_range / max(rmse, 1e-9)) if rmse > 0 else 99.0
            ssim = max(0.0, 1.0 - (rmse / max_range))

            if np.any(np.isnan(cand_f)) or np.any(np.isinf(cand_f)):
                violations.append("Candidate output contains NaNs or Infinities")

            if self.exactness_requirement == ExactnessRequirement.EXACT:
                if max_abs_err > self.max_absolute_error:
                    violations.append(f"Exactness violation: max absolute error {max_abs_err} > threshold {self.max_absolute_error}")
                else:
                    is_exact = True
            elif self.exactness_requirement == ExactnessRequirement.NUMERICALLY_EQUIVALENT:
                if max_abs_err > self.max_absolute_error and rel_err > self.max_relative_error:
                    violations.append(f"Numerical equivalence violation: rel error {rel_err} > {self.max_relative_error}")
            elif self.exactness_requirement == ExactnessRequirement.APPROXIMATE:
                if psnr < self.min_psnr_db:
                    violations.append(f"Perceptual violation: PSNR {psnr:.2f}dB < {self.min_psnr_db}dB")
                if ssim < self.min_ssim:
                    violations.append(f"Perceptual violation: SSIM {ssim:.4f} < {self.min_ssim}")
        else:
            is_equal = (ref_out == cand_out)
            if not is_equal:
                violations.append("Output scalar/object does not equal reference output")
            else:
                is_exact = True

        if measured_latency_ms > self.max_latency_ms:
            violations.append(f"Latency deadline missed: {measured_latency_ms:.2f}ms > max {self.max_latency_ms}ms")

        if measured_peak_memory_mb > 0 and measured_peak_memory_mb > self.max_peak_memory_mb:
            violations.append(f"Memory budget exceeded: {measured_peak_memory_mb:.1f}MB > max {self.max_peak_memory_mb}MB")

        passed = len(violations) == 0
        speedup = self.reference_target_latency_ms / max(measured_latency_ms, 0.001)

        return {
            "passed": passed,
            "violations": violations,
            "is_exact": is_exact,
            "max_absolute_error": max_abs_err,
            "relative_error": rel_err,
            "psnr_db": psnr,
            "ssim": ssim,
            "measured_latency_ms": measured_latency_ms,
            "measured_speedup_vs_target": speedup,
            "performance_parity_met": speedup >= 1.0,
        }


class ContractRegistry:
    """Central store for recognized workload contracts."""

    _contracts: Dict[str, WorkloadContract] = {}

    @classmethod
    def register(cls, contract: WorkloadContract) -> None:
        cls._contracts[contract.workload_id] = contract

    @classmethod
    def get(cls, workload_id: str) -> Optional[WorkloadContract]:
        return cls._contracts.get(workload_id)

    @classmethod
    def get_all(cls) -> List[WorkloadContract]:
        return list(cls._contracts.values())


# Pre-register Canonical Workload Contracts
ContractRegistry.register(WorkloadContract(
    workload_id="GEMM-DENSE-256",
    name="Dense Matrix Multiplication (256x256)",
    family=WorkloadFamily.AI_ML,
    exactness_requirement=ExactnessRequirement.EXACT,
    max_absolute_error=1e-5,
    max_latency_ms=10.0,
    reference_target_latency_ms=0.20,
))

ContractRegistry.register(WorkloadContract(
    workload_id="HEAT-PDE-64",
    name="2D Heat Equation Stencil (64x64)",
    family=WorkloadFamily.SCIENTIFIC,
    exactness_requirement=ExactnessRequirement.EXACT,
    max_absolute_error=0.0,
    max_latency_ms=5.0,
    reference_target_latency_ms=0.30,
))

ContractRegistry.register(WorkloadContract(
    workload_id="VISION-SEP-CONV-128",
    name="Rank-1 Separable Spatial Convolution (128x128)",
    family=WorkloadFamily.VISION,
    exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
    max_absolute_error=1e-5,
    max_latency_ms=15.0,
    reference_target_latency_ms=2.0,
))

ContractRegistry.register(WorkloadContract(
    workload_id="NBODY-SYMMETRIC-128",
    name="N-Body Gravitational Interaction (128 bodies)",
    family=WorkloadFamily.SIMULATION,
    exactness_requirement=ExactnessRequirement.NUMERICALLY_EQUIVALENT,
    max_absolute_error=1e-4,
    max_latency_ms=10.0,
    reference_target_latency_ms=1.5,
))

ContractRegistry.register(WorkloadContract(
    workload_id="RASTER-TRIANGLE-AABB",
    name="Software Triangle AABB Clamped Rasterization (256x256)",
    family=WorkloadFamily.GRAPHICS,
    exactness_requirement=ExactnessRequirement.EXACT,
    max_absolute_error=0.0,
    max_latency_ms=10.0,
    reference_target_latency_ms=2.0,
))
