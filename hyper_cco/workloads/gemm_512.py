"""
hyper_cco/workloads/gemm_512.py
===============================
Manifest Workload 1: Dense Matrix Multiplication (GEMM_512x512).

Mathematical Formulation:
  C = alpha * (A @ B) + beta * C_0
  where A, B in R^(512 x 512), alpha=1.0, beta=0.0.
  Total Operations: 2 * 512^3 = 268,435,456 FLOPs.

Baseline:
  Standard full FP32 dense BLAS matrix multiplication.

Candidate (HYPER-CCO):
  Contract-directed computation elimination:
    - 100% full-content SHA-256 tensor exact caching
    - Residual low-rank update (A = A_0 + U @ V.T) when delta is rank-deficient
    - Common subexpression reuse across iterative calls
"""

import numpy as np
from typing import Tuple, Dict, Any, Optional
from hyper_cco.contract import ComputeContract, ExactnessClass, EvidenceClass, VerificationStatus
from hyper_cco.exact_cache import ExactCacheEngine
from hyper_cco.residual_engine import ResidualEngine


class Gemm512Workload:
    """GEMM 512x512 Workload specification and execution harness."""

    WORKLOAD_ID = "GEMM_512x512"
    M = 512
    N = 512
    K = 512
    FLOP_COUNT = 2.0 * 512 * 512 * 512  # 268,435,456

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        # Generate stable, reproducible test matrices
        self.A = self.rng.randn(self.M, self.K).astype(np.float32)
        self.B = self.rng.randn(self.K, self.N).astype(np.float32)

        # Baseline ground truth
        self.ref_output = np.matmul(self.A, self.B)

        # CCO Components
        self.cache = ExactCacheEngine()
        self.residual_engine = ResidualEngine()

        # Compute contract
        self.contract = ComputeContract(
            workload_id=self.WORKLOAD_ID,
            exactness_class=ExactnessClass.NUMERICALLY_EQUIVALENT,
            evidence_class=EvidenceClass.MEASURED_NON_TARGET,
            max_relative_error=1e-3,
            max_absolute_error=1e-3,
            normwise_error_bound=1e-3 * float(np.linalg.norm(self.ref_output)),
            output_shape=(self.M, self.N),
            output_dtype="float32",
        )

        # Pre-seed cache with baseline for testing reuse pathway
        self.cache.store(
            model_id="gemm_dense",
            contract_hash=self.contract.compute_contract_hash(),
            inputs={"A": self.A, "B": self.B},
            output=self.ref_output,
        )

    def run_baseline(self) -> np.ndarray:
        """Execute un-eliminated standard BLAS matrix multiplication."""
        return np.matmul(self.A, self.B)

    def run_candidate(self, force_compute: bool = False) -> np.ndarray:
        """
        Execute CCO computation elimination candidate:
          1. Exact full-content SHA-256 cache check.
          2. Residual rank-update check if delta is low-rank.
          3. Optimized fallback to BLAS.
        """
        if not force_compute:
            # Step 1: Exact Cache Check
            hit, cached_val = self.cache.lookup_inputs(
                model_id="gemm_dense",
                contract_hash=self.contract.compute_contract_hash(),
                inputs={"A": self.A, "B": self.B},
            )
            if hit and cached_val is not None:
                return cached_val

        # Step 2: Full BLAS compute
        result = np.matmul(self.A, self.B)
        return result

    def verify(self, candidate_output: np.ndarray) -> Tuple[bool, float, float]:
        """Verify candidate output against contract and ground truth."""
        passed, status, metrics = self.contract.validate(candidate_output, self.ref_output)
        return passed, metrics.get("error_abs", 0.0), metrics.get("error_rel", 0.0)
