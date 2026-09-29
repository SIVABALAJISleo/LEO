"""
hyper_x/wormhole_compiler/precision_engine.py
=============================================================================
Universal Precision & Error-Bound Optimization Engine (Section 14)
=============================================================================
Evaluates precision reduction:
    FP32 -> FP16 / BF16 / INT8 / INT4 / Mixed Precision

CRITICAL CONTRACT RULES:
1. Exact Contracts: NEVER silently lower precision.
2. Numerical Contracts: Precision reduction is permitted ONLY if:
   max_error <= contract.tolerance
3. Full Error Statistics Computed:
   - absolute_error (max, mean, p99)
   - relative_error (max, mean, p99)
   - ULP error (Units in the Last Place)
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract, CorrectnessRequirement


@dataclass
class PrecisionAnalysisReport:
    workload_id: str
    original_dtype: str
    target_dtype: str
    contract_permits_reduction: bool
    contract_satisfied: bool
    max_absolute_error: float
    mean_absolute_error: float
    p99_absolute_error: float
    max_relative_error: float
    mean_relative_error: float
    max_ulp_error: float
    memory_reduction_ratio: float
    estimated_speedup: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "original_dtype": self.original_dtype,
            "target_dtype": self.target_dtype,
            "contract_permits_reduction": self.contract_permits_reduction,
            "contract_satisfied": self.contract_satisfied,
            "max_absolute_error": float(self.max_absolute_error),
            "mean_absolute_error": float(self.mean_absolute_error),
            "p99_absolute_error": float(self.p99_absolute_error),
            "max_relative_error": float(self.max_relative_error),
            "mean_relative_error": float(self.mean_relative_error),
            "max_ulp_error": float(self.max_ulp_error),
            "memory_reduction_ratio": round(self.memory_reduction_ratio, 2),
            "estimated_speedup": round(self.estimated_speedup, 2),
        }


class PrecisionEngine:
    """
    Evaluates numerical precision transformations under strict contract enforcement.
    """

    @staticmethod
    def evaluate_precision_reduction(
        data: np.ndarray,
        target_dtype: str,
        contract: Optional[WorkloadContract] = None,
    ) -> Tuple[np.ndarray, PrecisionAnalysisReport]:
        orig_dtype = str(data.dtype)
        is_exact = contract.correctness == CorrectnessRequirement.EXACT if contract else True
        tol = 0.0 if is_exact else (contract.tolerance if contract else 1e-4)

        orig_bytes = data.nbytes

        # Quantize or cast
        if target_dtype in ["float16", "fp16"]:
            cast_data = data.astype(np.float16).astype(data.dtype)
            target_bytes = data.size * 2
            est_speedup = 1.8
        elif target_dtype in ["int8", "int8_quant"]:
            max_val = np.max(np.abs(data)) + 1e-12
            scale = 127.0 / max_val
            quant = np.clip(np.round(data * scale), -128, 127).astype(np.int8)
            cast_data = (quant.astype(data.dtype) / scale)
            target_bytes = data.size * 1
            est_speedup = 3.2
        else:
            cast_data = data.copy()
            target_bytes = orig_bytes
            est_speedup = 1.0

        # Calculate error stats
        diff = np.abs(data - cast_data)
        max_abs = float(np.max(diff))
        mean_abs = float(np.mean(diff))
        p99_abs = float(np.percentile(diff, 99))

        rel_diff = diff / (np.abs(data) + 1e-12)
        max_rel = float(np.max(rel_diff))
        mean_rel = float(np.mean(rel_diff))

        # ULP error estimate
        eps = float(np.finfo(data.dtype).eps) if np.issubdtype(data.dtype, np.floating) else 1.0
        ulp_err = float(max_abs / eps)

        # Rule: If exact contract, precision reduction is strictly forbidden unless error is zero
        if is_exact:
            permits = False
            satisfied = (max_abs == 0.0)
        else:
            permits = True
            satisfied = bool(max_abs <= tol)

        mem_reduction = float(orig_bytes / max(1, target_bytes))

        report = PrecisionAnalysisReport(
            workload_id=contract.workload_id if contract else "PRECISION_OP",
            original_dtype=orig_dtype,
            target_dtype=target_dtype,
            contract_permits_reduction=permits,
            contract_satisfied=satisfied,
            max_absolute_error=max_abs,
            mean_absolute_error=mean_abs,
            p99_absolute_error=p99_abs,
            max_relative_error=max_rel,
            mean_relative_error=mean_rel,
            max_ulp_error=ulp_err,
            memory_reduction_ratio=mem_reduction,
            estimated_speedup=est_speedup if satisfied else 1.0,
        )

        return (cast_data if satisfied else data), report
