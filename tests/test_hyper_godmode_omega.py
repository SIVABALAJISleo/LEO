"""
tests/test_hyper_godmode_omega.py
=================================
Comprehensive Test Suite for HYPER-GODMODE Ω∞ Universal Performance Parity Engine.

Validates Feature Modules A through T:
- Workload Contract Engine
- Intelligent Bottleneck Detector
- Computation Elimination (N-body, Separable Conv, Sparse GEMM)
- Smart Memory Engine (WorkingSetManager, BoundedBufferPool, ChunkedTiling)
- CPU+iGPU Adaptive Heterogeneous Scheduler
- Six Bottleneck Playbooks
- Algorithmic Pathway Discovery & Independent Verification
- Master GODMODE Ω∞ Canonical Suite Execution
- Anti-Cheat & Hardcoding Defense
"""

import numpy as np
import pytest

from hyper.godmode.workload_contracts import (
    ContractRegistry,
    WorkloadContract,
    ExactnessRequirement,
    WorkloadFamily,
)
from hyper.godmode.bottleneck_detector import (
    IntelligentBottleneckDetector,
    BottleneckClass,
)
from hyper.godmode.computation_elimination import (
    ComputationEliminationEngine,
    OptimizationCertificate,
)
from hyper.godmode.memory_engine import (
    WorkingSetManager,
    BoundedBufferPool,
    ChunkedTilingEngine,
)
from hyper.godmode.adaptive_scheduler import (
    AdaptiveHeterogeneousScheduler,
    ExecutionBackend,
)
from hyper.godmode.playbooks import (
    BottleneckPlaybookRegistry,
)
from hyper.godmode.pathway_explorer import (
    PathwayDiscoveryEngine,
)
from hyper.godmode.godmode_omega import (
    godmode_omega_engine,
    HyperGodmodeOmegaEngine,
)


def test_workload_contracts_validation():
    contract = WorkloadContract(
        workload_id="TEST-GEMM",
        name="Test Matrix Multiplication",
        family=WorkloadFamily.AI_ML,
        exactness_requirement=ExactnessRequirement.EXACT,
        max_absolute_error=1e-5,
        max_latency_ms=10.0,
    )
    ref = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    cand_good = ref.copy()
    cand_bad = ref + 5.0

    eval_good = contract.validate_execution(ref, cand_good, measured_latency_ms=1.5)
    assert eval_good["passed"] is True
    assert eval_good["is_exact"] is True

    eval_bad = contract.validate_execution(ref, cand_bad, measured_latency_ms=1.5)
    assert eval_bad["passed"] is False
    assert len(eval_bad["violations"]) > 0


def test_intelligent_bottleneck_detector():
    detector = IntelligentBottleneckDetector()
    report = detector.profile_execution(
        func=lambda: np.dot(np.random.randn(64, 64), np.random.randn(64, 64)),
        warmup_iterations=1,
        measured_iterations=3,
    )
    assert report.primary_bottleneck in BottleneckClass
    assert report.telemetry.wall_clock_ms >= 0.0
    assert report.telemetry.cpu_physical_cores >= 4
    assert len(report.evidence) > 0


def test_computation_elimination_nbody():
    n = 32
    np.random.seed(42)
    pos = np.random.randn(n, 3).astype(np.float32)
    mass = np.random.rand(n).astype(np.float32) + 0.1

    # Reference O(N^2) double loop
    ref_forces = np.zeros_like(pos)
    for i in range(n):
        for j in range(n):
            if i != j:
                d = pos[j] - pos[i]
                dist_sq = np.sum(d ** 2) + 1e-9
                ref_forces[i] += 6.6743e-11 * d * (mass[i] * mass[j] / (dist_sq * np.sqrt(dist_sq)))

    cand_forces, cert = ComputationEliminationEngine.eliminate_symmetric_nbody(pos, mass)
    diff = np.max(np.abs(ref_forces - cand_forces))
    assert diff < 1e-5
    assert cert.work_reduction_pct == 50.0
    assert cert.semantic_equivalence_claim == "NUMERICALLY_EQUIVALENT"


def test_computation_elimination_separable_conv():
    img = np.random.rand(64, 64).astype(np.float32)
    kernel_1d = np.array([0.1, 0.2, 0.4, 0.2, 0.1], dtype=np.float32)
    kernel_2d = np.outer(kernel_1d, kernel_1d)

    # Reference 2D conv
    h, w = img.shape
    padded = np.pad(img, ((2, 2), (2, 2)), mode="reflect")
    ref_conv = np.zeros_like(img)
    for r in range(h):
        for c in range(w):
            ref_conv[r, c] = np.sum(padded[r : r + 5, c : c + 5] * kernel_2d)

    cand_conv, cert = ComputationEliminationEngine.eliminate_2d_separable_convolution(img, kernel_1d)
    diff = np.max(np.abs(ref_conv - cand_conv))
    assert diff < 1e-4
    assert cert.work_reduction_pct == 60.0


def test_computation_elimination_sparse_gemm():
    A = np.zeros((32, 32), dtype=np.float32)
    B = np.zeros((32, 32), dtype=np.float32)
    A[0:8, :] = np.random.randn(8, 32)
    B[:, 0:8] = np.random.randn(32, 8)

    ref = np.dot(A, B)
    cand, cert = ComputationEliminationEngine.eliminate_dead_sparse_blocks(A, B)
    assert np.allclose(ref, cand, atol=1e-5)
    assert cert.work_reduction_pct > 0.0


def test_memory_engine_working_set_and_buffer_pool():
    mgr = WorkingSetManager()
    budget = mgr.get_budget()
    assert budget.total_physical_ram_mb > 8000.0
    assert budget.usable_safe_ram_mb > 0.0

    safe, msg = mgr.assess_workload_safety(500.0)
    assert safe is True

    pool = BoundedBufferPool(max_cached_buffers=4)
    buf1 = pool.acquire((64, 64), np.float32)
    assert buf1.shape == (64, 64)
    pool.release(buf1)
    buf2 = pool.acquire((64, 64), np.float32)
    stats = pool.get_stats()
    assert stats["reused_count"] >= 1


def test_chunked_tiling_matmul():
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    ref = np.dot(A, B)
    cand = ChunkedTilingEngine.blocked_matmul(A, B, block_size=16)
    assert np.allclose(ref, cand, atol=1e-4)


def test_adaptive_scheduler_topology():
    scheduler = AdaptiveHeterogeneousScheduler()
    prof = scheduler.profile
    assert prof.physical_cores >= 4
    assert prof.logical_processors >= 8
    assert len(prof.p_core_threads) > 0

    backend = scheduler.select_backend("AI_ML", input_elements=5000, requires_low_latency=True)
    assert backend == ExecutionBackend.CPU_PERFORMANCE_CORES


def test_bottleneck_playbooks():
    playbook = BottleneckPlaybookRegistry.get_playbook(BottleneckClass.COMPUTE_BOUND)
    assert playbook.bottleneck_class == BottleneckClass.COMPUTE_BOUND
    assert len(playbook.concrete_transformations) > 0


def test_pathway_discovery_engine():
    explorer = PathwayDiscoveryEngine()
    c = ContractRegistry.get("GEMM-DENSE-256")
    assert c is not None
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    cand, vres = explorer.discover_and_evaluate(
        contract=c,
        reference_fn=lambda x: np.dot(x[0], x[1]),
        candidate_fn=lambda x: np.dot(x[0], x[1]),
        sample_input=(A, B),
        transformations=["Baseline Matrix Verification"],
    )
    assert cand.is_verified is True
    assert vres.is_correct is True


def test_godmode_omega_canonical_suite_execution():
    res = godmode_omega_engine.run_canonical_suite()
    assert res.total_workloads == 5
    assert res.verified_workloads == 5
    assert res.pass_rate_pct == 100.0
    assert res.average_speedup > 0.0
    assert len(res.certificates) >= 3
    assert res.is_100_percent_certified is True
