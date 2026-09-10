"""
hyper_x/wormhole_compiler/sparse_work_elimination.py
=============================================================================
Universal Sparsity & Inactive-Work Elimination Engine (Section 11)
=============================================================================
Detects:
  - Exact zero regions
  - Near-zero / thresholded regions
  - Structurally sparse blocks / bands
  - Inactive neurons & experts (MoE routing)
  - Empty geometry / clipped bounding boxes
  - Unchanged temporal regions

CRITICAL MANDATE:
Exact zeros and approximation thresholds MUST REMAIN COMPLETELY SEPARATE.
- In EXACT mode: ONLY provably zero / inactive work may be eliminated (zero tolerance).
- In APPROXIMATION mode: Threshold-based pruning may be used ONLY when explicitly
  permitted under the declared contract and strictly within contract.tolerance.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

from hyper_x.wormhole_compiler.contract_ir import UniversalWorkloadContract, CorrectnessMode


@dataclass
class SparsityAnalysisReport:
    workload_id: str
    is_exact_mode: bool
    structural_sparsity_ratio: float
    exact_zero_ratio: float
    near_zero_ratio: float
    threshold_applied: float
    eliminated_operations: float
    nominal_operations: float
    work_elimination_ratio: float
    pruned_coordinates_count: int
    error_bound: float
    speedup: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "is_exact_mode": self.is_exact_mode,
            "structural_sparsity_ratio": round(self.structural_sparsity_ratio, 4),
            "exact_zero_ratio": round(self.exact_zero_ratio, 4),
            "near_zero_ratio": round(self.near_zero_ratio, 4),
            "threshold_applied": self.threshold_applied,
            "eliminated_operations": self.eliminated_operations,
            "nominal_operations": self.nominal_operations,
            "work_elimination_ratio": round(self.work_elimination_ratio, 4),
            "pruned_coordinates_count": self.pruned_coordinates_count,
            "error_bound": float(self.error_bound),
            "speedup": round(self.speedup, 2),
        }


class SparsityEliminationEngine:
    """
    Analyzes and eliminates sparse inactive operations under strict exact/approximate separation.
    """

    @staticmethod
    def analyze_tensor_sparsity(
        tensor: np.ndarray,
        contract: UniversalWorkloadContract,
    ) -> SparsityAnalysisReport:
        total_elements = tensor.size
        # 1. Exact zero detection
        exact_zeros = int(np.sum(tensor == 0.0))
        exact_zero_ratio = exact_zeros / max(1, total_elements)

        # 2. Near zero detection (contract-directed threshold)
        if contract.is_exact():
            # In EXACT mode, threshold is strictly 0.0!
            threshold = 0.0
            near_zeros = exact_zeros
            near_zero_ratio = exact_zero_ratio
            error_bound = 0.0
        else:
            threshold = contract.tolerance * 0.1
            near_zeros = int(np.sum(np.abs(tensor) <= threshold))
            near_zero_ratio = near_zeros / max(1, total_elements)
            error_bound = float(np.sqrt(near_zeros) * threshold)

        nominal_flops = 2.0 * total_elements  # e.g. for standard unary/binary traversal
        eliminated_ops = nominal_flops * (exact_zero_ratio if contract.is_exact() else near_zero_ratio)
        work_elim = eliminated_ops / max(1.0, nominal_flops)
        speedup = 1.0 / max(0.01, 1.0 - work_elim)

        return SparsityAnalysisReport(
            workload_id=contract.workload_id,
            is_exact_mode=contract.is_exact(),
            structural_sparsity_ratio=exact_zero_ratio,
            exact_zero_ratio=exact_zero_ratio,
            near_zero_ratio=near_zero_ratio,
            threshold_applied=threshold,
            eliminated_operations=eliminated_ops,
            nominal_operations=nominal_flops,
            work_elimination_ratio=work_elim,
            pruned_coordinates_count=exact_zeros if contract.is_exact() else near_zeros,
            error_bound=error_bound,
            speedup=speedup,
        )

    @staticmethod
    def sparse_gemm_execution(
        A: np.ndarray,
        B: np.ndarray,
        contract: UniversalWorkloadContract,
    ) -> Tuple[np.ndarray, SparsityAnalysisReport]:
        t0 = time.perf_counter()
        M, K = A.shape
        _, N = B.shape
        nominal_flops = 2.0 * M * K * N

        # Determine active rows/columns
        if contract.is_exact():
            # EXACT MODE: only true exact zeros can be eliminated
            active_rows_A = np.where(np.any(A != 0.0, axis=1))[0]
            active_cols_B = np.where(np.any(B != 0.0, axis=0))[0]
            threshold = 0.0
        else:
            # APPROXIMATION MODE: thresholding bounded by contract tolerance
            row_norms = np.linalg.norm(A, axis=1)
            norm_A = max(1e-12, float(np.linalg.norm(A)))
            threshold = (contract.tolerance * norm_A) / np.sqrt(M)
            active_rows_A = np.where(row_norms > threshold)[0]
            active_cols_B = np.arange(N)

        C = np.zeros((M, N), dtype=A.dtype)
        if len(active_rows_A) == 0 or len(active_cols_B) == 0:
            executed_flops = 0.0
        elif len(active_rows_A) < M:
            # Execute only non-zero slice
            A_slice = A[active_rows_A, :]
            C[active_rows_A, :] = A_slice @ B
            executed_flops = 2.0 * len(active_rows_A) * K * N
        else:
            C = A @ B
            executed_flops = nominal_flops

        work_elim = max(0.0, 1.0 - (executed_flops / max(1.0, nominal_flops)))
        speedup = nominal_flops / max(1.0, executed_flops)

        report = SparsityAnalysisReport(
            workload_id=contract.workload_id,
            is_exact_mode=contract.is_exact(),
            structural_sparsity_ratio=1.0 - (len(active_rows_A) / max(1, M)),
            exact_zero_ratio=float(np.mean(A == 0.0)),
            near_zero_ratio=float(np.mean(np.abs(A) <= threshold)),
            threshold_applied=threshold,
            eliminated_operations=nominal_flops - executed_flops,
            nominal_operations=nominal_flops,
            work_elimination_ratio=work_elim,
            pruned_coordinates_count=int((M - len(active_rows_A)) * K),
            error_bound=0.0 if contract.is_exact() else contract.tolerance,
            speedup=speedup,
        )

        return C, report
