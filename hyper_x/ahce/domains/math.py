"""
hyper_x/ahce/domains/math.py
============================
Mathematics domain adapter for AHCE.
"""

from typing import Dict, Any, Tuple
import numpy as np
from ..contract import AHCEContract, CorrectnessClass


class MathDomainAdapter:
    """Mathematics and linear algebra computational adapter."""

    def execute_contracted_gemm(
        self,
        A: np.ndarray,
        B: np.ndarray,
        contract: AHCEContract,
        rank: int = 16
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        # Check if low-rank is permitted and effective
        if contract.allow_approximation and min(A.shape) >= 64:
            # Associative low-rank
            from hyper.low_rank.low_rank_engine import LowRankEngine
            engine = LowRankEngine(default_rank=rank)
            tol = contract.max_relative_error or 1e-3
            out, telem = engine.benchmark_and_execute(A, B, max_allowed_rel_error=tol)
            return out, telem

        # Fallback exact dense
        return A @ B, {"strategy": "dense_blas", "path_class": "EXACT"}
