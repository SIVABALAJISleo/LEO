#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compute_fabric/worker_pool.py
=====================================
Project Omega: Software-Defined Parallel Compute Fabric.
Heterogeneous Worker Pool with Work Stealing and Locality Scheduling.
"""

from __future__ import annotations
import time
from collections import deque
from typing import Dict, List, Any, Optional
import numpy as np

from hyper_x.compute_fabric.work_unit import (
    WorkUnit,
    WorkUnitStatus,
    WorkClassification,
    ExecutionTarget
)
from hyper_x.compute_fabric.virtual_worker import VirtualWorker, WorkerState
from hyper_x.compute_fabric.task_graph import TaskGraph
from hyper_x.compute_fabric.cost_model import FabricCostModel


class FabricWorkerPool:
    """
    Manages physical-to-virtual execution scheduling across the Intel Core i5-12450H
    (4 P-cores, 4 E-cores) and Intel integrated UHD Graphics (48 EUs).
    Implements work stealing, queue balancing, and locality affinity.
    """

    NUM_P_CORES = 4
    NUM_E_CORES = 4
    NUM_UHD_EUS = 48

    def __init__(self, cost_model: Optional[FabricCostModel] = None):
        self.cost_model = cost_model or FabricCostModel()

        # Initialize Virtual Workers mapped to hardware execution domains
        self.cpu_p_workers: List[VirtualWorker] = [
            VirtualWorker(f"cpu_p_core_{i}", ExecutionTarget.CPU, physical_core_id=i)
            for i in range(self.NUM_P_CORES)
        ]
        self.cpu_e_workers: List[VirtualWorker] = [
            VirtualWorker(f"cpu_e_core_{i}", ExecutionTarget.CPU, physical_core_id=i + self.NUM_P_CORES)
            for i in range(self.NUM_E_CORES)
        ]
        # UHD workers: Group 48 EUs into 4 multi-EU dispatchers for efficient queueing
        self.uhd_workers: List[VirtualWorker] = [
            VirtualWorker(f"intel_uhd_cluster_{i}", ExecutionTarget.UHD)
            for i in range(4)
        ]
        self.cache_worker = VirtualWorker("exact_cache_worker", ExecutionTarget.CACHE)
        self.predictor_worker = VirtualWorker("predictor_worker", ExecutionTarget.PREDICTOR)
        self.reconstructor_worker = VirtualWorker("reconstructor_worker", ExecutionTarget.RECONSTRUCTOR)

        self.all_workers: List[VirtualWorker] = (
            self.cpu_p_workers +
            self.cpu_e_workers +
            self.uhd_workers +
            [self.cache_worker, self.predictor_worker, self.reconstructor_worker]
        )

        # Worker local task queues for work stealing
        self.worker_queues: Dict[str, deque[WorkUnit]] = {
            w.worker_id: deque() for w in self.all_workers
        }

    def dispatch_work_unit(self, unit: WorkUnit, *args, **kwargs) -> Any:
        """Selects optimal target and dispatches a single WorkUnit."""
        target = self.cost_model.select_cheapest_target(unit)

        if unit.classification == WorkClassification.CAN_REUSE:
            worker = self.cache_worker
        elif unit.classification == WorkClassification.CAN_PREDICT:
            worker = self.predictor_worker
        elif unit.classification == WorkClassification.CAN_RECONSTRUCT:
            worker = self.reconstructor_worker
        elif target == ExecutionTarget.UHD:
            # Round-robin among UHD clusters
            worker = min(self.uhd_workers, key=lambda w: len(self.worker_queues[w.worker_id]))
        else:
            # Priority >= 10 to P-cores; lower priority to E-cores
            pool = self.cpu_p_workers if unit.priority >= 10 else self.cpu_e_workers
            worker = min(pool, key=lambda w: len(self.worker_queues[w.worker_id]))

        t_est = self.cost_model.estimate_cost(unit, target)
        t0 = time.perf_counter()
        result = worker.assign_and_execute(unit, *args, **kwargs)
        t_meas = (time.perf_counter() - t0) * 1000.0

        # Self-calibrate cost model
        self.cost_model.update_empirical_measurement(target, t_est, t_meas)
        return result

    def execute_graph(self, graph: TaskGraph, *args, **kwargs) -> Dict[str, Any]:
        """
        Executes an entire TaskGraph through the worker pool using topological waves
        and work-stealing when queues become empty.
        """
        t_start = time.perf_counter()
        total_executed = 0
        total_eliminated = 0
        total_reused = 0

        # Process units as they become ready
        while True:
            ready_units = graph.get_ready_units()
            if not ready_units:
                # Check if all units are processed or graph is stalled
                remaining = [u for u in graph.units.values() if u.status == WorkUnitStatus.IDLE]
                if not remaining:
                    break
                # If stalled due to dead-end dependencies, mark remaining eliminated
                for rem in remaining:
                    graph.mark_eliminated(rem.work_id, reason="unresolvable_dependency")
                break

            for unit in ready_units:
                if unit.classification == WorkClassification.CAN_ELIMINATE:
                    unit.mark_eliminated()
                    graph.mark_eliminated(unit.work_id)
                    total_eliminated += 1
                elif unit.classification == WorkClassification.CAN_REUSE:
                    self.dispatch_work_unit(unit, *args, **kwargs)
                    graph.mark_completed(unit.work_id)
                    total_reused += 1
                else:
                    self.dispatch_work_unit(unit, *args, **kwargs)
                    graph.mark_completed(unit.work_id)
                    total_executed += 1

        total_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        return {
            "total_units": len(graph.units),
            "executed_units": total_executed,
            "eliminated_units": total_eliminated,
            "reused_units": total_reused,
            "elapsed_ms": round(total_elapsed_ms, 3),
            "worker_telemetry": [w.get_stats() for w in self.all_workers if w.tasks_executed > 0 or w.tasks_eliminated > 0 or w.tasks_reused > 0]
        }
