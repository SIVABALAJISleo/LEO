#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/necessity/compiler.py
=============================
Phase 4: Necessary-Work Compiler.

Evaluates original workload requirements, computes irreducible remainder,
and formally compiles the exact work breakdown via dependency DAG analysis.
Attempts: DELETE, REUSE, MERGE, FACTOR, REORDER, SPARSE, LOW_RANK, COMPRESS,
          APPROXIMATE, PREDICT, RECONSTRUCT, TILE, FUSE, STREAM, SPECIALIZE.
"""

from typing import Dict, Any, Optional, List
import numpy as np
from .work_ledger import WorkBreakdown, WorkLedger, DAGOperationNode, OperationTransform


class NecessaryWorkCompiler:
    """Compiles necessary vs eliminable work for candidate pathways."""

    def __init__(self):
        self.ledger = WorkLedger()

    def build_matrix_dag(
        self,
        M: int,
        K: int,
        N: int,
        effective_rank: Optional[int] = None,
        sparsity_ratio: float = 0.0,
        is_exact_cache_hit: bool = False
    ) -> List[DAGOperationNode]:
        """Builds an operation DAG representing the candidate transformations."""
        nodes: List[DAGOperationNode] = []

        if is_exact_cache_hit:
            nodes.append(DAGOperationNode(
                operation_id="op_exact_reuse",
                operation_type=OperationTransform.REUSE.value,
                estimated_cost=0.0,
                eliminability=True,
                reuseability=True
            ))
            return nodes

        r = effective_rank if effective_rank is not None else min(M, K, N)
        if r < min(M, K, N):
            nodes.append(DAGOperationNode(
                operation_id="op_factor_left",
                operation_type=OperationTransform.FACTOR.value,
                estimated_cost=float(2 * M * r * K),
                eliminability=False
            ))
            nodes.append(DAGOperationNode(
                operation_id="op_low_rank_mult",
                operation_type=OperationTransform.LOW_RANK.value,
                dependencies=["op_factor_left"],
                estimated_cost=float(2 * M * r * N),
                eliminability=False
            ))
        elif sparsity_ratio > 0.0:
            nodes.append(DAGOperationNode(
                operation_id="op_sparse_skip",
                operation_type=OperationTransform.SPARSE.value,
                estimated_cost=float(2 * M * K * N * (1.0 - sparsity_ratio)),
                eliminability=True
            ))
        else:
            nodes.append(DAGOperationNode(
                operation_id="op_dense_irreducible",
                operation_type=OperationTransform.SPECIALIZE.value,
                estimated_cost=float(2 * M * K * N),
                eliminability=False
            ))

        return nodes

    def compile_matrix_work(
        self,
        M: int,
        K: int,
        N: int,
        effective_rank: Optional[int] = None,
        sparsity_ratio: float = 0.0,
        is_exact_cache_hit: bool = False,
        is_fallback: bool = False,
        reconstructed_ratio: float = 0.0,
        predicted_ratio: float = 0.0
    ) -> WorkBreakdown:
        """
        Calculates arithmetic operation counts for matrix multiply (M x K) @ (K x N).
        Original brute force: 2 * M * K * N FLOPs.
        """
        original_flops = float(2 * M * K * N)

        if is_fallback:
            breakdown = WorkBreakdown(
                original_flops=original_flops,
                necessary_flops=original_flops,
                eliminable_flops=0.0,
                fallback_flops=original_flops,
                verification_overhead_flops=float(M * N)
            )
            return self.ledger.record(breakdown)

        if is_exact_cache_hit:
            # All compute eliminated; lookup cost is negligible O(1)
            breakdown = WorkBreakdown(
                original_flops=original_flops,
                necessary_flops=0.0,
                eliminable_flops=original_flops,
                reused_flops=original_flops,
                verification_overhead_flops=float(M * N) # Hash verification
            )
            return self.ledger.record(breakdown)

        r = effective_rank if effective_rank is not None else min(M, K, N)
        is_low_rank = (r < min(M, K, N))

        if is_low_rank:
            # Low-rank factorization: (M x r) @ (r x N) -> 2 * M * r * N + decomposition overhead
            low_rank_flops = float(2 * M * r * N)
            verification_flops = float(3 * (M * r + r * N)) # Freivalds probe
            eliminable = max(0.0, original_flops - (low_rank_flops + verification_flops))

            breakdown = WorkBreakdown(
                original_flops=original_flops,
                necessary_flops=low_rank_flops,
                eliminable_flops=eliminable,
                reformulated_flops=low_rank_flops,
                approximated_flops=eliminable,
                verification_overhead_flops=verification_flops
            )
        elif reconstructed_ratio > 0.0:
            reconstructed_flops = float(original_flops * reconstructed_ratio)
            necessary = original_flops - reconstructed_flops
            breakdown = WorkBreakdown(
                original_flops=original_flops,
                necessary_flops=necessary,
                eliminable_flops=reconstructed_flops,
                reconstructed_flops=reconstructed_flops,
                verification_overhead_flops=float(M * N * 0.1)
            )
        elif predicted_ratio > 0.0:
            predicted_flops = float(original_flops * predicted_ratio)
            necessary = original_flops - predicted_flops
            breakdown = WorkBreakdown(
                original_flops=original_flops,
                necessary_flops=necessary,
                eliminable_flops=predicted_flops,
                predicted_flops=predicted_flops,
                verification_overhead_flops=float(M * N * 0.2)
            )
        elif sparsity_ratio > 0.0:
            # Sparse execution: only non-zero entries
            active_fraction = max(0.01, 1.0 - sparsity_ratio)
            sparse_flops = float(original_flops * active_fraction)
            breakdown = WorkBreakdown(
                original_flops=original_flops,
                necessary_flops=sparse_flops,
                eliminable_flops=original_flops - sparse_flops,
                verification_overhead_flops=0.0
            )
        else:
            # Irreducible dense full-rank: 100% of work is necessary
            breakdown = WorkBreakdown(
                original_flops=original_flops,
                necessary_flops=original_flops,
                eliminable_flops=0.0
            )

        return self.ledger.record(breakdown)
