"""
hyper_x/ahce/feature_extractor.py
=================================
Fast structural feature extraction for AHCE (Section 5).
"""

from __future__ import annotations
import time
from typing import Tuple, Optional, Any
import numpy as np
from .workload_signature import StructuralFeatures


class AHCEFeatureExtractor:
    """Extracts reliable, measurable structural properties from input tensors."""

    def extract_matrix_features(
        self,
        A: np.ndarray,
        sample_limit: int = 100_000
    ) -> StructuralFeatures:
        shape = tuple(A.shape)
        dtype_str = str(A.dtype)
        total_elements = A.size

        # 1. Sparsity & Density (Fast sample or exact if moderate)
        if total_elements <= sample_limit:
            zeros = int(np.sum(np.abs(A) <= 1e-6))
            sparsity = float(zeros / max(1, total_elements))
        else:
            stride = total_elements // sample_limit
            sample = A.flat[::stride]
            zeros = int(np.sum(np.abs(sample) <= 1e-6))
            sparsity = float(zeros / max(1, sample.size))

        density = 1.0 - sparsity

        # 2. Effective rank estimation (using randomized range finder on small 2D sample)
        eff_rank = None
        cond_est = None
        if A.ndim == 2 and min(A.shape) >= 8:
            M, N = A.shape
            k = min(32, min(M, N))
            try:
                # Approximate singular value decay on sub-block
                sub_M = min(128, M)
                sub_N = min(128, N)
                sub = A[:sub_M, :sub_N].astype(np.float32)
                s = np.linalg.svd(sub, compute_uv=False)
                if len(s) > 0 and s[0] > 1e-12:
                    cond_est = float(s[0] / max(1e-12, s[-1]))
                    # Find rank capturing 95% of energy
                    energy = np.cumsum(s ** 2) / max(1e-12, np.sum(s ** 2))
                    eff_rank = int(np.searchsorted(energy, 0.95) + 1)
                    eff_rank = min(eff_rank, min(M, N))
            except Exception:
                eff_rank = min(M, N)

        # 3. Arithmetic intensity estimate: FLOPs / Byte (for matmul 2*M*K*N / (bytes loaded+stored))
        if A.ndim == 2:
            M, K = A.shape
            bytes_data = M * K * A.itemsize
            flops = 2 * M * K * K
            arith_intensity = float(flops / max(1, bytes_data * 2))
        else:
            arith_intensity = 1.0

        return StructuralFeatures(
            dimensions=shape,
            dtype=dtype_str,
            sparsity=round(sparsity, 4),
            density=round(density, 4),
            estimated_effective_rank=eff_rank,
            condition_estimate=round(cond_est, 2) if cond_est is not None else None,
            entropy=1.0,
            arithmetic_intensity=round(arith_intensity, 2),
            repeated_inputs_detected=False
        )
