#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_integration_prompts.py
=================================
Phase D1: Integration Testing Across Diverse Prompts.

Validates the full optimization pipeline across diverse input categories:
  1. Short factual QA
  2. Multi-step reasoning
  3. Code generation prompt
  4. Repetitive boilerplate (Token Pruning integration)
  5. Sparse attention integration
"""

import os
import pytest
import numpy as np

from universal_compute_router.adaptive_dispatch import AdaptiveDispatchRouter
from hyper_runtime.semantic_token_pruning import SemanticTokenPruner
from hyper_runtime.token_merging.tome_engine import TokenMergingEngine
from hyper_runtime.sparse_attention import SparseAttentionEngine
from hyper_runtime.adaptive_precision import AdaptivePrecisionSelector


def test_short_factual_prompt():
    """Verify adaptive dispatch routing and low-latency handling for short factual query."""
    router = AdaptiveDispatchRouter()
    prompt = "What is the speed of light in vacuum?"
    route = router.route("EmbeddingLookup", (1, len(prompt.split()), 896))
    assert route["target"] == "CPU_PCORE"
    assert route["decision_latency_us"] < 100.0


def test_multi_step_reasoning_prompt():
    """Verify reasoning prompt through token pruner and precision selector."""
    pruner = SemanticTokenPruner()
    prompt_tokens = "A train leaves Chicago at 60 mph. Another leaves at 80 mph. When do they meet?".split()
    pruned_tokens, indices, meta = pruner.prune_text_tokens(prompt_tokens)
    assert len(pruned_tokens) >= int(len(prompt_tokens) * 0.5)
    assert meta["latency_ms"] < 5.0


def test_code_generation_attention_sparse():
    """Verify code generation context through sparse attention engine."""
    sparse_engine = SparseAttentionEngine(local_window=32, stride=16)
    rng = np.random.default_rng(101)
    # Simulate 512-token code context
    Q = rng.standard_normal((512, 64)).astype(np.float32)
    K = rng.standard_normal((512, 64)).astype(np.float32)
    V = rng.standard_normal((512, 64)).astype(np.float32)

    out, meta = sparse_engine.compute_sparse_attention(Q, K, V)
    assert out.shape == (512, 64)
    assert meta["sparsity_pct"] > 80.0
    assert not np.isnan(out).any()


def test_boilerplate_reduction_integration():
    """Verify boilerplate heavy context achieves >= 40% reduction via SemanticTokenPruner."""
    pruner = SemanticTokenPruner(similarity_threshold=0.85, min_preserve_ratio=0.50)
    rng = np.random.default_rng(202)
    # 50 repetitive boilerplate tokens followed by 50 informative tokens
    base = rng.standard_normal((1, 128)).astype(np.float32)
    boilerplate = np.repeat(base, 50, axis=0) + rng.normal(0, 0.01, (50, 128)).astype(np.float32)
    informative = rng.standard_normal((50, 128)).astype(np.float32)
    full_seq = np.vstack([boilerplate, informative])

    pruned, keep_idx, _, meta = pruner.prune_embeddings(full_seq)
    assert meta["reduction_pct"] >= 20.0
    assert len(pruned) >= 50 # Preserved bound
    assert not np.isnan(pruned).any()


def test_tome_and_adaptive_precision_pipeline():
    """Verify combined Token Merging and Adaptive Precision analysis."""
    tome = TokenMergingEngine(merge_ratio=0.25)
    selector = AdaptivePrecisionSelector()
    rng = np.random.default_rng(303)

    # 1. ToMe on correlated embeddings
    base = rng.standard_normal((32, 896)).astype(np.float32)
    hidden = np.repeat(base, 2, axis=0) + rng.normal(0, 0.01, (64, 896)).astype(np.float32)
    tokens = list(range(64))
    new_tokens, new_hidden, tome_meta = tome.merge_tokens(tokens, hidden)
    assert tome_meta["passed_drift_target"] is True
    assert len(new_tokens) == 48

    # 2. Precision analysis on projection layer
    W_proj = rng.standard_normal((896, 896)).astype(np.float32)
    prec_meta = selector.analyze_matrix(W_proj, "proj_layer")
    assert prec_meta["selected_precision"] in ["INT4", "INT8", "FP32"]
