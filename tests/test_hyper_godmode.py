"""
tests/test_hyper_godmode.py
===========================
Comprehensive unit and integration test suite for HYPER-GODMODE:
- Information Sufficiency Engine
- Counterfactual Optimizer
- Inverse Computation Engine
- Physical Resource Mirror
- Observable Equivalence Matrix
- Universal Workload Router
- Failure Knowledge Base
- Immutable Experiment Database
- 100% Certification Engine (All 13 Criteria)
- Mathematical Reformulation Library
- Pathway Evolution Engine
- 5 Section 40 Proof-of-Concept Discovery Experiments
- GODMODE Dashboard & Terminal Scoreboard
"""

import pytest
import numpy as np

from hyper.information_sufficiency import (
    InformationSufficiencyEngine,
    InfluenceType,
    ProofStatus,
)
from hyper.counterfactual import (
    CounterfactualOptimizer,
    CounterfactualVerdict,
)
from hyper.inverse_computation import (
    InverseComputationEngine,
    DerivationStrategy,
)
from hyper.physical_resource_mirror import (
    PhysicalResourceMirror,
    LiteralPhysicalParityStatus,
    ObservableEquivalenceStatus,
    GPUHardwareSubsystem,
)
from hyper.observable_equivalence import (
    ObservableEquivalenceMatrix,
    EquivalenceStatus,
)
from hyper.workload_router import (
    UniversalWorkloadRouter,
    WorkloadCategory,
    PathwayFamily,
)
from hyper.failure_knowledge import (
    FailureKnowledgeBase,
    FailureCategory,
)
from hyper.experiment_database import (
    ImmutableExperimentDatabase,
    EvidenceClass,
)
from hyper.certificates import (
    GodmodeCertificationEngine,
    CertificationVerdict,
)
from hyper.mathematical_reformulation import (
    MathematicalReformulationLibrary,
)
from hyper.godmode.pathway_evolution import (
    PathwayEvolutionEngine,
)
from hyper.parity_engine.pathway_ir import PathwayIR
from benchmarks.godmode_experiments import (
    GodmodeExperiments,
)
from hyper.godmode.dashboard import (
    GodmodeDashboard,
)


def test_information_sufficiency_engine():
    ops = [
        {"id": "op_load", "type": "load", "inputs": [], "output": "A"},
        {"id": "op_dead", "type": "noop", "inputs": ["A"], "output": "dead_temp", "is_redundant": True},
        {"id": "op_core", "type": "matmul", "inputs": ["A"], "output": "result"},
    ]
    graph, report = InformationSufficiencyEngine.analyze_sufficiency(
        workload_name="test_sufficiency",
        operations=ops,
        output_targets=["result"],
    )
    assert graph.total_operations == 3
    assert graph.eliminable_operations >= 1
    assert report.is_contract_invariant is True
    assert report.information_sufficiency_ratio <= 1.0


def test_counterfactual_optimizer():
    # Test safe elimination
    base_fn = lambda x: (x * 2.0) + 0.0
    bypassed_fn = lambda x: x * 2.0  # Removing dead + 0.0
    inputs = [np.array([1.0, 2.0]), np.array([5.0, 10.0])]

    eval_res = CounterfactualOptimizer.evaluate_operation_removal(
        operation_id="op_dead_add",
        operation_name="Add Zero",
        baseline_fn=base_fn,
        bypassed_fn=bypassed_fn,
        test_inputs=inputs,
    )
    assert eval_res.verdict == CounterfactualVerdict.ELIMINATION_PROVEN_SAFE
    assert eval_res.counterexample_found is False

    # Test unsafe elimination (violates contract)
    unsafe_bypassed = lambda x: x * 1.0
    eval_unsafe = CounterfactualOptimizer.evaluate_operation_removal(
        operation_id="op_scale",
        operation_name="Multiply by Two",
        baseline_fn=base_fn,
        bypassed_fn=unsafe_bypassed,
        test_inputs=inputs,
    )
    assert eval_unsafe.verdict == CounterfactualVerdict.REJECT_VIOLATES_CONTRACT
    assert eval_unsafe.counterexample_found is True


def test_inverse_computation_engine():
    plan = InverseComputationEngine.derive_minimal_computation(
        workload_name="gemm_inverse_test",
        contract_id="CTR_GEMM",
        output_spec={"matrix_result": np.ones((16, 16))},
        known_invariants=["Row major layout"],
    )
    assert len(plan.requirements) >= 1
    assert len(plan.what_must_be_known) >= 1
    assert len(plan.what_does_not_need_to_be_known) >= 1
    assert plan.total_elimination_pct > 0.0


def test_physical_resource_mirror():
    mirror = PhysicalResourceMirror()
    summary = mirror.get_mirror_summary()
    assert summary["subsystems_tracked"] >= 4
    assert summary["literal_physical_parity_verdict"] == LiteralPhysicalParityStatus.PHYSICAL_SILICON_EXCLUDED.value
    assert summary["observable_resource_equivalence_verified_pct"] == 100.0

    tensor_mapping = mirror.mappings[GPUHardwareSubsystem.TENSOR_CORES]
    assert "AVX2" in tensor_mapping.local_hardware_available
    assert tensor_mapping.literal_physical_parity == LiteralPhysicalParityStatus.PHYSICAL_SILICON_EXCLUDED
    assert tensor_mapping.observable_equivalence == ObservableEquivalenceStatus.OBSERVABLE_EQUIVALENCE_VERIFIED


def test_observable_equivalence_matrix():
    matrix = ObservableEquivalenceMatrix()
    rows = matrix.get_matrix_rows()
    assert len(rows) >= 8
    gemm_row = matrix.rows.get("Matrix Multiplication (GEMM)")
    assert gemm_row is not None
    assert gemm_row.status == EquivalenceStatus.VERIFIED
    table_md = matrix.to_markdown_table()
    assert "| GPU Capability |" in table_md
    assert "Tensor Cores" in table_md


def test_universal_workload_router():
    r1 = UniversalWorkloadRouter.classify_and_route("transformer_attention_sdpa")
    assert r1.detected_category in [WorkloadCategory.AI, WorkloadCategory.LINEAR_ALGEBRA]
    assert r1.recommended_pathway_family == PathwayFamily.SPARSE_BLOCK_TILING

    r2 = UniversalWorkloadRouter.classify_and_route("heat_stencil_pde_solver")
    assert r2.detected_category == WorkloadCategory.SCIENTIFIC
    assert r2.recommended_pathway_family == PathwayFamily.SEPARABLE_FILTER_FACTORIZATION

    r3 = UniversalWorkloadRouter.classify_and_route("sha256_cryptographic_hash")
    assert r3.detected_category == WorkloadCategory.CRYPTOGRAPHY
    assert r3.recommended_pathway_family == PathwayFamily.EXACT_CONSTANT_TIME_ARITHMETIC


def test_failure_knowledge_base():
    kb = FailureKnowledgeBase(storage_path="reports/test_failure_knowledge.json")
    rec = kb.record_failure(
        workload_name="test_workload",
        pathway_id="PTH_TEST_FAIL",
        category=FailureCategory.CORRECTNESS_FAILURE,
        failed_transformation="NAIVE_FP16_TRUNCATION",
        counterexample_summary="Inf on large exponents",
        bottleneck_description="Dynamic range underflow",
        learned_constraint="Require FP32 accumulator for large dynamic ranges",
    )
    assert rec.failure_id.startswith("FAIL_")
    assert kb.is_transformation_forbidden("test_workload", "NAIVE_FP16_TRUNCATION") is True
    assert kb.is_transformation_forbidden("test_workload", "CACHE_BLOCKING") is False


def test_immutable_experiment_database():
    db = ImmutableExperimentDatabase(db_path="reports/test_experiment_db.json")
    exp = db.record_experiment(
        workload_name="test_workload",
        pathway_id="PTH_TEST_EXP",
        raw_latencies_ms=[2.1, 2.2, 2.0, 2.15],
        input_data=np.zeros((4, 4)),
        output_data=np.zeros((4, 4)),
        is_correct=True,
        reference_latency_ms=4.4,
        evidence_level=EvidenceClass.MEASURED,
    )
    assert exp.experiment_id.startswith("EXP_")
    assert exp.median_latency_ms > 0.0
    assert exp.measured_speedup_vs_reference >= 1.9
    assert exp.evidence_level == EvidenceClass.MEASURED
    assert len(exp.record_sha256) == 64


def test_godmode_certification_engine():
    # Test valid 13/13 criteria
    cert_valid = GodmodeCertificationEngine.audit_and_certify(
        workload_name="test_cert",
        pathway_id="PTH_VALID",
        contract_defined=True,
        reference_exists=True,
        optimized_exists=True,
        exactness_passed=True,
        quality_passed=True,
        performance_passed=True,
        memory_passed=True,
        thermal_passed=True,
        worst_case_passed=True,
        adversarial_passed=True,
        blind_holdout_passed=True,
        reproducibility_passed=True,
        real_app_passed=True,
    )
    assert cert_valid.verdict == CertificationVerdict.VERIFIED_100_PERCENT
    assert cert_valid.all_13_criteria_passed is True

    # Test failure on 1 criterion
    cert_invalid = GodmodeCertificationEngine.audit_and_certify(
        workload_name="test_cert_fail",
        pathway_id="PTH_INVALID",
        contract_defined=True,
        reference_exists=True,
        optimized_exists=True,
        exactness_passed=True,
        quality_passed=True,
        performance_passed=False,  # Performance failed!
        memory_passed=True,
        thermal_passed=True,
        worst_case_passed=True,
        adversarial_passed=True,
        blind_holdout_passed=True,
        reproducibility_passed=True,
        real_app_passed=True,
    )
    assert cert_invalid.verdict == CertificationVerdict.NOT_100_PERCENT_VERIFIED
    assert cert_invalid.all_13_criteria_passed is False


def test_mathematical_reformulation_library():
    # 1. Contiguous GEMM
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32).T
    res_gemm = MathematicalReformulationLibrary.blocked_contiguous_gemm(A, B)
    assert np.allclose(res_gemm, A @ B, atol=1e-5)

    # 2. Strassen
    res_strassen = MathematicalReformulationLibrary.strassen_2x2_submatrix(A, B)
    assert np.allclose(res_strassen, A @ B, atol=1e-5)

    # 3. Separable Laplacian Stencil
    grid = np.zeros((32, 32), dtype=np.float32)
    grid[16, 16] = 50.0
    res_stencil = MathematicalReformulationLibrary.separable_laplacian_2d(grid, steps=2)
    assert res_stencil.shape == (32, 32)
    assert res_stencil[16, 16] < 50.0

    # 4. Temporal Frame Reconstruction
    history = np.zeros((16, 16, 3), dtype=np.float32)
    dirty = np.zeros((16, 16), dtype=bool)
    dirty[4:8, 4:8] = True
    new_patch = np.ones((16, 16, 3), dtype=np.float32)
    recon = MathematicalReformulationLibrary.temporal_frame_reconstruction(history, dirty, new_patch)
    assert recon[0, 0, 0] == 0.0
    assert recon[5, 5, 0] == 1.0

    # 5. Exact Cryptographic Hash
    digest = MathematicalReformulationLibrary.exact_constant_time_digest(b"HYPER-GODMODE")
    assert len(digest) == 64


def test_pathway_evolution_engine():
    base = PathwayIR(
        pathway_id="PTH_EVO_TEST",
        capability_id="CAP_TEST",
        workload_id="WLD_TEST",
        contract_id="CTR_TEST",
        algorithm_name="baseline",
        mathematical_basis="direct",
    )
    engine = PathwayEvolutionEngine(seed=42)
    trace = engine.evolve_pathways(
        workload_name="test_evolution",
        base_pathway=base,
        evaluate_fitness_fn=lambda genes: (True, 1.0 + len(genes) * 0.2, 50.0 + len(genes) * 5.0),
        generations=3,
        population_size=4,
    )
    assert trace.generations_completed == 3
    assert len(trace.generation_summaries) == 4  # Gen 0 + Gen 1-3
    assert trace.fittest_speedup >= 1.0


def test_section_40_experiments_suite():
    experiments = GodmodeExperiments()
    result = experiments.run_all_five_experiments()
    assert result.total_experiments == 5
    assert result.certified_100_percent_count == 5, f"Failing experiments: {[(r.workload_name, r.measured_speedup, r.is_100_percent_certified) for r in result.experiment_results if not getattr(r, 'is_100_percent_certified', False)]}"
    assert result.average_speedup >= 0.8
    assert result.average_work_reduction_pct >= 50.0


def test_godmode_dashboard_and_scoreboard():
    dash = GodmodeDashboard(state_path="reports/test_godmode_dash_state.json")
    text = dash.render_cli()
    assert "HYPER-GODMODE OBSERVABLE PARITY SCOREBOARD" in text
    assert "PHYSICAL RESOURCE MIRROR" in text
    assert "100% CERTIFICATION VERDICT" in text
    assert "PHYSICAL_SILICON_EXCLUDED" in text
