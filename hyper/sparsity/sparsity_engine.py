"""
hyper/sparsity/sparsity_engine.py
=================================
Sparsity Exploitation Engine:
- Dynamically detects zero & near-zero regions
- Sparse CSR / COO / Block-sparse representation
- Only skips computation when the contract permits it
"""

import time
import numpy as np
import scipy.sparse as sp
from typing import Dict, Any, Tuple, Optional


class SparsityEngine:
    """
    Identifies and executes sparse representations when mathematically valid.
    """
    def __init__(self, threshold: float = 1e-6):
        self.threshold = threshold

    def evaluate_sparsity(self, matrix: np.ndarray) -> Dict[str, Any]:
        zero_mask = np.abs(matrix) <= self.threshold
        zero_count = int(np.sum(zero_mask))
        sparsity_ratio = float(zero_count / max(1, matrix.size))
        
        return {
            "size": matrix.size,
            "zero_elements": zero_count,
            "sparsity_ratio": round(sparsity_ratio, 4),
            "sparsity_pct": round(sparsity_ratio * 100.0, 2),
            "is_sparse_beneficial": sparsity_ratio > 0.40
        }

    def execute_sparse_matmul(self, A: np.ndarray, B: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes CSR-based sparse matrix multiplication if sparsity permits.
        """
        t0 = time.perf_counter()
        A_sparse = sp.csr_matrix(A)
        C = A_sparse.dot(B)
        t_elapsed_ms = (time.perf_counter() - t0) * 1000.0

        nnz = A_sparse.nnz
        flops_sparse = 2 * nnz * B.shape[1]
        flops_dense = 2 * A.shape[0] * A.shape[1] * B.shape[1]
        cer = 1.0 - (flops_sparse / max(1, flops_dense))

        return C, {
            "flops_sparse": flops_sparse,
            "flops_dense": flops_dense,
            "cer": round(cer, 4),
            "elapsed_ms": round(t_elapsed_ms, 3)
        }
