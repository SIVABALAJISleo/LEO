#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compute_fabric/__init__.py
==================================
Project Omega: Ultra-Sonic Software-Defined Parallel Compute Fabric.
"""

from hyper_x.compute_fabric.work_unit import (
    WorkUnit,
    WorkUnitStatus,
    WorkClassification,
    ExecutionTarget,
    LocalityClass
)
from hyper_x.compute_fabric.virtual_worker import VirtualWorker, WorkerState
from hyper_x.compute_fabric.task_graph import TaskGraph
from hyper_x.compute_fabric.cost_model import FabricCostModel
from hyper_x.compute_fabric.worker_pool import FabricWorkerPool
from hyper_x.compute_fabric.fabric import ComputeFabric

__all__ = [
    "WorkUnit",
    "WorkUnitStatus",
    "WorkClassification",
    "ExecutionTarget",
    "LocalityClass",
    "VirtualWorker",
    "WorkerState",
    "TaskGraph",
    "FabricCostModel",
    "FabricWorkerPool",
    "ComputeFabric",
    "HeterogeneousExecutionFabric",
]

HeterogeneousExecutionFabric = ComputeFabric
