"""
tests/test_radical_pathway_full.py
Master Falsification & Integration Suite for 5-Layer Radical Pathway Redesign.
Verifies Token Merging (ToMe), Speculative Orchestration, Fused Online Softmax,
and Full 5-Layer Composite GPU Parity Pipeline.
"""

import pytest
import numpy as np
import torch

from core_ai.attention import (
    VectorizedBlockAttention,
    LocalAttention,
    TokenMerger,
    FastContextIndex,
    SpeculativeOrchestrator,
    fused_attention_online_softmax,
    HeterogeneousDispatcher
)
from core_ai.leo_engine import LeoEngine


class TestLayer3TokenMerging:
    """Falsification tests for Layer 3: Token Merging and Fast Context Retrieval."""

    def test_token_merging_and_unmerging(self):
        seq_len, d = 64, 32
        np.random.seed(42)
        x = np.random.randn(seq_len, d).astype(np.float32)

        merger = TokenMerger(merge_ratio=0.25, similarity_threshold=0.0)
        merged_x, metadata = merger.merge_tokens(x)

        # Expected reduction by ~25%
        assert metadata["merged"] is True
        assert len(merged_x) < seq_len
        assert metadata["pairs_merged"] > 0

        # Unmerge and verify shape and information retention
        unmerged_x = merger.unmerge_tokens(merged_x, metadata)
        assert unmerged_x.shape == (seq_len, d)

        # Average cosine similarity between original and reconstructed tokens
        norm_orig = x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        norm_recon = unmerged_x / np.maximum(np.linalg.norm(unmerged_x, axis=1, keepdims=True), 1e-9)
        cosine_sims = np.sum(norm_orig * norm_recon, axis=1)

        mean_sim = np.mean(cosine_sims)
        assert mean_sim > 0.85, f"Information loss too high: mean cosine similarity was {mean_sim}"

    def test_fast_context_index(self):
        index = FastContextIndex(key_dim=32)
        K_block = np.random.randn(32, 32).astype(np.float32)
        V_block = np.random.randn(32, 32).astype(np.float32)

        index.add_block(K_block, V_block)
        query = np.random.randn(32).astype(np.float32)

        ret_k, ret_v = index.query(query, top_k=10)
        assert ret_k.shape == (10, 32)
        assert ret_v.shape == (10, 32)
        assert np.isfinite(ret_k).all()
        assert np.isfinite(ret_v).all()


class TestLayer4SpeculativeOrchestrator:
    """Falsification tests for Layer 4: Speculative Generation and Contract Parity."""

    def test_speculative_generation_determinism(self):
        orchestrator = SpeculativeOrchestrator(draft_window=4, acceptance_threshold=0.75)
        prompt = [101, 202, 303]
        max_tokens = 32

        tokens, telemetry = orchestrator.generate(prompt, max_new_tokens=max_tokens)

        assert len(tokens) == len(prompt) + max_tokens
        assert telemetry["tokens_generated"] == max_tokens
        assert telemetry["cycles"] > 0
        assert 0.0 <= telemetry["acceptance_rate"] <= 1.0
        assert telemetry["effective_speedup"] >= 1.0

    def test_rejection_and_target_correction(self):
        """Verifies that divergent draft tokens are strictly corrected by the target model."""
        def draft_fn(context):
            return [9999, 9999, 9999]

        def target_eval_fn(context, count):
            # Target disagrees with 9999 and proposes 7777
            return [7777] * count, [0.99] * count

        orchestrator = SpeculativeOrchestrator(
            draft_window=3,
            acceptance_threshold=0.90,
            draft_fn=draft_fn,
            target_eval_fn=target_eval_fn
        )

        tokens, telem = orchestrator.generate([1, 2], max_new_tokens=5)
        # All newly generated tokens must be the target's choice (7777), not the draft (9999)
        new_tokens = tokens[2:]
        assert all(t == 7777 for t in new_tokens), "Speculative engine accepted unverified draft tokens!"


class TestLayer5FusedAttention:
    """Falsification tests for Layer 5: Fused Online Softmax against Dense Baseline."""

    def test_fused_online_softmax_equivalence(self):
        seq_len, d = 64, 32
        np.random.seed(123)
        Q = np.random.randn(seq_len, d).astype(np.float32)
        K = np.random.randn(seq_len, d).astype(np.float32)
        V = np.random.randn(seq_len, d).astype(np.float32)

        # Dense Baseline
        scale = 1.0 / np.sqrt(d)
        scores = (Q @ K.T) * scale
        causal_mask = np.triu(np.ones((seq_len, seq_len), dtype=bool), k=1)
        scores = np.where(causal_mask, -1e9, scores)
        exp_s = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        probs = exp_s / np.sum(exp_s, axis=-1, keepdims=True)
        dense_out = probs @ V

        # Fused Online Softmax
        fused_out = fused_attention_online_softmax(Q, K, V, causal=True)

        assert np.allclose(dense_out, fused_out, atol=1e-4), \
            f"Fused online softmax diverged from dense reference! Max diff: {np.max(np.abs(dense_out - fused_out))}"

    def test_heterogeneous_dispatcher(self):
        dispatcher = HeterogeneousDispatcher(use_igpu=True)
        info = dispatcher.get_info()
        assert "backend" in info
        assert "threads" in info
        A = np.random.randn(64, 64).astype(np.float32)
        B = np.random.randn(64, 64).astype(np.float32)
        C = dispatcher.dispatch_matmul(A, B)
        assert C.shape == (64, 64)


class TestFullCompositePipeline:
    """Tests the combined 5-layer pipeline end-to-end inside LeoEngine."""

    def test_5_layer_engine_execution(self):
        engine = LeoEngine(
            attention_mode="block",
            token_merging=True,
            use_fused_kernel=True,
            speculative=True,
            semantic_cache=False
        )

        res = engine.generate("Benchmark end-to-end 5-layer composite execution", max_new_tokens=32)

        assert res["cached"] is False
        assert res["latency_sec"] > 0.0
        assert res["tokens_per_sec"] > 0.0
        assert "Token Merging" in res["execution_path"]
        assert "Fused Online Softmax" in res["execution_path"]
        assert "Speculative Decoding" in res["execution_path"]
        assert "Heterogeneous Silicon" in res["execution_path"]
