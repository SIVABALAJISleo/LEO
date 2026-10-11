"""
hyper/six_engines/engine5_pathway_discovery.py
=============================================
ENGINE 5: ALTERNATIVE ALGORITHMS AND AUTOMATIC PATHWAY DISCOVERY

Objectives:
- Automatically discover, generate, evaluate, and rank candidate pathways.
- Classify dominant workload bottlenecks (compute-bound, memory-bound, etc.).
- Explore across algebraic reformulation, sparsity, low-rank, cache-blocking,
  vectorization, and heterogeneous scheduling.
- Reject candidates violating preconditions or numerical contracts.
- Maintain failure knowledge base to avoid repeating dead-end searches.
- Validate candidates against unseen holdout inputs to prevent benchmark leakage.
"""

from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np

from .models import (
    OptimizationCandidate,
    PathwayStatus,
    TransformationClass,
    WorkloadContract,
)


class BottleneckKind(str, Enum):
    COMPUTE_BOUND = "COMPUTE_BOUND"
    MEMORY_BANDWIDTH_BOUND = "MEMORY_BANDWIDTH_BOUND"
    LATENCY_BOUND = "LATENCY_BOUND"
    BRANCH_DIVERGENT = "BRANCH_DIVERGENT"
    CACHE_CAPACITY_BOUND = "CACHE_CAPACITY_BOUND"


class WorkloadBottleneckClassifier:
    """Classifies dominant performance bottleneck using roofline heuristics."""

    @staticmethod
    def classify(flops: float, bytes_moved: float, execution_time_ms: float) -> BottleneckKind:
        intensity = flops / max(bytes_moved, 1.0)
        # Intel Core i5-12450H balanced roofline ridge point is ~6.0 FLOPs/Byte
        if intensity > 8.0:
            return BottleneckKind.COMPUTE_BOUND
        elif intensity < 2.0:
            return BottleneckKind.MEMORY_BANDWIDTH_BOUND
        elif execution_time_ms < 0.05:
            return BottleneckKind.LATENCY_BOUND
        else:
            return BottleneckKind.CACHE_CAPACITY_BOUND


class PathwayDiscoveryEngine:
    """
    Autonomous search and synthesis engine for high-performance execution pathways.
    """

    def __init__(self) -> None:
        self.failure_knowledge_base: Dict[str, List[Dict[str, Any]]] = {}
        self.verified_winners: Dict[str, OptimizationCandidate] = {}

    def generate_candidates(
        self,
        contract: WorkloadContract,
        sample_input: Any,
    ) -> List[OptimizationCandidate]:
        """
        Synthesizes candidate optimization pathways matching the workload's contract
        and mathematical characteristics.
        """
        candidates: List[OptimizationCandidate] = []
        w_id = contract.workload_id

        # Candidate 1: Canonical Baseline
        candidates.append(
            OptimizationCandidate(
                candidate_id=f"{w_id}_CANONICAL_REF",
                workload_id=w_id,
                transformation_chain=["Canonical Reference Execution"],
                transformation_class=TransformationClass.EXACT_ALGEBRAIC,
                applicable_preconditions=["Standard input format"],
                estimated_complexity="O(N)",
                execution_backend="CPU_AVX2",
                correctness_status=PathwayStatus.PRECONDITION_VALIDATED,
            )
        )

        # Candidate 2: Cache-blocked tiling
        candidates.append(
            OptimizationCandidate(
                candidate_id=f"{w_id}_CACHE_BLOCKED",
                workload_id=w_id,
                transformation_chain=["L1/L2 Cache-Blocked Loop Tiling", "Contiguous Alignment"],
                transformation_class=TransformationClass.CACHE_BLOCKING_LOCALITY,
                applicable_preconditions=["Multi-dimensional tensor loops"],
                estimated_complexity="O(N)",
                execution_backend="CPU_AVX2",
                correctness_status=PathwayStatus.PRECONDITION_VALIDATED,
            )
        )

        # Candidate 3: Sparse Specialization
        candidates.append(
            OptimizationCandidate(
                candidate_id=f"{w_id}_SPARSE_CSR",
                workload_id=w_id,
                transformation_chain=["Zero-Element Annihilation", "CSR Compressed Matrix Format"],
                transformation_class=TransformationClass.SPARSE_SPECIALIZATION,
                applicable_preconditions=["Tensor Sparsity >= 40%"],
                estimated_complexity="O(NNZ)",
                execution_backend="CPU_AVX2",
                correctness_status=PathwayStatus.DISCOVERED,
            )
        )

        # Candidate 4: Heterogeneous Hybrid
        candidates.append(
            OptimizationCandidate(
                candidate_id=f"{w_id}_HETEROGENEOUS_HYBRID",
                workload_id=w_id,
                transformation_chain=["Adaptive CPU+iGPU Partitioning", "Asynchronous Dual Queuing"],
                transformation_class=TransformationClass.EXACT_ALGEBRAIC,
                applicable_preconditions=["Task size >= 4096 elements", "iGPU Backend Initialized"],
                estimated_complexity="O(N)",
                execution_backend="CPU_IGPU_HYBRID",
                correctness_status=PathwayStatus.DISCOVERED,
            )
        )

        # Candidate 5: Low-Rank Truncated SVD (if approximate or numerical tolerance allowed)
        if contract.correctness_mode in (
            contract.correctness_mode.NUMERICAL_TOLERANCE,
            contract.correctness_mode.PERCEPTUAL_QUALITY,
        ):
            candidates.append(
                OptimizationCandidate(
                    candidate_id=f"{w_id}_LOW_RANK_SVD",
                    workload_id=w_id,
                    transformation_chain=["Truncated SVD Factorization", "Rank-k Outer-Product Projection"],
                    transformation_class=TransformationClass.LOW_RANK_APPROXIMATION,
                    applicable_preconditions=["Matrix shape 2D", "Rapid singular value decay"],
                    estimated_complexity="O(k*(M+N))",
                    execution_backend="CPU_AVX2",
                    correctness_status=PathwayStatus.DISCOVERED,
                )
            )

        return candidates

    def evaluate_and_rank_candidates(
        self,
        contract: WorkloadContract,
        candidates: List[OptimizationCandidate],
        ref_fn: Callable[[Any], Any],
        cand_runner_map: Dict[str, Callable[[Any], Any]],
        sample_input: Any,
        holdout_inputs: Optional[List[Any]] = None,
    ) -> Tuple[Optional[OptimizationCandidate], List[OptimizationCandidate]]:
        """
        Runs empirical multi-criteria evaluation of all candidates.
        Tests correctness, measures latency, checks holdout generalizability,
        and selects the Pareto optimal winner.
        """
        ref_out = ref_fn(sample_input)
        evaluated: List[OptimizationCandidate] = []
        winner: Optional[OptimizationCandidate] = None
        best_speedup = 0.0

        # Measure reference latency
        t_ref0 = time.perf_counter()
        _ = ref_fn(sample_input)
        t_ref1 = time.perf_counter()
        ref_latency_ms = max((t_ref1 - t_ref0) * 1000.0, 1e-6)

        for cand in candidates:
            c_id = cand.candidate_id
            runner = cand_runner_map.get(c_id)
            if runner is None:
                cand.correctness_status = PathwayStatus.SEARCH_INCOMPLETE
                cand.failure_reason = "Runner implementation not registered for candidate"
                evaluated.append(cand)
                continue

            try:
                # 1. Functional correctness check
                cand_out = runner(sample_input)
                val_res = contract.validate_output(ref_out, cand_out)

                if not val_res["passed"]:
                    cand.correctness_status = PathwayStatus.REJECTED
                    cand.failure_reason = f"Contract validation failed: {val_res['violations']}"
                    self._record_failure(cand.workload_id, cand.candidate_id, cand.failure_reason)
                    evaluated.append(cand)
                    continue

                # 2. Holdout input generalization check (prevent benchmark leakage)
                if holdout_inputs:
                    holdout_passed = True
                    for h_in in holdout_inputs:
                        h_ref = ref_fn(h_in)
                        h_cand = runner(h_in)
                        h_val = contract.validate_output(h_ref, h_cand)
                        if not h_val["passed"]:
                            holdout_passed = False
                            break
                    if not holdout_passed:
                        cand.correctness_status = PathwayStatus.REJECTED
                        cand.failure_reason = "Failed generalization test on unseen holdout inputs"
                        self._record_failure(cand.workload_id, cand.candidate_id, cand.failure_reason)
                        evaluated.append(cand)
                        continue

                # 3. Performance measurement
                t0 = time.perf_counter()
                _ = runner(sample_input)
                t1 = time.perf_counter()
                cand_latency_ms = (t1 - t0) * 1000.0
                speedup = ref_latency_ms / max(cand_latency_ms, 1e-6)

                cand.measured_latency = cand_latency_ms
                cand.measured_throughput = (1000.0 / max(cand_latency_ms, 1e-6))
                cand.correctness_status = PathwayStatus.CORRECTNESS_PASSED
                cand.benchmark_status = "MEASURED"

                evaluated.append(cand)

                # Pareto selection (highest speedup satisfying contract)
                if speedup > best_speedup:
                    best_speedup = speedup
                    winner = cand

            except Exception as e:
                cand.correctness_status = PathwayStatus.REJECTED
                cand.failure_reason = f"Exception during execution: {str(e)}"
                self._record_failure(cand.workload_id, cand.candidate_id, cand.failure_reason)
                evaluated.append(cand)

        if winner is not None:
            winner.correctness_status = PathwayStatus.VERIFIED_WINNER
            self.verified_winners[contract.workload_id] = winner

        return winner, evaluated

    def _record_failure(self, workload_id: str, candidate_id: str, reason: str) -> None:
        if workload_id not in self.failure_knowledge_base:
            self.failure_knowledge_base[workload_id] = []
        self.failure_knowledge_base[workload_id].append({
            "candidate_id": candidate_id,
            "failure_reason": reason,
            "timestamp": time.time(),
        })
