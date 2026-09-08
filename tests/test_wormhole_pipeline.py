"""
tests/test_wormhole_pipeline.py
=============================================================================
HYPER-X Wormhole Compiler End-to-End Pipeline & Multi-Domain Tests
=============================================================================
Validates:
  1. Low-rank GEMM shortcut discovery and Freivalds verification.
  2. Output-sensitive Top-K projection work elimination.
  3. Graphics temporal denoising with perceptual SSIM contract.
  4. 2D Scientific stencil multi-step simulation.
  5. Vector database cosine retrieval adapter.
  6. Autonomous Research Loop Pareto discovery & self-rectification.
  7. Strict No-Free-Lunch fallback on unstructured dense matrices.
"""

import pytest
import numpy as np

from hyper_x.wormhole_compiler import (
    WormholeCompiler,
    AutonomousResearchLoop,
    MatrixMultiplicationAdapter,
    GraphicsTemporalAdapter,
    OutputSensitiveTopKAdapter,
    ScientificStencilAdapter,
    RAGEmbeddingRetrievalAdapter,
    ContractCompiler,
    ObservableCompiler,
    CorrectnessRequirement,
    CachePolicy,
)


def test_gemm_structured_wormhole_discovery():
    """Validates that a low-rank structured matrix produces a verified wormhole."""
    rng = np.random.default_rng(42)
    M, K, N = 128, 128, 128
    rank = 12
    U = rng.standard_normal((M, rank)).astype(np.float32)
    V = rng.standard_normal((rank, K)).astype(np.float32)
    A = (U @ V) + (rng.standard_normal((M, K)).astype(np.float32) * 0.001)
    B = rng.standard_normal((K, N)).astype(np.float32)

    compiler = WormholeCompiler()
    result = compiler.compile_and_execute(A, B)

    assert result["status"] == "WORMHOLE_DISCOVERED_AND_VERIFIED"
    assert result["work_elimination_pct"] > 0.0
    assert result["numerical_error"] <= 1e-2
    assert "LOW_RANK" in result["selected_algorithm"]
    assert "hardware_fingerprint" in result


def test_gemm_unstructured_no_free_lunch():
    """Validates that high-entropy dense random matrix yields NO wormhole."""
    rng = np.random.default_rng(1234)
    M, K, N = 64, 64, 64
    A = rng.standard_normal((M, K)).astype(np.float32)
    B = rng.standard_normal((K, N)).astype(np.float32)

    compiler = WormholeCompiler()
    contract = ContractCompiler.compile_matrix_contract("DENSE_RANDOM", (M, K, N), tolerance=1e-4)
    result = compiler.compile_and_execute(A, B, contract=contract)

    assert result["status"] == "NO_VERIFIED_WORMHOLE_DISCOVERED"
    assert result["work_elimination_pct"] == 0.0
    assert "No verified computational wormhole discovered" in result["message"]


def test_output_sensitive_top_k_adapter():
    """Validates output-sensitive Top-K projection adapter."""
    rng = np.random.default_rng(99)
    M, K = 256, 128
    k = 8
    A = rng.standard_normal((M, K)).astype(np.float32)
    x = rng.standard_normal((K,)).astype(np.float32)

    (top_vals, top_indices), elapsed_ms = OutputSensitiveTopKAdapter.execute_reference(A, x, k=k)

    assert len(top_vals) == k
    assert len(top_indices) == k
    assert np.all(top_vals[:-1] >= top_vals[1:])  # Descending order


def test_graphics_temporal_adapter():
    """Validates graphics temporal denoising contract and reference execution."""
    rng = np.random.default_rng(77)
    curr_frame = rng.uniform(0.0, 1.0, size=(128, 128, 3)).astype(np.float32)

    contract = GraphicsTemporalAdapter.build_contract((128, 128))
    assert "graphics" in contract.operation
    assert contract.min_ssim == 0.92

    ref_out, elapsed_ms = GraphicsTemporalAdapter.execute_reference(curr_frame)
    assert ref_out.shape == (128, 128, 3)
    assert elapsed_ms >= 0.0


def test_scientific_stencil_adapter():
    """Validates 2D scientific stencil simulation adapter."""
    field = np.zeros((64, 64), dtype=np.float32)
    field[30:34, 30:34] = 10.0  # Heat impulse in center

    contract = ScientificStencilAdapter.build_contract((64, 64))
    assert "stencil" in contract.operation

    sim_field, elapsed_ms = ScientificStencilAdapter.execute_reference(field, steps=5)
    assert sim_field.shape == (64, 64)
    assert np.max(sim_field) < 10.0  # Heat has diffused outward


def test_rag_embedding_retrieval_adapter():
    """Validates vector database cosine similarity retrieval adapter."""
    rng = np.random.default_rng(55)
    doc_count = 1000
    dim = 64
    top_k = 5
    corpus = rng.standard_normal((doc_count, dim)).astype(np.float32)
    query = rng.standard_normal((dim,)).astype(np.float32)

    (scores, indices), elapsed_ms = RAGEmbeddingRetrievalAdapter.execute_reference(corpus, query, top_k=top_k)

    assert len(scores) == top_k
    assert len(indices) == top_k
    assert np.all(scores[:-1] >= scores[1:])


def test_autonomous_research_loop_gemm():
    """Validates that AutonomousResearchLoop explores hypotheses, proves them, and records failures."""
    loop = AutonomousResearchLoop(time_budget_sec=15.0, max_iterations=4)
    report = loop.run_gemm_research(M=64, K=64, N=64, structured=True, rank=8, tolerance=1e-3)

    assert report.domain == "matrix_multiplication"
    assert report.iterations_run > 0
    assert report.hardware_fingerprint["cpu_model"] != "UNKNOWN"

    # Should have evaluated hypotheses and registered failure or success
    it_exprs = [it.grammar_expression for it in report.iterations]
    assert any("LOW_RANK" in expr for expr in it_exprs)


def test_autonomous_research_loop_graphics():
    """Validates autonomous research loop for temporal graphics."""
    loop = AutonomousResearchLoop(time_budget_sec=10.0, max_iterations=3)
    report = loop.run_graphics_research(resolution=(64, 64), temporal_correlation=0.95)

    assert report.domain == "graphics_temporal"
    assert report.iterations_run == 3
    assert len(report.iterations) == 3
