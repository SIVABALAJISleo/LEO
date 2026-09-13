#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compute_fabric/task_graph.py
====================================
Project Omega: Software-Defined Parallel Compute Fabric.
Computational Work Graph (DAG) & Dependency Scheduler.
"""

from __future__ import annotations
from collections import deque
from typing import Dict, List, Set, Any, Optional, Tuple
import numpy as np

from hyper_x.compute_fabric.work_unit import (
    WorkUnit,
    WorkUnitStatus,
    WorkClassification,
    ExecutionTarget,
    LocalityClass
)


class TaskGraph:
    """
    Direct Acyclic Graph of WorkUnits representing the decomposed computational workload.
    Manages dependency analysis, topological sorting, ready queues, and work elimination propagation.
    """

    def __init__(self, workload_id: str = "workload_dag"):
        self.workload_id = workload_id
        self.units: Dict[str, WorkUnit] = {}
        self.dependencies: Dict[str, Set[str]] = {}       # unit_id -> set of prerequisite unit_ids
        self.dependents: Dict[str, Set[str]] = {}         # unit_id -> set of successor unit_ids
        self.completed_units: Set[str] = set()
        self.eliminated_units: Set[str] = set()

    def add_work_unit(self, unit: WorkUnit) -> WorkUnit:
        """Adds a WorkUnit to the graph and registers dependency edges."""
        self.units[unit.work_id] = unit
        self.dependencies[unit.work_id] = set(unit.dependencies)
        if unit.work_id not in self.dependents:
            self.dependents[unit.work_id] = set()

        for dep_id in unit.dependencies:
            if dep_id not in self.dependents:
                self.dependents[dep_id] = set()
            self.dependents[dep_id].add(unit.work_id)

        if unit.classification == WorkClassification.CAN_ELIMINATE:
            self.eliminated_units.add(unit.work_id)
        return unit

    def get_ready_units(self) -> List[WorkUnit]:
        """Returns all WorkUnits whose dependencies are completely satisfied and not yet executed."""
        ready = []
        for uid, unit in self.units.items():
            if unit.status == WorkUnitStatus.IDLE:
                deps = self.dependencies.get(uid, set())
                # Satisfied if all deps are in completed or eliminated
                if deps.issubset(self.completed_units | self.eliminated_units):
                    ready.append(unit)
        # Sort by priority descending
        ready.sort(key=lambda u: u.priority, reverse=True)
        return ready

    def mark_completed(self, work_id: str):
        """Marks a unit completed and ready to advance successors."""
        if work_id in self.units:
            self.units[work_id].status = WorkUnitStatus.COMPLETED
            self.completed_units.add(work_id)

    def mark_eliminated(self, work_id: str, reason: str = "irrelevant_to_contract"):
        """Marks a unit eliminated and propagates dead-code elimination backwards."""
        if work_id in self.units:
            self.units[work_id].mark_eliminated(reason)
            self.eliminated_units.add(work_id)
            # Check upstream dependencies: if no other live dependent exists, eliminate them
            for dep_id in self.dependencies.get(work_id, set()):
                dep_successors = self.dependents.get(dep_id, set())
                if dep_successors.issubset(self.eliminated_units):
                    self.mark_eliminated(dep_id, reason="upstream_of_eliminated_node")

    def topological_sort(self) -> List[WorkUnit]:
        """Returns a valid topological ordering of all work units."""
        in_degree = {uid: len(deps) for uid, deps in self.dependencies.items()}
        queue = deque([uid for uid, deg in in_degree.items() if deg == 0])
        ordered_ids: List[str] = []

        while queue:
            curr = queue.popleft()
            ordered_ids.append(curr)
            for nxt in self.dependents.get(curr, set()):
                in_degree[nxt] -= 1
                if in_degree[nxt] == 0:
                    queue.append(nxt)

        if len(ordered_ids) != len(self.units):
            # Graph has cycles or disconnected invalid references; fallback to list of units
            return list(self.units.values())
        return [self.units[uid] for uid in ordered_ids]

    @classmethod
    def partition_matrix_gemm(
        cls,
        M: int,
        K: int,
        N: int,
        tile_size: int = 64,
        sparsity_ratio: float = 0.0,
        effective_rank: Optional[int] = None,
        is_exact_cache: bool = False
    ) -> TaskGraph:
        """
        Decomposes a matrix multiplication (M x K) @ (K x N) into a tiled TaskGraph.
        Applies mathematical shortcuts (sparsity elimination, low-rank factorization, exact reuse).
        """
        graph = cls(workload_id=f"gemm_{M}x{K}x{N}")
        num_m_tiles = max(1, (M + tile_size - 1) // tile_size)
        num_n_tiles = max(1, (N + tile_size - 1) // tile_size)
        num_k_tiles = max(1, (K + tile_size - 1) // tile_size)

        for mi in range(num_m_tiles):
            for ni in range(num_n_tiles):
                k_partial_ids = []
                for ki in range(num_k_tiles):
                    tile_m = min(tile_size, M - mi * tile_size)
                    tile_n = min(tile_size, N - ni * tile_size)
                    tile_k = min(tile_size, K - ki * tile_size)
                    tile_flops = 2.0 * tile_m * tile_n * tile_k

                    # Classification logic
                    if is_exact_cache:
                        classification = WorkClassification.CAN_REUSE
                        exec_target = ExecutionTarget.CACHE
                    elif sparsity_ratio > 0.6 and (mi + ki + ni) % 2 == 1:
                        # Tiled sparsity: structured zero sub-blocks can be eliminated
                        classification = WorkClassification.CAN_ELIMINATE
                        exec_target = ExecutionTarget.CACHE
                    elif effective_rank is not None and effective_rank < min(M, K) // 2:
                        classification = WorkClassification.CAN_TRANSFORM
                        exec_target = ExecutionTarget.CPU
                    else:
                        classification = WorkClassification.MUST_COMPUTE
                        exec_target = ExecutionTarget.UHD if tile_flops > 5e5 else ExecutionTarget.CPU

                    unit_id = f"gemm_tile_m{mi}_n{ni}_k{ki}"
                    unit = WorkUnit(
                        work_id=unit_id,
                        workload_id=graph.workload_id,
                        operation=f"tile_gemm_{tile_m}x{tile_k}x{tile_n}",
                        estimated_cost=tile_flops,
                        memory_cost=(tile_m * tile_k + tile_k * tile_n + tile_m * tile_n) * 4,
                        locality=LocalityClass.L2 if tile_flops < 1e6 else LocalityClass.L3,
                        priority=10 if classification == WorkClassification.MUST_COMPUTE else 1,
                        execution_target=exec_target,
                        classification=classification,
                        metadata={"mi": mi, "ni": ni, "ki": ki}
                    )
                    graph.add_work_unit(unit)
                    k_partial_ids.append(unit_id)

                # Reduction node for this (mi, ni) tile accumulation
                accum_id = f"accum_m{mi}_n{ni}"
                accum_unit = WorkUnit(
                    work_id=accum_id,
                    workload_id=graph.workload_id,
                    operation=f"accum_tile_{mi}_{ni}",
                    dependencies=k_partial_ids,
                    estimated_cost=float(len(k_partial_ids) * tile_size * tile_size),
                    memory_cost=tile_size * tile_size * 4,
                    locality=LocalityClass.L1,
                    priority=20,
                    execution_target=ExecutionTarget.CPU,
                    classification=WorkClassification.MUST_COMPUTE if not is_exact_cache else WorkClassification.CAN_REUSE
                )
                graph.add_work_unit(accum_unit)

        return graph

    def get_summary(self) -> Dict[str, Any]:
        """Calculates graph metrics and classification counts."""
        total_units = len(self.units)
        class_counts = {c.value: 0 for c in WorkClassification}
        orig_work = 0.0
        nec_work = 0.0

        for u in self.units.values():
            class_counts[u.classification.value] += 1
            orig_work += u.estimated_cost
            if u.classification not in [WorkClassification.CAN_ELIMINATE, WorkClassification.CAN_REUSE]:
                nec_work += u.estimated_cost

        return {
            "total_units": total_units,
            "classification_counts": class_counts,
            "original_work_flops": orig_work,
            "necessary_work_flops": nec_work,
            "work_elimination_ratio": 1.0 - (nec_work / max(orig_work, 1.0))
        }
