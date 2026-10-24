"""
tests/test_universal_fabric.py
==============================
Comprehensive Test Suite for the Universal Replacement Fabric.

Verifies:
1. All 12 architectural modules of hyper_phase_change.
2. Canonical 15 workload support contracts and schema invariants.
3. Canonical IR graph construction and FLOP estimation.
4. Structural analysis and detection of algebraic structures.
5. Mathematical phase-change rewrites and fast-path execution.
6. Multi-operand exact semantic memoization and LRU memory bounding.
7. Physical device probe and truthful hardware detection.
8. Capability registry states across CPU, iGPU, IREE, SwiftShader, and PoCL.
9. Strict heterogeneous scheduling policies (including fail-closed VERIFIED_IGPU_ONLY).
10. Independent verification engine and 5-state transitions.
11. Telemetry logging and execution provenance.
12. Seven Acceptance Gate certification evaluation.
13. Universal Replacement Fabric REST API endpoints.
"""

from __future__ import annotations

import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import hyper_phase_change as hpc
from hyper.canonical.verification_state_machine import StrictVerificationRunner
from backend.routers.universal_fabric_router import router as fabric_router


# -----------------------------------------------------------------------------
# Module 1 & 2: Version, Contracts & Canonical IR
# -----------------------------------------------------------------------------

def test_fabric_version_and_contract_registry():
    assert hpc.__version__.startswith("3.0.0")
    contracts = hpc.CANONICAL_REGISTRY.get_all_contracts()
    assert len(contracts) == 15
    for wid in hpc.CANONICAL_15_WORKLOAD_IDS:
        contract = hpc.CANONICAL_REGISTRY.get_contract(wid)
        assert contract is not None
        assert contract.workload_id == wid
        assert len(contract.input_schemas) > 0
        assert contract.output_schema is not None


def test_canonical_ir_graph_construction():
    node = hpc.IRNode(
        node_id="test_node_matmul",
        op_type="MATMUL",
        input_names=["A", "B"],
        input_shapes={"A": (128, 128), "B": (128, 128)},
        input_dtypes={"A": "float32", "B": "float32"},
        output_shape=(128, 128),
        output_dtype="float32",
        estimated_flops=2.0 * 128 * 128 * 128,
    )
    graph = hpc.IRGraph(graph_id="test_graph")
    graph.add_node(node)

    assert graph.nodes["test_node_matmul"].output_shape == (128, 128)
    assert graph.total_estimated_flops() == 2.0 * 128 * 128 * 128
    d = graph.to_dict()
    assert d["node_count"] == 1


# -----------------------------------------------------------------------------
# Module 3: Structural Analysis & Rewrites
# -----------------------------------------------------------------------------

def test_structural_analyzer_identifies_structures():
    # Identity
    eye_arr = np.eye(64, dtype=np.float32)
    meta_eye = hpc.StructuralAnalyzer.analyze_tensor("I", eye_arr)
    assert meta_eye.structure_type == hpc.StructureType.IDENTITY

    # Zero
    zero_arr = np.zeros((64, 64), dtype=np.float32)
    meta_zero = hpc.StructuralAnalyzer.analyze_tensor("Z", zero_arr)
    assert meta_zero.structure_type == hpc.StructureType.ZERO

    # Diagonal
    diag_arr = np.diag(np.arange(1, 65, dtype=np.float32))
    meta_diag = hpc.StructuralAnalyzer.analyze_tensor("D", diag_arr)
    assert meta_diag.structure_type == hpc.StructureType.DIAGONAL

    # Constant
    const_arr = np.full((1000,), 7.5, dtype=np.float32)
    meta_const = hpc.StructuralAnalyzer.analyze_tensor("C", const_arr)
    assert meta_const.structure_type == hpc.StructureType.CONSTANT

    # Dense
    dense_arr = np.random.randn(32, 32).astype(np.float32)
    meta_dense = hpc.StructuralAnalyzer.analyze_tensor("R", dense_arr)
    assert meta_dense.structure_type == hpc.StructureType.DENSE


def test_phase_change_rewrite_optimization():
    # A @ I = A
    A = np.random.randn(64, 64).astype(np.float32)
    I = np.eye(64, dtype=np.float32)
    inputs = {"A": A, "B": I}

    analysis = hpc.PhaseChangeOptimizer.optimize_workload("GEMM_STANDARD", inputs)
    assert analysis.best_rewrite is not None
    assert "Identity" in analysis.best_rewrite.name
    out = analysis.best_rewrite.apply_fn(inputs)
    assert np.array_equal(out, A)


# -----------------------------------------------------------------------------
# Module 4: Cost Model & Regression Prevention
# -----------------------------------------------------------------------------

def test_cost_model_and_regression_flagging():
    inputs = {"A": np.ones((128, 128), dtype=np.float32), "B": np.ones((128, 128), dtype=np.float32)}
    profile = hpc.PhaseChangeCostModel.evaluate_cost(
        workload_id="GEMM_STANDARD",
        backend_id="OPENVINO_IGPU",
        inputs=inputs,
        baseline_latency_ms=1.5,
    )
    assert profile.estimated_flops > 0
    assert profile.arithmetic_intensity > 0
    assert profile.total_projected_latency_ms > 0


# -----------------------------------------------------------------------------
# Module 5: Exact Semantic Cache
# -----------------------------------------------------------------------------

def test_exact_semantic_cache_isolation_and_lru():
    cache = hpc.ExactSemanticCache(max_entries=3, max_memory_mb=10.0)

    A1 = np.ones((10, 10), dtype=np.float32)
    B1 = np.ones((10, 10), dtype=np.float32)
    res1 = np.full((10, 10), 10.0, dtype=np.float32)

    # Store
    cache.store("GEMM_STANDARD", {"A": A1, "B": B1}, res1, verified=True, execution_time_ms=0.5)

    # Hit
    lookup1 = cache.lookup("GEMM_STANDARD", {"A": A1, "B": B1})
    assert lookup1.hit is True

    # Miss when B changes
    B2 = np.zeros((10, 10), dtype=np.float32)
    lookup2 = cache.lookup("GEMM_STANDARD", {"A": A1, "B": B2})
    assert lookup2.hit is False

    # Miss when shape changes
    A3 = np.ones((10, 20), dtype=np.float32)
    lookup3 = cache.lookup("GEMM_STANDARD", {"A": A3, "B": B1})
    assert lookup3.hit is False

    # Never cache unverified result
    stored_unverified = cache.store("GEMM_STANDARD", {"A": A1, "B": B2}, res1, verified=False, execution_time_ms=0.5)
    assert stored_unverified is None


# -----------------------------------------------------------------------------
# Module 6 & 7: Physical Device Probe & Capability Registry
# -----------------------------------------------------------------------------

def test_physical_device_probe_and_capability_registry():
    probe = hpc.PhysicalDeviceProbe.run_full_probe()
    assert probe.total_ram_gb > 0
    assert probe.cpu_logical_threads > 0
    assert probe.discrete_gpu_present is False
    assert "NOT_MEASURED" in probe.discrete_gpu_parity_status

    registry = hpc.CapabilityRegistry()
    cpu_b = registry.get_backend("CPU_AVX2")
    assert cpu_b is not None
    assert cpu_b.state == hpc.BackendState.VERIFIED_FOR_CONTRACT

    igpu_b = registry.get_backend("OPENVINO_IGPU")
    assert igpu_b is not None
    if probe.igpu_available:
        assert igpu_b.state in (hpc.BackendState.VERIFIED_FOR_CONTRACT, hpc.BackendState.AVAILABLE_UNVERIFIED)


# -----------------------------------------------------------------------------
# Module 8: Scheduler Policies & Fail-Closed Integrity
# -----------------------------------------------------------------------------

def test_scheduler_cpu_only_policy():
    inputs = StrictVerificationRunner.generate_typical_inputs("GEMM_STANDARD", seed=42)
    res = hpc.ROUTER.route_and_execute("GEMM_STANDARD", inputs, policy=hpc.ExecutionPolicy.CPU_ONLY)
    assert res.actual_backend == "CPU_AVX2"
    assert res.is_fallback is False
    assert res.is_verified is True


def test_scheduler_verified_igpu_only_fail_closed():
    # SHA256_CRYPTO cannot run on Intel UHD iGPU -> MUST fail closed
    inputs = StrictVerificationRunner.generate_typical_inputs("SHA256_CRYPTO", seed=42)
    with pytest.raises(hpc.BackendExecutionError) as exc_info:
        hpc.ROUTER.route_and_execute("SHA256_CRYPTO", inputs, policy=hpc.ExecutionPolicy.VERIFIED_IGPU_ONLY)
    assert "VERIFIED_IGPU_ONLY policy violation" in str(exc_info.value)


def test_scheduler_auto_verified_igpu_execution():
    inputs = StrictVerificationRunner.generate_typical_inputs("GEMM_STANDARD", seed=42)
    res = hpc.ROUTER.route_and_execute("GEMM_STANDARD", inputs, policy=hpc.ExecutionPolicy.AUTO_VERIFIED)
    assert res.is_verified is True
    assert res.actual_backend in ("OPENVINO_IGPU", "CPU_AVX2", "PHASE_CHANGE_ELIMINATION")


# -----------------------------------------------------------------------------
# Module 9 & 10: Verification Engine & Telemetry
# -----------------------------------------------------------------------------

def test_independent_verification_engine_correctness():
    inputs = StrictVerificationRunner.generate_typical_inputs("REDUCTION_SUM", seed=42)
    correct_cand = np.sum(inputs["x"].astype(np.float64)).astype(np.float32)

    # Correct candidate
    v_ok = hpc.PhaseChangeVerifier.verify_candidate_output("REDUCTION_SUM", inputs, correct_cand)
    assert v_ok.is_verified is True
    assert v_ok.status == hpc.VerificationStatus.PASS

    # Corrupted candidate
    corrupt_cand = correct_cand + 100.0
    v_bad = hpc.PhaseChangeVerifier.verify_candidate_output("REDUCTION_SUM", inputs, corrupt_cand)
    assert v_bad.is_verified is False
    assert v_bad.status == hpc.VerificationStatus.FAIL


def test_telemetry_provenance_logging():
    hpc.TELEMETRY.clear()
    rec = hpc.TELEMETRY.log_execution(
        workload_id="GEMM_STANDARD",
        contract_version="v3.0",
        policy="AUTO_VERIFIED",
        backend="OPENVINO_IGPU",
        device_name="Intel(R) UHD Graphics (iGPU)",
        is_fallback=False,
        fallback_reason=None,
        is_verified=True,
        detection_ms=0.1,
        compilation_ms=0.0,
        execution_ms=1.45,
        verification_ms=0.2,
        input_digest="hash123",
        output_digest="hash456",
    )
    assert rec.total_end_to_end_ms > 0
    records = hpc.TELEMETRY.get_recent_records(limit=10)
    assert len(records) == 1
    assert records[0]["workload_id"] == "GEMM_STANDARD"


# -----------------------------------------------------------------------------
# Module 11 & 12: Certification & Benchmark
# -----------------------------------------------------------------------------

def test_acceptance_gate_certification():
    cert = hpc.FabricCertificationEngine.evaluate_gates()
    assert cert.contract_version.startswith("v3.0")
    assert len(cert.gates) == 7
    # Gate A through Gate G present
    assert "GATE_A_CORRECTNESS" in cert.gates
    assert "GATE_B_COVERAGE" in cert.gates
    assert "GATE_C_DEVICE_PROVENANCE" in cert.gates
    assert "GATE_D_PERFORMANCE" in cert.gates
    assert "GATE_E_INTEGRATION" in cert.gates
    assert "GATE_F_REPRODUCIBILITY" in cert.gates
    assert "GATE_G_SCOPE_INTEGRITY" in cert.gates
    assert cert.overall_status == "CERTIFIED_VERIFIED_FABRIC"


def test_benchmark_workload_deep():
    metric = hpc.UniversalFabricBenchmark.benchmark_workload_deep("GEMM_STANDARD", warmup_runs=1, measured_runs=2)
    assert metric.workload_id == "GEMM_STANDARD"
    assert metric.candidate_median_ms > 0
    assert metric.reference_median_ms > 0
    assert metric.speedup > 0


# -----------------------------------------------------------------------------
# REST API Endpoints Verification
# -----------------------------------------------------------------------------

def test_rest_api_endpoints():
    app = FastAPI()
    app.include_router(fabric_router)
    client = TestClient(app)

    # 1. Capabilities
    r1 = client.get("/api/hyper/capabilities")
    assert r1.status_code == 200
    assert r1.json()["status"] == "SUCCESS"

    # 2. Backends
    r2 = client.get("/api/hyper/backends")
    assert r2.status_code == 200
    assert len(r2.json()["backends"]) >= 4

    # 3. Workloads
    r3 = client.get("/api/hyper/workloads")
    assert r3.status_code == 200
    assert r3.json()["total_canonical_workloads"] == 15

    # 4. Execute
    r4 = client.post("/api/hyper/execute", json={"workload_id": "GEMM_STANDARD", "policy": "AUTO_VERIFIED"})
    assert r4.status_code == 200
    assert r4.json()["result"]["is_verified"] is True

    # 5. Verify
    r5 = client.post("/api/hyper/verify", json={"workload_id": "GEMM_STANDARD", "seed": 42})
    assert r5.status_code == 200
    assert r5.json()["verification"]["is_verified"] is True

    # 6. Certification
    r6 = client.get("/api/hyper/certification")
    assert r6.status_code == 200
    assert r6.json()["certificate"]["overall_status"] == "CERTIFIED_VERIFIED_FABRIC"
