"""
hyper/core/escape/low_rank_engine.py
Breakthrough Engine E — Exact Low-Rank / Factorization (Prompt Section 11).
Distinguishes strictly between:
- EXACT_FACTORISATION (residual ||A - U V^T|| == 0 up to machine epsilon)
- APPROXIMATE_FACTORISATION (requires explicit contract error tolerance)
- REJECTED (when rank reduction is not beneficial or contract is violated)
Never calls approximate computation 'exact'.
"""
from __future__ import annotations
from enum import Enum
from typing import Optional, Tuple
import numpy as np
from pydantic import BaseModel

from hyper.core.cost.ledger import AccountingType, WorkLedger
from hyper.core.contract.models import SemanticContract, ContractType


class FactorizationType(str, Enum):
    EXACT_FACTORISATION = "EXACT_FACTORISATION"
    APPROXIMATE_FACTORISATION = "APPROXIMATE_FACTORISATION"
    REJECTED = "REJECTED"


class LowRankFactorizationResult(BaseModel):
    factorization_type: FactorizationType
    rank: int
    residual_norm: float
    is_exact: bool
    baseline_ops: int
    candidate_ops: int


class LowRankEngine:
    """
    Factorizes matrices into low-rank representations U (M x k) and V (k x N).
    A * x becomes U * (V * x), reducing cost from 2*M*N to 2*k*(M + N).
    """

    @classmethod
    def factorize_matrix(
        cls,
        A: np.ndarray,
        contract: SemanticContract,
        max_rank: Optional[int] = None,
    ) -> Tuple[Optional[Tuple[np.ndarray, np.ndarray]], LowRankFactorizationResult]:
        M, N = A.shape
        baseline_ops = 2 * M * N
        max_k = max_rank or (min(M, N) // 2)

        # Compute SVD: A = U @ diag(S) @ Vt
        U, S, Vt = np.linalg.svd(A, full_matrices=False)
        total_energy = np.sum(S ** 2)

        # 1. Check for Exact Low-Rank (zero singular values)
        exact_rank = int(np.count_nonzero(S > 1e-12))
        ops_at_exact = 2 * exact_rank * (M + N)

        if ops_at_exact < baseline_ops and exact_rank <= max_k:
            U_k = U[:, :exact_rank] * S[:exact_rank]
            V_k = Vt[:exact_rank, :]
            residual = float(np.max(np.abs(A - (U_k @ V_k))))
            if residual <= 1e-10:
                res = LowRankFactorizationResult(
                    factorization_type=FactorizationType.EXACT_FACTORISATION,
                    rank=exact_rank,
                    residual_norm=residual,
                    is_exact=True,
                    baseline_ops=baseline_ops,
                    candidate_ops=ops_at_exact,
                )
                return (U_k, V_k), res

        # 2. Check for Approximate Factorization under Contract Parity
        if contract.contract_type in [ContractType.NUMERICAL_FLOAT, ContractType.BOUNDED_ERROR]:
            for k in range(1, max_k + 1):
                U_k = U[:, :k] * S[:k]
                V_k = Vt[:k, :]
                residual = float(np.max(np.abs(A - (U_k @ V_k))))
                if residual <= contract.abs_tolerance:
                    cand_ops = 2 * k * (M + N)
                    if cand_ops < baseline_ops:
                        res = LowRankFactorizationResult(
                            factorization_type=FactorizationType.APPROXIMATE_FACTORISATION,
                            rank=k,
                            residual_norm=residual,
                            is_exact=False,
                            baseline_ops=baseline_ops,
                            candidate_ops=cand_ops,
                        )
                        return (U_k, V_k), res

        # 3. Otherwise: REJECTED
        res = LowRankFactorizationResult(
            factorization_type=FactorizationType.REJECTED,
            rank=min(M, N),
            residual_norm=0.0,
            is_exact=False,
            baseline_ops=baseline_ops,
            candidate_ops=baseline_ops,
        )
        return None, res
