"""
hyper_x/leaf/symbolic/closed_form.py
====================================
Closed-form pattern discovery and validation engine for EFSC.

Scientific mandate:
    Determine whether an expensive loop or recurrence can be replaced by a
    mathematically proven lower-complexity O(1) closed form expression.

Matrix Multiplication Warning (Phase 3):
    NEVER assume A @ B can be replaced by an arbitrary scalar function.
    For GEMM, C[i,j] = sum_k A[i,k]*B[k,j], the candidate must produce C.
    Any shortcut that does not produce C must be classified as INVALID.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from .expression import SymExpr, OpType


@dataclass
class ClosedFormResult:
    """Outcome of a closed form discovery attempt."""
    pattern_name: str
    original_complexity: str
    closed_form_complexity: str
    is_exact_equivalent: bool
    closed_form_expr: Optional[SymExpr]
    speedup_ratio: float


class ClosedFormSolver:
    """
    Identifies structured loops and recurrences and collapses them into O(1) closed forms.
    """

    def solve_summation(self, expr: SymExpr) -> Optional[ClosedFormResult]:
        """
        Attempts to find a closed form for a summation node.
        """
        if expr.op != OpType.SUMMATION:
            return None

        idx_var = expr.meta.get("idx_var", "i")
        lower_node = expr.children[0]
        upper_node = expr.children[1]
        body_node = expr.children[2]

        # Case 1: Sum of a constant c from 1 to N: sum_{i=1}^N c = N * c
        if body_node.op == OpType.CONST:
            c = body_node.val
            # N * c
            closed = SymExpr.mul(upper_node, SymExpr.const(c))
            return ClosedFormResult(
                pattern_name="SUMMATION_CONSTANT",
                original_complexity="O(N)",
                closed_form_complexity="O(1)",
                is_exact_equivalent=True,
                closed_form_expr=closed,
                speedup_ratio=1000.0,
            )

        # Case 2: Sum of identity: sum_{i=1}^N i = N * (N + 1) / 2
        if body_node.op == OpType.VAR and body_node.val == idx_var:
            # (N * (N + 1)) / 2
            n_plus_1 = SymExpr.add(upper_node, SymExpr.const(1))
            n_times_n_plus_1 = SymExpr.mul(upper_node, n_plus_1)
            closed = SymExpr.div(n_times_n_plus_1, SymExpr.const(2))
            return ClosedFormResult(
                pattern_name="SUMMATION_ARITHMETIC_SERIES",
                original_complexity="O(N)",
                closed_form_complexity="O(1)",
                is_exact_equivalent=True,
                closed_form_expr=closed,
                speedup_ratio=1000.0,
            )

        # Case 3: Sum of squares: sum_{i=1}^N i^2 = N * (N + 1) * (2N + 1) / 6
        if body_node.op == OpType.MUL:
            left, right = body_node.children[0], body_node.children[1]
            if (
                left.op == OpType.VAR and left.val == idx_var
                and right.op == OpType.VAR and right.val == idx_var
            ):
                n_plus_1 = SymExpr.add(upper_node, SymExpr.const(1))
                two_n = SymExpr.mul(SymExpr.const(2), upper_node)
                two_n_plus_1 = SymExpr.add(two_n, SymExpr.const(1))
                num = SymExpr.mul(SymExpr.mul(upper_node, n_plus_1), two_n_plus_1)
                closed = SymExpr.div(num, SymExpr.const(6))
                return ClosedFormResult(
                    pattern_name="SUMMATION_SQUARES",
                    original_complexity="O(N)",
                    closed_form_complexity="O(1)",
                    is_exact_equivalent=True,
                    closed_form_expr=closed,
                    speedup_ratio=1000.0,
                )

        return None

    def validate_gemm_candidate(
        self,
        candidate_fn: Callable[[np.ndarray, np.ndarray], np.ndarray],
        A: np.ndarray,
        B: np.ndarray,
    ) -> Tuple[bool, str]:
        """
        Rigid verification for GEMM candidates under Phase 3 rules.
        Rejects candidates that replace GEMM with invalid scalar or ad-hoc functions.
        """
        C_ref = np.matmul(A, B)
        try:
            C_cand = candidate_fn(A, B)
        except Exception as e:
            return False, f"Candidate crashed: {e}"

        if not isinstance(C_cand, np.ndarray) or C_cand.shape != C_ref.shape:
            return False, f"INVALID: Candidate output shape {getattr(C_cand, 'shape', None)} != {C_ref.shape}"

        max_err = float(np.max(np.abs(C_cand - C_ref)))
        if max_err > 1e-4:
            return False, f"INVALID: Candidate deviates from reference GEMM by {max_err:.2e} > 1e-4"

        return True, "VALID_GEMM_EQUIVALENT"
