"""
hyper_x/cpce/structural_analysis.py
===================================
Structural Analysis and Classification Engine for CPCE.
Detects mathematical structures (Zero, Identity, Diagonal, Sparse, Low-Rank)
with bounded inspection budgets to prevent expensive full-array scanning.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict, Optional, Tuple
import numpy as np

from hyper_x.cpce.types import (
    TaggedMatrix,
    DenseMatrix,
    IdentityMatrix,
    ZeroMatrix,
    DiagonalMatrix,
    SparseMatrix,
    LowRankMatrix,
)
from hyper_x.cpce.ir import CIRNode


@dataclasses.dataclass
class StructuralMetadata:
    """Metadata characterizing the mathematical structure of a tensor."""
    structure_tag: str  # DENSE, IDENTITY, ZERO, DIAGONAL, SPARSE, LOW_RANK
    is_identity: bool = False
    is_zero: bool = False
    is_diagonal: bool = False
    is_sparse: bool = False
    is_low_rank: bool = False
    sparsity_ratio: float = 0.0
    estimated_rank: Optional[int] = None
    confidence: float = 1.0


class StructuralAnalyzer:
    """
    Performs fast, budget-bounded mathematical structure discovery.
    """

    def __init__(self, max_sample_elements: int = 4096):
        self.max_sample_elements = max_sample_elements

    def analyze(self, value: Any) -> StructuralMetadata:
        """Discovers mathematical structure of the operand."""
        # 1. Direct inspection of TaggedMatrix instances
        if isinstance(value, TaggedMatrix):
            tag = value.structure_type
            if isinstance(value, IdentityMatrix):
                return StructuralMetadata(structure_tag="IDENTITY", is_identity=True, confidence=1.0)
            if isinstance(value, ZeroMatrix):
                return StructuralMetadata(structure_tag="ZERO", is_zero=True, sparsity_ratio=1.0, confidence=1.0)
            if isinstance(value, DiagonalMatrix):
                return StructuralMetadata(structure_tag="DIAGONAL", is_diagonal=True, confidence=1.0)
            if isinstance(value, SparseMatrix):
                return StructuralMetadata(structure_tag="SPARSE", is_sparse=True, sparsity_ratio=value.sparsity, confidence=1.0)
            if isinstance(value, LowRankMatrix):
                return StructuralMetadata(structure_tag="LOW_RANK", is_low_rank=True, estimated_rank=value.rank, confidence=1.0)
            return StructuralMetadata(structure_tag="DENSE")

        # 2. Raw NumPy Array Inspection
        if not isinstance(value, np.ndarray):
            try:
                arr = np.asarray(value)
            except Exception:
                return StructuralMetadata(structure_tag="DENSE")
        else:
            arr = value

        if arr.ndim != 2:
            return StructuralMetadata(structure_tag="DENSE")

        rows, cols = arr.shape
        total_elements = rows * cols

        # Check for Zero Matrix (budget bounded)
        if total_elements <= self.max_sample_elements:
            if not np.any(arr):
                return StructuralMetadata(structure_tag="ZERO", is_zero=True, sparsity_ratio=1.0, confidence=1.0)
        else:
            # Sample random locations
            rng = np.random.RandomState(42)
            sample_r = rng.randint(0, rows, size=min(128, rows))
            sample_c = rng.randint(0, cols, size=min(128, cols))
            if np.all(arr[sample_r, sample_c] == 0):
                # Verify exactness if small enough, otherwise dense
                pass

        # Check for Identity Matrix (square matrices only)
        if rows == cols:
            if total_elements <= self.max_sample_elements:
                # Fast diagonal check
                diag = np.diagonal(arr)
                if np.all(diag == 1.0):
                    # Check off-diagonal elements
                    off_diag_sum = np.sum(np.abs(arr)) - np.sum(diag)
                    if off_diag_sum == 0.0:
                        return StructuralMetadata(structure_tag="IDENTITY", is_identity=True, confidence=1.0)
                elif np.all(diag != 0.0):
                    # Check if purely diagonal
                    off_diag_sum = np.sum(np.abs(arr)) - np.sum(np.abs(diag))
                    if off_diag_sum == 0.0:
                        return StructuralMetadata(structure_tag="DIAGONAL", is_diagonal=True, confidence=1.0)

        # Check Sparsity
        if total_elements <= self.max_sample_elements:
            nnz = np.count_nonzero(arr)
            sparsity = 1.0 - (nnz / total_elements)
            if sparsity >= 0.70:
                return StructuralMetadata(
                    structure_tag="SPARSE",
                    is_sparse=True,
                    sparsity_ratio=round(sparsity, 3),
                    confidence=1.0,
                )

        return StructuralMetadata(structure_tag="DENSE")

    def tag_node(self, node: CIRNode, value: Any) -> CIRNode:
        """Annotates CIRNode with detected structural metadata."""
        meta = self.analyze(value)
        node.structural_tag = meta.structure_tag
        if meta.is_zero:
            node.resource_cost_flops = 0.0
        elif meta.is_identity:
            node.resource_cost_flops = 0.0
        return node
