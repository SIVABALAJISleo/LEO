"""
hyper/escape_engine/contracts/information_boundary.py
====================================================
VAEE Section 7: Information Boundary Analyzer.

Analyzes the mathematical and information-theoretic requirements of a computational task:
1. Input-output dependency coverage
2. Sparsity and structural redundancy
3. Temporal locality & incremental recomputation potential
4. Rank deficiency and dimensionality bounds
5. Representation work reduction potential
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .schema import ComputationalContract


@dataclasses.dataclass
class InformationBoundaryProfile:
    contract_id: str
    total_input_elements: int
    total_output_elements: int
    sparsity_ratio: float             # Fraction of zeros or ignorable elements
    rank_ratio: float                 # Estimated rank / min(M, N)
    is_sparse: bool                   # Sparsity > 0.5
    is_low_rank: bool                 # Rank ratio < 0.35
    is_symmetric: bool                # Matrix is symmetric
    temporal_locality_potential: bool # Successive calls may share prefix or subregion
    incremental_computation_possible: bool
    can_reduce_representation: bool   # e.g., dense -> CSR or dense -> factored
    unnecessary_intermediates_detected: bool
    theoretical_minimum_operations: Optional[int] = None
    information_barrier_notes: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


class InformationBoundaryAnalyzer:
    """Probes computational workload to establish information boundaries."""

    @staticmethod
    def analyze(
        contract: ComputationalContract,
        input_sample: Any,
        workload_context: Optional[Dict[str, Any]] = None,
    ) -> InformationBoundaryProfile:
        notes = []
        is_sparse = False
        is_low_rank = False
        is_symmetric = False
        can_reduce_representation = False
        unnecessary_intermediates = False
        sparsity_ratio = 0.0
        rank_ratio = 1.0
        in_elements = int(np.prod(contract.input_shape))
        out_elements = int(np.prod(contract.output_shape))

        if isinstance(input_sample, np.ndarray):
            # 1. Sparsity check
            zeros = np.count_nonzero(input_sample == 0)
            sparsity_ratio = float(zeros / max(1, input_sample.size))
            if sparsity_ratio > 0.4:
                is_sparse = True
                can_reduce_representation = True
                notes.append(f"Input is {sparsity_ratio*100:.1f}% sparse; representation bypass viable")

            # 2. Rank & Structural analysis for 2D matrices
            if input_sample.ndim == 2:
                M, N = input_sample.shape
                if M == N and np.allclose(input_sample, input_sample.T, atol=1e-5):
                    is_symmetric = True
                    notes.append("Input matrix is symmetric; redundant off-diagonal computation can be halved")

                if min(M, N) >= 8:
                    try:
                        s = np.linalg.svd(input_sample, compute_uv=False)
                        energy = np.cumsum(s ** 2) / max(1e-12, np.sum(s ** 2))
                        effective_rank = int(np.searchsorted(energy, 0.99)) + 1
                        rank_ratio = float(effective_rank / min(M, N))
                        if rank_ratio <= 0.35:
                            is_low_rank = True
                            can_reduce_representation = True
                            notes.append(f"Matrix exhibits low numerical rank ({effective_rank}/{min(M, N)}); SVD factorization viable")
                    except Exception:
                        pass

        # 3. Output dependency check: is output dimension much smaller than input?
        if out_elements < (in_elements * 0.1) and contract.output_type in ["scalar", "vector"]:
            unnecessary_intermediates = True
            notes.append("Output dimensionality is significantly smaller than input; full matrix materialization is unnecessary")

        # 4. Incremental potential
        incremental = bool(workload_context and workload_context.get("streaming", False))
        if incremental:
            notes.append("Streaming workload context detected; delta residual computation possible")

        # Theoretical minimal operations estimate
        min_ops = None
        if contract.input_type == "matrix" and contract.output_type == "matrix":
            if len(contract.input_shape) == 2 and len(contract.output_shape) == 2:
                M = contract.input_shape[0]
                K = contract.input_shape[1]
                N = contract.output_shape[1]
                # Lower bound for general matrix mult is Omega(N^2)
                min_ops = int(M * N)

        return InformationBoundaryProfile(
            contract_id=contract.contract_id,
            total_input_elements=in_elements,
            total_output_elements=out_elements,
            sparsity_ratio=round(sparsity_ratio, 4),
            rank_ratio=round(rank_ratio, 4),
            is_sparse=is_sparse,
            is_low_rank=is_low_rank,
            is_symmetric=is_symmetric,
            temporal_locality_potential=bool(contract.deterministic),
            incremental_computation_possible=incremental,
            can_reduce_representation=can_reduce_representation,
            unnecessary_intermediates_detected=unnecessary_intermediates,
            theoretical_minimum_operations=min_ops,
            information_barrier_notes=notes,
        )
