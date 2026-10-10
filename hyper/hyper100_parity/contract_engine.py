"""
hyper/hyper100_parity/contract_engine.py
=========================================
Performance Contract & Strict Verification Bounds Engine (Section 28).

Enforces:
1. Performance Contract:
   - max_latency_ms
   - min_throughput_ops_sec
   - min_fps
   - deadline_ms
   - max_memory_mb
   - max_temperature_c
   - maximum_fallback_ratio
   - minimum_quality_score (e.g. SSIM / PSNR)
   - required_precision

   Rule: If the contract is not known:
     status = CONTRACT_UNDEFINED (Do NOT invent a target).

2. Equivalence Classes:
   - EXACT (bit-for-bit or discrete equality)
   - NUMERICALLY_EQUIVALENT (floating-point tolerance within strict bounds)
   - PERCEPTUALLY_EQUIVALENT (SSIM >= threshold, PSNR >= threshold)
   - CONTRACT_EQUIVALENT (satisfies application contract constraints)

3. Error Budget & Contract Dominance:
   Never silently weaken or change precision unless explicitly declared.
"""

from __future__ import annotations
import math
from enum import Enum
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

from .taxonomy import EquivalenceClass


class ContractStatus(str, Enum):
    CONTRACT_DEFINED = "CONTRACT_DEFINED"
    CONTRACT_UNDEFINED = "CONTRACT_UNDEFINED"


class PrecisionMode(str, Enum):
    FP64 = "FP64"
    FP32 = "FP32"
    FP16 = "FP16"
    BF16 = "BF16"
    INT32 = "INT32"
    INT16 = "INT16"
    INT8 = "INT8"
    TERNARY_1_58 = "TERNARY_1_58"
    BINARY = "BINARY"
    EXACT_DISCRETE = "EXACT_DISCRETE"


class PerformanceContract(BaseModel):
    """
    Formal hardware-agnostic contract defining required external latency,
    throughput, frame rate, deadline, memory, thermal, and quality bounds.
    """
    contract_id: str
    workload_name: str
    status: ContractStatus = ContractStatus.CONTRACT_DEFINED

    # Timing & Throughput
    max_latency_ms: Optional[float] = None
    min_throughput_ops_sec: Optional[float] = None
    min_fps: Optional[float] = None
    deadline_ms: Optional[float] = None

    # Memory & System
    max_memory_mb: Optional[float] = None
    max_temperature_c: Optional[float] = 85.0
    maximum_fallback_ratio: float = 0.05  # Max 5% fallback permitted

    # Quality & Correctness
    equivalence_class: EquivalenceClass = EquivalenceClass.EXACT
    precision: PrecisionMode = PrecisionMode.FP32
    max_abs_error: float = 0.0
    max_rel_error: float = 0.0
    max_rmse: float = 0.0
    min_ssim: Optional[float] = None
    min_psnr: Optional[float] = None

    allows_cache: bool = True
    allows_prediction: bool = False
    allows_approximation: bool = False

    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def undefined(cls, workload_name: str, contract_id: Optional[str] = None) -> PerformanceContract:
        """Constructs an explicitly undefined contract."""
        return cls(
            contract_id=contract_id or f"CTR-UNDEF-{workload_name.upper()}",
            workload_name=workload_name,
            status=ContractStatus.CONTRACT_UNDEFINED,
        )

    def is_defined(self) -> bool:
        return self.status == ContractStatus.CONTRACT_DEFINED

    def validate_result(
        self,
        ref_output: Any,
        cand_output: Any,
        measured_latency_ms: float,
        peak_memory_mb: float = 0.0,
        temperature_c: float = 45.0,
        fallback_ratio: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Rigorously evaluates whether an execution output satisfies this contract.
        Returns a verification record with boolean pass/fail and dimension diagnostics.
        """
        if not self.is_defined():
            return {
                "contract_status": ContractStatus.CONTRACT_UNDEFINED.value,
                "passed": False,
                "reason": "Contract target is explicitly CONTRACT_UNDEFINED. Cannot verify without declared contract.",
            }

        failures: List[str] = []

        # 1. Performance: Latency & Deadline
        if self.max_latency_ms is not None and measured_latency_ms > self.max_latency_ms:
            failures.append(f"Latency exceeded: {measured_latency_ms:.3f}ms > max {self.max_latency_ms:.3f}ms")
        if self.deadline_ms is not None and measured_latency_ms > self.deadline_ms:
            failures.append(f"Deadline missed: {measured_latency_ms:.3f}ms > deadline {self.deadline_ms:.3f}ms")

        # 2. Performance: Memory & Temperature
        if self.max_memory_mb is not None and peak_memory_mb > self.max_memory_mb:
            failures.append(f"Memory limit exceeded: {peak_memory_mb:.1f}MB > max {self.max_memory_mb:.1f}MB")
        if self.max_temperature_c is not None and temperature_c > self.max_temperature_c:
            failures.append(f"Thermal ceiling exceeded: {temperature_c:.1f}C > max {self.max_temperature_c:.1f}C")
        if fallback_ratio > self.maximum_fallback_ratio:
            failures.append(f"Fallback ratio exceeded: {fallback_ratio:.3f} > max {self.maximum_fallback_ratio:.3f}")

        # 3. Correctness & Error bounds
        abs_err = 0.0
        rel_err = 0.0
        rmse = 0.0
        ssim_val = 1.0

        if isinstance(ref_output, np.ndarray) and isinstance(cand_output, np.ndarray):
            if ref_output.shape != cand_output.shape:
                failures.append(f"Tensor shape mismatch: reference {ref_output.shape} vs candidate {cand_output.shape}")
            else:
                diff = np.abs(ref_output.astype(np.float64) - cand_output.astype(np.float64))
                abs_err = float(np.max(diff))
                norm_ref = np.linalg.norm(ref_output.astype(np.float64))
                rel_err = float(np.linalg.norm(diff) / max(norm_ref, 1e-12))
                rmse = float(np.sqrt(np.mean(diff ** 2)))

                if self.equivalence_class == EquivalenceClass.EXACT:
                    if abs_err > 0.0 or not np.array_equal(ref_output, cand_output):
                        failures.append(f"EXACT equivalence failed: max absolute error = {abs_err}")
                elif self.equivalence_class == EquivalenceClass.NUMERICALLY_EQUIVALENT:
                    if self.max_abs_error > 0.0 and abs_err > self.max_abs_error:
                        failures.append(f"Absolute tolerance exceeded: {abs_err} > max {self.max_abs_error}")
                    if self.max_rel_error > 0.0 and rel_err > self.max_rel_error:
                        failures.append(f"Relative tolerance exceeded: {rel_err} > max {self.max_rel_error}")
                elif self.equivalence_class == EquivalenceClass.PERCEPTUALLY_EQUIVALENT:
                    # Normalized perceptual proxy
                    ref_f64 = ref_output.astype(np.float64)
                    max_range = max(float(np.max(ref_f64) - np.min(ref_f64)), 1.0)
                    psnr = 20.0 * math.log10(max_range / max(rmse, 1e-9)) if rmse > 0 else 99.0
                    ssim_proxy = max(0.0, 1.0 - (rmse / max_range))
                    ssim_val = ssim_proxy
                    if self.min_ssim is not None and ssim_val < self.min_ssim:
                        failures.append(f"SSIM failed: {ssim_val:.4f} < min {self.min_ssim:.4f}")
                    if self.min_psnr is not None and psnr < self.min_psnr:
                        failures.append(f"PSNR failed: {psnr:.2f}dB < min {self.min_psnr:.2f}dB")
        elif ref_output != cand_output:
            if self.equivalence_class == EquivalenceClass.EXACT:
                failures.append(f"Discrete output mismatch: {ref_output} != {cand_output}")

        passed = len(failures) == 0
        return {
            "contract_id": self.contract_id,
            "workload_name": self.workload_name,
            "status": "PASSED" if passed else "FAILED",
            "passed": passed,
            "failures": failures,
            "measured_latency_ms": measured_latency_ms,
            "abs_error": abs_err,
            "rel_error": rel_err,
            "rmse": rmse,
            "ssim": ssim_val,
        }
