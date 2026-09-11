"""
tests/test_universal_escape_engine.py
======================================
Comprehensive unit and integration tests for:
  - UniversalEscapeEngine (21-step search order)
  - LowerBoundAnalyzer (Sections 28 & 62)
  - HardwareAdvantageAnalyzer (Sections 18 & 19)
  - UniversalityAnalyzer (Section 81)
  - CoverageEngine (Section 47)
  - ApplicationParityEngine (Section 48)
  - ClaimValidator (Section 58)
"""

import pytest
import numpy as np

from hyper_cco.contract import WorkloadContract, CorrectnessClass
from hyper_cco.universal_escape_engine import UniversalEscapeEngine, EscapeOutcome
from hyper_cco.lower_bound_analyzer import LowerBoundAnalyzer, NecessityStatus, BoundConstraintType
from hyper_cco.hardware_advantage_analyzer import HardwareAdvantageAnalyzer, GPUAdvantageType
from hyper_cco.universality_analyzer import UniversalityAnalyzer, TransformationScope
from hyper_cco.coverage_engine import CoverageEngine
from hyper_cco.application_parity_engine import ApplicationParityEngine, ApplicationContract, ApplicationDomain
from hyper_cco.claim_validator import ClaimValidator


def test_universal_escape_engine_exact_cache():
    engine = UniversalEscapeEngine()
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    contract = WorkloadContract(workload_id="TEST_GEMM", exactness_class=CorrectnessClass.NUMERICALLY_BOUNDED)

    # First run: cold run
    res1 = engine.run_matrix_escape_search("TEST_GEMM", A, B, contract)
    assert res1.contract_satisfied is True

    # Second run with same input: MUST hit exact cache
    res2 = engine.run_matrix_escape_search("TEST_GEMM", A, B, contract)
    assert res2.outcome == EscapeOutcome.WORMHOLE_FOUND
    assert res2.winning_step == 1
    assert res2.winning_transformation == "EXACT_CACHE"
    assert res2.work_elimination_ratio == 1.0
    assert res2.gadr == 0.0
    assert res2.hae == 1.0


def test_universal_escape_engine_observable_reduction():
    engine = UniversalEscapeEngine()
    A = np.random.randn(128, 64).astype(np.float32)
    B = np.random.randn(64, 64).astype(np.float32)
    contract = WorkloadContract(workload_id="TEST_TOPK", exactness_class=CorrectnessClass.REDUCED_WORK)

    # Downstream consumer only requires top-8 rows
    res = engine.run_matrix_escape_search("TEST_TOPK", A, B, contract, observable_top_k=8)
    assert res.outcome == EscapeOutcome.WORMHOLE_FOUND
    assert res.winning_step == 4
    assert "OBSERVABLE_SLICING_TOP_8" in res.winning_transformation
    assert res.work_elimination_ratio > 0.90


def test_universal_escape_engine_necessary_computation():
    engine = UniversalEscapeEngine()
    # Unstructured Gaussian matrix with full rank
    rng = np.random.default_rng(1234)
    A = rng.standard_normal((64, 64)).astype(np.float32)
    B = rng.standard_normal((64, 64)).astype(np.float32)
    contract = WorkloadContract(workload_id="TEST_EXACT_GAUSS", exactness_class=CorrectnessClass.EXACT_EQUIVALENT)

    res = engine.run_matrix_escape_search("TEST_EXACT_GAUSS", A, B, contract)
    assert res.outcome == EscapeOutcome.NECESSARY_COMPUTATION_IDENTIFIED
    assert res.winning_step == 21
    assert res.work_elimination_ratio == 0.0
    assert res.gadr == 1.0
    assert res.hae == 0.0
    assert res.contract_satisfied is True


def test_lower_bound_analyzer():
    contract_exact = WorkloadContract(workload_id="EXACT_GEMM", exactness_class=CorrectnessClass.EXACT_EQUIVALENT)
    A = np.random.randn(32, 32).astype(np.float32)
    B = np.random.randn(32, 32).astype(np.float32)

    report = LowerBoundAnalyzer.analyze_matrix_lower_bound(A, B, contract_exact, [])
    assert report.status == NecessityStatus.PROVABLY_NECESSARY_UNDER_MODEL
    assert report.primary_barrier == BoundConstraintType.EXACTNESS_CONTRACT
    assert report.confidence == 1.0


def test_hardware_advantage_analyzer():
    inversion = HardwareAdvantageAnalyzer.evaluate_inversion(
        advantage_type=GPUAdvantageType.MASSIVE_PARALLELISM,
        original_work_units=1000.0,
        remaining_necessary_units=3.0
    )
    assert inversion.gadr == 0.003
    assert inversion.hae == 0.997
    assert inversion.hae > 0.99


def test_universality_analyzer():
    # Contract-specific test
    assessment = UniversalityAnalyzer.assess(
        transformation_name="low_rank_svd",
        tested_domains=["dense_gemm"],
        tested_tolerances=[1e-2],
        passed_exact=False,
        spectral_dependency=True
    )
    assert assessment.primary_scope == TransformationScope.CONTRACT_SPECIFIC
    assert assessment.is_universal_claim_valid is False

    # Broadly general test
    assessment_general = UniversalityAnalyzer.assess(
        transformation_name="associative_reordering",
        tested_domains=["linear_algebra", "deep_learning", "graphics", "physics"],
        tested_tolerances=[0.0],
        passed_exact=True,
        spectral_dependency=False
    )
    assert assessment_general.primary_scope == TransformationScope.BROADLY_GENERAL
    assert assessment_general.is_universal_claim_valid is True


def test_coverage_engine():
    cov = CoverageEngine.calculate_current_coverage(
        evaluated_workloads=6,
        closed_workloads=6,
        audited_ops=24,
        classified_ops=24,
        adversarial_run=56,
        adversarial_passed=56,
    )
    assert cov.contract_coverage == 1.0
    assert cov.necessity_coverage == 1.0
    assert cov.verification_coverage == 1.0
    d = cov.to_dict()
    assert d["ContractCoverage"] == 100.0
    assert d["NecessityCoverage"] == 100.0


def test_application_parity_engine():
    # Test graphics viewport contract
    frame_ref = np.zeros((100, 100, 3), dtype=np.uint8)
    frame_cand = np.zeros((100, 100, 3), dtype=np.uint8)
    contract_gfx = ApplicationContract(
        domain=ApplicationDomain.GRAPHICS_VIEWPORT,
        workload_name="720p_Viewport",
        latency_slo_ms=16.6,
        min_quality_metric="SSIM",
        min_quality_threshold=0.92
    )
    res_gfx = ApplicationParityEngine.evaluate_graphics_parity(
        candidate_frame=frame_cand,
        reference_frame=frame_ref,
        frame_time_ms=1.43,
        contract=contract_gfx
    )
    assert res_gfx.parity_satisfied is True
    assert res_gfx.observed_quality_value == 1.0

    # Test scientific simulation contract
    u_ref = np.ones((50, 50), dtype=np.float32)
    u_cand = np.ones((50, 50), dtype=np.float32) + 1e-4
    contract_sci = ApplicationContract(
        domain=ApplicationDomain.SCIENTIFIC_SIMULATION,
        workload_name="Poisson_Grid",
        latency_slo_ms=10.0,
        min_quality_metric="L2_RESIDUAL",
        min_quality_threshold=1e-2
    )
    res_sci = ApplicationParityEngine.evaluate_scientific_parity(
        candidate_field=u_cand,
        reference_field=u_ref,
        solve_time_ms=0.96,
        contract=contract_sci
    )
    assert res_sci.parity_satisfied is True


def test_claim_validator():
    # Legitimate scientific text
    legit_text = "HYPER-CCO achieves 100% Contract Parity on the Poisson PDE workload via multi-grid residual smoothing."
    report_legit = ClaimValidator.validate_text(legit_text)
    assert report_legit.is_valid is True

    # Prohibited claim: "beats every NVIDIA GPU"
    bad_text = "LEO beats every NVIDIA GPU in raw computing throughput!"
    report_bad = ClaimValidator.validate_text(bad_text)
    assert report_bad.is_valid is False
    assert len(report_bad.violations) >= 1
    assert "Universal Hardware Superiority" in report_bad.violations[0].reason
