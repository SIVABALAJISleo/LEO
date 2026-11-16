"""
tests/test_leaf_engine_master_suite.py
======================================
Comprehensive verification suite for HYPER-Ω Leaf Engine:
1. Woodbury Analytic Training Subsumption (Primal, Dual Woodbury, Rank-k update).
2. Genuine Online Recursive Least Squares (RLS).
3. Adversarial, rank-deficient, ill-conditioned, and multi-output edge cases.
4. Analytic vs Iterative gradient descent convergence and loss optimality.
5. Decoupled Knowledge Architecture (mmap, inverted index, cache, exact fallback, provenance).
6. Mathematical Computation Elimination Engine (all 6 contract transformations).
7. Real Intel UHD iGPU OpenCL kernel execution and CPU IEEE-754 verification.
8. Search Space Compiler & Counterfactual Engine plan falsification.
9. Memory Intelligence (bounded streaming, constant-RAM Gram, tiled GEMM).
10. FunctionalReplacementEngine master integration dispatch.
"""

import os
import shutil
import numpy as np
import pytest

from backend.canonical.woodbury_analytic_training_subsumption import (
    WoodburyAnalyticTrainer,
    OnlineRecursiveLeastSquares,
    compare_analytic_vs_iterative
)
from backend.canonical.decoupled_knowledge_engine import (
    DecoupledKnowledgeEngine,
    MemoryMappedKnowledgeStore,
    CompactFrozenReasoner
)
from backend.canonical.mathematical_elimination_engine import (
    MathematicalEliminationEngine,
    AlgebraicDistributiveTransformation,
    CommonSubexpressionEliminationTransformation,
    LowRankDecompositionTransformation,
    ShermanMorrisonIncrementalTransformation,
    SparseThresholdingTransformation,
    KroneckerAssociativeTransformation
)
from backend.canonical.intel_gpu_opencl_engine import (
    IntelGpuOpenClEngine
)
from backend.canonical.counterfactual_compiler_engine import (
    SearchSpaceCompiler,
    CounterfactualEvaluationEngine,
    ExecutionPathway
)
from backend.canonical.memory_intelligence_engine import (
    MemoryIntelligenceEngine,
    IntermediateResultMemoizer,
    CacheAwareTiledGemm
)
from backend.canonical.functional_replacement_engine import FunctionalReplacementEngine


# ==============================================================================
# 1. WOODBURY ANALYTIC SOLVER & OPTIMALITY
# ==============================================================================

def test_woodbury_batch_ridge_cholesky_optimality():
    """Verifies that Cholesky solve achieves zero gradient norm (global analytic minimizer)."""
    np.random.seed(42)
    N, r, c = 150, 24, 3
    Z = np.random.randn(N, r)
    W_star = np.random.randn(r, c)
    Y = Z @ W_star + 0.01 * np.random.randn(N, c)

    trainer = WoodburyAnalyticTrainer(lambda_reg=1e-2)
    res_primal = trainer.solve_batch_ridge(Z, Y, force_mode="PRIMAL_CHOLESKY")

    assert res_primal.status == "OPTIMAL"
    assert res_primal.gradient_norm < 1e-4
    assert res_primal.W.shape == (r, c)

    # Verify Dual Woodbury formulation yields identical result within machine precision
    res_dual = trainer.solve_batch_ridge(Z, Y, force_mode="DUAL_WOODBURY")
    rel_diff = np.linalg.norm(res_primal.W - res_dual.W) / np.linalg.norm(res_primal.W)
    assert rel_diff < 1e-10


def test_woodbury_rank_k_update_exactness():
    """Verifies that Woodbury rank-k update matches full retraining from scratch."""
    np.random.seed(101)
    N0, k, r, c = 100, 10, 20, 2
    Z0 = np.random.randn(N0, r)
    Y0 = np.random.randn(N0, c)

    lambda_reg = 0.05
    trainer = WoodburyAnalyticTrainer(lambda_reg=lambda_reg)
    res0 = trainer.solve_batch_ridge(Z0, Y0)

    # Initial inverse covariance P0 = (Z0^T Z0 + lambda I)^{-1}
    Gram0 = Z0.T @ Z0 + lambda_reg * np.eye(r)
    P0 = np.linalg.inv(Gram0)

    # New batch Delta_Z, Delta_Y
    Delta_Z = np.random.randn(k, r)
    Delta_Y = np.random.randn(k, c)

    # Woodbury rank-k update
    W_woodbury, P_woodbury = trainer.solve_woodbury_rank_k_update(P0, res0.W, Delta_Z, Delta_Y)

    # Full batch retraining on combined data
    Z_comb = np.vstack([Z0, Delta_Z])
    Y_comb = np.vstack([Y0, Delta_Y])
    res_comb = trainer.solve_batch_ridge(Z_comb, Y_comb)

    rel_diff = np.linalg.norm(W_woodbury - res_comb.W) / np.linalg.norm(res_comb.W)
    assert rel_diff < 1e-9


# ==============================================================================
# 2. GENUINE ONLINE RECURSIVE LEAST SQUARES (RLS)
# ==============================================================================

def test_genuine_online_rls_convergence():
    """Verifies that streaming RLS with beta=1.0 converges to exact batch ridge regression."""
    np.random.seed(77)
    N, r, c = 120, 16, 2
    Z = np.random.randn(N, r)
    Y = np.random.randn(N, c)
    lambda_reg = 0.01

    trainer = WoodburyAnalyticTrainer(lambda_reg=lambda_reg)
    res_batch = trainer.solve_batch_ridge(Z, Y)

    rls = OnlineRecursiveLeastSquares(feature_dim=r, target_dim=c, lambda_reg=lambda_reg, forgetting_factor=1.0)
    rls.update_stream(Z, Y)

    rel_diff = np.linalg.norm(res_batch.W - rls.W) / np.linalg.norm(res_batch.W)
    assert rel_diff < 1e-10
    assert rls.steps_processed == N


def test_woodbury_edge_cases():
    """Tests rank-deficient inputs, ill-conditioned matrices, and invalid dimensions."""
    trainer = WoodburyAnalyticTrainer(lambda_reg=1e-3)

    # 1. Collinear / rank-deficient features
    Z_rank1 = np.ones((50, 10))
    Y = np.random.randn(50, 1)
    res = trainer.solve_batch_ridge(Z_rank1, Y)
    assert res.W.shape == (10, 1)
    assert np.all(np.isfinite(res.W))

    # 2. Zero-sample exception
    with pytest.raises(ValueError):
        trainer.solve_batch_ridge(np.empty((0, 10)), np.empty((0, 1)))

    # 3. Dimension mismatch
    with pytest.raises(ValueError):
        trainer.solve_batch_ridge(np.random.randn(10, 5), np.random.randn(12, 1))


def test_analytic_vs_iterative_benchmark():
    """Compares exact closed-form Woodbury solve against iterative gradient descent."""
    np.random.seed(33)
    N, r, c = 100, 16, 1
    Z = np.random.randn(N, r)
    Y = Z @ np.random.randn(r, c) + 0.05 * np.random.randn(N, c)

    comp = compare_analytic_vs_iterative(Z, Y, lambda_reg=1e-2, max_iter_epochs=150)
    assert comp["analytic_loss"] <= comp["iterative_loss"] + 1e-6
    assert comp["analytic_speedup_vs_iterative"] > 1.0


# ==============================================================================
# 3. DECOUPLED KNOWLEDGE ARCHITECTURE
# ==============================================================================

def test_decoupled_knowledge_mmap_and_retrieval(tmp_path):
    """Tests out-of-core mmap document ingestion, inverted index, cache, and fallback."""
    store_dir = str(tmp_path / "knowledge_test")
    engine = DecoupledKnowledgeEngine(storage_dir=store_dir)

    docs = [
        ("doc_alpha", "Golden Cove Performance cores execute AVX-VNNI 32 INT8 multiply-accumulates per cycle."),
        ("doc_beta", "Sherman-Morrison formula updates the matrix inverse in O(N^2) time for rank-1 updates."),
        ("doc_gamma", "Intel UHD Graphics provides 48 Execution Units running OpenCL 3.0 NEO drivers.")
    ]

    for doc_id, text in docs:
        engine.ingest_document(doc_id, text)

    # Query 1: Inverted index retrieval
    results, metrics = engine.retrieve("AVX-VNNI multiply-accumulates", top_k=1)
    assert len(results) >= 1
    assert "doc_alpha" in results[0].doc_id
    assert results[0].retrieval_mode == "INVERTED_INDEX"

    # Query 2: LRU Cache Hit
    results_cached, metrics_cached = engine.retrieve("AVX-VNNI multiply-accumulates", top_k=1)
    assert metrics_cached.cache_hit is True

    # Query 3: Exact substring fallback
    results_fallback, metrics_fallback = engine.retrieve("48 Execution Units", top_k=1)
    assert len(results_fallback) >= 1
    assert "doc_gamma" in results_fallback[0].doc_id

    # Query 4: Compact Frozen Reasoner
    reasoner = CompactFrozenReasoner()
    response = reasoner.reason("How many execution units?", results_fallback)
    assert "48 Execution Units" in response["answer"]
    assert response["model_parameters_updated"] is False

    engine.store.close()


# ==============================================================================
# 4. MATHEMATICAL COMPUTATION ELIMINATION ENGINE
# ==============================================================================

def test_mathematical_elimination_all_transformations():
    """Verifies that all 6 declared mathematical transformations satisfy their contracts."""
    engine = MathematicalEliminationEngine()
    results = engine.run_all_contract_verifications()

    assert len(results) == 6
    for decl in results:
        assert decl.passed_contract, f"Transformation {decl.name} failed contract: {decl.metadata.get('rejection_reason')}"
        assert decl.measured_error <= decl.theoretical_error_bound


# ==============================================================================
# 5. INTEL UHD iGPU OPENCL LIVE EXECUTION
# ==============================================================================

def test_intel_gpu_opencl_live_execution():
    """Verifies runtime discovery and execution of OpenCL kernels on Intel UHD iGPU."""
    engine = IntelGpuOpenClEngine()
    assert engine.device_info is not None

    # Test SAXPY vector execution
    x = np.linspace(1, 10, 2048, dtype=np.float32)
    y = np.linspace(10, 20, 2048, dtype=np.float32)
    res_saxpy = engine.execute_vector_saxpy(3.0, x, y)
    assert res_saxpy.verified is True
    assert res_saxpy.max_numerical_error < 1e-4

    # Test GEMV matrix-vector execution
    A = np.random.randn(128, 256).astype(np.float32)
    vec = np.random.randn(256).astype(np.float32)
    res_gemv = engine.execute_matrix_vector_gemv(A, vec)
    assert res_gemv.verified is True
    assert res_gemv.max_numerical_error < 1e-4

    engine.close()


# ==============================================================================
# 6. SEARCH SPACE COMPILER & COUNTERFACTUAL ENGINE
# ==============================================================================

def test_counterfactual_compiler_plan_falsification():
    """Verifies that the Counterfactual Engine evaluates alternative plans and rejects violations."""
    engine = CounterfactualEvaluationEngine()
    A = np.random.randn(64, 64).astype(np.float32)
    B = np.random.randn(64, 8).astype(np.float32)

    # With tight tolerance 1e-5, lossy approximations should be rejected
    rep = engine.audit_and_select_plan(A, B, error_tolerance=1e-5)
    assert rep.candidates_evaluated == 10
    assert rep.candidates_rejected >= 2
    assert rep.selected_plan is not None
    assert rep.selected_plan.passes_contract is True
    assert rep.selected_plan.measured_error <= 1e-5

    engine.close()


# ==============================================================================
# 7. MEMORY INTELLIGENCE & BOUNDED STREAMING
# ==============================================================================

def test_memory_intelligence_bounded_streaming_and_tiling():
    """Verifies constant-RAM bounded streaming and cache-aware tiled GEMM."""
    engine = MemoryIntelligenceEngine()

    # Bounded streaming Gram profile
    prof = engine.profile_bounded_streaming_gram(total_samples=20_000, feature_dim=16, chunk_size=1000)
    assert prof.status == "VERIFIED_CONSTANT_RAM"
    assert prof.actual_bytes_read_or_streamed == 20_000 * 16 * 4

    # Cache-aware tiled GEMM
    res_tile = engine.benchmark_tiled_vs_dense_gemm(M=128, K=128, N=128)
    assert res_tile["verified"] is True
    assert res_tile["max_difference"] < 1e-4


# ==============================================================================
# 8. FUNCTIONAL REPLACEMENT ENGINE MASTER DISPATCH
# ==============================================================================

def test_functional_replacement_engine_leaf_dispatch():
    """Verifies that FunctionalReplacementEngine exposes all Leaf Engine capabilities."""
    engine = FunctionalReplacementEngine()

    # 1. Woodbury solve dispatch
    Z = np.random.randn(50, 10)
    Y = np.random.randn(50, 2)
    res_w = engine.solve_woodbury_analytic_training(Z, Y, lambda_reg=1e-2)
    assert res_w.status == "OPTIMAL"

    # 2. Mathematical elimination audit dispatch
    decls = engine.run_mathematical_elimination_audits()
    assert len(decls) == 6

    # 3. Intel UHD OpenCL kernel dispatch
    x = np.ones(512, dtype=np.float32)
    y = np.ones(512, dtype=np.float32)
    res_cl = engine.execute_intel_gpu_opencl_kernel(2.0, x, y)
    assert res_cl.verified is True

    # 4. Memory streaming profile dispatch
    prof = engine.profile_bounded_memory_stream(total_samples=5000, feature_dim=16, chunk_size=500)
    assert prof.status == "VERIFIED_CONSTANT_RAM"

