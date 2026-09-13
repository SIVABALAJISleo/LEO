#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compiler/__init__.py
============================
Total GPU Omega: Universal Compiler Ecosystem.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
import numpy as np

from hyper_x.strict.contracts import WorkloadContract, CorrectnessMode
from hyper_x.cws.search import ComputationalWormholeSearch, PathwayCandidate

from .ir import (
    IROperation,
    IRTensorDescriptor,
    IRNode,
    IRGraph
)
from .optimizer import IROptimizer
from .lowering import (
    ExecutableStep,
    ExecutablePlan,
    IRLowerer
)


@dataclass
class CompiledPathway:
    workload_id: str
    selected_candidate: PathwayCandidate
    expected_speedup: float
    fallback_fn: Callable[[], Any]


class HyperCompiler:
    """Compiles workloads into scheduled executable pathways."""

    def __init__(self):
        self.cws = ComputationalWormholeSearch()
        self.optimizer = IROptimizer()
        self.lowerer = IRLowerer()

    def compile(
        self,
        workload_id: str,
        A: np.ndarray,
        B: np.ndarray,
        contract: WorkloadContract
    ) -> CompiledPathway:
        candidates = self.cws.search_matrix_wormholes(A, B, contract)
        best = candidates[0]
        for c in candidates:
            if c.expected_work_reduction > best.expected_work_reduction:
                best = c

        return CompiledPathway(
            workload_id=workload_id,
            selected_candidate=best,
            expected_speedup=1.0 + best.expected_work_reduction * 2.0,
            fallback_fn=lambda: A @ B
        )


__all__ = [
    "IROperation",
    "IRTensorDescriptor",
    "IRNode",
    "IRGraph",
    "IROptimizer",
    "ExecutableStep",
    "ExecutablePlan",
    "IRLowerer",
    "CompiledPathway",
    "HyperCompiler"
]
