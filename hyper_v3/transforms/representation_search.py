"""
hyper_v3/transforms/representation_search.py
Automated search across alternative data representations: dense, 2:4 structured sparse,
BitNet ternary quantized, randomized low-rank factorized, and Morton spatial LBVH.
"""

from typing import Dict, Any, Tuple
import numpy as np
from hyper_v3.transforms.factorization import FactorizationTransformer
from hyper_v3.transforms.sparse import SparseTransformer
from hyper_v3.transforms.representation import RepresentationTransformer


class RepresentationSearchEngine:
    """Evaluates whether changing the mathematical representation reduces computation and memory."""

    @staticmethod
    def evaluate_representation_options(tensor: np.ndarray, contract_allows_approx: bool = True) -> Dict[str, Any]:
        """Profiles a tensor and ranks candidate representations."""
        n_elements = tensor.size
        dense_bytes = tensor.nbytes
        zero_ratio = float(np.sum(tensor == 0) / max(n_elements, 1))

        candidates = []

        # 1. Dense baseline
        candidates.append({
            "representation": "dense",
            "footprint_bytes": dense_bytes,
            "compression_ratio": 1.0,
            "error": 0.0,
            "suitable": True
        })

        # 2. 2:4 Structured Sparsity
        if contract_allows_approx and tensor.ndim == 2 and tensor.shape[1] % 4 == 0:
            sp_tensor = SparseTransformer.enforce_2_to_4_sparsity(tensor)
            err = float(np.linalg.norm(tensor - sp_tensor) / max(np.linalg.norm(tensor), 1e-6))
            candidates.append({
                "representation": "sparse_2to4",
                "footprint_bytes": dense_bytes // 2,
                "compression_ratio": 0.50,
                "error": round(err, 4),
                "suitable": err <= 0.20
            })

        # 3. BitNet 1.58b Ternary Quantization
        if contract_allows_approx and tensor.ndim == 2:
            q_w, gamma = FactorizationTransformer.bitnet_ternary_quantize(tensor)
            recon = q_w.astype(np.float32) * gamma
            err = float(np.linalg.norm(tensor - recon) / max(np.linalg.norm(tensor), 1e-6))
            # 1.58 bits per weight vs 32 bits = ~20x compression
            candidates.append({
                "representation": "bitnet_ternary",
                "footprint_bytes": int(dense_bytes * 0.06),
                "compression_ratio": 0.06,
                "error": round(err, 4),
                "suitable": err <= 0.35
            })

        # 4. Randomized Low-Rank SVD
        if contract_allows_approx and tensor.ndim == 2 and min(tensor.shape) >= 64:
            r = min(tensor.shape) // 4
            u, v = FactorizationTransformer.randomized_svd(tensor, rank=r)
            recon = u @ v
            err = float(np.linalg.norm(tensor - recon) / max(np.linalg.norm(tensor), 1e-6))
            lr_bytes = (u.size + v.size) * 4
            candidates.append({
                "representation": "low_rank_svd",
                "footprint_bytes": lr_bytes,
                "compression_ratio": round(lr_bytes / max(dense_bytes, 1), 2),
                "error": round(err, 4),
                "suitable": err <= 0.25
            })

        return {
            "tensor_shape": list(tensor.shape),
            "dense_footprint_bytes": dense_bytes,
            "zero_ratio": zero_ratio,
            "candidates": candidates
        }
