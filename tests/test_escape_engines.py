#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_escape_engines.py
============================
Unit & Integration Test Suite for:
  - Phase 3: Information Boundary & Backward Slicing Subsystem
  - Phase 9: Temporal Escape Engine
  - Phase 10: Lossless Speculative Execution Engine
  - Phase 13: Heterogeneous CPU + Intel UHD Execution Fabric
"""

import numpy as np
import pytest

from hyper_x.contract import WorkloadContract
from hyper_x.information_boundary import (
    InfluenceGraph,
    InformationCategory,
    DependencyAnalyzer,
    ObservableAnalyzer,
    BackwardSliceEngine,
    ForwardSliceEngine,
    NecessityMapEngine,
    IrrelevantWorkDetector,
    DependencyCertificateGenerator,
)
from hyper_x.temporal_escape import StateDeltaEngine, TemporalVerifier
from hyper_x.speculative import SpeculativeDraftEngine, SpeculativeController
from hyper_x.execution_fabric import (
    CapabilityDetector,
    CPUScheduler,
    IGPUScheduler,
    HeterogeneousScheduler,
    ExecutionDevice,
    MemoryPlanner,
    KernelDispatch,
    FabricTelemetry,
)


# --- Phase 3 Tests ---

def test_influence_graph_and_dependency_analyzer():
    graph = InfluenceGraph()
    graph.add_node("in_0", InformationCategory.REQUIRED_INFORMATION)
    graph.add_node("in_1", InformationCategory.REQUIRED_INFORMATION)
    graph.add_node("mid_0", InformationCategory.REQUIRED_INFORMATION, dependencies=["in_0", "in_1"])
    graph.add_node("out_0", InformationCategory.REQUIRED_INFORMATION, dependencies=["mid_0"], is_observable=True)
    graph.add_node("dead_branch", InformationCategory.REDUNDANT_INFORMATION, dependencies=["in_0"])

    analyzer = DependencyAnalyzer(graph)
    ancestors = analyzer.get_ancestors("out_0")
    assert ancestors == {"mid_0", "in_0", "in_1"}

    descendants = analyzer.get_descendants("in_0")
    assert descendants == {"mid_0", "out_0", "dead_branch"}

    depth = analyzer.compute_dependency_depth("out_0")
    assert depth == 2

    reachability = analyzer.analyze_reachability(["out_0"])
    assert reachability["required_nodes_count"] == 4
    assert reachability["dead_nodes_count"] == 1
    assert "dead_branch" in reachability["dead_node_ids"]


def test_backward_slice_engine():
    graph = InfluenceGraph()
    graph.add_node("in_a", InformationCategory.REQUIRED_INFORMATION)
    graph.add_node("in_b", InformationCategory.REQUIRED_INFORMATION)
    graph.add_node("unneeded_heavy_sim", InformationCategory.REDUNDANT_INFORMATION)
    graph.add_node("target_output", InformationCategory.REQUIRED_INFORMATION, dependencies=["in_a"], is_observable=True)

    slicer = BackwardSliceEngine(graph)
    result = slicer.compute_slice(["target_output"])

    assert "target_output" in result["slice_node_ids"]
    assert "in_a" in result["slice_node_ids"]
    assert "unneeded_heavy_sim" not in result["slice_node_ids"]
    assert "unneeded_heavy_sim" in result["pruned_node_ids"]
    assert result["pruning_ratio"] > 0.0


def test_forward_slice_engine():
    graph = InfluenceGraph()
    graph.add_node("state_0", InformationCategory.REQUIRED_INFORMATION)
    graph.add_node("state_1", InformationCategory.REQUIRED_INFORMATION)
    graph.add_node("obs_x", InformationCategory.REQUIRED_INFORMATION, dependencies=["state_0"], is_observable=True)
    graph.add_node("obs_y", InformationCategory.REQUIRED_INFORMATION, dependencies=["state_1"], is_observable=True)

    forward = ForwardSliceEngine(graph)
    result = forward.compute_slice(["state_0"])

    assert "obs_x" in result["impacted_observables"]
    assert "obs_y" not in result["impacted_observables"]
    assert result["impacted_observable_count"] == 1


def test_necessity_map_engine():
    engine = NecessityMapEngine(sparsity_threshold=1e-3)
    A_dense = np.random.randn(64, 64).astype(np.float32)
    B_dense = np.random.randn(64, 64).astype(np.float32)

    # 1. Dense compute
    entry_dense = engine.classify_gemm("gemm_dense", A_dense, B_dense, is_cached=False)
    assert entry_dense.category == InformationCategory.REQUIRED_INFORMATION
    assert entry_dense.elimination_ratio == 0.0

    # 2. Sparse compute
    A_sparse = np.zeros((64, 64), dtype=np.float32)
    A_sparse[:5, :5] = 1.0  # >95% zeros
    entry_sparse = engine.classify_gemm("gemm_sparse", A_sparse, B_dense, is_cached=False)
    assert entry_sparse.category == InformationCategory.REDUNDANT_INFORMATION
    assert entry_sparse.elimination_ratio > 0.50

    # 3. Exact cache hit
    entry_cached = engine.classify_gemm("gemm_cached", A_dense, B_dense, is_cached=True)
    assert entry_cached.category == InformationCategory.REUSABLE_INFORMATION
    assert entry_cached.elimination_ratio == 1.0

    summary = engine.summary()
    assert summary["total_nodes"] == 3
    assert summary["flops_eliminated"] > 0


def test_irrelevant_work_detector():
    # Viewport culling test
    boxes = np.array([
        [100, 100, 200, 200],   # Inside 1920x1080
        [3000, 4000, 3100, 4100]  # Far outside
    ], dtype=np.float32)
    res = IrrelevantWorkDetector.detect_spatial_culled(boxes, viewport=(0, 0, 1920, 1080))
    assert res["culled_primitives"] == 1
    assert res["visible_primitives"] == 1

    # Logit reduction test
    res_logits = IrrelevantWorkDetector.detect_unobserved_logits(vocab_size=32000, k=1)
    assert res_logits["unobserved_ratio"] > 0.999


def test_dependency_certificate_generator():
    cert = DependencyCertificateGenerator.generate(
        workload_id="gemm_pruning_test",
        contract_hash="abcd" * 16,
        total_nominal_nodes=100,
        eliminated_nodes=["node_1", "node_2"],
        elimination_categories={"REDUNDANT": 2},
        remaining_flops=50000.0,
    )
    assert cert.certificate_id.startswith("CERT-NW-")
    assert cert.elimination_ratio == 0.02
    assert cert.certificate_hash != ""


# --- Phase 9 Tests ---

def test_state_delta_and_temporal_verifier():
    delta_engine = StateDeltaEngine(dirty_threshold=1e-4, fallback_threshold=0.75)
    prev_state = np.zeros((100, 100), dtype=np.float32)
    curr_state = np.zeros((100, 100), dtype=np.float32)
    curr_state[10:15, 10:15] = 1.0  # Minor change (25 / 10000 = 0.25%)

    delta_res = delta_engine.compute_delta(prev_state, curr_state)
    assert delta_res.is_mostly_static is True
    assert delta_res.requires_full_refresh is False
    assert delta_res.dirty_fraction < 0.01

    # Neighborhood envelope clamping
    history = np.full((100, 100), 5.0, dtype=np.float32)
    clamped = delta_engine.apply_neighborhood_clamping(history, curr_state)
    assert np.max(clamped) <= 1.0

    # Temporal fidelity verifier
    verifier = TemporalVerifier(min_psnr_db=30.0, min_ssim=0.90)
    ver_res = verifier.verify(curr_state, curr_state)
    assert ver_res.passed is True
    assert ver_res.psnr_db > 90.0


# --- Phase 10 Tests ---

def test_speculative_draft_and_controller():
    # Target evaluator generates [10, 20, 30, 40]
    def ground_truth_target(prefix_and_draft):
        return [10, 20, 99, 100]

    # Draft proposes [10, 20, 30, 40]
    draft_engine = SpeculativeDraftEngine(draft_model_fn=lambda ctx, k: [10, 20, 30, 40])
    controller = SpeculativeController(
        target_evaluator=ground_truth_target,
        draft_engine=draft_engine,
        speculative_window=4
    )

    summary = controller.step(current_context=[1, 2, 3])
    # The first 2 tokens match [10, 20], then divergence at 30 vs 99 triggers rollback + append 99
    assert summary.accepted_tokens == [10, 20, 99]
    assert 30 in summary.rejected_tokens
    assert summary.is_lossless is True


# --- Phase 13 Tests ---

def test_execution_fabric():
    profile = CapabilityDetector.detect()
    assert profile.physical_cores >= 4
    assert profile.has_avx2 is True
    assert "Intel" in profile.igpu_model

    planner = MemoryPlanner(max_budget_bytes=1024 * 1024 * 1024)
    scratch = planner.get_or_allocate_scratchpad("test_buf", (256, 256), dtype=np.float32)
    assert scratch.shape == (256, 256)
    stats = planner.stats()
    assert stats["current_allocated_bytes"] > 0
    planner.release_all()

    # Kernel dispatch and telemetry
    telemetry = FabricTelemetry()
    A = np.random.randn(128, 128).astype(np.float32)
    B = np.random.randn(128, 128).astype(np.float32)

    res, lat_ms = KernelDispatch.dispatch("test_matmul", np.matmul, A, B)
    assert res.shape == (128, 128)
    assert lat_ms >= 0.0

    telemetry.record_kernel("test_matmul", lat_ms)
    summary = telemetry.get_summary("test_matmul")
    assert summary["count"] == 1
    assert summary["mean_ms"] == round(lat_ms, 4)

    # Heterogeneous scheduler
    het_sched = HeterogeneousScheduler(hardware_profile=profile)
    C, dev = het_sched.schedule_gemm(A, B)
    assert C.shape == (128, 128)
    assert dev in (ExecutionDevice.CPU_P_CORE, ExecutionDevice.CPU_E_CORE)
    het_sched.shutdown()
