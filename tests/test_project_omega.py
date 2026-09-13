#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_project_omega.py
===========================
Comprehensive Test Suite for Project Omega:
Ultra-Sonic Software-Defined Parallel Compute Fabric.
"""

import pytest
import numpy as np
import time

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
from hyper_x.rtx5090.gap_engine import RTX5090GapEngine, BottleneckCause
from hyper_x.pipeline import AuthoritativePipeline


def test_work_unit_lifecycle_and_elimination():
    """Validates WorkUnit lifecycle, elimination, and reuse markings."""
    u1 = WorkUnit(
        work_id="wu_001",
        operation="test_add",
        estimated_cost=100.0,
        compute_fn=lambda x: x + 10
    )
    assert u1.status == WorkUnitStatus.IDLE
    assert u1.is_ready(set())

    # Execute
    res = u1.execute(5)
    assert res == 15
    assert u1.status == WorkUnitStatus.COMPLETED
    assert u1.measured_cost >= 0.0

    # Elimination
    u2 = WorkUnit(work_id="wu_002", operation="dead_op")
    u2.mark_eliminated("unreferenced")
    assert u2.status == WorkUnitStatus.ELIMINATED
    assert u2.classification == WorkClassification.CAN_ELIMINATE


def test_virtual_worker_multiplexing():
    """Validates VirtualWorker dispatch and performance counter updates."""
    worker = VirtualWorker("vworker_cpu_0", ExecutionTarget.CPU, physical_core_id=0)
    assert worker.state == WorkerState.IDLE

    unit = WorkUnit(
        work_id="wu_test_gemm",
        estimated_cost=2000.0,
        compute_fn=lambda a, b: float(np.dot(a, b))
    )
    v1 = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    v2 = np.array([4.0, 5.0, 6.0], dtype=np.float32)

    res = worker.assign_and_execute(unit, v1, v2)
    assert res == 32.0
    assert worker.tasks_executed == 1
    assert worker.total_flops_processed == 2000.0
    stats = worker.get_stats()
    assert stats["worker_id"] == "vworker_cpu_0"


def test_task_graph_dag_topological_sort_and_partition():
    """Validates TaskGraph DAG construction, matrix partitioning, and topological ordering."""
    graph = TaskGraph.partition_matrix_gemm(
        M=128, K=128, N=128,
        tile_size=64,
        sparsity_ratio=0.7
    )
    assert len(graph.units) > 0
    summary = graph.get_summary()
    assert summary["total_units"] == len(graph.units)
    assert "MUST_COMPUTE" in summary["classification_counts"]

    # Topological sort must return all units without cycles
    ordered = graph.topological_sort()
    assert len(ordered) == len(graph.units)

    # Elimination propagation
    leaf_id = list(graph.units.keys())[0]
    graph.mark_eliminated(leaf_id, reason="test_pruning")
    assert leaf_id in graph.eliminated_units


def test_fabric_cost_model_estimation_and_calibration():
    """Validates live cost model estimation across CPU and UHD, and self-calibration."""
    model = FabricCostModel()
    unit_small = WorkUnit(estimated_cost=1000.0, memory_cost=512)
    unit_large = WorkUnit(estimated_cost=1e8, memory_cost=1024 * 1024)

    # Small unit should favor CPU (lower launch overhead)
    target_small = model.select_cheapest_target(unit_small)
    assert target_small == ExecutionTarget.CPU

    # Cost model self-calibration
    t_est = model.estimate_cost(unit_small, ExecutionTarget.CPU)
    model.update_empirical_measurement(ExecutionTarget.CPU, estimated_ms=t_est, measured_ms=t_est * 1.5)
    assert model.total_evaluations == 1


def test_fabric_worker_pool_work_stealing_and_execution():
    """Validates FabricWorkerPool heterogeneous scheduling and graph execution."""
    pool = FabricWorkerPool()
    assert len(pool.cpu_p_workers) == 4
    assert len(pool.cpu_e_workers) == 4
    assert len(pool.uhd_workers) == 4

    graph = TaskGraph.partition_matrix_gemm(M=64, K=64, N=64, tile_size=32)
    exec_res = pool.execute_graph(graph)
    assert exec_res["total_units"] == len(graph.units)
    assert exec_res["executed_units"] > 0
    assert exec_res["elapsed_ms"] >= 0.0


def test_compute_fabric_worker_equivalence_and_compression_ratio():
    """Validates SOFTWARE_PARALLEL_WORKER_EQUIVALENCE and COMPUTATIONAL_COMPRESSION_RATIO."""
    fabric = ComputeFabric()
    graph = TaskGraph.partition_matrix_gemm(
        M=128, K=128, N=128,
        tile_size=64,
        sparsity_ratio=0.8
    )

    equiv = fabric.measure_parallel_worker_equivalence(graph)
    assert equiv["physical_execution_units"] == 56  # 8 CPU cores + 48 UHD EUs
    assert equiv["virtual_work_units"] == len(graph.units)
    assert equiv["multiplexing_ratio"] > 0.0

    comp = fabric.measure_computational_compression_ratio(
        original_work=2e6,
        optimized_work=5e5,
        eliminated_work=1.5e6
    )
    assert comp["computational_compression_ratio"] == 4.0
    assert comp["breakdown"]["algorithmic_compression"] == 4.0


def test_rtx5090_gap_engine_diagnosis():
    """Validates RTX 5090 gap calculation, bottleneck diagnosis, and escape hypotheses."""
    engine = RTX5090GapEngine()
    rep = engine.analyze_gap(
        workload_id="gemm_test",
        current_latency_ms=10.0,  # RTX 5090 target is 0.045 ms
        current_memory_mb=100.0,
        arithmetic_flops=2e7
    )
    assert rep.target_rtx5090_latency_ms == 0.045
    assert rep.current_hyper_latency_ms == 10.0
    assert rep.latency_gap_ratio < 0.1
    assert len(rep.hypotheses) > 0
    assert any(h.proposed_escape.startswith("MATHEMATICAL_ESCAPE") or h.proposed_escape.startswith("KERNEL_FUSION") for h in rep.hypotheses)


def test_authoritative_pipeline_project_omega_integration():
    """Validates full authoritative pipeline execution with Project Omega Compute Fabric."""
    pipeline = AuthoritativePipeline()
    rng = np.random.default_rng(42)
    u = rng.standard_normal((64, 8)).astype(np.float32)
    v = rng.standard_normal((8, 64)).astype(np.float32)
    A = u @ v
    B = rng.standard_normal((64, 64)).astype(np.float32)

    hints = {"numerical_tolerance": 1e-3}
    out, cert, summary = pipeline.execute_matrix_workload("gemm_omega_test", A, B, hints)

    assert out.shape == (64, 64)
    assert cert.physical_execution_units == 56
    assert cert.virtual_work_units > 0
    assert cert.software_parallel_worker_equivalence >= 1.0
    assert cert.computational_compression_ratio >= 1.0
    assert cert.verify_tamper_evident()
    assert summary["correctness"] == "PASS"
    assert "rtx5090_target_latency_ms" in summary
