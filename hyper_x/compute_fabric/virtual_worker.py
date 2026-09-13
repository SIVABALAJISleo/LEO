#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compute_fabric/virtual_worker.py
========================================
Project Omega: Software-Defined Parallel Compute Fabric.
Virtual Worker Abstraction.

CRITICAL ARCHITECTURAL PRINCIPLE:
A VirtualWorker is NOT a simulated physical CUDA core.
It is a software agent / execution slot that services units of useful
computational work across available physical execution units (8 CPU cores, 
48 Intel UHD EUs, L1/L2/L3 caches, and prediction/reconstruction engines).
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Dict, Any, Optional
import numpy as np

from hyper_x.compute_fabric.work_unit import WorkUnit, WorkUnitStatus, WorkClassification, ExecutionTarget


class WorkerState(str, Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    BLOCKED = "BLOCKED"
    COMPLETED = "COMPLETED"


class VirtualWorker:
    """
    Logical worker executing work units assigned by the fabric scheduler.
    Multiplexes logical work units onto physical silicon or computational shortcuts.
    """

    def __init__(
        self,
        worker_id: str,
        target_affinity: ExecutionTarget = ExecutionTarget.CPU,
        physical_core_id: Optional[int] = None
    ):
        self.worker_id = worker_id
        self.target_affinity = target_affinity
        self.physical_core_id = physical_core_id
        self.state = WorkerState.IDLE
        self.current_work_unit: Optional[WorkUnit] = None

        # Empirical Performance Counters
        self.tasks_executed: int = 0
        self.tasks_eliminated: int = 0
        self.tasks_reused: int = 0
        self.total_compute_time_ms: float = 0.0
        self.total_flops_processed: float = 0.0
        self.work_steals_performed: int = 0

    def assign_and_execute(self, unit: WorkUnit, *args, **kwargs) -> Any:
        """Assigns a work unit and dispatches it through its designated computational pathway."""
        self.state = WorkerState.BUSY
        self.current_work_unit = unit
        unit.worker_id = self.worker_id

        t0 = time.perf_counter()
        try:
            if unit.classification == WorkClassification.CAN_ELIMINATE:
                unit.mark_eliminated("eliminated_by_information_boundary")
                self.tasks_eliminated += 1
                res = None
            elif unit.classification == WorkClassification.CAN_REUSE:
                unit.mark_reused("exact_cache_hit")
                self.tasks_reused += 1
                res = kwargs.get("cached_value", unit.result)
            else:
                res = unit.execute(*args, **kwargs)
                self.tasks_executed += 1
                self.total_flops_processed += unit.estimated_cost

            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            self.total_compute_time_ms += elapsed_ms
            return res
        finally:
            self.state = WorkerState.IDLE
            self.current_work_unit = None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "target_affinity": self.target_affinity.value,
            "physical_core_id": self.physical_core_id,
            "state": self.state.value,
            "tasks_executed": self.tasks_executed,
            "tasks_eliminated": self.tasks_eliminated,
            "tasks_reused": self.tasks_reused,
            "total_compute_time_ms": round(self.total_compute_time_ms, 3),
            "total_flops_processed": self.total_flops_processed,
            "work_steals_performed": self.work_steals_performed
        }
