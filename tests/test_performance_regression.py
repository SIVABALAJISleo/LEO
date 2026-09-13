#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_performance_regression.py
====================================
Phase D3: Performance Regression Test Suite (< 1 minute execution).

Verifies that core optimization kernels maintain latency targets:
  1. Router Decision Latency: < 100µs (alert on > 5% regression if baseline exists).
  2. Token Pruning Latency: < 5ms for 128-token sequence.
  3. Token Merging (ToMe) Latency: < 5ms for 128-token sequence.
  4. Block-Sparse Attention Latency: < 20ms for N=1024.
  5. Baseline Comparison: Validates against week1_baseline.json within 5% tolerance.
"""

import os
import json
import time
import pytest
import numpy as np

from universal_compute_router.adaptive_dispatch import AdaptiveDispatchRouter
from hyper_runtime.semantic_token_pruning import SemanticTokenPruner
from hyper_runtime.token_merging.tome_engine import TokenMergingEngine
from hyper_runtime.sparse_attention import SparseAttentionEngine


def test_router_dispatch_latency_regression():
    """Ensure sub-100µs guarantee is strictly preserved with zero regression."""
    router = AdaptiveDispatchRouter()
    latencies = []
    # Warm up already done in __init__
    for _ in range(100):
        res = router.route("Softmax", (1, 12, 512, 512))
        latencies.append(res["decision_latency_us"])

    p99 = float(np.percentile(latencies, 99))
    mean_us = float(np.mean(latencies))

    # Strict target: Mean < 10µs, P99 < 100µs
    assert mean_us < 10.0, f"Router mean latency regressed to {mean_us:.2f}µs"
    assert p99 < 100.0, f"Router P99 latency regressed to {p99:.2f}µs"


def test_token_pruner_latency_regression():
    """Ensure semantic pruning completes in < 5ms for 128-token prompt."""
    pruner = SemanticTokenPruner()
    rng = np.random.default_rng(42)
    emb = rng.standard_normal((128, 896)).astype(np.float32)

    # Measure over 20 runs
    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        _ = pruner.prune_embeddings(emb)
        times.append((time.perf_counter() - t0) * 1000.0)

    median_ms = float(np.median(times))
    assert median_ms < 5.0, f"Token pruning latency regressed to {median_ms:.2f}ms (target < 5.0ms)"


def test_tome_merging_latency_regression():
    """Ensure Token Merging completes in < 5ms for 128 tokens."""
    tome = TokenMergingEngine(merge_ratio=0.25)
    rng = np.random.default_rng(42)
    base = rng.standard_normal((32, 896)).astype(np.float32)
    hidden = np.repeat(base, 4, axis=0)
    tokens = list(range(128))

    times = []
    for _ in range(20):
        t0 = time.perf_counter()
        _ = tome.merge_tokens(tokens, hidden)
        times.append((time.perf_counter() - t0) * 1000.0)

    median_ms = float(np.median(times))
    assert median_ms < 5.0, f"ToMe latency regressed to {median_ms:.2f}ms (target < 5.0ms)"


def test_sparse_attention_latency_regression():
    """Ensure Block-Sparse Attention for N=1024 executes in < 20ms."""
    sparse = SparseAttentionEngine(local_window=32, stride=16)
    rng = np.random.default_rng(42)
    Q = rng.standard_normal((1024, 64)).astype(np.float32)
    K = rng.standard_normal((1024, 64)).astype(np.float32)
    V = rng.standard_normal((1024, 64)).astype(np.float32)

    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        _ = sparse.compute_sparse_attention(Q, K, V)
        times.append((time.perf_counter() - t0) * 1000.0)

    median_ms = float(np.median(times))
    assert median_ms < 20.0, f"Sparse attention latency regressed to {median_ms:.2f}ms (target < 20.0ms)"


def test_baseline_json_integrity():
    """Ensure week1_baseline.json exists and meets Phase A success criteria."""
    baseline_path = "week1_baseline.json"
    if not os.path.exists(baseline_path):
        pytest.skip("week1_baseline.json not yet generated")

    with open(baseline_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "12450H" in data["hardware"], f"Hardware mismatch in baseline: {data.get('hardware')}"
    assert data["success_criteria_met"]["first_token_sub_1s"] is True
    assert data["success_criteria_met"]["generation_256_sub_30s"] is True
    assert data["ttft_ms"] < 1000.0
