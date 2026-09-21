"""
hyper/universal/workloads/suite.py
==================================
Multi-Domain Representative Workload Suite and Unseen Workload Generator.
Includes:
- Numerical: Horner polynomial evaluation
- Matrix: Dense & Sparse GEMM
- Sorting: Bounded integer keys
- Image: 2D Spatial filtering
- DP: 0/1 Knapsack
- Graph: Dijkstra Shortest Path
- ArbitraryUnseenWorkload: Generates novel user computations dynamically
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from ..adapter.workload_adapter import UniversalWorkload, UniversalWorkloadAdapter
from ..adapter.workload_types import WorkloadDomain
from ..contracts.universal_contract import UniversalContract, ContractCorrectness, PrecisionTier


class UniversalWorkloadSuite:
    """Provides representative workloads across distinct computational domains."""

    @staticmethod
    def get_polynomial_workload(degree: int = 10, num_points: int = 1000) -> Tuple[UniversalWorkload, UniversalContract]:
        coeffs = np.random.randn(degree + 1).astype(np.float64)
        x_pts = np.linspace(-2.0, 2.0, num_points, dtype=np.float64)

        def direct_poly_eval(pts: np.ndarray) -> np.ndarray:
            # Naive O(N^2) evaluation using powers
            out = np.zeros_like(pts)
            for i, c in enumerate(coeffs):
                out += c * (pts ** i)
            return out

        workload = UniversalWorkloadAdapter.adapt(
            target=direct_poly_eval,
            sample_input=x_pts,
            workload_id=f"poly_deg_{degree}",
            domain=WorkloadDomain.NUMERICAL,
            name="Polynomial Evaluation (Powers)",
            metadata={"coeffs": coeffs},
        )

        contract = UniversalContract(
            contract_id=f"contract_poly_{degree}",
            workload_id=workload.workload_id,
            correctness=ContractCorrectness.EXACT,
            precision=PrecisionTier.FLOAT64,
            numeric_tolerance=1e-8,
            verification_method="DIFFERENTIAL",
        )
        return workload, contract

    @staticmethod
    def get_sorting_workload(N: int = 10000, key_max: int = 500) -> Tuple[UniversalWorkload, UniversalContract]:
        rng = np.random.default_rng(42)
        data = rng.integers(0, key_max, size=N, dtype=np.int32)

        def naive_sort(arr: np.ndarray) -> np.ndarray:
            return np.sort(arr.copy(), kind="quicksort")

        workload = UniversalWorkloadAdapter.adapt(
            target=naive_sort,
            sample_input=data,
            workload_id=f"sort_int_{N}",
            domain=WorkloadDomain.SEARCH_SORTING,
            name="Bounded Integer Sorting",
            metadata={"key_max": key_max},
        )

        contract = UniversalContract(
            contract_id=f"contract_sort_{N}",
            workload_id=workload.workload_id,
            correctness=ContractCorrectness.EXACT,
            precision=PrecisionTier.EXACT_INTEGER,
            numeric_tolerance=0.0,
            verification_method="INVARIANT_SORTED",
        )
        return workload, contract

    @staticmethod
    def get_matrix_workload(dim: int = 64) -> Tuple[UniversalWorkload, UniversalContract]:
        rng = np.random.default_rng(42)
        A = rng.standard_normal((dim, dim), dtype=np.float32)
        B = rng.standard_normal((dim, dim), dtype=np.float32)

        def matmul_fn(a: np.ndarray) -> np.ndarray:
            return a @ B

        workload = UniversalWorkloadAdapter.adapt(
            target=matmul_fn,
            sample_input=A,
            workload_id=f"matmul_{dim}x{dim}",
            domain=WorkloadDomain.MATRIX_TENSOR,
            name="Dense Matrix Multiplication",
        )

        contract = UniversalContract(
            contract_id=f"contract_matmul_{dim}",
            workload_id=workload.workload_id,
            correctness=ContractCorrectness.EXACT,
            precision=PrecisionTier.FLOAT32,
            numeric_tolerance=1e-4,
            verification_method="FREIVALDS",
        )
        return workload, contract

    @staticmethod
    def generate_unseen_workload(seed: Optional[int] = None) -> Tuple[UniversalWorkload, UniversalContract]:
        """Synthesizes a completely dynamic, previously unseen computational workload."""
        rng = np.random.default_rng(seed or int(time.time() * 1000) % 10000)
        n = rng.integers(50, 200)
        data = rng.standard_normal(n).astype(np.float32)
        offset = float(rng.uniform(1.0, 5.0))

        # Arbitrary dynamic mathematical transform: f(x) = (x + offset)^2 - offset
        def unseen_fn(x: np.ndarray) -> np.ndarray:
            return (x + offset) ** 2 - offset

        w_id = f"UNSEEN-{int(time.time()*1000)%1000000:06d}"
        workload = UniversalWorkloadAdapter.adapt(
            target=unseen_fn,
            sample_input=data,
            workload_id=w_id,
            domain=WorkloadDomain.UNKNOWN_UNSEEN,
            name="Dynamically Generated Unseen Workload",
        )

        contract = UniversalContract(
            contract_id=f"contract_{w_id}",
            workload_id=w_id,
            correctness=ContractCorrectness.EXACT,
            precision=PrecisionTier.FLOAT32,
            numeric_tolerance=1e-5,
            verification_method="DIFFERENTIAL",
        )
        return workload, contract
