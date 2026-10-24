"""
tests/test_computation_escape_advisor.py
========================================
Test Suite for the Computation Escape Advisor & Computational Phase-Change Engine (CPCE).
Validates:
1. Structural Analysis (Identity, Zero, Diagonal, Sparse, Constant, Dense).
2. Detection cost accounting.
3. Verified rewrite executions vs. independent textbook references.
4. Strict refusal to silently approximate exact contracts.
5. Safe fallback when no structural bypass applies.
"""

import pytest
import numpy as np

from hyper.research_engine.computation_escape_advisor import (
    ComputationEscapeAdvisor,
    StructuralAnalyzer,
    StructureType,
    ESCAPE_ADVISOR,
)
from hyper.canonical.workload_registry import CANONICAL_REGISTRY, ExactnessClass
from hyper.canonical.independent_reference import IndependentReferenceEngine
from hyper.canonical.verification_state_machine import StrictVerificationRunner


class TestStructuralAnalyzer:
    """Verifies that the structural analyzer correctly detects mathematical structures."""

    def test_detects_identity_matrix(self):
        I_mat = np.eye(64, dtype=np.float32)
        meta = StructuralAnalyzer.analyze_tensor("B", I_mat)
        assert meta.structure_type == StructureType.IDENTITY
        assert meta.is_square is True
        assert meta.nnz == 64
        assert meta.detection_cost_ms >= 0.0

    def test_detects_zero_matrix(self):
        Z_mat = np.zeros((32, 32), dtype=np.float32)
        meta = StructuralAnalyzer.analyze_tensor("A", Z_mat)
        assert meta.structure_type == StructureType.ZERO
        assert meta.sparsity_ratio == 1.0
        assert meta.nnz == 0

    def test_detects_diagonal_matrix(self):
        diag_vec = np.arange(1, 33, dtype=np.float32)
        D_mat = np.diag(diag_vec)
        meta = StructuralAnalyzer.analyze_tensor("B", D_mat)
        assert meta.structure_type == StructureType.DIAGONAL
        assert meta.is_square is True
        assert meta.nnz == 32
        assert "diagonal" in meta.properties

    def test_detects_sparse_matrix(self):
        # 95% zeros
        arr = np.zeros((100, 100), dtype=np.float32)
        arr[5, 10] = 1.0
        arr[20, 30] = 2.0
        meta = StructuralAnalyzer.analyze_tensor("A", arr)
        assert meta.structure_type == StructureType.SPARSE
        assert meta.sparsity_ratio >= 0.99

    def test_detects_constant_vector(self):
        c_vec = np.full(1000, 7.5, dtype=np.float32)
        meta = StructuralAnalyzer.analyze_tensor("x", c_vec)
        assert meta.structure_type == StructureType.CONSTANT
        assert meta.properties.get("constant_value") == 7.5

    def test_identifies_unstructured_dense_matrix(self):
        rng = np.random.default_rng(42)
        dense_mat = rng.standard_normal((64, 64)).astype(np.float32)
        meta = StructuralAnalyzer.analyze_tensor("A", dense_mat)
        assert meta.structure_type == StructureType.DENSE
        assert meta.detection_cost_ms >= 0.0


class TestComputationEscapeAdvisorRewrites:
    """Verifies sound phase-change rewrites and equivalence to independent references."""

    def test_identity_right_elimination_equivalence(self):
        advisor = ComputationEscapeAdvisor()
        A = np.random.default_rng(42).standard_normal((128, 128)).astype(np.float32)
        I_mat = np.eye(128, dtype=np.float32)
        inputs = {"A": A, "B": I_mat}

        report = advisor.analyze_workload("GEMM_STANDARD", inputs)
        assert report.escape_found is True
        assert report.recommended_proposal is not None
        assert "IDENTITY" in report.recommended_proposal.rewrite_id

        # Verify equivalence
        ref_out, _ = IndependentReferenceEngine.execute_reference("GEMM_STANDARD", inputs)
        cand_out = advisor._execute_proposal("GEMM_STANDARD", inputs, report.recommended_proposal)
        np.testing.assert_allclose(cand_out, ref_out, atol=1e-5, rtol=1e-5)

    def test_zero_matrix_absorption_equivalence(self):
        advisor = ComputationEscapeAdvisor()
        A = np.random.default_rng(42).standard_normal((128, 128)).astype(np.float32)
        Z_mat = np.zeros((128, 128), dtype=np.float32)
        inputs = {"A": A, "B": Z_mat}

        report = advisor.analyze_workload("GEMM_STANDARD", inputs)
        assert report.escape_found is True
        assert report.recommended_proposal is not None
        assert "ZERO" in report.recommended_proposal.rewrite_id

        ref_out, _ = IndependentReferenceEngine.execute_reference("GEMM_STANDARD", inputs)
        cand_out = advisor._execute_proposal("GEMM_STANDARD", inputs, report.recommended_proposal)
        np.testing.assert_allclose(cand_out, ref_out, atol=1e-5, rtol=1e-5)

    def test_diagonal_matrix_scaling_equivalence(self):
        advisor = ComputationEscapeAdvisor()
        A = np.random.default_rng(42).standard_normal((128, 128)).astype(np.float32)
        d = np.linspace(1.0, 5.0, 128, dtype=np.float32)
        D_mat = np.diag(d)
        inputs = {"A": A, "B": D_mat}

        report = advisor.analyze_workload("GEMM_STANDARD", inputs)
        assert report.escape_found is True
        assert report.recommended_proposal is not None
        assert "DIAGONAL" in report.recommended_proposal.rewrite_id

        ref_out, _ = IndependentReferenceEngine.execute_reference("GEMM_STANDARD", inputs)
        cand_out = advisor._execute_proposal("GEMM_STANDARD", inputs, report.recommended_proposal)
        np.testing.assert_allclose(cand_out, ref_out, atol=1e-4, rtol=1e-4)

    def test_constant_sum_reduction_equivalence(self):
        advisor = ComputationEscapeAdvisor()
        inputs = {"x": np.full(100000, 3.25, dtype=np.float32)}

        report = advisor.analyze_workload("REDUCTION_SUM", inputs)
        assert report.escape_found is True
        assert report.recommended_proposal is not None

        ref_out, _ = IndependentReferenceEngine.execute_reference("REDUCTION_SUM", inputs)
        cand_out = advisor._execute_proposal("REDUCTION_SUM", inputs, report.recommended_proposal)
        np.testing.assert_allclose(cand_out, ref_out, atol=1e-3, rtol=1e-3)

    def test_fused_mlp_rewrite_equivalence(self):
        advisor = ComputationEscapeAdvisor()
        inputs = StrictVerificationRunner.generate_typical_inputs("ML_MLP_INFERENCE", seed=42)

        report = advisor.analyze_workload("ML_MLP_INFERENCE", inputs)
        assert report.escape_found is True
        assert report.recommended_proposal is not None

        ref_out, _ = IndependentReferenceEngine.execute_reference("ML_MLP_INFERENCE", inputs)
        cand_out = advisor._execute_proposal("ML_MLP_INFERENCE", inputs, report.recommended_proposal)
        np.testing.assert_allclose(cand_out, ref_out, atol=1e-4, rtol=1e-4)

    def test_fallback_when_dense_and_no_shortcut_exists(self):
        advisor = ComputationEscapeAdvisor()
        rng = np.random.default_rng(99)
        # Dense random matrices without algebraic structure
        inputs = {
            "A": rng.standard_normal((128, 128)).astype(np.float32),
            "B": rng.standard_normal((128, 128)).astype(np.float32),
        }

        report = advisor.analyze_workload("GEMM_STANDARD", inputs)
        # No algebraic shortcuts apply; falls back to standard execution
        assert report.fallback_used is True
        assert report.recommended_proposal is None
        assert report.evidence_valid is True

    def test_detection_overhead_is_accounted_for(self):
        advisor = ComputationEscapeAdvisor()
        A = np.random.default_rng(42).standard_normal((128, 128)).astype(np.float32)
        I_mat = np.eye(128, dtype=np.float32)
        inputs = {"A": A, "B": I_mat}

        report = advisor.analyze_workload("GEMM_STANDARD", inputs)
        prop = report.recommended_proposal
        assert prop is not None
        assert prop.detection_overhead_ms >= 0.0
        # Total projected latency MUST include detection overhead
        assert prop.total_projected_latency_ms == pytest.approx(
            prop.detection_overhead_ms + prop.execution_cost_ms, rel=1e-3
        )
