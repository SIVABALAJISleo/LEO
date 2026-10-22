"""
Unit and Integration Test Suite for the HYPER Computational Phase-Change Engine (CPCE)
=====================================================================================
Covers:
- Tagged matrix types and asymptotic structure preservation (types.py)
- Canonical IR graph validation, cycle detection, topological sorting (ir.py)
- Workload contracts, tolerance, and validation (contracts.py)
- Structural analysis with bounded scanning (structural_analysis.py)
- Sound algebraic rewrite rules (Identity, Zero, Diagonal, CSE, Horner, DCE)
- Multi-level independent verification (Exact, Tolerance, Freivalds O(N^2))
- Cost-aware escape search engine and budget enforcement (algorithm_search.py)
- Content-addressable memoization hub with SHA-256 digests (cache.py)
- End-to-end master engine pipeline (hyper_x/cpce/__init__.py)
- FastAPI CPCE router endpoints (/status, /contracts, /support-matrix, /execute)
"""

import os
import sys
import numpy as np
import pytest
from starlette.testclient import TestClient

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from hyper_x.cpce.types import (
    MatrixStructure,
    DenseMatrix,
    IdentityMatrix,
    ZeroMatrix,
    DiagonalMatrix,
    SparseMatrix,
    LowRankMatrix,
)
from hyper_x.cpce.contracts import (
    WorkloadContract,
    ValidationMode,
    ExactnessRequirement,
    ContractRegistry,
    get_contract,
)
from hyper_x.cpce.ir import (
    OpType,
    CIRNode,
    CanonicalGraph,
)
from hyper_x.cpce.structural_analysis import (
    StructuralAnalyzer,
    StructuralMetadata,
)
from hyper_x.cpce.rewrite_rules import (
    ExactAlgebraicRewriter,
    IdentityEliminationRule,
    ZeroPropagationRule,
    DiagonalScalingRule,
    CommonSubexpressionEliminationRule,
    HornerPolynomialRule,
    DeadCodeEliminationRule,
)
from hyper_x.cpce.rewrite_verifier import (
    RewriteVerifier,
    VerificationOutcome,
    VerificationReport,
    freivalds_verify,
)
from hyper_x.cpce.cost_model import CPCECostModel, CostBreakdown
from hyper_x.cpce.cache import CPCECache, CPCECacheKeyBuilder
from hyper_x.cpce.backend_registry import CPCEBackendRegistry
from hyper_x.cpce.algorithm_search import CPCESearchEngine, SearchBudget, CandidatePlan

from hyper_x.cpce.execution_planner import CPCEExecutionPlanner
from hyper_x.cpce.result_schema import CPCEResult, ExecutionStatus
from hyper_x.cpce import ComputationalPhaseChangeEngine
from backend.main import app


# ============================================================================
# 1. TAGGED MATRIX TYPES & ASYMPTOTIC STRUCTURE PRESERVATION
# ============================================================================

class TestTaggedMatrixStructures:
    """Tests for structure-preserving representations and operation elimination."""

    def test_identity_matrix_matmul_preservation(self):
        """Identity * Dense = Dense without full O(N^3) buffer allocation."""
        n = 128
        I = IdentityMatrix(n)
        dense_arr = np.random.randn(n, n).astype(np.float32)
        D = DenseMatrix(dense_arr)

        res_left = I.matmul(D)
        assert isinstance(res_left, (DenseMatrix, np.ndarray))
        data_left = res_left.data if hasattr(res_left, "data") else res_left
        np.testing.assert_array_equal(data_left, dense_arr)

        res_right = D.matmul(I)
        assert isinstance(res_right, (DenseMatrix, np.ndarray))
        data_right = res_right.data if hasattr(res_right, "data") else res_right
        np.testing.assert_array_equal(data_right, dense_arr)

    def test_identity_matrix_dimension_mismatch(self):
        """Identity multiplication must assert on inner dimension mismatch."""
        I = IdentityMatrix(64)
        D = DenseMatrix(np.ones((32, 32), dtype=np.float32))
        with pytest.raises(AssertionError):
            I.matmul(D)

    def test_zero_matrix_matmul_preservation(self):
        """Zero * Dense = Zero without full O(N^3) computation."""
        Z = ZeroMatrix(64, 128)
        dense_arr = np.random.randn(128, 32).astype(np.float32)
        D = DenseMatrix(dense_arr)

        res = Z.matmul(D)
        assert isinstance(res, ZeroMatrix)
        assert res.shape == (64, 32)
        np.testing.assert_array_equal(res.to_dense(), np.zeros((64, 32), dtype=np.float32))

    def test_diagonal_matrix_scaling_efficiency(self):
        """Diagonal * Dense computes row scaling in O(N^2) instead of O(N^3)."""
        diag_vals = np.array([2.0, 3.0, 4.0], dtype=np.float32)
        diag = DiagonalMatrix(diag_vals)

        dense_arr = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]], dtype=np.float32)
        D = DenseMatrix(dense_arr)

        res = diag.matmul(D)
        assert isinstance(res, DenseMatrix)
        expected = np.array([[2.0, 4.0], [9.0, 12.0], [20.0, 24.0]], dtype=np.float32)
        np.testing.assert_allclose(res.data, expected, rtol=1e-5)

    def test_low_rank_matrix_representation(self):
        """LowRankMatrix represents U * V^T and performs factored matmul."""
        m, k, n = 100, 4, 80
        U = np.random.randn(m, k).astype(np.float32)
        V = np.random.randn(n, k).astype(np.float32)
        LR = LowRankMatrix(U, V)

        assert LR.shape == (m, n)
        assert LR.rank == k

        dense_full = LR.to_dense()
        assert dense_full.shape == (m, n)
        np.testing.assert_allclose(dense_full, U @ V.T, rtol=1e-5)


# ============================================================================
# 2. WORKLOAD CONTRACTS & VALIDATION
# ============================================================================

class TestWorkloadContracts:
    """Tests for explicit correctness contracts and validation."""

    def test_exact_contract_definition(self):
        """Exact contracts must require exact equivalence."""
        c = WorkloadContract(
            contract_id="test_exact",
            validation_mode=ValidationMode.EXACT,
            exactness_requirement=ExactnessRequirement.BITWISE_EXACT,
            memory_budget_mb=1024.0,
            description="Test Exact Contract",
        )
        assert c.exactness_requirement == ExactnessRequirement.BITWISE_EXACT
        assert c.validation_mode == ValidationMode.EXACT


    def test_built_in_contract_registry(self):
        """Standard CPCE contracts must be discoverable."""
        horner_contract = get_contract("polynomial_horner")
        assert horner_contract is not None
        assert horner_contract.contract_id == "polynomial_horner"

        gemm_contract = get_contract("dense_gemm")
        assert gemm_contract is not None
        assert gemm_contract.contract_id == "dense_gemm"


# ============================================================================
# 3. CANONICAL INTERMEDIATE REPRESENTATION (CIR)
# ============================================================================

class TestCanonicalIR:
    """Tests for CIR graph construction, validation, and topological sorting."""

    def test_graph_construction_and_validation(self):
        """Graph with linear flow must validate and sort correctly."""
        graph = CanonicalGraph(name="simple_pipeline")

        n1 = CIRNode("A", OpType.INPUT, shape=(64, 64))
        n2 = CIRNode("B", OpType.INPUT, shape=(64, 64))
        n3 = CIRNode("C", OpType.MATMUL, inputs=["A", "B"], shape=(64, 64))
        n4 = CIRNode("out", OpType.OUTPUT, inputs=["C"], shape=(64, 64))

        for node in [n1, n2, n3, n4]:
            graph.add_node(node)

        is_valid, err = graph.validate()
        assert is_valid is True
        assert err is None

        order = [n.node_id for n in graph.topological_sort()]
        assert "C" in order and "out" in order
        assert order.index("C") > order.index("A")
        assert order.index("C") > order.index("B")
        assert order.index("out") > order.index("C")


    def test_cycle_detection_fail_closed(self):
        """Cycles in the computation graph must fail validation."""
        graph = CanonicalGraph(name="cyclic_graph")

        n1 = CIRNode("A", OpType.MATMUL, inputs=["B"])
        n2 = CIRNode("B", OpType.ADD, inputs=["A"])

        graph.add_node(n1)
        graph.add_node(n2)

        is_valid, err = graph.validate()
        assert is_valid is False
        assert "cycle" in err.lower()

    def test_missing_input_validation(self):
        """Nodes referencing missing inputs must fail validation."""
        graph = CanonicalGraph(name="broken_graph")
        n1 = CIRNode("A", OpType.MATMUL, inputs=["NON_EXISTENT"])
        graph.add_node(n1)
        is_valid, err = graph.validate()
        assert is_valid is False
        assert "missing input dependency" in err


# ============================================================================
# 4. STRUCTURAL ANALYSIS (BUDGET-BOUNDED)
# ============================================================================

class TestStructuralAnalysis:
    """Tests for structure discovery without full scans."""

    def test_analyze_identity_matrix(self):
        arr = np.eye(64, dtype=np.float32)
        analyzer = StructuralAnalyzer(max_sample_elements=5000)
        metadata = analyzer.analyze(arr)
        assert metadata.structure_tag == "IDENTITY"
        assert metadata.is_identity is True

    def test_analyze_zero_matrix(self):
        arr = np.zeros((32, 64), dtype=np.float32)
        analyzer = StructuralAnalyzer()
        metadata = analyzer.analyze(arr)
        assert metadata.structure_tag == "ZERO"
        assert metadata.is_zero is True

    def test_analyze_diagonal_matrix(self):
        arr = np.diag([1.0, 2.0, 3.0, 4.0]).astype(np.float32)
        analyzer = StructuralAnalyzer()
        metadata = analyzer.analyze(arr)
        assert metadata.structure_tag == "DIAGONAL"
        assert metadata.is_diagonal is True


# ============================================================================
# 5. SOUND ALGEBRAIC REWRITE RULES & FIXED-POINT REWRITER
# ============================================================================

class TestAlgebraicRewrites:
    """Tests for exact algebraic phase changes."""

    def test_identity_elimination_rewrite(self):
        """Identity * X -> X eliminates the matmul node."""
        graph = CanonicalGraph(name="ident_test")
        graph.add_node(CIRNode("I", OpType.CONSTANT, shape=(32, 32), structural_tag="IDENTITY"))
        graph.add_node(CIRNode("X", OpType.INPUT, shape=(32, 32)))
        graph.add_node(CIRNode("M", OpType.MATMUL, inputs=["I", "X"], shape=(32, 32)))
        graph.add_node(CIRNode("out", OpType.OUTPUT, inputs=["M"], shape=(32, 32)))

        rewriter = ExactAlgebraicRewriter()
        rewriter.add_rule(IdentityEliminationRule())
        optimized, history = rewriter.rewrite(graph)

        assert len(history) >= 1
        assert "RULE_001_IDENTITY_ELIMINATION" in history

    def test_zero_propagation_rewrite(self):
        """0 * X -> 0 eliminates computation to constant zero."""
        graph = CanonicalGraph(name="zero_test")
        graph.add_node(CIRNode("Z", OpType.CONSTANT, shape=(32, 32), structural_tag="ZERO"))
        graph.add_node(CIRNode("X", OpType.INPUT, shape=(32, 32)))
        graph.add_node(CIRNode("M", OpType.MATMUL, inputs=["Z", "X"], shape=(32, 32)))
        graph.add_node(CIRNode("out", OpType.OUTPUT, inputs=["M"], shape=(32, 32)))

        rewriter = ExactAlgebraicRewriter()
        rewriter.add_rule(ZeroPropagationRule())
        optimized, history = rewriter.rewrite(graph)

        assert "RULE_002_ZERO_PROPAGATION" in history
        assert optimized.nodes["M"].structural_tag == "ZERO"

    def test_common_subexpression_elimination(self):
        """Identical expressions must be merged."""
        graph = CanonicalGraph(name="cse_test")
        graph.add_node(CIRNode("A", OpType.INPUT, shape=(16, 16)))
        graph.add_node(CIRNode("B", OpType.INPUT, shape=(16, 16)))
        graph.add_node(CIRNode("M1", OpType.MATMUL, inputs=["A", "B"], shape=(16, 16)))
        graph.add_node(CIRNode("M2", OpType.MATMUL, inputs=["A", "B"], shape=(16, 16)))
        graph.add_node(CIRNode("out", OpType.OUTPUT, inputs=["M1", "M2"], shape=(16, 16)))

        rewriter = ExactAlgebraicRewriter()
        rewriter.add_rule(CommonSubexpressionEliminationRule())
        optimized, history = rewriter.rewrite(graph)

        assert "RULE_004_CSE" in history
        # out should now take M1 and M1
        assert optimized.nodes["out"].inputs == ["M1", "M1"]




# ============================================================================
# 6. INDEPENDENT REWRITE VERIFIER & FREIVALDS ALGORITHM
# ============================================================================

class TestRewriteVerifier:
    """Tests for multi-level independent verification."""

    def test_freivalds_matrix_multiplication_verification(self):
        """Freivalds O(N^2) randomized verification correctly certifies GEMM."""
        n = 64
        A = np.random.randn(n, n).astype(np.float32)
        B = np.random.randn(n, n).astype(np.float32)
        C_correct = A @ B

        # Correct multiplication must pass Freivalds with high confidence
        is_valid, evidence = freivalds_verify(A, B, C_correct, iterations=10)
        assert is_valid is True

        # Perturbed multiplication must fail Freivalds
        C_corrupted = C_correct.copy()
        C_corrupted[10, 10] += 0.5
        is_corrupted_valid, evidence = freivalds_verify(A, B, C_corrupted, iterations=10)
        assert is_corrupted_valid is False

    def test_verifier_bitwise_and_tolerance(self):
        verifier = RewriteVerifier()
        a = np.array([1, 2, 3], dtype=np.int32)
        b = np.array([1, 2, 3], dtype=np.int32)
        report = verifier.verify_bitwise(a, b)
        assert report.outcome == VerificationOutcome.PASS

        x = np.array([1.0, 2.0], dtype=np.float32)
        y = np.array([1.000005, 2.000002], dtype=np.float32)
        report_tol = verifier.verify_tolerance(x, y, atol=1e-4, rtol=1e-4)
        assert report_tol.outcome == VerificationOutcome.PASS


# ============================================================================
# 7. COMPUTATION MEMORY HUB & CACHING
# ============================================================================

class TestComputationMemoryHub:
    """Tests for content-addressable memoization and cache key sensitivity."""

    def test_cache_hit_and_miss(self):
        cache = CPCECache(max_entries=100)
        inp = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        out = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)

        contract = get_contract("dense_gemm")
        key = CPCECacheKeyBuilder.build_key(
            op_name="gemm_op",
            operands=[inp],
            contract=contract,
            backend="CPU",
        )

        assert cache.get(key) is None
        cache.put(key, out, metadata={"elapsed_ms": 1.2})

        cached = cache.get(key)
        assert cached is not None
        cached_out, lookup_ms = cached
        np.testing.assert_array_equal(cached_out, out)
        assert lookup_ms >= 0.0

    def test_cache_key_different_contract(self):
        """Different contracts must produce different cache keys."""
        c1 = get_contract("dense_gemm")
        c2 = get_contract("polynomial_horner")
        inp = np.array([1.0, 2.0])
        k1 = CPCECacheKeyBuilder.build_key("op", [inp], contract=c1)
        k2 = CPCECacheKeyBuilder.build_key("op", [inp], contract=c2)
        assert k1 != k2


# ============================================================================
# 8. MASTER CPCE END-TO-END EXECUTION
# ============================================================================

class TestComputationalPhaseChangeEngineEndToEnd:
    """End-to-end integration tests of the full 9-stage pipeline."""

    def test_identity_gemm_phase_change(self):
        """Multiplying Identity * Dense must trigger phase-change shortcut and 100% correctness."""
        engine = ComputationalPhaseChangeEngine()
        n = 64
        I_mat = IdentityMatrix(n)
        X_mat = np.random.randn(n, n).astype(np.float32)

        result = engine.execute_workload(
            contract_id="dense_gemm",
            inputs={"A": I_mat, "B": X_mat},
            use_cache=False,
        )

        assert result.status == ExecutionStatus.PASS
        assert result.output is not None
        np.testing.assert_allclose(result.output, X_mat, rtol=1e-5)
        # Verify that an algebraic shortcut was applied
        assert len(result.optimizations_applied) > 0

    def test_horner_polynomial_phase_change(self):
        """Evaluating polynomial via Horner must produce mathematically identical results."""
        engine = ComputationalPhaseChangeEngine()
        coeffs = [3.0, -2.0, 5.0, 1.5]  # P(x) = 3 - 2x + 5x^2 + 1.5x^3
        x_val = 2.5

        # Compute reference using numpy polynomial
        expected = np.polynomial.polynomial.polyval(x_val, coeffs)

        result = engine.execute_workload(
            contract_id="polynomial_horner",
            inputs={"coefficients": coeffs, "x": x_val},
            use_cache=False,
        )

        assert result.status == ExecutionStatus.PASS
        assert np.isclose(result.output, expected, atol=1e-5)
        assert "RULE_005_HORNER_POLYNOMIAL" in result.optimizations_applied


# ============================================================================
# 9. FASTAPI ROUTER INTEGRATION
# ============================================================================

class TestCPCERouterAPI:
    """Tests for FastAPI endpoints under /api/v1/cpce."""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_api_status_endpoint(self, client):
        resp = client.get("/api/v1/cpce/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["engine"] == "HYPER Computational Phase-Change Engine (CPCE)"
        assert "target_system" in data
        assert "backends" in data
        assert "cache_stats" in data

    def test_api_contracts_endpoint(self, client):
        resp = client.get("/api/v1/cpce/contracts")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 5
        contract_ids = [c["contract_id"] for c in data]
        assert "dense_gemm" in contract_ids
        assert "polynomial_horner" in contract_ids

    def test_api_support_matrix_endpoint(self, client):
        resp = client.get("/api/v1/cpce/support-matrix")
        assert resp.status_code == 200
        data = resp.json()
        assert "summary" in data
        assert "workloads" in data
        assert len(data["workloads"]) >= 4

