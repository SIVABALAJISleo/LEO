"""
tests/test_hyper100_parity_engine.py
====================================
Comprehensive Test Suite for HYPER 100% Universal Computational Parity Engine.

Validates all 17 implementation phases and Section 48 first automated experiment:
1. Universal GPU Capability Taxonomy & Registry (Sections 1-4)
2. Performance Contract Engine & CONTRACT_UNDEFINED guard (Section 28)
3. Pathway IR Data Structure & 10 Architectural Pillars (Section 8)
4. GPU Capability & Workload Decomposer + DAG dead branch pruning (Section 5)
5. Counterfactual Engine, Information Sufficiency & Reuse (Sections 10-15)
6. Kimi K3 Discovery Brain with 14 Specialist Roles (Section 7)
7. Search Space Compiler with 12 Strategies & Progressive Search (Sections 6, 8, 9)
8. Certificate Engine with 12 Certificate Types (Section 25)
9. Trusted Reference, Freivalds Randomized Probe & Anti-Cheat (Sections 27, 32, 33)
10. Adversarial Testing Gauntlet (Section 26)
11. Heterogeneous CPU+iGPU Dynamic Placement & Memory Engine (Sections 23, 24)
12. Pathway Composer & Re-Verification (Section 35)
13. Knowledge Graph, Failure Learning & Cross-Domain Discovery (Sections 36-38)
14. Blind Holdout Mode & Generalization Score (Sections 40, 41)
15. Universal Application Parity across 12 Software Targets (Section 29)
16. 100% Parity Score Engine & Global Coverage Matrix (Sections 30, 31, 46)
17. Section 48 First Automated Experiment across all 8 Workloads
18. Live Dashboard HTML & API Endpoints (Section 45)
"""

import pytest
import numpy as np

from hyper.hyper100_parity.taxonomy import (
    ParityLevel,
    CapabilityFamily,
    EquivalenceClass,
    EvidenceLevel,
    UniversalCapabilityRegistry,
    GLOBAL_CAPABILITY_REGISTRY,
)
from hyper.hyper100_parity.contract_engine import (
    ContractStatus,
    PrecisionMode,
    PerformanceContract,
)
from hyper.hyper100_parity.pathway_ir import (
    PathwayIR,
    DevicePlacement,
    DataRepresentation,
    MemoryStrategy,
    SchedulingStrategy,
    TransformationRecord,
)
from hyper.hyper100_parity.workload_decomposer import GPUCapabilityDecomposer
from hyper.hyper100_parity.counterfactual_engine import CounterfactualEngine, ReuseMemoEngine, WorkEliminationLedger
from hyper.hyper100_parity.k3_brain import KimiK3DiscoveryBrain, K3ResearchRole
from hyper.hyper100_parity.search_compiler import SearchSpaceCompiler, SearchStrategyType
from hyper.hyper100_parity.certificate_engine import CertificateEngine, CertificateType
from hyper.hyper100_parity.verification_engine import TrustedReferenceEngine, IndependentVerifier
from hyper.hyper100_parity.adversarial_engine import AdversarialGauntlet
from hyper.hyper100_parity.heterogeneous_compiler import HeterogeneousCompiler
from hyper.hyper100_parity.pathway_composer import PathwayComposer
from hyper.hyper100_parity.knowledge_graph import DiscoveryKnowledgeGraph, FailureRecord
from hyper.hyper100_parity.blind_holdout import BlindHoldoutRunner
from hyper.hyper100_parity.application_parity import ApplicationParityValidator
from hyper.hyper100_parity.score_engine import ParityScoreEngine, CapabilityParityScore
from hyper.hyper100_parity.master_engine import HyperMasterEngine
from hyper.hyper100_parity.first_experiment import FirstAutomatedExperimentRunner
from hyper.hyper100_parity.dashboard import generate_dashboard_html


# 1. Capability Taxonomy & Registry
def test_capability_taxonomy_and_registry():
    registry = GLOBAL_CAPABILITY_REGISTRY
    caps = registry.all_capabilities()
    assert len(caps) >= 11, "Taxonomy must register at least 11 capability specifications"

    # Check 6 unique IDs per capability
    for c in caps:
        assert c.capability_id.startswith("CAP-")
        assert c.workload_id.startswith("WRK-")
        assert c.contract_id.startswith("CTR-")
        assert c.verification_id.startswith("VRF-")
        assert c.benchmark_id.startswith("BNCH-")
        assert c.evidence_id.startswith("EVD-")

    # Check Level 1 exclusion
    assert "OUT_OF_SCOPE" in ParityLevel.LEVEL_1_PHYSICAL.value


# 2. Performance Contract Engine
def test_performance_contract_engine():
    # Defined contract
    ctr = PerformanceContract(
        contract_id="CTR-TEST-001",
        workload_name="TestWorkload",
        equivalence_class=EquivalenceClass.EXACT,
        max_abs_error=0.0,
        max_latency_ms=10.0,
    )
    assert ctr.is_defined() is True

    # Validate passing
    res_pass = ctr.validate_result(
        ref_output=np.array([1, 2, 3]),
        cand_output=np.array([1, 2, 3]),
        measured_latency_ms=2.5,
    )
    assert res_pass["passed"] is True

    # Validate failing latency
    res_fail_lat = ctr.validate_result(
        ref_output=np.array([1, 2, 3]),
        cand_output=np.array([1, 2, 3]),
        measured_latency_ms=15.0,
    )
    assert res_fail_lat["passed"] is False

    # Undefined contract guard
    undef = PerformanceContract.undefined("UnknownKernel")
    assert undef.is_defined() is False
    res_undef = undef.validate_result(None, None, 1.0)
    assert res_undef["passed"] is False
    assert "CONTRACT_UNDEFINED" in res_undef["contract_status"]


# 3. Pathway IR
def test_pathway_ir_schema():
    ctr = PerformanceContract(contract_id="CTR-IR-001", workload_name="GEMM")
    pw = PathwayIR(
        workload_id="WRK-GEMM",
        capability_family=CapabilityFamily.AI_ML,
        contract=ctr,
        algorithm_name="strassen_cache_tiled",
        representation=DataRepresentation.DENSE_FP32,
        memory_strategy=MemoryStrategy.CACHE_TILED_L1_L2,
        scheduling_strategy=SchedulingStrategy.SYNCHRONOUS_AFFINITY_PINNED,
        placement=DevicePlacement.CPU_AVX2,
    )
    d = pw.to_dict()
    assert d["workload_id"] == "WRK-GEMM"
    assert d["placement"] == DevicePlacement.CPU_AVX2.value


# 4. Workload Decomposer & DAG Pruning
def test_workload_decomposer():
    decomposer = GPUCapabilityDecomposer()
    res = decomposer.decompose("vertex_and_geometry_processing")
    assert res.capability_family == CapabilityFamily.GRAPHICS
    assert len(res.analysis.must_happen) > 0
    assert len(res.dag.nodes) >= 3

    # Check dead branch pruning
    assert res.dag.nodes["n2_unreferenced_dead_branch"].is_eliminable is True
    assert res.dag.total_flops() < res.dag.original_flops()


# 5. Counterfactual Engine, Reuse & Work Elimination
def test_counterfactual_and_reuse():
    cf = CounterfactualEngine()
    hyps = cf.generate_hypotheses("conv2d", "AI_ML")
    assert len(hyps) >= 5

    # Reuse memoization with dependency tracking
    memo = ReuseMemoEngine()
    arr = np.array([10.0, 20.0, 30.0], dtype=np.float32)
    k = memo.make_key("gemm", arr, dependencies=["weights_v1"])
    memo.store(k, arr * 2, dependencies=["weights_v1"])

    assert memo.lookup(k) is not None
    # Invalidate dependency
    invalidated = memo.invalidate_dependency("weights_v1")
    assert invalidated == 1
    assert memo.lookup(k) is None

    # Work elimination calculation
    ledger = WorkEliminationLedger.calculate(original=1000.0, executed=400.0)
    assert ledger.work_reduction_ratio == 0.6


# 6. Kimi K3 Discovery Brain & 14 Roles
def test_k3_discovery_brain():
    brain = KimiK3DiscoveryBrain()
    roles = list(K3ResearchRole)
    assert len(roles) == 14

    ctr = PerformanceContract(contract_id="CTR-K3", workload_name="Sobel")
    session = brain.conduct_research_session("Sobel", CapabilityFamily.IMAGE, ctr)
    assert len(session.proposals) > 0
    assert len(session.criticisms) >= 2
    assert session.consensus_hypothesis != ""


# 7. Search Space Compiler & Progressive Search
def test_search_space_compiler():
    compiler = SearchSpaceCompiler()
    ctr = PerformanceContract(contract_id="CTR-SRCH", workload_name="PDE")
    cands, ledger = compiler.compile_search_space(
        workload_name="PDE",
        family=CapabilityFamily.SCIENTIFIC,
        contract=ctr,
        strategy=SearchStrategyType.BEAM_SEARCH,
        candidate_budget=10,
    )
    assert len(cands) >= 5
    assert ledger.candidates_generated >= 5
    assert ledger.search_space_explored_nodes > 0


# 8. Certificate Engine & 12 Types
def test_certificate_engine():
    engine = CertificateEngine()
    assert len(CertificateType) == 12

    cert = engine.issue_certificate(
        cert_type=CertificateType.EXACT_EQUIVALENCE,
        original_desc="Canonical loop",
        replacement_desc="Vectorized SIMD",
        assumptions=["Field ring axioms"],
        formal_proof="Algebraic identity holds for all inputs.",
        test_results=[{"passed": True}],
        adversarial_results=[{"passed": True}],
        numerical_error=0.0,
    )
    assert cert.status.value == "VALID"
    assert engine.verify_certificate(cert.id) is True


# 9. Trusted Reference & Freivalds Probe
def test_freivalds_matrix_verify():
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)
    C_correct = np.dot(A, B)
    C_corrupt = C_correct.copy()
    C_corrupt[0, 0] += 5.0

    assert TrustedReferenceEngine.freivalds_matrix_verify(A, B, C_correct) is True
    assert TrustedReferenceEngine.freivalds_matrix_verify(A, B, C_corrupt) is False


# 10. Adversarial Gauntlet
def test_adversarial_gauntlet():
    gauntlet = AdversarialGauntlet()
    inputs = gauntlet.generate_adversarial_inputs((16, 16))
    assert len(inputs) >= 6

    # Test candidate on gauntlet
    ref = lambda x: x * 2.0
    cand = lambda x: x * 2.0
    ctr = PerformanceContract(contract_id="CTR-ADV", workload_name="Scale")
    results = gauntlet.attack_candidate(cand, ref, (16, 16), ctr)
    assert len(results) >= 6
    assert all(r.survived for r in results) is True


# 11. Heterogeneous CPU+iGPU Compiler
def test_heterogeneous_compiler():
    compiler = HeterogeneousCompiler()
    # Small workload fits in L2 cache -> CPU_AVX2
    dec_small = compiler.schedule_workload("tiny_dot", tensor_size_bytes=64 * 1024, estimated_flops=1e5)
    assert dec_small.selected_device == DevicePlacement.CPU_AVX2

    # High intensity large workload -> cooperative
    dec_large = compiler.schedule_workload("huge_gemm", tensor_size_bytes=8 * 1024 * 1024, estimated_flops=3e8)
    assert dec_large.selected_device == DevicePlacement.CPU_IGPU_COOPERATIVE


# 12. Pathway Composer
def test_pathway_composer():
    composer = PathwayComposer()
    ctr = PerformanceContract(contract_id="CTR-COMP", workload_name="Double")
    base = PathwayIR(
        workload_id="WRK-DOUBLE",
        capability_family=CapabilityFamily.GENERAL_COMPUTE,
        contract=ctr,
        algorithm_name="scalar_double",
    )
    t1 = TransformationRecord(name="simd_vector", category="COMPILER", mathematical_basis="AVX2")
    t2 = TransformationRecord(name="unroll_4x", category="COMPILER", mathematical_basis="Unroll")

    ref_fn = lambda x: x * 2.0
    cand_builder = lambda names: (lambda x: x * 2.0)
    arr = np.array([1.0, 2.0, 3.0], dtype=np.float32)

    results = composer.compose_transformations(
        base_pathway=base,
        available_transformations=[t1, t2],
        reference_fn=ref_fn,
        candidate_builder_fn=cand_builder,
        sample_input=arr,
        contract=ctr,
    )
    assert len(results) == 1
    assert results[0].composition_valid is True


# 13. Knowledge Graph & Cross-Domain Discovery
def test_knowledge_graph():
    kg = DiscoveryKnowledgeGraph(storage_path="reports/test_kg.json")
    transfers = kg.get_cross_domain_suggestions(CapabilityFamily.VIDEO)
    assert len(transfers) > 0
    assert transfers[0].source_domain == CapabilityFamily.GRAPHICS


# 14. Blind Holdout Mode & Generalization
def test_blind_holdout_runner():
    runner = BlindHoldoutRunner()
    rep = runner.run_holdout_evaluation(known_passed=8, known_total=8)
    assert rep.unseen_holdouts_tested == 4
    assert rep.unseen_holdouts_passed == 4
    assert rep.generalization_score == 1.0
    assert rep.verdict == "TRUE_GENERALIZATION_PROVEN"


# 15. Universal Application Parity (12 Targets)
def test_universal_application_parity():
    validator = ApplicationParityValidator()
    records = validator.run_all_application_validations()
    assert len(records) == 12
    assert all(r.contract_passed for r in records) is True
    assert all(r.status == "VERIFIED" for r in records) is True


# 16. Section 48 First Automated Experiment (8 Workloads)
def test_section_48_first_automated_experiment():
    runner = FirstAutomatedExperimentRunner()
    res = runner.run_all()
    assert res.workloads_executed == 8
    assert res.workloads_verified == 8
    assert res.global_coverage_matrix.global_verified_parity_pct == 100.0
    assert res.global_coverage_matrix.exact_coverage_pct == 100.0
    assert len(res.pathway_reports) == 8

    # Verify each report satisfies Section 46 schema
    for rep in res.pathway_reports:
        assert rep.status == "VERIFIED"
        assert rep.reproducibility == "100% REPRODUCIBLE (DETERMINISTIC SEED 42)"
        assert rep.evidence_level == "VERIFIED"


# 17. Live Dashboard HTML Generation
def test_dashboard_html_generation():
    runner = FirstAutomatedExperimentRunner()
    res = runner.run_all()
    data = {
        "matrix": res.global_coverage_matrix.model_dump(),
        "reports": [r.model_dump() for r in res.pathway_reports],
    }
    html = generate_dashboard_html(data)
    assert "HYPER 100% PARITY DASHBOARD" in html
    assert "PHYSICAL_PARITY = EXCLUDED" in html
    assert "Dense_Matrix_Multiplication" in html
    assert "PDE_2D_Heat_Stencil" in html
