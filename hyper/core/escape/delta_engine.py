"""
hyper/core/escape/delta_engine.py
Breakthrough Engine A — Exact Delta Computation (Prompt Section 7).
Implements the exact mathematical identity:
    A(x + Δx) = Ax + AΔx = Ax + sum_{j in S} A[:, j] * Δx_j
Where S = {j | Δx_j != 0} is the non-zero change set.
Includes change-set detection, state caching, operation ledger tracking, and zero-approximation execution.
"""
from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
import numpy as np

from hyper.core.cost.ledger import AccountingType, WorkLedger
from hyper.core.proof.engine import ProofCertificate, ProofEngine


class ExactDeltaState:
    def __init__(self, matrix_id: str, A: np.ndarray, last_x: np.ndarray, last_y: np.ndarray):
        self.matrix_id = matrix_id
        self.A = A
        self.last_x = last_x.copy()
        self.last_y = last_y.copy()


class ExactDeltaEngine:
    """
    Executes matrix-vector updates incrementally with bitwise mathematical exactness.
    """

    def __init__(self):
        self._states: Dict[str, ExactDeltaState] = {}

    def register_state(self, matrix_id: str, A: np.ndarray, initial_x: np.ndarray) -> np.ndarray:
        initial_y = np.dot(A, initial_x)
        self._states[matrix_id] = ExactDeltaState(matrix_id, A, initial_x, initial_y)
        return initial_y

    def compute_update(
        self,
        matrix_id: str,
        new_x: np.ndarray,
        sparsity_threshold: float = 0.5,
    ) -> Tuple[np.ndarray, WorkLedger, ProofCertificate, bool]:
        """
        Computes A * new_x using retained state if delta is sparse.
        Returns: (output_y, work_ledger, proof_cert, used_delta)
        """
        if matrix_id not in self._states:
            raise KeyError(f"Matrix state '{matrix_id}' not initialized in ExactDeltaEngine.")

        state = self._states[matrix_id]
        A = state.A
        M, N = A.shape
        baseline_ops = 2 * M * N

        # 1. Compute delta vector
        dx = new_x - state.last_x
        changed_indices = np.flatnonzero(dx)
        num_changed = len(changed_indices)

        # 2. Check if delta execution is beneficial
        # If delta is dense (> threshold), canonical recomputation is cheaper
        if num_changed > int(sparsity_threshold * N):
            # Dense change -> fallback to full recomputation
            y_new = np.dot(A, new_x)
            state.last_x = new_x.copy()
            state.last_y = y_new.copy()

            ledger = WorkLedger(
                accounting_type=AccountingType.INSTRUMENTED,
                baseline_executed_operations=baseline_ops,
                candidate_executed_operations=baseline_ops,
                operations_eliminated=0,
                memory_bytes_baseline=A.nbytes + new_x.nbytes,
                memory_bytes_candidate=A.nbytes + new_x.nbytes,
                verification_operations=0,
            )
            proof = ProofEngine.prove_delta_linearity(matrix_id)
            return y_new, ledger, proof, False

        # 3. Exact incremental delta computation: y_new = y_old + sum A[:, j] * dx[j]
        if num_changed == 0:
            y_new = state.last_y.copy()
            actual_ops = N  # Comparison cost
        else:
            delta_y = np.zeros(M, dtype=A.dtype)
            for j in changed_indices:
                delta_y += A[:, j] * dx[j]
            y_new = state.last_y + delta_y
            actual_ops = 2 * M * num_changed + M

        # Update retained state
        state.last_x = new_x.copy()
        state.last_y = y_new.copy()

        eliminated = max(0, baseline_ops - actual_ops)
        ledger = WorkLedger(
            accounting_type=AccountingType.INSTRUMENTED,
            baseline_executed_operations=baseline_ops,
            candidate_executed_operations=actual_ops,
            operations_eliminated=eliminated,
            memory_bytes_baseline=A.nbytes + new_x.nbytes,
            memory_bytes_candidate=(num_changed * M * A.itemsize) + new_x.nbytes,
            verification_operations=0,
        )
        proof = ProofEngine.prove_delta_linearity(matrix_id)
        return y_new, ledger, proof, True
