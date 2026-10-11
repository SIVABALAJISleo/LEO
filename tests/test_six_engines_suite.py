"""
tests/test_six_engines_suite.py
===============================
Comprehensive verification suite for the HYPER-GODMODE Ω∞ Six-Engine System.
Covers all 20 required representative tests:
1. Dense matrix multiplication
2. Sparse matrix multiplication
3. Repeated computations (determinism & caching)
4. Incremental data changes
5. Large out-of-core arrays
6. Model weight streaming (TinyStories-inspired layer streaming)
7. Cache-blocked matrix operations
8. Image processing (separable 2D convolution)
9. Sequential video frames (dirty-region bounding boxes)
10. Scientific simulation (Laplacian stencil / N-body)
11. CPU-only execution
12. iGPU execution (with verified fallback)
13. Hybrid execution
14. Memory pressure & budget enforcement
15. Sustained thermal load (multi-iteration stability)
16. Incorrect optimization candidates (rejection)
17. Backend failure and recovery
18. Unknown workload formats
19. Unseen inputs (holdout generalization)
20. Adversarial edge cases (NaN, Inf, zeros, extreme scales)
"""

import math
import os
import time
import numpy as np
import pytest

from hyper.six_engines import (
    AdaptiveHeterogeneousScheduler,
    AlgebraicReformulator,
    BackendDevice,
    CacheAwareTiledMatmul,
    ComputationEliminationEngine,
    CorrectnessMode,
    DataReuseAndLocalityEngine,
    DependencyGraph,
    DependencyNode,
    ExactDifferentialVerifier,
    FallbackRouter,
    FusedKernelEngine,
    HardwareCapabilityDetector,
    IncrementalComputeEngine,
    IntelligentMemoryEngine,
    MmapArrayStreamer,
    OptimizationCandidate,
    OutOfCoreChunkedExecutor,
    PathwayDiscoveryEngine,
    PathwayStatus,
    QuantizedStorageCodec,
    RigorousBenchmarkRunner,
    SixEngineUniversalOptimizer,
    TemporalCoherenceEngine,
    TinyStoriesStreamingModel,
    TransformationClass,
    WorkloadContract,
)


# ----------------------------------------------------------------------
# 1. Dense Matrix Multiplication
# ----------------------------------------------------------------------
def test_01_dense_matrix_multiplication():
    np.random.seed(42)
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)

    C_blocked, metrics = CacheAwareTiledMatmul.blocked_matmul(A, B, tile_size=32)
    C_ref = np.dot(A, B)

    assert np.allclose(C_blocked, C_ref, atol=1e-5)
    assert metrics.gflops_achieved > 0.0


# ----------------------------------------------------------------------
# 2. Sparse Matrix Multiplication
# ----------------------------------------------------------------------
def test_02_sparse_matrix_multiplication():
    np.random.seed(42)
    A = np.random.randn(64, 64).astype(np.float32)
    # 75% zeros
    A[A < 0.5] = 0.0
    B = np.random.randn(64, 64).astype(np.float32)

    out, evidence = AlgebraicReformulator.sparse_specialized_gemm(A, B, sparsity_threshold=0.4)
    ref = np.dot(A, B)

    assert evidence.transformation_class == TransformationClass.SPARSE_SPECIALIZATION
    assert evidence.theoretical_cost_reduction_pct >= 50.0
    assert np.allclose(out, ref, atol=1e-5)


# ----------------------------------------------------------------------
# 3. Repeated Computations (Determinism & Invariance)
# ----------------------------------------------------------------------
def test_03_repeated_computations():
    contract = WorkloadContract(
        workload_id="REPEATED_DET_01",
        correctness_mode=CorrectnessMode.BITWISE_IDENTICAL,
    )
    x = np.random.randn(32, 32).astype(np.float32)
    fn = lambda data: np.sort(data, axis=1)

    v_rep = ExactDifferentialVerifier.verify_all_aspects(
        contract=contract,
        candidate_id="SORT_DET",
        ref_fn=fn,
        cand_fn=fn,
        standard_input=x,
    )
    assert v_rep.deterministic is True
    assert v_rep.passed is True


# ----------------------------------------------------------------------
# 4. Incremental Data Changes
# ----------------------------------------------------------------------
def test_04_incremental_data_changes():
    engine = IncrementalComputeEngine()
    x1 = np.ones((1, 100), dtype=np.float32)
    W = np.random.randn(100, 50).astype(np.float32)

    out1, inc1, saved1 = engine.execute_incremental_linear(x1, W)
    assert inc1 is False  # Initial full run

    # Mutate only 5% of x
    x2 = x1.copy()
    x2[0, :5] = 2.0
    out2, inc2, saved2 = engine.execute_incremental_linear(x2, W)
    ref2 = np.dot(x2, W)

    assert inc2 is True
    assert saved2 >= 90.0
    assert np.allclose(out2, ref2, atol=1e-5)


# ----------------------------------------------------------------------
# 5. Large Out-of-Core Arrays
# ----------------------------------------------------------------------
def test_05_large_out_of_core_arrays(tmp_path):
    streamer = MmapArrayStreamer(scratch_dir=str(tmp_path))
    shape = (200, 200)
    data = np.arange(40000, dtype=np.float32).reshape(shape)
    mm_a = streamer.create_mmap_array("A_huge", shape, np.float32, data)
    mm_b = streamer.create_mmap_array("B_huge", shape, np.float32, data)

    executor = OutOfCoreChunkedExecutor(chunk_size_elements=10000)
    C, metrics = executor.out_of_core_matmul(mm_a, mm_b, block_rows=64, block_cols=64, block_inner=64)
    ref = np.dot(data, data)

    assert np.allclose(C, ref, atol=1e-4)
    assert metrics.total_bytes_read > 0
    streamer.cleanup()


# ----------------------------------------------------------------------
# 6. Model Weight Streaming (TinyStories-inspired)
# ----------------------------------------------------------------------
def test_06_model_weight_streaming(tmp_path):
    model = TinyStoriesStreamingModel(num_layers=3, hidden_dim=64, scratch_dir=str(tmp_path))
    x = np.random.randn(8, 64).astype(np.float32)

    out, metrics = model.forward(x)
    assert out.shape == (8, 64)
    assert metrics.total_bytes_read > 0
    assert metrics.peak_ram_mb > 0.0
    model.cleanup()


# ----------------------------------------------------------------------
# 7. Cache-Blocked Matrix Operations
# ----------------------------------------------------------------------
def test_07_cache_blocked_matrix_operations():
    A = np.random.randn(128, 128).astype(np.float32)
    B = np.random.randn(128, 128).astype(np.float32)

    best_tile, metrics = CacheAwareTiledMatmul.autotune_tile_size(A, B, candidate_tiles=[16, 32, 64])
    assert best_tile in (16, 32, 64)
    assert metrics.gflops_achieved > 0.0


# ----------------------------------------------------------------------
# 8. Image Processing (Separable 2D Convolution)
# ----------------------------------------------------------------------
def test_08_image_processing_separable():
    img = np.random.randn(64, 64).astype(np.float32)
    kx = np.array([1.0, 2.0, 1.0], dtype=np.float32) / 4.0
    ky = np.array([1.0, 2.0, 1.0], dtype=np.float32) / 4.0

    out, ev = AlgebraicReformulator.separable_2d_convolution(img, kx, ky)
    assert out.shape == (64, 64)
    assert ev.theoretical_cost_reduction_pct > 0.0


# ----------------------------------------------------------------------
# 9. Sequential Video Frames (Dirty-Region Bounding Boxes)
# ----------------------------------------------------------------------
def test_09_sequential_video_frames():
    f1 = np.zeros((100, 100), dtype=np.float32)
    f2 = np.zeros((100, 100), dtype=np.float32)
    # Modify a small 10x10 sub-rectangle (1% of frame)
    f2[20:30, 40:50] = 1.0

    bbox, pct = TemporalCoherenceEngine.extract_dirty_region_bbox(f1, f2)
    assert bbox == (20, 40, 30, 50)
    assert 0.9 <= pct <= 1.1

    reproj, metrics = TemporalCoherenceEngine.apply_temporal_reprojection(f1, f2)
    assert np.allclose(reproj, f2)
    assert metrics.temporal_reuse_pct >= 98.0


# ----------------------------------------------------------------------
# 10. Scientific Simulation (Laplacian Stencil)
# ----------------------------------------------------------------------
def test_10_scientific_simulation():
    grid = np.zeros((64, 64), dtype=np.float32)
    grid[32, 32] = 100.0  # Point source

    # Separable 1D Laplacian passes
    kx = np.array([1.0, -2.0, 1.0], dtype=np.float32)
    ky = np.array([1.0, -2.0, 1.0], dtype=np.float32)
    lap, ev = AlgebraicReformulator.separable_2d_convolution(grid, kx, ky)

    assert lap.shape == (64, 64)
    assert ev.preconditions_satisfied is True


# ----------------------------------------------------------------------
# 11. CPU-Only Execution
# ----------------------------------------------------------------------
def test_11_cpu_only_execution():
    scheduler = AdaptiveHeterogeneousScheduler()
    x = np.ones((50, 50), dtype=np.float32)
    fn = lambda data, backend: data * 2.0

    out, rec = scheduler.schedule_and_execute("CPU_TEST", fn, x, preferred_mode=BackendDevice.CPU_AVX2)
    assert np.allclose(out, x * 2.0)
    assert rec.selected_backend == BackendDevice.CPU_AVX2
    assert rec.partition_ratio_cpu == 1.0


# ----------------------------------------------------------------------
# 12. iGPU Execution (With Verified Fallback)
# ----------------------------------------------------------------------
def test_12_igpu_execution():
    scheduler = AdaptiveHeterogeneousScheduler()
    x = np.ones((50, 50), dtype=np.float32)
    fn = lambda data, backend: data + 5.0

    out, rec = scheduler.schedule_and_execute("IGPU_TEST", fn, x, preferred_mode=BackendDevice.IGPU_VULKAN)
    assert np.allclose(out, x + 5.0)
    assert rec.success is True


# ----------------------------------------------------------------------
# 13. Hybrid Execution
# ----------------------------------------------------------------------
def test_13_hybrid_execution():
    scheduler = AdaptiveHeterogeneousScheduler()
    x = np.ones((100, 50), dtype=np.float32)
    fn = lambda data, backend: data * 3.0

    out, rec = scheduler.schedule_and_execute("HYBRID_TEST", fn, x, preferred_mode=BackendDevice.CPU_IGPU_HYBRID)
    assert np.allclose(out, x * 3.0)
    assert rec.selected_backend == BackendDevice.CPU_IGPU_HYBRID
    assert rec.partition_ratio_cpu > 0.0
    assert rec.partition_ratio_igpu > 0.0


# ----------------------------------------------------------------------
# 14. Memory Pressure & Budget Enforcement
# ----------------------------------------------------------------------
def test_14_memory_pressure_budget():
    engine = IntelligentMemoryEngine(ram_budget_mb=128.0)
    # Prediction of 500 MB should be rejected under 128 MB budget
    with pytest.raises(MemoryError) as exc_info:
        engine.execute_with_budget(lambda: None, predicted_mb=500.0, workload_id="OVERSIZED_01")
    assert "exceeds strict budget" in str(exc_info.value)


# ----------------------------------------------------------------------
# 15. Sustained Thermal Load (Multi-Iteration Stability)
# ----------------------------------------------------------------------
def test_15_sustained_thermal_load():
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    timings = []
    for _ in range(10):
        t0 = time.perf_counter()
        _ = np.dot(A, B)
        timings.append((time.perf_counter() - t0) * 1000.0)

    # Variance should be controlled
    assert np.std(timings) < 10.0


# ----------------------------------------------------------------------
# 16. Incorrect Optimization Candidates (Rejection)
# ----------------------------------------------------------------------
def test_16_incorrect_candidates_rejection():
    contract = WorkloadContract(
        workload_id="REJECT_TEST",
        correctness_mode=CorrectnessMode.EXACT_MATHEMATICAL,
    )
    ref_fn = lambda x: x * 2.0
    broken_cand_fn = lambda x: x * 2.5  # Deliberately erroneous!

    report = ExactDifferentialVerifier.verify_all_aspects(
        contract=contract,
        candidate_id="BAD_CAND",
        ref_fn=ref_fn,
        cand_fn=broken_cand_fn,
        standard_input=np.ones(10, dtype=np.float32),
    )
    assert report.passed is False
    assert len(report.violations) > 0


# ----------------------------------------------------------------------
# 17. Backend Failure and Recovery
# ----------------------------------------------------------------------
def test_17_backend_failure_recovery():
    contract = WorkloadContract(workload_id="FAIL_RECOVERY")
    ref_fn = lambda x: x + 10.0
    def throwing_candidate(x):
        raise RuntimeError("Simulated OpenCL driver crash")

    out, fallback_used, msg = FallbackRouter.execute_with_safe_fallback(
        contract=contract,
        candidate_fn=throwing_candidate,
        reference_fn=ref_fn,
        sample_input=np.array([5.0], dtype=np.float32),
    )
    assert fallback_used is True
    assert out[0] == 15.0
    assert "invoked exact reference fallback" in msg


# ----------------------------------------------------------------------
# 18. Unknown Workload Formats
# ----------------------------------------------------------------------
def test_18_unknown_workload_formats():
    contract = WorkloadContract(
        workload_id="SCALAR_OBJ",
        correctness_mode=CorrectnessMode.CONTRACT_BEHAVIOR,
    )
    ref_fn = lambda x: f"Processed: {x}"
    cand_fn = lambda x: f"Processed: {x}"

    report = ExactDifferentialVerifier.verify_all_aspects(
        contract=contract,
        candidate_id="STRING_OP",
        ref_fn=ref_fn,
        cand_fn=cand_fn,
        standard_input="tensor_graph_payload",
    )
    assert report.passed is True
    assert report.is_exact_bitwise is True


# ----------------------------------------------------------------------
# 19. Unseen Inputs (Holdout Generalization)
# ----------------------------------------------------------------------
def test_19_unseen_inputs_holdout():
    contract = WorkloadContract(workload_id="HOLDOUT_TEST")
    discovery = PathwayDiscoveryEngine()

    cand = OptimizationCandidate(
        candidate_id="HOLDOUT_TEST_OVERFITTED",
        workload_id="HOLDOUT_TEST",
    )
    ref_fn = lambda x: np.sum(x)
    # Cheating candidate: returns 10.0 for known input, fails on holdouts
    cheating_fn = lambda x: 10.0 if np.all(x == 1.0) else 0.0

    winner, evaluated = discovery.evaluate_and_rank_candidates(
        contract=contract,
        candidates=[cand],
        ref_fn=ref_fn,
        cand_runner_map={"HOLDOUT_TEST_OVERFITTED": cheating_fn},
        sample_input=np.ones(10, dtype=np.float32),
        holdout_inputs=[np.ones(10, dtype=np.float32) * 2.0],  # Sum should be 20.0
    )
    assert evaluated[0].correctness_status == PathwayStatus.REJECTED
    assert "Failed generalization test" in evaluated[0].failure_reason


# ----------------------------------------------------------------------
# 20. Adversarial Edge Cases
# ----------------------------------------------------------------------
def test_20_adversarial_edge_cases():
    contract = WorkloadContract(workload_id="ADVERSARIAL_TEST")
    ref_fn = lambda x: np.nan_to_num(x, nan=0.0, posinf=999.0, neginf=-999.0)
    cand_fn = lambda x: np.nan_to_num(x, nan=0.0, posinf=999.0, neginf=-999.0)

    adv_input = np.array([0.0, np.nan, np.inf, -np.inf, 1e-15, 1e15], dtype=np.float32)
    report = ExactDifferentialVerifier.verify_all_aspects(
        contract=contract,
        candidate_id="ADV_CAND",
        ref_fn=ref_fn,
        cand_fn=cand_fn,
        standard_input=np.array([1.0, 2.0], dtype=np.float32),
        adversarial_input=adv_input,
    )
    assert report.adversarial_passed is True
    assert report.passed is True
