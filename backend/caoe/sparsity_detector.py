"""
backend/caoe/sparsity_detector.py
=================================
CAOE Layer 3: Sparsity & Redundancy Detection.

Identifies work elimination opportunities across 4 patterns:
1. Structural zeros (sparse matrix representations)
2. Value-based redundancy (histogram & unique element distribution)
3. Temporal redundancy (frame-to-frame coherence)
4. Dimension redundancy (truncated SVD low-rank factorability)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import scipy.sparse as sp


class SparsityDetector:
    """Find work that can be eliminated."""

    def __init__(self) -> None:
        self._prev_tensor: Optional[np.ndarray] = None

    def detect_sparsity(
        self,
        tensor: np.ndarray,
        workload_context: Any = None,
        svd_energy_threshold: float = 0.99,
    ) -> Dict[str, Any]:
        """
        Analyze tensor for structural, value, temporal, and dimensional redundancy.
        Returns elimination strategy and estimated percentage of skip-able work.
        """
        # Pattern 1: Structural zeros
        nonzero_count = np.count_nonzero(tensor)
        structural_zeros = 1.0 - (nonzero_count / max(1, tensor.size))

        # Pattern 2: Value-based redundancy (identical elements)
        unique_count = len(np.unique(tensor))
        value_redundancy = 1.0 - (unique_count / max(1, tensor.size))

        # Pattern 3: Temporal redundancy (coherence with previous state)
        temporal_coherence = 0.0
        if self._prev_tensor is not None and self._prev_tensor.shape == tensor.shape:
            diff_elements = np.count_nonzero(tensor != self._prev_tensor)
            temporal_coherence = 1.0 - (diff_elements / max(1, tensor.size))
        self._prev_tensor = tensor.copy()

        # Pattern 4: Dimension redundancy (low-rank factorization)
        low_rank_ratio = 1.0
        estimated_rank = min(tensor.shape) if tensor.ndim >= 2 else 1
        if tensor.ndim == 2 and min(tensor.shape) > 1:
            try:
                # Fast SVD energy capture
                s = np.linalg.svd(tensor, compute_uv=False)
                total_energy = np.sum(s ** 2)
                cum_energy = np.cumsum(s ** 2) / max(1e-9, total_energy)
                rank = int(np.searchsorted(cum_energy, svd_energy_threshold)) + 1
                estimated_rank = min(rank, min(tensor.shape))
                low_rank_ratio = estimated_rank / min(tensor.shape)
            except Exception:
                pass

        # Strategy selection
        strategy = "DENSE"
        work_elimination = 0.0

        if structural_zeros >= 0.85:
            strategy = "SPARSE_CSR"
            work_elimination = structural_zeros
        elif temporal_coherence >= 0.80:
            strategy = "TEMPORAL_DELTA"
            work_elimination = temporal_coherence
        elif low_rank_ratio <= 0.25 and tensor.ndim == 2:
            strategy = "LOW_RANK_SVD"
            work_elimination = 1.0 - (2.0 * low_rank_ratio)
        elif value_redundancy >= 0.70:
            strategy = "QUANTIZED_LUT"
            work_elimination = value_redundancy * 0.5

        return {
            "structural_zeros": round(structural_zeros, 4),
            "value_redundancy": round(value_redundancy, 4),
            "temporal_coherence": round(temporal_coherence, 4),
            "low_rank_ratio": round(low_rank_ratio, 4),
            "estimated_rank": estimated_rank,
            "best_strategy": strategy,
            "work_elimination": max(0.0, round(work_elimination, 4)),
        }

    @staticmethod
    def apply_low_rank(matrix: np.ndarray, target_rank: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Factor matrix A into U and V where A ≈ U @ V.
        U is (M x r), V is (r x N).
        """
        U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
        r = max(1, min(target_rank, len(s)))
        U_r = U[:, :r] * np.sqrt(s[:r])
        V_r = np.sqrt(s[:r])[:, None] * Vt[:r, :]
        return U_r, V_r

    @staticmethod
    def apply_structural_sparsity(matrix: np.ndarray) -> sp.csr_matrix:
        """Convert matrix to Compressed Sparse Row representation."""
        return sp.csr_matrix(matrix)
