"""
hyper/core/escape/slicing_engine.py
Breakthrough Engine F — Output-Directed Slicing (Prompt Section 12).
Prunes calculation of unobserved intermediate values and output slices.
If the contract only queries a sub-slice (e.g. y[:k] or top-1 class),
proves that unobserved rows/columns can be eliminated with zero contract impact.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import numpy as np

from hyper.core.cost.ledger import AccountingType, WorkLedger


class OutputDirectedSlicingEngine:
    """
    Executes output-directed matrix-vector and tensor evaluations.
    """

    @classmethod
    def compute_observed_slice(
        cls,
        W: np.ndarray,
        x: np.ndarray,
        observed_indices: List[int],
    ) -> Tuple[np.ndarray, WorkLedger]:
        """
        Computes only y[i] for i in observed_indices.
        Mathematically proven that for any linear map y = W @ x,
        y[i] = dot(W[i, :], x), independent of y[j] for j != i.
        """
        M, N = W.shape
        baseline_ops = 2 * M * N
        K = len(observed_indices)

        W_sub = W[observed_indices, :]
        y_sub = np.dot(W_sub, x)
        actual_ops = 2 * K * N

        eliminated = max(0, baseline_ops - actual_ops)
        ledger = WorkLedger(
            accounting_type=AccountingType.INSTRUMENTED,
            baseline_executed_operations=baseline_ops,
            candidate_executed_operations=actual_ops,
            operations_eliminated=eliminated,
            memory_bytes_baseline=W.nbytes + x.nbytes,
            memory_bytes_candidate=W_sub.nbytes + x.nbytes,
        )
        return y_sub, ledger
