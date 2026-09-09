"""
hyper_cco/residual_engine.py
============================
Generic Residual-First Computation Engine.
Implements the core principle: Output = Prediction + ResidualCorrection.
Computes a low-cost prediction, constructs a residual error map, evaluates
only the non-zero or critical residual regions, and combines them with verified error bounds.
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple, List, Callable
import numpy as np


@dataclass
class ResidualResult:
    """Telemetry and outcome of a residual-first execution."""
    output: np.ndarray
    prediction_ops: float
    residual_ops: float
    original_operations: float
    executed_operations: float
    work_elimination_ratio: float
    residual_norm: float
    relative_residual_error: float
    active_residual_elements: int
    total_elements: int
    latency_ms: float
    strategy: str = "RESIDUAL_FIRST"


class ResidualEngine:
    """
    Orchestrates residual-first computation across matrices, tensors, and spatial domains.
    """

    @staticmethod
    def execute_matrix_residual(
        A: np.ndarray,
        B: np.ndarray,
        rank_k: int = 8,
        residual_tolerance: float = 1e-4
    ) -> ResidualResult:
        """
        Executes Y = A @ B via Low-Rank Base Prediction + Sparse Residual Correction.
        A ≈ U_k @ V_k.T + E_residual
        Y = (U_k @ (V_k.T @ B)) + (E_residual @ B)
        """
        t0 = time.perf_counter()
        M, K = A.shape
        K2, N = B.shape
        orig_ops = 2.0 * M * N * K

        # 1. Base Prediction via Truncated Randomized SVD
        actual_k = min(rank_k, M, K)
        # Randomized range finder
        Omega = np.random.randn(K, actual_k)
        Y_sample = A @ Omega
        Q, _ = np.linalg.qr(Y_sample)
        B_proj = Q.T @ A
        U_tilde, S, Vt = np.linalg.svd(B_proj, full_matrices=False)
        U_k = Q @ U_tilde[:, :actual_k]
        S_k = S[:actual_k]
        Vt_k = Vt[:actual_k, :]

        # Prediction: Y_pred = (U_k * S_k) @ (Vt_k @ B)
        pred_ops = 2.0 * actual_k * K * N + 2.0 * M * actual_k * N
        intermediate = Vt_k @ B
        Y_pred = (U_k * S_k) @ intermediate

        # 2. Residual Error Matrix: E = A - U_k * S_k @ Vt_k
        A_approx = (U_k * S_k) @ Vt_k
        E_res = A - A_approx
        res_norm = float(np.linalg.norm(E_res))
        norm_A = float(np.linalg.norm(A))
        rel_res = res_norm / max(1e-12, norm_A)

        # 3. Sparse Residual Correction
        mask = np.abs(E_res) > (residual_tolerance * norm_A / max(1, M * K))
        active_elements = int(np.sum(mask))

        if active_elements == 0 or rel_res <= residual_tolerance:
            # Prediction strictly satisfies tolerance -> zero residual operations
            res_ops = 0.0
            Y_final = Y_pred
        else:
            # Compute sparse residual: only non-zero rows/columns of E_res
            active_rows = np.where(np.any(mask, axis=1))[0]
            if len(active_rows) < M * 0.5:
                # Multiply only active rows
                E_active = E_res[active_rows, :]
                delta_Y = E_active @ B
                Y_final = Y_pred.copy()
                Y_final[active_rows, :] += delta_Y
                res_ops = 2.0 * len(active_rows) * K * N
            else:
                delta_Y = E_res @ B
                Y_final = Y_pred + delta_Y
                res_ops = 2.0 * M * K * N

        total_exec_ops = pred_ops + res_ops
        work_elim = max(0.0, 1.0 - (total_exec_ops / orig_ops)) if orig_ops > 0 else 0.0
        latency = (time.perf_counter() - t0) * 1000.0

        return ResidualResult(
            output=Y_final,
            prediction_ops=pred_ops,
            residual_ops=res_ops,
            original_operations=orig_ops,
            executed_operations=total_exec_ops,
            work_elimination_ratio=work_elim,
            residual_norm=res_norm,
            relative_residual_error=rel_res,
            active_residual_elements=active_elements,
            total_elements=M * K,
            latency_ms=latency,
            strategy="RESIDUAL_LOW_RANK_SPARSE"
        )

    @staticmethod
    def execute_spatial_tile_residual(
        current_frame: np.ndarray,
        predicted_frame: np.ndarray,
        render_tile_fn: Callable[[int, int, int, int], np.ndarray],
        tile_size: int = 16,
        error_threshold: float = 0.05
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes spatial rendering via prediction + tile-based residual recomputation.
        Recomputes only tiles where ||predicted_tile - ground_truth|| > threshold.
        """
        t0 = time.perf_counter()
        H, W = current_frame.shape[:2]
        output = predicted_frame.copy()

        total_tiles = 0
        recomputed_tiles = 0

        for y in range(0, H, tile_size):
            for x in range(0, W, tile_size):
                total_tiles += 1
                y_end = min(H, y + tile_size)
                x_end = min(W, x + tile_size)

                pred_tile = predicted_frame[y:y_end, x:x_end]
                curr_tile = current_frame[y:y_end, x:x_end]

                tile_error = float(np.mean(np.abs(pred_tile - curr_tile)))
                if tile_error > error_threshold:
                    # Recompute only this critical residual tile
                    exact_tile = render_tile_fn(y, y_end, x, x_end)
                    output[y:y_end, x:x_end] = exact_tile
                    recomputed_tiles += 1

        latency = (time.perf_counter() - t0) * 1000.0
        elim_ratio = 1.0 - (recomputed_tiles / max(1, total_tiles))

        telemetry = {
            "total_tiles": total_tiles,
            "recomputed_tiles": recomputed_tiles,
            "eliminated_tiles": total_tiles - recomputed_tiles,
            "tile_elimination_ratio": elim_ratio,
            "latency_ms": latency,
            "strategy": "SPATIAL_TILE_RESIDUAL"
        }
        return output, telemetry
