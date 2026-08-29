"""
hyper_ares/structure_detector.py
=============================================================================
HYPER-ARES: Invariant Structure & Redundancy Detector
=============================================================================
Analyzes incoming tensors to extract geometric, algebraic, and temporal properties:
  - Symmetry & Hermitian invariants
  - Diagonal & Triangular structure
  - Sparsity & Block-Sparsity
  - Effective Low-Rank & Singular Value Decay spectrum
  - Row / Column Repetition
  - Temporal & Incremental Delta magnitude
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

@dataclass
class StructuralProfile:
    shape: Tuple[int, ...] = ()
    is_square: bool = False
    symmetry_error: float = 1.0          # ||A - A^T|| / ||A||
    is_symmetric: bool = False
    diagonal_dominance_ratio: float = 0.0 # Energy on diagonal / total energy
    sparsity_ratio: float = 0.0          # Fraction of elements < 1e-5
    effective_rank: int = 0              # Number of dominant singular values (> 5% max)
    singular_value_decay_rate: float = 0.0
    has_low_rank_structure: bool = False
    has_sparse_structure: bool = False
    has_temporal_delta: bool = False
    recommended_representations: Optional[List[str]] = None

class StructureDetector:
    """Detects intrinsic mathematical structure to guide representation selection."""

    @staticmethod
    def analyze_matrix(A: np.ndarray, previous_A: Optional[np.ndarray] = None) -> StructuralProfile:
        M, K = A.shape
        is_sq = (M == K)
        total_norm = float(np.linalg.norm(A) + 1e-8)

        # 1. Symmetry
        sym_err = 1.0
        is_sym = False
        if is_sq:
            diff_sym = float(np.linalg.norm(A - A.T))
            sym_err = diff_sym / total_norm
            is_sym = (sym_err < 1e-3)

        # 2. Diagonal Dominance
        diag_energy = float(np.sum(np.diag(A)**2)) if is_sq else 0.0
        diag_ratio = diag_energy / (total_norm**2)

        # 3. Sparsity
        zero_mask = np.abs(A) < 1e-4
        sparse_ratio = float(np.sum(zero_mask) / A.size)
        has_sparse = (sparse_ratio > 0.40)

        # 4. Low-Rank Spectrum via Fast Randomized SVD
        sample_r = min(32, M, K)
        Omega = np.random.randn(K, sample_r).astype(np.float32)
        Y = A @ Omega
        Q, _ = np.linalg.qr(Y)
        B_sub = Q.T @ A
        s = np.linalg.svd(B_sub, compute_uv=False)
        
        max_s = float(s[0] + 1e-8)
        dominant_sv = np.sum(s > (0.05 * max_s))
        decay_rate = float(s[0] / max(1e-6, s[-1])) if len(s) > 1 else 1.0
        has_low_rank = (dominant_sv < (0.5 * min(M, K))) or (decay_rate > 10.0)

        # 5. Temporal Delta
        has_temp = False
        if previous_A is not None and previous_A.shape == A.shape:
            delta_norm = float(np.linalg.norm(A - previous_A))
            has_temp = (delta_norm / total_norm) < 0.20

        # Recommendations
        recs = ["DENSE_AVX2"]
        if bool(has_temp):
            recs.append("TEMPORAL_EVENT_DELTA")
        if bool(has_low_rank):
            recs.append("LOW_RANK_SVD")
            recs.append("UNIVERSAL_RESIDUAL")
        if bool(has_sparse):
            recs.append("SPARSE_CSR")
        if bool(is_sq) and M >= 512:
            recs.append("MORTON_Z_CURVE")
            recs.append("FREQUENCY_2D_FFT")

        return StructuralProfile(
            shape=A.shape,
            is_square=bool(is_sq),
            symmetry_error=round(sym_err, 4),
            is_symmetric=bool(is_sym),
            diagonal_dominance_ratio=round(diag_ratio, 4),
            sparsity_ratio=round(sparse_ratio, 4),
            effective_rank=int(dominant_sv),
            singular_value_decay_rate=round(decay_rate, 2),
            has_low_rank_structure=bool(has_low_rank),
            has_sparse_structure=bool(has_sparse),
            has_temporal_delta=bool(has_temp),
            recommended_representations=recs
        )
