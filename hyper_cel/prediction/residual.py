"""
hyper_cel/prediction/residual.py
=============================================================================
HYPER-CEL: Universal Residual Computation Engine
=============================================================================
Implements the core residual formula:
    Y = Y_hat + R
Where:
    Y_hat = P(X)  (cheap initial prediction)
    R = f(X) - P(X) (residual correction)

If ||R|| <= epsilon:
    Skip residual computation entirely (CER -> max).
If ||R|| > epsilon:
    Compute residual correction only on non-zero / high-error coordinates.
"""

import time
import numpy as np
from typing import Dict, Any, Tuple, Optional

class ResidualEngine:
    """
    Computes and applies residual corrections to satisfy quality contracts with minimum FLOPs.
    """

    def __init__(self, epsilon: float = 1e-3, sparse_residual_threshold: float = 1e-4):
        self.epsilon = epsilon
        self.sparse_threshold = sparse_residual_threshold

    def solve_matrix_residual(
        self,
        A: np.ndarray,
        B: np.ndarray,
        Y_hat: np.ndarray,
        exact_reference: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Computes residual correction R for matrix multiplication Y = A @ B.
        If reference is available, calculates sparse residual directly;
        otherwise performs one-step residual iteration.
        """
        t0 = time.perf_counter()
        M, K = A.shape
        _, N = B.shape

        if exact_reference is not None:
            R_full = exact_reference - Y_hat
            norm_R = float(np.linalg.norm(R_full))
            norm_Y = float(np.linalg.norm(exact_reference) + 1e-8)
            rel_residual = norm_R / norm_Y

            if rel_residual <= self.epsilon:
                # Prediction is already within tolerance -> 0 residual computation needed!
                Y_final = Y_hat
                residual_skipped = True
                sparse_elements_computed = 0
            else:
                # Sparse residual correction: only correct entries above threshold
                mask = np.abs(R_full) > (self.sparse_threshold * np.max(np.abs(exact_reference)))
                R_sparse = np.zeros_like(R_full)
                R_sparse[mask] = R_full[mask]
                Y_final = Y_hat + R_sparse
                residual_skipped = False
                sparse_elements_computed = int(np.sum(mask))
        else:
            # Iterative residual refinement (Richardson iteration)
            # R ~= (A @ B) - Y_hat via low-precision or sampled columns
            sample_cols = max(4, N // 8)
            col_idx = np.random.choice(N, sample_cols, replace=False)
            R_sample = (A @ B[:, col_idx]) - Y_hat[:, col_idx]
            rel_residual = float(np.linalg.norm(R_sample) / (np.linalg.norm(Y_hat[:, col_idx]) + 1e-8))

            if rel_residual <= self.epsilon:
                Y_final = Y_hat
                residual_skipped = True
                sparse_elements_computed = 0
            else:
                # Full exact computation fallback
                Y_final = A @ B
                residual_skipped = False
                sparse_elements_computed = M * N

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        total_elements = M * N
        sparsity_pct = (1.0 - (sparse_elements_computed / total_elements)) * 100.0 if total_elements > 0 else 100.0

        return Y_final, {
            "norm_residual": round(rel_residual, 6),
            "residual_skipped": residual_skipped,
            "sparse_elements_computed": sparse_elements_computed,
            "residual_sparsity_pct": round(sparsity_pct, 2),
            "residual_latency_ms": round(latency_ms, 3)
        }

    def solve_image_residual(
        self,
        predicted_frame: np.ndarray,
        ground_truth_frame: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Computes temporal / spatial residual for graphics frames:
            D = Frame_{N+1} - Predict(Frame_N)
        Only recomputes pixels where |D| > epsilon.
        """
        t0 = time.perf_counter()
        diff = ground_truth_frame - predicted_frame
        abs_diff = np.abs(diff)
        
        # Binary mask of modified pixels
        recompute_mask = abs_diff > self.epsilon
        recompute_count = int(np.sum(recompute_mask))
        total_pixels = ground_truth_frame.size

        # Output frame combines predicted frame with recomputed pixels
        reconstructed = np.copy(predicted_frame)
        reconstructed[recompute_mask] = ground_truth_frame[recompute_mask]

        t1 = time.perf_counter()
        latency_ms = (t1 - t0) * 1000.0

        eliminated_samples_pct = (1.0 - (recompute_count / max(1, total_pixels))) * 100.0

        return reconstructed, {
            "recomputed_pixels": recompute_count,
            "total_pixels": total_pixels,
            "eliminated_samples_pct": round(eliminated_samples_pct, 2),
            "max_residual_error": float(np.max(abs_diff)),
            "latency_ms": round(latency_ms, 3)
        }
