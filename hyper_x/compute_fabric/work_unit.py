#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compute_fabric/work_unit.py
===================================
Project Omega: Software-Defined Parallel Compute Fabric.
Work Unit Abstraction: A discrete, schedulable unit of useful computational work.

IMPORTANT:
A virtual work unit is NOT a fake CUDA core.
It represents a discrete unit of useful computational work (e.g. matrix tile,
sparse sub-block, residual update, attention token, verification unit).
"""

from __future__ import annotations
import uuid
import time
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
import numpy as np


class WorkUnitStatus(str, Enum):
    IDLE = "IDLE"
    ASSIGNED = "ASSIGNED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    ELIMINATED = "ELIMINATED"
    REUSED = "REUSED"
    FAILED = "FAILED"


class WorkClassification(str, Enum):
    MUST_COMPUTE = "MUST_COMPUTE"
    CAN_REUSE = "CAN_REUSE"
    CAN_ELIMINATE = "CAN_ELIMINATE"
    CAN_TRANSFORM = "CAN_TRANSFORM"
    CAN_APPROXIMATE = "CAN_APPROXIMATE"
    CAN_PREDICT = "CAN_PREDICT"
    CAN_RECONSTRUCT = "CAN_RECONSTRUCT"
    UNKNOWN = "UNKNOWN"


class ExecutionTarget(str, Enum):
    CPU = "CPU"
    UHD = "UHD"
    CPU_UHD = "CPU+UHD"
    CACHE = "CACHE"
    PREDICTOR = "PREDICTOR"
    RECONSTRUCTOR = "RECONSTRUCTOR"
    FALLBACK = "FALLBACK"


class LocalityClass(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    RAM = "RAM"
    SHARED_UNIFIED = "SHARED_UNIFIED"


class WorkUnit:
    """
    Encapsulates a single atomic node of computational work scheduled on the fabric.
    """

    def __init__(
        self,
        work_id: Optional[str] = None,
        workload_id: str = "generic_workload",
        operation: str = "tile_gemm",
        dependencies: Optional[List[str]] = None,
        estimated_cost: float = 1.0,
        measured_cost: float = 0.0,
        memory_cost: int = 1024,
        data_dependencies: Optional[List[str]] = None,
        locality: LocalityClass = LocalityClass.L2,
        priority: int = 0,
        correctness_requirement: str = "NUMERICAL_TOLERANCE_1E-4",
        execution_target: ExecutionTarget = ExecutionTarget.CPU,
        verification_requirement: str = "FAIL_CLOSED_CONJUNCTION",
        classification: WorkClassification = WorkClassification.MUST_COMPUTE,
        compute_fn: Optional[Callable[..., Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.work_id = work_id or f"wu_{uuid.uuid4().hex[:10]}"
        self.workload_id = workload_id
        self.operation = operation
        self.dependencies: List[str] = list(dependencies or [])
        self.estimated_cost: float = float(estimated_cost)
        self.measured_cost: float = float(measured_cost)
        self.memory_cost: int = int(memory_cost)
        self.data_dependencies: List[str] = list(data_dependencies or [])
        self.locality = locality if isinstance(locality, LocalityClass) else LocalityClass(locality)
        self.priority: int = int(priority)
        self.correctness_requirement = correctness_requirement
        self.execution_target = execution_target if isinstance(execution_target, ExecutionTarget) else ExecutionTarget(execution_target)
        self.verification_requirement = verification_requirement
        self.classification = classification if isinstance(classification, WorkClassification) else WorkClassification(classification)
        self.compute_fn = compute_fn
        self.metadata: Dict[str, Any] = dict(metadata or {})

        self.status = WorkUnitStatus.IDLE
        self.result: Any = None
        self.error_message: Optional[str] = None
        self.worker_id: Optional[str] = None
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def is_ready(self, completed_work_ids: set[str]) -> bool:
        """Returns True if all dependencies have completed."""
        return all(dep in completed_work_ids for dep in self.dependencies)

    def execute(self, *args, **kwargs) -> Any:
        """Executes the internal compute function if present, tracking actual timing."""
        self.status = WorkUnitStatus.EXECUTING
        self.start_time = time.perf_counter()
        try:
            if self.classification == WorkClassification.CAN_ELIMINATE:
                self.status = WorkUnitStatus.ELIMINATED
                self.result = None
            elif self.classification == WorkClassification.CAN_REUSE:
                self.status = WorkUnitStatus.REUSED
                self.result = kwargs.get("cached_value", None)
            elif self.compute_fn is not None:
                self.result = self.compute_fn(*args, **kwargs)
                self.status = WorkUnitStatus.COMPLETED
            else:
                # Default identity / passthrough
                self.result = kwargs.get("default_result", 0.0)
                self.status = WorkUnitStatus.COMPLETED
        except Exception as e:
            self.status = WorkUnitStatus.FAILED
            self.error_message = str(e)
            raise e
        finally:
            self.end_time = time.perf_counter()
            self.measured_cost = (self.end_time - self.start_time) * 1000.0  # ms
        return self.result

    def mark_eliminated(self, reason: str = "irrelevant_to_observable"):
        self.classification = WorkClassification.CAN_ELIMINATE
        self.status = WorkUnitStatus.ELIMINATED
        self.metadata["elimination_reason"] = reason

    def mark_reused(self, cache_key: str):
        self.classification = WorkClassification.CAN_REUSE
        self.status = WorkUnitStatus.REUSED
        self.metadata["cache_key"] = cache_key

    def to_dict(self) -> Dict[str, Any]:
        return {
            "work_id": self.work_id,
            "workload_id": self.workload_id,
            "operation": self.operation,
            "dependencies": self.dependencies,
            "estimated_cost": self.estimated_cost,
            "measured_cost": self.measured_cost,
            "memory_cost": self.memory_cost,
            "data_dependencies": self.data_dependencies,
            "locality": self.locality.value,
            "priority": self.priority,
            "correctness_requirement": self.correctness_requirement,
            "execution_target": self.execution_target.value,
            "verification_requirement": self.verification_requirement,
            "classification": self.classification.value,
            "status": self.status.value,
            "worker_id": self.worker_id,
            "error_message": self.error_message,
        }
