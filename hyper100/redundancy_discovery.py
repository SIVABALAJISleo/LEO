"""
hyper100/redundancy_discovery.py
================================
Redundancy Discovery Engine.
Measures and quantifies temporal, spatial, algebraic, spectral, and sparsity
redundancies across arbitrary tensors and compute sequences without speculation.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class RedundancyReport:
    """Quantitative measurement of workload redundancies."""
    sparsity_ratio: float           # Fraction of elements with |x| <= threshold
    near_zero_ratio: float          # Fraction of elements with |x| <= 1e-4
    rank_estimate: int              # Number of singular values containing >= 99% energy
    spectral_energy_ratio_k: float  # Energy in top-k singular values
    effective_compression_ratio: float
    temporal_delta_ratio: float     # L2 norm delta between successive states (0.0 = static)
    spatial_smoothness: float       # Spatial gradient energy (lower = smoother / more redundant)
    is_symmetric: bool
    is_toeplitz_like: bool
    redundancy_score: float         # 0.0 (incompressible/dense noise) to 1.0 (highly redundant)
    recommended_transformations: List[str]


class RedundancyDiscoveryEngine:
    """Discovers and measures redundancy structures in numerical tensors."""

    @staticmethod
    def analyze_tensor(
        tensor: np.ndarray,
        previous_tensor: Optional[np.ndarray] = None,
        sparsity_threshold: float = 1e-5,
        target_energy_retention: float = 0.99
    ) -> RedundancyReport:
        """
        Performs mathematical decomposition to measure redundancy.
        """
        arr = np.asarray(tensor, dtype=np.float32)
        total_elements = max(arr.size, 1)

        # 1. Sparsity analysis
        zero_count = np.count_nonzero(np.abs(arr) <= sparsity_threshold)
        near_zero_count = np.count_nonzero(np.abs(arr) <= 1e-4)
        sparsity_ratio = float(zero_count / total_elements)
        near_zero_ratio = float(near_zero_count / total_elements)

        # 2. Low-rank spectral decay (if 2D or reshaped to 2D)
        if arr.ndim >= 2:
            mat = arr.reshape(arr.shape[0], -1) if arr.ndim > 2 else arr
            min_dim = min(mat.shape)
            k_sample = min(min_dim, 64)
            try:
                # Fast randomized / truncated SVD for spectral energy estimation
                u, s, vh = np.linalg.svd(mat, full_matrices=False)
                total_energy = float(np.sum(s ** 2))
                if total_energy > 0:
                    cum_energy = np.cumsum(s ** 2) / total_energy
                    k_idx = int(np.searchsorted(cum_energy, target_energy_retention)) + 1
                    rank_est = min(k_idx, min_dim)
                    top_k_energy = float(cum_energy[min(rank_est - 1, len(cum_energy) - 1)])
                else:
                    rank_est = 1
                    top_k_energy = 1.0
            except Exception:
                rank_est = min_dim
                top_k_energy = 1.0
            
            comp_ratio = float(min_dim / max(rank_est, 1))
        else:
            rank_est = 1
            top_k_energy = 1.0
            comp_ratio = 1.0

        # 3. Temporal delta measurement
        temporal_ratio = 1.0
        if previous_tensor is not None and previous_tensor.shape == arr.shape:
            prev_arr = np.asarray(previous_tensor, dtype=np.float32)
            norm_prev = float(np.linalg.norm(prev_arr))
            norm_diff = float(np.linalg.norm(arr - prev_arr))
            temporal_ratio = float(norm_diff / (norm_prev + 1e-12)) if norm_prev > 0 else (0.0 if norm_diff == 0 else 1.0)

        # 4. Spatial smoothness (gradient variance)
        smoothness = 1.0
        if arr.ndim == 2 and arr.shape[0] > 1 and arr.shape[1] > 1:
            gx = np.diff(arr, axis=1)
            gy = np.diff(arr, axis=0)
            grad_mag = np.mean(np.abs(gx)) + np.mean(np.abs(gy))
            val_mag = np.mean(np.abs(arr)) + 1e-12
            smoothness = float(grad_mag / val_mag)

        # 5. Algebraic symmetries
        is_sym = False
        is_toep = False
        if arr.ndim == 2 and arr.shape[0] == arr.shape[1]:
            diff_sym = np.max(np.abs(arr - arr.T))
            is_sym = bool(diff_sym < 1e-5)

        # Overall composite redundancy score
        score = 0.0
        transforms = []
        if sparsity_ratio > 0.40:
            score += 0.35 * sparsity_ratio
            transforms.append("SPARSE_TRANSFORMATION")
        if comp_ratio > 2.0 and rank_est < 0.5 * min(arr.shape[:2]):
            score += 0.35 * (1.0 - rank_est / max(arr.shape[0], 1))
            transforms.append("LOW_RANK_DECOMPOSITION")
        if temporal_ratio < 0.20:
            score += 0.30 * (1.0 - temporal_ratio)
            transforms.append("TEMPORAL_DELTA_REUSE")
        if smoothness < 0.15:
            score += 0.20
            transforms.append("SPATIAL_INTERPOLATION")

        score = min(1.0, max(0.0, score))
        if not transforms:
            transforms.append("DENSE_EXACT_BASELINE")

        return RedundancyReport(
            sparsity_ratio=sparsity_ratio,
            near_zero_ratio=near_zero_ratio,
            rank_estimate=rank_est,
            spectral_energy_ratio_k=top_k_energy,
            effective_compression_ratio=comp_ratio,
            temporal_delta_ratio=temporal_ratio,
            spatial_smoothness=smoothness,
            is_symmetric=is_sym,
            is_toeplitz_like=is_toep,
            redundancy_score=score,
            recommended_transformations=transforms
        )
