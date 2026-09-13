#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/compute_fabric/fabric.py
================================
Project Omega: Software-Defined Parallel Compute Fabric.
Master Fabric Coordinator.

Implements the fundamental metrics:
1. SOFTWARE_PARALLEL_WORKER_EQUIVALENCE:
   Quantifies how much useful independent work the software-defined fabric
   exposes, schedules, and completes across fixed physical hardware.
2. COMPUTATIONAL_COMPRESSION_RATIO:
   Original necessary work / optimized necessary work, subject to contract correctness.
"""

from __future__ import annotations
import time
from typing import Dict, Any, Optional, Tuple
import numpy as np

from hyper_x.compute_fabric.work_unit import WorkUnit, WorkClassification, ExecutionTarget
from hyper_x.compute_fabric.task_graph import TaskGraph
from hyper_x.compute_fabric.worker_pool import FabricWorkerPool
from hyper_x.compute_fabric.cost_model import FabricCostModel


class ComputeFabric:
    """
    Master Software-Defined Parallel Compute Fabric for Project Omega.
    Transforms brute-force physical parallel computation into information reduction,
    computational multiplexing, and heterogeneous CPU+UHD scheduling.
    """

    TOTAL_PHYSICAL_CORES = 8       # Intel Core i5-12450H (4 P-cores + 4 E-cores)
    TOTAL_PHYSICAL_UHD_EUS = 48    # Intel UHD Graphics Execution Units
    TOTAL_PHYSICAL_UNITS = 56      # 8 CPU cores + 48 UHD EUs

    def __init__(self):
        self.cost_model = FabricCostModel()
        self.worker_pool = FabricWorkerPool(self.cost_model)
        self.execution_history: list[Dict[str, Any]] = []

    def execute_task_graph(self, graph: TaskGraph, *args, **kwargs) -> Dict[str, Any]:
        """Executes a TaskGraph on the worker pool and records fabric metrics."""
        summary = graph.get_summary()
        pool_res = self.worker_pool.execute_graph(graph, *args, **kwargs)

        # Compute Software Parallel Worker Equivalence
        parallel_equiv = self.measure_parallel_worker_equivalence(graph)

        # Compute Computational Compression Ratio
        orig_flops = summary["original_work_flops"]
        nec_flops = summary["necessary_work_flops"]
        comp_ratio = self.measure_computational_compression_ratio(
            original_work=orig_flops,
            optimized_work=nec_flops,
            eliminated_work=orig_flops - nec_flops
        )

        record = {
            "workload_id": graph.workload_id,
            "total_units": len(graph.units),
            "pool_execution": pool_res,
            "graph_summary": summary,
            "software_parallel_worker_equivalence": parallel_equiv,
            "computational_compression_ratio": comp_ratio
        }
        self.execution_history.append(record)
        return record

    def measure_parallel_worker_equivalence(self, graph: TaskGraph) -> Dict[str, Any]:
        """
        Part LV: Computes SOFTWARE_PARALLEL_WORKER_EQUIVALENCE.
        Investigates how many virtual work units are serviced by 56 physical execution resources
        through software-defined decomposition, reuse, and elimination.
        """
        total_virtual_units = len(graph.units)
        summary = graph.get_summary()

        eliminated_units = summary["classification_counts"].get(WorkClassification.CAN_ELIMINATE.value, 0)
        reused_units = summary["classification_counts"].get(WorkClassification.CAN_REUSE.value, 0)
        transformed_units = summary["classification_counts"].get(WorkClassification.CAN_TRANSFORM.value, 0)
        computed_units = summary["classification_counts"].get(WorkClassification.MUST_COMPUTE.value, 0)

        multiplexing_ratio = total_virtual_units / max(float(self.TOTAL_PHYSICAL_UNITS), 1.0)
        effective_useful_ratio = (reused_units + eliminated_units + transformed_units + computed_units) / max(float(computed_units + 1e-6), 1.0)

        return {
            "virtual_work_units": total_virtual_units,
            "physical_execution_units": self.TOTAL_PHYSICAL_UNITS,
            "multiplexing_ratio": round(multiplexing_ratio, 3),
            "computed_units": computed_units,
            "eliminated_units": eliminated_units,
            "reused_units": reused_units,
            "transformed_units": transformed_units,
            "effective_worker_amplification": round(effective_useful_ratio, 2),
            "scientific_note": "A virtual worker is a software unit of useful computation, NOT a physical silicon core."
        }

    def measure_computational_compression_ratio(
        self,
        original_work: float,
        optimized_work: float,
        eliminated_work: float = 0.0,
        reused_work: float = 0.0,
        predicted_work: float = 0.0
    ) -> Dict[str, Any]:
        """
        Part LVII: Computes COMPUTATIONAL_COMPRESSION_RATIO = original / optimized.
        Breaks down compression across algorithmic, data, cache, and prediction axes.
        """
        orig = max(float(original_work), 1.0)
        opt = max(float(optimized_work), 1.0)
        overall_ratio = orig / opt

        # Separate contributory compression factors
        algo_compression = max(1.0, (eliminated_work / opt) + 1.0)
        cache_compression = max(1.0, (reused_work / opt) + 1.0)
        prediction_compression = max(1.0, (predicted_work / opt) + 1.0)

        return {
            "computational_compression_ratio": round(overall_ratio, 3),
            "original_work_flops": orig,
            "optimized_work_flops": opt,
            "eliminated_work_flops": eliminated_work,
            "reused_work_flops": reused_work,
            "breakdown": {
                "algorithmic_compression": round(algo_compression, 2),
                "cache_reuse_compression": round(cache_compression, 2),
                "prediction_compression": round(prediction_compression, 2),
                "hardware_multiplexing_factor": round(float(self.TOTAL_PHYSICAL_UNITS), 1)
            }
        }
