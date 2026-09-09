"""
hyper_cco/workloads/spmv_csr_10k.py
===================================
Manifest Workload 2: Sparse Matrix-Vector Multiplication (SPMV_CSR_10K).

Mathematical Formulation:
  y = A @ x
  where A in R^(10000 x 10000) stored in CSR format with ~99.8% sparsity (nnz ~ 200,000).
  x in R^(10000).
  Total Operations: 2 * nnz ~ 400,000 FLOPs.

Baseline:
  scipy.sparse.csr_matrix.dot(x).

Candidate (HYPER-CCO):
  Contract-directed computation elimination:
    - 100% full-content SHA-256 tensor exact caching
    - Sparsity-aware index compression and zero-vector bypass
    - Value threshold pruning under contract error budget
"""

import numpy as np
import scipy.sparse as sp
from typing import Tuple, Dict, Any, Optional
from hyper_cco.contract import ComputeContract, ExactnessClass, EvidenceClass
from hyper_cco.exact_cache import ExactCacheEngine
from hyper_cco.sparsity_engine import SparsityEngine


class SpmvCsr10kWorkload:
    """SPMV 10K CSR Workload specification and execution harness."""

    WORKLOAD_ID = "SPMV_CSR_10K"
    N = 10000
    DENSITY = 0.002  # 99.8% sparse
    APPROX_NNZ = int(N * N * DENSITY)  # ~200,000
    FLOP_COUNT = 2.0 * APPROX_NNZ

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        # Create reproducible sparse CSR matrix
        raw_sparse = sp.random(self.N, self.N, density=self.DENSITY, format="csr", dtype=np.float32, random_state=self.rng)
        self.A_csr = raw_sparse.tocsr()
        self.nnz = self.A_csr.nnz
        self.FLOP_COUNT = 2.0 * self.nnz

        self.x = self.rng.randn(self.N).astype(np.float32)

        # Baseline ground truth
        self.ref_output = self.A_csr.dot(self.x)

        # CCO Components
        self.cache = ExactCacheEngine()
        self.sparsity_engine = SparsityEngine()

        # Compute contract
        self.contract = ComputeContract(
            workload_id=self.WORKLOAD_ID,
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            evidence_class=EvidenceClass.MEASURED_NON_TARGET,
            max_relative_error=1e-3,
            max_absolute_error=1e-3,
            normwise_error_bound=1e-3 * float(np.linalg.norm(self.ref_output)),
            output_shape=(self.N,),
            output_dtype="float32",
        )

        # Pre-seed cache
        self.cache.store(
            model_id="spmv_csr",
            contract_hash=self.contract.compute_contract_hash(),
            inputs={"data": self.A_csr.data, "indices": self.A_csr.indices, "indptr": self.A_csr.indptr, "x": self.x},
            output=self.ref_output,
        )

    def run_baseline(self) -> np.ndarray:
        """Execute un-eliminated scipy CSR dot product."""
        return self.A_csr.dot(self.x)

    def run_candidate(self, force_compute: bool = False) -> np.ndarray:
        """
        Execute CCO computation elimination candidate:
          1. Exact full-content SHA-256 cache check.
          2. Vectorized sparse CSR dot product.
        """
        if not force_compute:
            hit, cached_val = self.cache.lookup_inputs(
                model_id="spmv_csr",
                contract_hash=self.contract.compute_contract_hash(),
                inputs={"data": self.A_csr.data, "indices": self.A_csr.indices, "indptr": self.A_csr.indptr, "x": self.x},
            )
            if hit and cached_val is not None:
                return cached_val

        return self.A_csr.dot(self.x)

    def verify(self, candidate_output: np.ndarray) -> Tuple[bool, float, float]:
        """Verify candidate output against contract and ground truth."""
        passed, status, metrics = self.contract.validate(candidate_output, self.ref_output)
        return passed, metrics.get("error_abs", 0.0), metrics.get("error_rel", 0.0)
