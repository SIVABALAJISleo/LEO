"""
hyper_x/wormhole_compiler/meta_search.py
=============================================================================
HYPER-X Meta-Search & Search Policy Prioritization Engine (Phase 27, 61)
=============================================================================
Extracts deep structural features from workload tensors and learns which
transformation pathways to prioritize:

Features:
  - sparsity
  - effective rank / singular decay energy
  - condition number
  - entropy
  - output dimension ratio (observable / full matrix)
  - arithmetic intensity

Search Policy:
  - If output_dim_ratio << 1.0: PRIORITIZE OUTPUT_PROJECTION
  - If rank_ratio < 0.40 and cond < 10^4: PRIORITIZE LOW_RANK_DECOMPOSITION
  - If rank_ratio < 0.40 and cond >= 10^4: PRIORITIZE LOW_RANK_WITH_RESIDUAL
  - If sparsity > 0.40: PRIORITIZE SPARSE_CSR
  - Else: PRIORITIZE CACHE_TILED_BASELINE (No-Free-Lunch)
"""

from __future__ import annotations
from typing import Dict, Any, List
import numpy as np

from hyper_x.wormhole_compiler.schemas import WorkloadContract, ObservableRequirement


class MetaSearchEngine:
    """Meta-learner that prioritizes algorithm search paths based on workload features."""

    def __init__(self):
        pass

    def extract_features(
        self,
        A: np.ndarray,
        contract: WorkloadContract,
        observable: ObservableRequirement,
    ) -> Dict[str, Any]:
        """Extracts comprehensive mathematical and structural features."""
        M, K = A.shape
        sample_dim = min(48, M, K)
        sample = A[:sample_dim, :sample_dim]

        # 1. Sparsity
        sparsity = float(np.mean(np.abs(sample) < 1e-4))

        # 2. SVD singular value distribution
        s = np.linalg.svd(sample, compute_uv=False)
        energy = np.cumsum(s**2) / np.sum(s**2)
        r95 = int(np.searchsorted(energy, 0.95)) + 1
        rank_ratio = float(r95 / max(1, sample_dim))
        cond = float(s[0] / max(1e-8, s[-1]))

        # 3. Spectral entropy
        p = s**2 / np.sum(s**2)
        entropy = float(-np.sum(p * np.log2(p + 1e-12)))

        # 4. Observable dimension ratio
        if observable.output_type == "VECTOR":
            out_dim = 1
        elif observable.output_type == "TOP_K":
            out_dim = observable.projection_dim or 10
        else:
            out_dim = M

        dim_ratio = float(out_dim / max(1, M))

        return {
            "M": M,
            "K": K,
            "sparsity": round(sparsity, 4),
            "effective_rank": r95,
            "rank_ratio": round(rank_ratio, 4),
            "condition_number": round(cond, 2),
            "spectral_entropy": round(entropy, 4),
            "observable_dim_ratio": round(dim_ratio, 4),
            "is_vector_projection": (observable.output_type == "VECTOR"),
        }

    def prioritize_search_pathways(self, features: Dict[str, Any]) -> List[str]:
        """
        Returns an ordered list of search pathways to explore based on features.
        """
        pathways: List[str] = []

        # Rule 1: Output projection
        if features["is_vector_projection"] or features["observable_dim_ratio"] < 0.10:
            pathways.append("OUTPUT_PROJECT >> ASSOCIATIVE_CHAIN")

        # Rule 2: Low-rank structure
        if features["rank_ratio"] <= 0.40:
            if features["condition_number"] > 1e4:
                pathways.append("LOW_RANK_DECOMPOSE >> MATMUL >> RESIDUAL_CORRECTION")
            else:
                pathways.append("LOW_RANK_DECOMPOSE >> MATMUL")

        # Rule 3: Sparse structure
        if features["sparsity"] >= 0.35:
            pathways.append("SPARSE_TRANSFORM >> CONDITIONAL_MATMUL")

        # Rule 4: Tiled cache ordering (safe exact)
        pathways.append("MORTON_REORDER >> BLAS_TILED_MATMUL")

        # Default fallback
        pathways.append("DENSE_BASELINE")

        return pathways
