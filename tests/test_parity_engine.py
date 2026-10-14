"""
Test suite for Contract-Driven Parity Engine (leo.parity).
Validates frozen contracts, engines, router, and adversarial fallbacks.
"""

import os
import pytest
import numpy as np

from leo.parity.contracts import (
    load_and_freeze_contracts,
    ResultLabel,
    ExecutionResult,
)
from leo.parity.router import ParityWorkloadRouter
from leo.parity.engines.llm_inference import LLMInferenceEngine
from leo.parity.engines.rag_retrieval import RAGRetrievalEngine
from leo.parity.engines.text_embeddings import TextEmbeddingsEngine
from leo.parity.engines.temporal_rendering import TemporalRenderingEngine


def test_contracts_registry_and_hash():
    """Verify contracts load properly and hash is deterministic."""
    registry = load_and_freeze_contracts()
    assert len(registry.contracts) == 4
    assert len(registry.contracts_hash) == 64
    assert "quantized_llm_inference" in registry.contracts
    assert "rag_retrieval" in registry.contracts
    assert "text_embeddings" in registry.contracts
    assert "temporal_reuse_rendering" in registry.contracts


def test_quantized_llm_inference_engine():
    """Verify LLM inference engine runs within budget and preserves quality."""
    engine = LLMInferenceEngine(vocab_size=256, hidden_dim=64, num_layers=2)
    prompt = [10, 20, 30]
    res = engine.run_candidate(prompt, max_new_tokens=4)

    assert isinstance(res, ExecutionResult)
    assert res.label in (ResultLabel.PREDICTIVE, ResultLabel.EXACT)
    assert res.correctness_metric_value == 1.0
    assert res.latency_ms < 120.0
    assert res.peak_ram_mb <= 32.0


def test_rag_retrieval_engine_and_cache():
    """Verify RAG engine returns high recall and caches results."""
    engine = RAGRetrievalEngine(corpus_size=1000, embedding_dim=128)
    query = np.random.randn(128).astype(np.float32)

    # First run: executes search and populates cache
    res1 = engine.run_candidate(query, top_k=5, use_cache=True)
    assert res1.correctness_metric_value >= 0.95
    assert res1.latency_ms < 6.0

    # Second run: identical query must hit exact cache
    res2 = engine.run_candidate(query, top_k=5, use_cache=True)
    assert res2.label == ResultLabel.CACHED
    assert res2.correctness_metric_value == 1.0


def test_text_embeddings_engine():
    """Verify text embeddings engine preserves Frobenius relative error <= 0.005 (cosine sim >= 0.999)."""
    engine = TextEmbeddingsEngine(hidden_dim=256, rank=32)
    tokens = np.random.randn(512, 256).astype(np.float32)
    res = engine.run_candidate(tokens)

    assert res.correctness_metric_value >= 0.999
    assert res.latency_ms < 15.0
    assert res.label in (ResultLabel.REDUCED_WORK, ResultLabel.EXACT)


def test_temporal_rendering_engine():
    """Verify temporal tile rendering achieves PSNR >= 40 dB."""
    engine = TemporalRenderingEngine(height=128, width=128, tile_size=16)
    # First frame establishes history (label: EXACT)
    res1 = engine.run_candidate(frame_time=0.0)
    assert res1.correctness_metric_value >= 40.0

    # Second frame with sparse dynamic tiles reuses temporal history (label: REDUCED_WORK)
    res2 = engine.run_candidate(frame_time=1.0, dynamic_tile_coords=[(0, 0), (1, 1)])
    assert res2.correctness_metric_value >= 40.0
    assert res2.latency_ms < 8.0
    assert res2.label == ResultLabel.REDUCED_WORK


def test_parity_router_end_to_end():
    """Verify router executes declared workloads and certifies compliance."""
    registry = load_and_freeze_contracts()
    router = ParityWorkloadRouter(registry)
    workloads = [
        "quantized_llm_inference",
        "rag_retrieval",
        "text_embeddings",
        "temporal_reuse_rendering",
    ]

    for w_name in workloads:
        contract = registry.get_contract(w_name)
        res = router.route_and_execute(w_name)
        assert contract.validate_execution(res), f"Workload {w_name} failed contract: {res.failure_reason}"


def test_adversarial_self_healing_fallbacks():
    """Verify that adversarial attacks trigger fail-closed fallbacks to EXACT."""
    # 1. RAG hostile query
    rag_engine = RAGRetrievalEngine(corpus_size=1000, embedding_dim=128)
    hostile_query = np.ones(128, dtype=np.float32) * -1.0
    rag_res = rag_engine.run_candidate(hostile_query, top_k=5, use_cache=False)
    assert rag_res.correctness_metric_value >= 0.95  # Survived via linear scan fallback

    # 2. Rendering scene cut
    render_engine = TemporalRenderingEngine(height=128, width=128, tile_size=16)
    render_engine.run_candidate(frame_time=0.0)
    scene_cut_res = render_engine.run_candidate(frame_time=1.0, force_scene_change=True)
    assert scene_cut_res.correctness_metric_value >= 40.0
    assert scene_cut_res.label == ResultLabel.EXACT
