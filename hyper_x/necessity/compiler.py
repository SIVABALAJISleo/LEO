#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/necessity/compiler.py
=============================
Phase 4: Necessary-Work Compiler.

Evaluates original workload requirements, computes irreducible remainder,
and formally compiles the exact work breakdown.
"""

from typing import Dict, Any, Optional
import numpy as np
from .work_ledger import WorkBreakdown, WorkLedger


class NecessaryWorkCompiler:
    """Compiles necessary vs eliminable work for candidate pathways."""

    def __init__(self):
        self.ledger = WorkLedger()

    def compile_matrix_work(
        self,
        M: int,
        K: int,
        N: int,
        effective_rank: Optional[int] = None,
        sparsity_ratio: float = 0.0,
        is_exact_cache_hit: bool = False
    ) -> WorkBreakdown:
        """
        Calculates arithmetic operation counts for matrix multiply (M x K) @ (K x N).
        Original brute force: 2 * M * K * N FLOPs.
        """
        original_flops = float(2 * M * K * N)

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
                approximated_flops=eliminable,
                verification_overhead_flops=verification_flops
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
