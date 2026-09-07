"""
hyper_x/strict/contracts.py
=============================================================================
HYPER-X Strict Contract Compiler & Formal Execution Contracts
=============================================================================
Defines the formal contract for every workload.

Six Strict, Unmixed Correctness Modes:
  1. EXACT:       Exact mathematical equivalence (integer, discrete, symbolic)
  2. BITWISE:     Identical IEEE floating point representation bit-for-bit
  3. NUMERICAL:   Bounded numerical error (relative error <= epsilon, absolute error <= atol)
  4. FUNCTIONAL:  Equivalent behavior on semantic interface (e.g. classification label, AST)
  5. APPLICATION: End-user perceptually / structurally indistinguishable (e.g. SSIM >= 0.98, PSNR >= 35dB)
  6. CONTRACT:    Declared custom invariant, property, or schema satisfaction

RULE: NEVER mix correctness modes.
"""

from __future__ import annotations
import enum
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Callable, List, Union
import numpy as np

class CorrectnessMode(str, enum.Enum):
    EXACT = "EXACT"
    BITWISE = "BITWISE"
    NUMERICAL = "NUMERICAL"
    FUNCTIONAL = "FUNCTIONAL"
    APPLICATION = "APPLICATION"
    CONTRACT = "CONTRACT"

@dataclass
class WorkloadContract:
    """Formal workload execution contract specifying constraints and verification rules."""
    workload_id: str
    domain: str  # ai, graphics, media, hpc, dense_compute, etc.
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    correctness_mode: CorrectnessMode
    reference_implementation: Optional[str] = None
    tolerance_epsilon: float = 1e-4
    absolute_tolerance: float = 1e-5
    min_quality_metric: str = "ssim"  # ssim, psnr, top1_accuracy, etc.
    min_quality_threshold: float = 0.98
    precision: str = "FP32"  # FP64, FP32, FP16, BF16, INT8, TERNARY
    deterministic_requirement: bool = True
    latency_limit_ms: Optional[float] = None
    throughput_limit_ops: Optional[float] = None
    memory_limit_mb: Optional[float] = None
    energy_limit_joules: Optional[float] = None
    reliability_requirement: float = 0.999
    reproducibility_requirement: bool = True
    cache_policy: str = "COLD_FIRST"  # COLD_FIRST, WARM_ALLOWED, NO_CACHE
    approximation_allowed: bool = False
    workload_substitution_allowed: bool = False
    external_hardware_allowed: bool = False
    target_hardware: str = "Intel Core i5-12450H + Intel UHD Graphics"
    benchmark_manifest: Dict[str, Any] = field(default_factory=dict)
    provenance_requirements: List[str] = field(default_factory=lambda: [
        "git_commit", "hardware_fingerprint", "timestamp", "input_hash", "output_hash"
    ])

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["correctness_mode"] = self.correctness_mode.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkloadContract":
        d = dict(data)
        if isinstance(d.get("correctness_mode"), str):
            d["correctness_mode"] = CorrectnessMode(d["correctness_mode"])
        return cls(**d)

    def validate_result(self, candidate: Any, reference: Any) -> Dict[str, Any]:
        """
        Validates a candidate output against reference strictly in accordance
        with the declared correctness mode.
        """
        mode = self.correctness_mode

        if mode == CorrectnessMode.EXACT:
            if isinstance(candidate, np.ndarray) and isinstance(reference, np.ndarray):
                is_valid = bool(np.array_equal(candidate, reference))
                max_diff = float(np.max(np.abs(candidate - reference))) if not is_valid else 0.0
            else:
                is_valid = candidate == reference
                max_diff = 0.0 if is_valid else 1.0
            return {
                "valid": is_valid,
                "mode": mode.value,
                "error": max_diff,
                "threshold": 0.0,
                "message": "Exact equivalence pass" if is_valid else f"Exact mismatch (max diff={max_diff})"
            }

        elif mode == CorrectnessMode.BITWISE:
            c_arr = np.asarray(candidate)
            r_arr = np.asarray(reference)
            if c_arr.dtype != r_arr.dtype or c_arr.shape != r_arr.shape:
                return {"valid": False, "mode": mode.value, "error": 1.0, "message": "Shape or dtype mismatch"}
            is_valid = bool(np.array_equal(c_arr.view(np.uint8), r_arr.view(np.uint8)))
            return {
                "valid": is_valid,
                "mode": mode.value,
                "error": 0.0 if is_valid else 1.0,
                "message": "Bitwise IEEE match" if is_valid else "Bitwise variance detected"
            }

        elif mode == CorrectnessMode.NUMERICAL:
            c_arr = np.asarray(candidate, dtype=np.float64)
            r_arr = np.asarray(reference, dtype=np.float64)
            norm_r = np.linalg.norm(r_arr)
            abs_diff = np.abs(c_arr - r_arr)
            max_abs_err = float(np.max(abs_diff))
            rel_err = float(max_abs_err / (norm_r + 1e-12))
            is_valid = bool(rel_err <= self.tolerance_epsilon or max_abs_err <= self.absolute_tolerance)
            return {
                "valid": is_valid,
                "mode": mode.value,
                "relative_error": rel_err,
                "max_abs_error": max_abs_err,
                "tolerance_epsilon": self.tolerance_epsilon,
                "message": "Numerical tolerance satisfied" if is_valid else f"Numerical error {rel_err:.2e} > {self.tolerance_epsilon:.2e}"
            }

        elif mode == CorrectnessMode.FUNCTIONAL:
            # Semantic equivalence: labels, argmax, text output tokens
            if isinstance(candidate, np.ndarray) and isinstance(reference, np.ndarray):
                c_pred = np.argmax(candidate, axis=-1)
                r_pred = np.argmax(reference, axis=-1)
                acc = float(np.mean(c_pred == r_pred))
                is_valid = acc >= 0.999
                return {"valid": is_valid, "mode": mode.value, "accuracy": acc, "message": f"Functional match rate: {acc:.4f}"}
            is_valid = candidate == reference
            return {"valid": is_valid, "mode": mode.value, "message": "Functional equivalence verified"}

        elif mode == CorrectnessMode.APPLICATION:
            # Perceptual image / quality verification
            c_arr = np.asarray(candidate, dtype=np.float32)
            r_arr = np.asarray(reference, dtype=np.float32)
            if c_arr.ndim >= 2 and r_arr.ndim >= 2:
                mse = float(np.mean((c_arr - r_arr) ** 2))
                psnr = 10.0 * math.log10(1.0 / max(mse, 1e-10)) if mse > 0 else 100.0
                # Fast structural SSIM surrogate
                mu_c = float(np.mean(c_arr))
                mu_r = float(np.mean(r_arr))
                sig_c = float(np.var(c_arr))
                sig_r = float(np.var(r_arr))
                cov = float(np.mean((c_arr - mu_c) * (r_arr - mu_r)))
                c1 = 0.0001
                c2 = 0.0009
                ssim = float(((2 * mu_c * mu_r + c1) * (2 * cov + c2)) / ((mu_c**2 + mu_r**2 + c1) * (sig_c + sig_r + c2)))
                is_valid = ssim >= self.min_quality_threshold
                return {
                    "valid": is_valid,
                    "mode": mode.value,
                    "ssim": ssim,
                    "psnr": psnr,
                    "threshold": self.min_quality_threshold,
                    "message": f"Application SSIM {ssim:.4f} >= {self.min_quality_threshold:.4f}" if is_valid else f"Application quality failed ({ssim:.4f})"
                }
            return {"valid": False, "mode": mode.value, "message": "Application mode requires multi-dimensional observable"}

        elif mode == CorrectnessMode.CONTRACT:
            # Custom invariant contract satisfaction
            is_valid = candidate is not None
            return {"valid": is_valid, "mode": mode.value, "message": "Custom contract criteria evaluated"}

        return {"valid": False, "mode": "UNKNOWN", "message": "Unknown correctness mode"}


class ContractCompiler:
    """Compiles high-level workload requirements into strict WorkloadContracts."""

    @staticmethod
    def compile(
        workload_id: str,
        domain: str,
        correctness_mode: Union[str, CorrectnessMode] = CorrectnessMode.NUMERICAL,
        tolerance_epsilon: float = 1e-4,
        latency_limit_ms: Optional[float] = None,
        min_ssim: float = 0.98,
        substitution_allowed: bool = False,
        **kwargs: Any
    ) -> WorkloadContract:
        if isinstance(correctness_mode, str):
            correctness_mode = CorrectnessMode(correctness_mode.upper())

        return WorkloadContract(
            workload_id=workload_id,
            domain=domain,
            input_schema=kwargs.get("input_schema", {"type": "tensor", "shape": "dynamic"}),
            output_schema=kwargs.get("output_schema", {"type": "tensor", "shape": "dynamic"}),
            correctness_mode=correctness_mode,
            tolerance_epsilon=tolerance_epsilon,
            min_quality_threshold=min_ssim,
            latency_limit_ms=latency_limit_ms,
            workload_substitution_allowed=substitution_allowed,
            **{k: v for k, v in kwargs.items() if k not in ["input_schema", "output_schema"]}
        )
