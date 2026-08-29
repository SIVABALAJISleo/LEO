"""
hyper100/information_reduction.py
=================================
Information-Requirement Analysis Engine.
Quantifies Shannon and Spectral Entropy to determine the minimum sufficient
subspace representation required to satisfy the application contract without information loss.
"""

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class InformationProfile:
    """Quantitative measurement of information content and compressibility."""
    shannon_entropy_bits: float
    spectral_entropy: float
    sufficient_dimension: int
    information_retention_ratio: float
    theoretical_minimum_bytes: int
    original_bytes: int
    compression_potential_ratio: float
    is_incompressible_noise: bool


class InformationReductionEngine:
    """Analyzes mathematical information density of numerical tensors."""

    @staticmethod
    def analyze_information_content(
        tensor: np.ndarray,
        target_variance_retention: float = 0.99,
        num_bins: int = 128
    ) -> InformationProfile:
        """
        Computes Shannon entropy and singular spectrum entropy.
        """
        arr = np.asarray(tensor, dtype=np.float32)
        total_elements = max(arr.size, 1)
        orig_bytes = arr.nbytes

        # 1. Shannon Entropy (empirical distribution)
        flat = arr.ravel()
        if flat.size > 0:
            hist, _ = np.histogram(flat, bins=num_bins, density=True)
            p = hist[hist > 0] / np.sum(hist[hist > 0])
            shannon_ent = float(-np.sum(p * np.log2(p)))
        else:
            shannon_ent = 0.0

        # 2. Spectral Entropy & Sufficient Subspace Dimension
        if arr.ndim >= 2:
            mat = arr.reshape(arr.shape[0], -1) if arr.ndim > 2 else arr
            min_dim = min(mat.shape)
            try:
                _, s, _ = np.linalg.svd(mat, full_matrices=False)
                total_energy = float(np.sum(s ** 2))
                if total_energy > 0:
                    p_s = (s ** 2) / total_energy
                    p_s_nz = p_s[p_s > 1e-15]
                    spec_ent = float(-np.sum(p_s_nz * np.log2(p_s_nz + 1e-15))) / np.log2(max(min_dim, 2))
                    
                    cum_energy = np.cumsum(s ** 2) / total_energy
                    k_idx = int(np.searchsorted(cum_energy, target_variance_retention)) + 1
                    suff_dim = min(k_idx, min_dim)
                    info_ret = float(cum_energy[min(suff_dim - 1, len(cum_energy) - 1)])
                else:
                    spec_ent = 0.0
                    suff_dim = 1
                    info_ret = 1.0
            except Exception:
                spec_ent = 1.0
                suff_dim = min_dim
                info_ret = 1.0
        else:
            spec_ent = 0.0
            suff_dim = 1
            info_ret = 1.0
            min_dim = 1

        # Theoretical minimum bytes based on sufficient dimension and Shannon entropy
        if arr.ndim >= 2:
            min_bytes = int(suff_dim * (arr.shape[0] + arr.shape[1]) * max(1.0, shannon_ent / 8.0))
        else:
            min_bytes = int(total_elements * max(1.0, shannon_ent / 8.0))
        min_bytes = min(min_bytes, orig_bytes)

        comp_potential = float(orig_bytes / max(min_bytes, 1))
        is_noise = bool(spec_ent > 0.95 and shannon_ent > 6.5)

        return InformationProfile(
            shannon_entropy_bits=shannon_ent,
            spectral_entropy=spec_ent,
            sufficient_dimension=suff_dim,
            information_retention_ratio=info_ret,
            theoretical_minimum_bytes=min_bytes,
            original_bytes=orig_bytes,
            compression_potential_ratio=comp_potential,
            is_incompressible_noise=is_noise
        )
