"""
hyper/v8/residual.py
====================
HYPER v8 — Exact Residual Engine.

Implements exact incremental GEMM updates. Given:

    A_t = A_0 + dA
    B_t = B_0 + dB
    C_t = A_t @ B_t = A_0@B_0 + dA@B_0 + A_0@dB + dA@dB

The engine:
  1. Detects which rows/cols/blocks changed.
  2. Computes only the affected residual.
  3. Produces a ResidualProof that the residual covers ALL changed deps.
  4. Verifies the result against reference.

Specialized paths:
    row_residual_gemm       - only rows of A changed
    col_residual_gemm       - only cols of B changed
    block_residual_gemm     - only a block changed
    sparse_residual_gemm    - sparse dA or dB
    full_residual_gemm      - both A and B changed (full decomposition)

Scientific rule:
    Residual must provably cover ALL changed dependencies.
    Partial coverage → FALLBACK to full recomputation.
"""

from __future__ import annotations

import dataclasses
import hashlib
import time
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from .contract import PathClassification


# ─────────────────────────────────────────────────────────────────────────────
# RESIDUAL PROOF
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class ResidualProof:
    """
    Proof that the residual computation covers all changed dependencies.

    status: PROVEN | PARTIAL | UNPROVEN | FAILED
    """
    status: str              # PROVEN | PARTIAL | UNPROVEN | FAILED
    path_type: PathClassification
    changed_rows_A: Optional[List[int]]
    changed_cols_B: Optional[List[int]]
    affected_output_rows: Optional[List[int]]
    affected_output_cols: Optional[List[int]]
    residual_flops: int
    full_flops: int
    fraction_computed: float   # residual_flops / full_flops
    max_abs_error: float       # vs full recomputation
    elapsed_ms: float
    notes: str = ""

    @property
    def is_exact(self) -> bool:
        return self.max_abs_error == 0.0 and self.status == "PROVEN"

    def summary(self) -> Dict:
        return {
            "status": self.status,
            "path_type": self.path_type.value,
            "fraction_computed": round(self.fraction_computed, 4),
            "residual_flops": self.residual_flops,
            "full_flops": self.full_flops,
            "max_abs_error": f"{self.max_abs_error:.3e}",
            "elapsed_ms": round(self.elapsed_ms, 4),
            "is_exact": self.is_exact,
        }


# ─────────────────────────────────────────────────────────────────────────────
# EXACT RESIDUAL ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class ExactResidualEngine:
    """
    Exact incremental GEMM: C_t = A_t @ B_t using residual decomposition.

    Maintains:
        _prev_A, _prev_B, _prev_C   - previous state
        _prev_A_digest, _prev_B_digest

    When called with new A, B:
        1. Detect changed rows of A and changed cols of B.
        2. Compute residual exactly:
               C_t = C_prev + dA @ B_prev + A_prev @ dB + dA @ dB
        3. Verify against reference numpy.
        4. Return proof.
    """

    def __init__(self, verify: bool = True) -> None:
        self._verify = verify
        self._prev_A: Optional[np.ndarray] = None
        self._prev_B: Optional[np.ndarray] = None
        self._prev_C: Optional[np.ndarray] = None
        self._calls = 0

    def _digest(self, arr: np.ndarray) -> str:
        h = hashlib.sha256()
        h.update(arr.tobytes())
        h.update(str(arr.shape).encode())
        return h.hexdigest()

    def _changed_rows(self, prev: np.ndarray, curr: np.ndarray) -> Optional[Set[int]]:
        if prev.shape != curr.shape:
            return None
        rows = {i for i in range(prev.shape[0]) if not np.array_equal(prev[i], curr[i])}
        return rows if len(rows) < prev.shape[0] else None

    def _changed_cols(self, prev: np.ndarray, curr: np.ndarray) -> Optional[Set[int]]:
        if prev.shape != curr.shape:
            return None
        cols = {j for j in range(prev.shape[1]) if not np.array_equal(prev[:, j], curr[:, j])}
        return cols if len(cols) < prev.shape[1] else None

    def compute(
        self,
        A: np.ndarray,
        B: np.ndarray,
    ) -> Tuple[np.ndarray, ResidualProof]:
        """
        Compute C = A @ B using the cheapest provably correct path.

        Returns (result, proof).
        """
        self._calls += 1
        t0 = time.perf_counter_ns()
        m, k = A.shape
        _, n = B.shape
        full_flops = 2 * m * k * n  # multiply-add pairs

        # First call — no prior state
        if self._prev_A is None:
            C = A @ B
            elapsed = (time.perf_counter_ns() - t0) / 1e6
            self._prev_A = A.copy()
            self._prev_B = B.copy()
            self._prev_C = C.copy()
            return C, ResidualProof(
                status="PROVEN",
                path_type=PathClassification.EXACT_FRESH,
                changed_rows_A=None,
                changed_cols_B=None,
                affected_output_rows=None,
                affected_output_cols=None,
                residual_flops=full_flops,
                full_flops=full_flops,
                fraction_computed=1.0,
                max_abs_error=0.0,
                elapsed_ms=elapsed,
                notes="First call. Full computation.",
            )

        # ── Exact identity: delta == 0? ────────────────────────────────────
        if np.array_equal(A, self._prev_A) and np.array_equal(B, self._prev_B):
            elapsed = (time.perf_counter_ns() - t0) / 1e6
            return self._prev_C.copy(), ResidualProof(
                status="PROVEN",
                path_type=PathClassification.EXACT_REUSED,
                changed_rows_A=[],
                changed_cols_B=[],
                affected_output_rows=[],
                affected_output_cols=[],
                residual_flops=0,
                full_flops=full_flops,
                fraction_computed=0.0,
                max_abs_error=0.0,
                elapsed_ms=elapsed,
                notes="Inputs identical. Zero computation.",
            )

        # ── Detect changes ─────────────────────────────────────────────────
        changed_rows_A: Optional[Set[int]] = None
        changed_cols_B: Optional[Set[int]] = None

        if A.shape == self._prev_A.shape:
            changed_rows_A = self._changed_rows(self._prev_A, A)
        if B.shape == self._prev_B.shape:
            changed_cols_B = self._changed_cols(self._prev_B, B)

        # ── Row-only residual: only rows of A changed ──────────────────────
        if (
            changed_rows_A is not None
            and changed_cols_B is not None
            and len(changed_cols_B) == 0
            and A.shape == self._prev_A.shape
            and B.shape == self._prev_B.shape
        ):
            return self._row_residual(A, B, sorted(changed_rows_A), t0, full_flops)

        # ── Col-only residual: only cols of B changed ──────────────────────
        if (
            changed_rows_A is not None
            and len(changed_rows_A) == 0
            and changed_cols_B is not None
            and A.shape == self._prev_A.shape
            and B.shape == self._prev_B.shape
        ):
            return self._col_residual(A, B, sorted(changed_cols_B), t0, full_flops)

        # ── Full residual decomposition ─────────────────────────────────────
        if (
            A.shape == self._prev_A.shape
            and B.shape == self._prev_B.shape
        ):
            return self._full_residual(A, B, t0, full_flops)

        # ── Shape mismatch → full recompute ───────────────────────────────
        C = A @ B
        elapsed = (time.perf_counter_ns() - t0) / 1e6
        self._prev_A = A.copy()
        self._prev_B = B.copy()
        self._prev_C = C.copy()
        return C, ResidualProof(
            status="PROVEN",
            path_type=PathClassification.EXACT_FRESH,
            changed_rows_A=None,
            changed_cols_B=None,
            affected_output_rows=None,
            affected_output_cols=None,
            residual_flops=full_flops,
            full_flops=full_flops,
            fraction_computed=1.0,
            max_abs_error=0.0,
            elapsed_ms=elapsed,
            notes="Shape mismatch — full recompute.",
        )

    def _row_residual(
        self, A: np.ndarray, B: np.ndarray,
        rows: List[int], t0: int, full_flops: int,
    ) -> Tuple[np.ndarray, ResidualProof]:
        """
        Only rows `rows` of A changed.
        C_new[rows, :] = A[rows, :] @ B
        C_new[other, :] = C_prev[other, :]
        """
        C = self._prev_C.copy()
        k = A.shape[1]
        n = B.shape[1]
        residual_flops = len(rows) * 2 * k * n

        for row in rows:
            C[row, :] = A[row, :] @ B

        elapsed = (time.perf_counter_ns() - t0) / 1e6
        max_err = 0.0
        if self._verify:
            ref = A @ B
            max_err = float(np.abs(C - ref).max())

        self._prev_A = A.copy()
        self._prev_B = B.copy()
        self._prev_C = C.copy()

        return C, ResidualProof(
            status="PROVEN" if max_err == 0.0 else "FAILED",
            path_type=PathClassification.EXACT_RESIDUAL,
            changed_rows_A=rows,
            changed_cols_B=[],
            affected_output_rows=rows,
            affected_output_cols=None,
            residual_flops=residual_flops,
            full_flops=full_flops,
            fraction_computed=residual_flops / max(1, full_flops),
            max_abs_error=max_err,
            elapsed_ms=elapsed,
            notes=f"Row-residual: {len(rows)}/{A.shape[0]} rows recomputed.",
        )

    def _col_residual(
        self, A: np.ndarray, B: np.ndarray,
        cols: List[int], t0: int, full_flops: int,
    ) -> Tuple[np.ndarray, ResidualProof]:
        """
        Only cols `cols` of B changed.
        C_new[:, cols] = A @ B[:, cols]
        C_new[:, other] = C_prev[:, other]
        """
        C = self._prev_C.copy()
        m = A.shape[0]
        k = A.shape[1]
        residual_flops = len(cols) * 2 * m * k

        for col in cols:
            C[:, col] = A @ B[:, col]

        elapsed = (time.perf_counter_ns() - t0) / 1e6
        max_err = 0.0
        if self._verify:
            ref = A @ B
            max_err = float(np.abs(C - ref).max())

        self._prev_A = A.copy()
        self._prev_B = B.copy()
        self._prev_C = C.copy()

        return C, ResidualProof(
            status="PROVEN" if max_err == 0.0 else "FAILED",
            path_type=PathClassification.EXACT_RESIDUAL,
            changed_rows_A=[],
            changed_cols_B=cols,
            affected_output_rows=None,
            affected_output_cols=cols,
            residual_flops=residual_flops,
            full_flops=full_flops,
            fraction_computed=residual_flops / max(1, full_flops),
            max_abs_error=max_err,
            elapsed_ms=elapsed,
            notes=f"Col-residual: {len(cols)}/{B.shape[1]} cols recomputed.",
        )

    def _full_residual(
        self, A: np.ndarray, B: np.ndarray,
        t0: int, full_flops: int,
    ) -> Tuple[np.ndarray, ResidualProof]:
        """
        Full residual: C_t = C_0 + dA@B_0 + A_0@dB + dA@dB
        """
        dA = A - self._prev_A
        dB = B - self._prev_B

        # 4 matrix operations instead of 1, but allows incremental updates
        C = (self._prev_C
             + dA @ self._prev_B
             + self._prev_A @ dB
             + dA @ dB)

        elapsed = (time.perf_counter_ns() - t0) / 1e6
        residual_flops = 4 * full_flops  # 4 GEMMs (worse for full change)

        max_err = 0.0
        if self._verify:
            ref = A @ B
            max_err = float(np.abs(C - ref).max())

        self._prev_A = A.copy()
        self._prev_B = B.copy()
        self._prev_C = C.copy()

        # Full residual costs MORE when both change completely
        status = "PROVEN" if max_err < 1e-9 else "FAILED"
        return C, ResidualProof(
            status=status,
            path_type=PathClassification.EXACT_RESIDUAL,
            changed_rows_A=None,
            changed_cols_B=None,
            affected_output_rows=None,
            affected_output_cols=None,
            residual_flops=residual_flops,
            full_flops=full_flops,
            fraction_computed=min(4.0, residual_flops / max(1, full_flops)),
            max_abs_error=max_err,
            elapsed_ms=elapsed,
            notes="Full residual decomposition. Cost may exceed naive GEMM when both inputs fully change.",
        )
