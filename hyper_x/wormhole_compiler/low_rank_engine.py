"""
hyper_x/wormhole_compiler/low_rank_engine.py
=============================================================================
Universal Low-Rank & Tensor Decomposition Engine (Section 12)
=============================================================================
Detects rank, effective rank, and factorization opportunities:
    A (M x N) -> U (M x r) @ V (r x N)

CRITICAL SEPARATION MANDATE:
- EXACT FACTORIZATION (A = UV): Applied when rank(A) = r << min(M, N) with ZERO
  numerical truncation error (e.g., outer product matrices, rank-deficient structures).
- APPROXIMATE LOW-RANK (A ≈ UV): Applied ONLY when the contract explicitly permits
  numerical tolerance / approximation (e.g. SVD truncation with singular values < tol).

Never mix or silently downgrade EXACT to APPROXIMATE.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract, CorrectnessRequirement


@dataclass
class LowRankReport:
    workload_id: str
    is_exact_factorization: bool
    matrix_shape: Tuple[int, int]
    true_rank: int
    factored_rank: int
    nominal_gemm_flops: float
    factored_gemm_flops: float
    work_elimination_ratio: float
    approximation_error_norm: float
    contract_satisfied: bool
    speedup: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_id": self.workload_id,
            "is_exact_factorization": self.is_exact_factorization,
            "matrix_shape": list(self.matrix_shape),
            "true_rank": self.true_rank,
            "factored_rank": self.factored_rank,
            "nominal_gemm_flops": self.nominal_gemm_flops,
            "factored_gemm_flops": self.factored_gemm_flops,
            "work_elimination_ratio": round(self.work_elimination_ratio, 4),
            "approximation_error_norm": float(self.approximation_error_norm),
            "contract_satisfied": self.contract_satisfied,
            "speedup": round(self.speedup, 2),
        }


class LowRankEngine:
    """
    Detects and factors low-rank matrix structures with formal exact/approximate separation.
    """

    @staticmethod
    def analyze_matrix_rank(
        A: np.ndarray,
        contract: Optional[WorkloadContract] = None,
    ) -> Tuple[bool, int, Optional[Tuple[np.ndarray, np.ndarray]], LowRankReport]:
        """
        Analyzes matrix A. Returns:
        (is_viable, r, (U, V) or None, report)
        """
        M, K = A.shape
        min_dim = min(M, K)
        nominal_gemm_flops = 2.0 * M * K * K  # representative GEMM cost A @ B where B is K x K

        # Compute SVD singular values
        U_full, S, Vt_full = np.linalg.svd(A, full_matrices=False)
        eps = float(np.finfo(A.dtype).eps) if np.issubdtype(A.dtype, np.floating) else 1e-12
        tol = float(S[0] * max(M, K) * eps) if len(S) > 0 and S[0] > 0 else 1e-12
        non_zeros = np.sum(S > tol)
        true_rank = int(non_zeros)

        # In exact mode: only exact rank r is allowed
        is_exact_mode = contract.correctness == CorrectnessRequirement.EXACT if contract else True

        if is_exact_mode:
            r = true_rank
            if r * (M + K) < (M * K):
                # Exact factorization is cheaper!
                U = U_full[:, :r] * np.sqrt(S[:r])[np.newaxis, :]
                V = np.sqrt(S[:r])[:, np.newaxis] * Vt_full[:r, :]
                factored_flops = 2.0 * (M * r + r * K) * K
                wer = max(0.0, 1.0 - (factored_flops / nominal_gemm_flops))
                report = LowRankReport(
                    workload_id=contract.workload_id if contract else f"LOW_RANK_{M}x{K}",
                    is_exact_factorization=True,
                    matrix_shape=(M, K),
                    true_rank=true_rank,
                    factored_rank=r,
                    nominal_gemm_flops=nominal_gemm_flops,
                    factored_gemm_flops=factored_flops,
                    work_elimination_ratio=wer,
                    approximation_error_norm=0.0,
                    contract_satisfied=True,
                    speedup=float(nominal_gemm_flops / max(1.0, factored_flops)),
                )
                return True, r, (U, V), report
            else:
                report = LowRankReport(
                    workload_id=contract.workload_id if contract else f"LOW_RANK_{M}x{K}",
                    is_exact_factorization=True,
                    matrix_shape=(M, K),
                    true_rank=true_rank,
                    factored_rank=min_dim,
                    nominal_gemm_flops=nominal_gemm_flops,
                    factored_gemm_flops=nominal_gemm_flops,
                    work_elimination_ratio=0.0,
                    approximation_error_norm=0.0,
                    contract_satisfied=True,
                    speedup=1.0,
                )
                return False, min_dim, None, report
        else:
            # Approximate mode: allowed within contract.tolerance
            contract_tol = contract.tolerance if contract else 1e-3
            cumulative_energy = np.cumsum(S**2) / np.sum(S**2)
            energy_threshold = 1.0 - (contract_tol**2)
            r_approx = int(np.searchsorted(cumulative_energy, energy_threshold)) + 1
            r_approx = min(r_approx, min_dim)

            if r_approx * (M + K) < (M * K):
                U = U_full[:, :r_approx] * np.sqrt(S[:r_approx])[np.newaxis, :]
                V = np.sqrt(S[:r_approx])[:, np.newaxis] * Vt_full[:r_approx, :]
                A_reconstructed = U @ V
                error_norm = float(np.linalg.norm(A - A_reconstructed) / (np.linalg.norm(A) + 1e-12))
                factored_flops = 2.0 * (M * r_approx + r_approx * K) * K
                wer = max(0.0, 1.0 - (factored_flops / nominal_gemm_flops))

                report = LowRankReport(
                    workload_id=contract.workload_id if contract else f"APPROX_RANK_{M}x{K}",
                    is_exact_factorization=False,
                    matrix_shape=(M, K),
                    true_rank=true_rank,
                    factored_rank=r_approx,
                    nominal_gemm_flops=nominal_gemm_flops,
                    factored_gemm_flops=factored_flops,
                    work_elimination_ratio=wer,
                    approximation_error_norm=error_norm,
                    contract_satisfied=bool(error_norm <= contract_tol),
                    speedup=float(nominal_gemm_flops / max(1.0, factored_flops)),
                )
                return True, r_approx, (U, V), report
            else:
                report = LowRankReport(
                    workload_id=contract.workload_id if contract else f"APPROX_RANK_{M}x{K}",
                    is_exact_factorization=False,
                    matrix_shape=(M, K),
                    true_rank=true_rank,
                    factored_rank=min_dim,
                    nominal_gemm_flops=nominal_gemm_flops,
                    factored_gemm_flops=nominal_gemm_flops,
                    work_elimination_ratio=0.0,
                    approximation_error_norm=0.0,
                    contract_satisfied=True,
                    speedup=1.0,
                )
                return False, min_dim, None, report
