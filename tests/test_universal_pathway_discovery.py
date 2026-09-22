"""
tests/test_universal_pathway_discovery.py
==========================================
Comprehensive Test Suite for HYPER Universal Computational Pathway Discovery Engine.

Validates:
1. GPU Capability Decomposer (7 families & formal contracts)
2. Workload Decomposer & Dependency Graph Engine
3. Pathway IR data structures
4. Multi-family Pathway Generator
5. Pathway Composer & Interaction Checker
6. Pathway Cost & Resource Model
7. Checkpoint Engine (Persistence & Resume)
8. Destination Tracker (Physical Parity NOT CLAIMED, Universal Parity UNPROVEN)
9. Controlled Workloads Suite (12 primary workloads)
10. Kimi K3 Discovery Brain & Multi-Agent Debate
11. Mathematical Reformulation Engine & Error Bounds
12. Application Target Registry (Blender, Unreal, Unity, WebGPU, PyTorch, etc.)
13. FastAPI Discovery Endpoints
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from hyper.discovery.capability_decomposer import GPUCapabilityDecomposer, CapabilityFamily
from hyper.discovery.workload_decomposer import WorkloadDecomposer, OperationType
from hyper.discovery.pathway_ir import (
    PathwayIR,
    ExecutionDevice,
    MemoryStrategy,
    SchedulingStrategy,
)
from hyper.discovery.pathway_generator import PathwayGenerator
from hyper.discovery.pathway_composer import PathwayComposer
from hyper.discovery.cost_model import PathwayCostModel
from hyper.discovery.checkpoint_engine import CheckpointEngine, DiscoveryCheckpoint
from hyper.discovery.destination_tracker import DestinationTracker
from hyper.discovery.controlled_workloads import ControlledWorkloadBenchmark
from hyper.ai.kimi_k3_brain import KimiK3DiscoveryBrain, K3ResearchRole
from hyper.mathematics.reformulation_engine import MathematicalReformulationEngine
from hyper.integrations.app_targets import ApplicationTargetRegistry, ApplicationTargetType
from backend.main import app


# 1. Capability Decomposer
def test_gpu_capability_decomposer():
    decomposer = GPUCapabilityDecomposer()
    assert len(decomposer.CAPABILITY_TAXONOMY) == 7

    # Test graphics decomposition
    detail_gfx = decomposer.decompose("Triangle_Rasterization")
    assert detail_gfx.family == CapabilityFamily.GRAPHICS
    assert detail_gfx.allows_approximation is True

    # Test scientific decomposition
    detail_sci = decomposer.decompose("Dense_Cholesky_LU")
    assert detail_sci.family == CapabilityFamily.SCIENTIFIC
    assert detail_sci.allows_approximation is False

    # Test contract creation
    contract = decomposer.create_contract_for_capability("Dense_GEMM", "workload-gemm")
    assert contract.workload_id == "workload-gemm"
    assert "AI_ML" in contract.metadata.get("capability_family", "")


# 2. Workload Decomposer & Dependency Graph
def test_workload_decomposer():
    decomposer = WorkloadDecomposer()
    res = decomposer.decompose_workload("Dense_Matrix_Multiplication", sample_input=np.eye(16))
    assert res.workload_name == "Dense_Matrix_Multiplication"
    assert len(res.dag.nodes) >= 3
    assert res.essential_operations_count > 0
    assert res.work_reduction_opportunity_ratio >= 0.0

    # Test custom operation spec
    ops = [
        {"node_id": "op0", "name": "load", "op_type": "MEMORY_LOAD", "can_reuse": True},
        {"node_id": "op1", "name": "fused_calc", "op_type": "ARITHMETIC", "flops": 500},
        {"node_id": "op2", "name": "redundant_check", "op_type": "BRANCH", "can_eliminate": True, "flops": 100},
    ]
    custom_res = decomposer.decompose_workload("CustomWorkload", sample_input=None, operations_spec=ops)
    assert custom_res.eliminable_operations_count == 1
    assert custom_res.reusable_operations_count == 1


# 3. Pathway IR
def test_pathway_ir():
    decomposer = GPUCapabilityDecomposer()
    contract = decomposer.create_contract_for_capability("Attention", "attn-01")
    generator = PathwayGenerator()
    cands = generator.generate_candidates("Attention", sample_input=None, contract=contract)
    assert len(cands) >= 3

    pw = cands[1]
    assert isinstance(pw, PathwayIR)
    summary = pw.summary()
    assert "pathway_id" in summary
    assert "family" in summary
    assert "device" in summary


# 4. Pathway Generator
def test_pathway_generator_families():
    generator = PathwayGenerator()
    cands = generator.generate_candidates("Rasterization_Pipeline", sample_input=None, max_candidates=7)
    assert len(cands) >= 4
    # Check that graphics selective reconstruction is synthesized for graphics workload
    has_gfx = any(any(t.category == "GRAPHICS" for t in c.transformations) for c in cands)
    assert has_gfx is True


# 5. Pathway Composer
def test_pathway_composer():
    generator = PathwayGenerator()
    cands = generator.generate_candidates("Dense_GEMM", sample_input=None, max_candidates=5)
    composer = PathwayComposer()

    # Compose pair
    res = composer.compose_pair(cands[1], cands[2])
    assert res.is_compatible is True
    assert res.composite_pathway is not None
    assert res.combined_work_reduction_pct > 0.0
    assert res.estimated_speedup_multiplier > 1.0


# 6. Cost Model
def test_pathway_cost_model():
    generator = PathwayGenerator()
    cands = generator.generate_candidates("Dense_GEMM", sample_input=None)
    model = PathwayCostModel()

    res = model.evaluate_cost(cands[1], baseline_latency_ms=10.0, bytes_transferred=2 * 1024 * 1024)
    assert res.is_cost_viable is True
    assert res.t_total_ms > 0.0
    assert res.resource_profile.memory_bandwidth_gb_s <= model.MAX_BANDWIDTH_GB_S
    assert res.resource_profile.ram_mb <= model.MAX_SYSTEM_RAM_MB
    assert res.overhead_ratio >= 0.0


# 7. Checkpoint Engine
def test_checkpoint_engine(tmp_path):
    cp_path = str(tmp_path / "test_discovery_checkpoint.json")
    engine = CheckpointEngine(checkpoint_path=cp_path)

    cp = DiscoveryCheckpoint(current_workload="test_gemm", iteration_count=5)
    engine.save_checkpoint(cp)

    loaded = engine.load_checkpoint()
    assert loaded is not None
    assert loaded.current_workload == "test_gemm"
    assert loaded.iteration_count == 5

    # Test record failure and success
    engine.record_failure("pw-123", "test_gemm", "Numerical divergence", True)
    loaded_after = engine.load_checkpoint()
    assert len(loaded_after.failed_candidates) == 1
    assert loaded_after.failed_candidates[0]["counterexample_found"] is True


# 8. Destination Tracker
def test_destination_tracker(tmp_path):
    tracker_file = str(tmp_path / "test_destination.json")
    tracker = DestinationTracker(state_file=tracker_file)
    summary = tracker.get_summary()

    # Scientific honesty assertion
    assert summary["physical_hardware_equivalence"] == "NOT CLAIMED (PHYSICALLY_DISJOINT)"
    assert "UNPROVEN" in summary["universal_parity_status"]

    # Update from benchmark results
    tracker.update_from_benchmark_results(
        workloads_total=12,
        workloads_verified=10,
        exact_matches=8,
        apps_covered=9,
        total_apps=12,
        avg_speedup_vs_gpu_target=2.5,
    )
    updated = tracker.get_summary()
    assert updated["verified_workload_contract_coverage_pct"] == 83.3
    assert updated["exact_computational_parity_pct"] == 66.7
    assert updated["measured_performance_parity_pct"] <= 65.0  # Never falsely 100%


# 9. Controlled Workloads Suite (12 Primary Workloads)
def test_controlled_workloads_suite():
    bench = ControlledWorkloadBenchmark()
    reports = bench.run_all()
    assert len(reports) == 12

    # Verify every report conforms to Section 42
    for r in reports:
        assert r.pathway_id.startswith("pw-ctrl-")
        assert r.status in ("VERIFIED", "DISCOVERED")
        assert r.speedup >= 1.0
        assert r.work_reduction >= 0.0
        assert "reference_ms" in r.execution_time
        assert "candidate_ms" in r.execution_time
        assert r.evidence_level == "MEASURED"


# 10. Kimi K3 Discovery Brain & Multi-Agent Debate
def test_kimi_k3_discovery_brain():
    brain = KimiK3DiscoveryBrain()
    decomposer = GPUCapabilityDecomposer()
    contract = decomposer.create_contract_for_capability("Dense_GEMM", "workload-gemm")

    debate = brain.conduct_adversarial_debate("Dense_GEMM", contract)
    assert len(debate.transcript) == 5
    assert debate.criticisms_resolved is True
    assert len(debate.novel_transformations) > 0

    # Verify distinct roles in transcript
    roles = {stmt.role for stmt in debate.transcript}
    assert K3ResearchRole.K3_ALGORITHM_RESEARCHER in roles
    assert K3ResearchRole.K3_COUNTEREXAMPLE_GENERATOR in roles
    assert K3ResearchRole.K3_PATHWAY_COMPOSER in roles


# 11. Mathematical Reformulation & Error Bounds
def test_mathematical_reformulation_engine():
    # 1. Horner polynomial evaluation
    coeffs = [2.0, -3.0, 1.5, 0.5]
    x = np.linspace(-2.0, 2.0, 100)
    res, report = MathematicalReformulationEngine.factorize_polynomial_horner(coeffs, x)
    assert report.is_exact is True
    assert report.error_bounds.max_absolute_error < 1e-10
    assert report.arithmetic_reduction_pct == 50.0

    # 2. Circulant matrix detection
    c = np.array([1.0, 2.0, 3.0, 4.0])
    circ = np.array([np.roll(c, i) for i in range(4)])
    first_row = MathematicalReformulationEngine.detect_and_compress_circulant(circ)
    assert first_row is not None
    assert np.allclose(first_row, c)


# 12. Application Target Registry
def test_application_target_registry():
    targets = ApplicationTargetRegistry.list_targets()
    assert len(targets) >= 9

    blender_t = ApplicationTargetRegistry.get_target("blender")
    assert blender_t is not None
    assert blender_t.app_type == ApplicationTargetType.BLENDER
    assert blender_t.capability_family == CapabilityFamily.RAY_TRACING


# 13. FastAPI Discovery Endpoints
def test_fastapi_discovery_endpoints():
    client = TestClient(app)

    # Capabilities taxonomy
    r1 = client.get("/api/v1/discovery/capabilities/families")
    assert r1.status_code == 200
    assert len(r1.json()["families"]) >= 7

    # Pathway candidate generation
    r2 = client.post("/api/v1/discovery/pathway/generate", json={"workload_name": "Attention_Flash", "max_candidates": 3})
    assert r2.status_code == 200
    assert r2.json()["total_generated"] >= 3

    # K3 debate
    r3 = client.post("/api/v1/discovery/k3/debate", json={"workload_name": "N_Body_Simulation"})
    assert r3.status_code == 200
    assert len(r3.json()["transcript"]) == 5

    # Destination tracker
    r4 = client.get("/api/v1/discovery/destination-tracker")
    assert r4.status_code == 200
    assert r4.json()["physical_hardware_equivalence"] == "NOT CLAIMED (PHYSICALLY_DISJOINT)"

    # Controlled suite execution
    r5 = client.get("/api/v1/discovery/workloads/controlled-suite")
    assert r5.status_code == 200
    data5 = r5.json()
    assert data5["total_workloads"] == 12

    # App targets
    r6 = client.get("/api/v1/discovery/app-targets")
    assert r6.status_code == 200
    assert len(r6.json()["targets"]) >= 9
