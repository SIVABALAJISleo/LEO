#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/information_boundary/engine.py
======================================
Phase 3: Information Boundary Engine.

Calculates the minimal sufficient statistic required to determine the requested observable.
"""

import time
from typing import Dict, Any, Tuple, Optional
import numpy as np
from .influence_graph import InfluenceGraph, InformationCategory


class InformationBoundaryEngine:
    """
    Answers: 'What information is sufficient to determine the requested result?'
    Discovers lower-information representations and eliminates redundant subspace data.
    """

    def analyze_matrix_workload(
        self,
        A: np.ndarray,
        B: Optional[np.ndarray] = None,
        target_observable: str = "full_product"
    ) -> Dict[str, Any]:
        """
        Analyzes matrix data to partition into required vs redundant spectral components.
        """
        t0 = time.perf_counter()
        A_f32 = np.asarray(A, dtype=np.float32)
        m, k = A_f32.shape
        total_elements = m * k

        # 1. Sparsity inspection
        exact_zeros = int(np.sum(A_f32 == 0.0))
        sparsity_ratio = exact_zeros / max(total_elements, 1)

        # 2. Fast singular value spectrum analysis
        # For large matrices, subsample to bound overhead < 2ms
        if min(m, k) > 256:
            step_m = max(1, m // 128)
            step_k = max(1, k // 128)
            sub = A_f32[::step_m, ::step_k]
            s = np.linalg.svd(sub, compute_uv=False)
        else:
            s = np.linalg.svd(A_f32, compute_uv=False)

        cum_energy = np.cumsum(s**2) / (np.sum(s**2) + 1e-12)
        rank_95 = int(np.searchsorted(cum_energy, 0.95)) + 1
        rank_99 = int(np.searchsorted(cum_energy, 0.99)) + 1
        effective_rank = min(rank_99, min(m, k))

        # Build formal influence graph
        graph = InfluenceGraph()
        graph.add_node("input_A", category=InformationCategory.REQUIRED_INFORMATION, shape=[m, k])
        if B is not None:
            graph.add_node("input_B", category=InformationCategory.REQUIRED_INFORMATION, shape=list(B.shape))
            graph.add_node("observable_Y", is_observable=True, dependencies=["input_A", "input_B"])
        else:
            graph.add_node("observable_Y", is_observable=True, dependencies=["input_A"])

        # Sufficient dimension: low-rank subspace dimension vs full dimension
        redundant_fraction = max(0.0, 1.0 - (effective_rank / min(m, k)))
        sufficient_statistic_dim = effective_rank

        dt_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "workload_type": "matrix",
            "shape": [m, k],
            "total_elements": total_elements,
            "sparsity_ratio": round(sparsity_ratio, 4),
            "effective_rank_99": effective_rank,
            "effective_rank_95": rank_95,
            "sufficient_rank": sufficient_statistic_dim,
            "redundant_information_ratio": round(redundant_fraction, 4),
            "can_eliminate_dense_full_rank": redundant_fraction > 0.40,
            "analysis_latency_ms": round(dt_ms, 3)
        }

    def analyze_sequence_workload(
        self,
        token_count: int,
        repetitive_tokens: int = 0
    ) -> Dict[str, Any]:
        """
        Analyzes sequential prompt data for semantic information boundaries.
        """
        redundant_ratio = repetitive_tokens / max(token_count, 1)
        return {
            "workload_type": "sequence",
            "total_tokens": token_count,
            "redundant_tokens": repetitive_tokens,
            "required_tokens": token_count - repetitive_tokens,
            "redundant_information_ratio": round(redundant_ratio, 4),
            "can_prune": redundant_ratio >= 0.20
        }
