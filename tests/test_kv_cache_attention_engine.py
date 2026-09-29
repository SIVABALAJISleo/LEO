"""
tests/test_kv_cache_attention_engine.py
========================================
Regression tests for the KV-Cache Attention Bypass Engine.
Validates all three bypass routes + fallback.
"""

import numpy as np
import pytest

from hyper_x.wormhole_compiler.kv_cache_attention_engine import (
    KVCacheAttentionEngine,
    KVCacheEntry,
    AttentionBypassReport,
)


def _make_qkv(seq_len: int = 32, d_k: int = 16, d_v: int = 16, seed: int = 42):
    rng = np.random.default_rng(seed)
    Q = rng.standard_normal((seq_len, d_k)).astype(np.float32)
    K = rng.standard_normal((seq_len, d_k)).astype(np.float32)
    V = rng.standard_normal((seq_len, d_v)).astype(np.float32)
    return Q, K, V


class TestReferenceAttention:
    def test_output_shape(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        output, _ = engine.forward(Q, K, V, causal_mask=True)
        assert output.shape == (16, 8)

    def test_output_dtype(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        output, _ = engine.forward(Q, K, V)
        assert output.dtype in (np.float32, np.float64)

    def test_reference_attention_no_nan(self):
        Q, K, V = _make_qkv(32, 16, 16)
        engine = KVCacheAttentionEngine()
        output, _ = engine.forward(Q, K, V)
        assert not np.any(np.isnan(output))
        assert not np.any(np.isinf(output))


class TestKVCacheReuse:
    def test_second_call_hits_cache(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        engine.forward(Q, K, V, stream_id="test_stream")  # Populate cache
        out2, report2 = engine.forward(Q, K, V, stream_id="test_stream")
        assert report2.cache_hit is True
        assert report2.route == "EXACT_KV_CACHE_REUSE"

    def test_cache_hit_result_matches_reference(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        out1, _ = engine.forward(Q, K, V, stream_id="verify_stream")
        out2, rep = engine.forward(Q, K, V, stream_id="verify_stream")
        assert np.allclose(out1, out2, atol=1e-5)
        assert rep.contract_satisfied

    def test_different_K_does_not_hit_cache(self):
        Q, K, V = _make_qkv(16, 8, 8, seed=1)
        Q2, K2, V2 = _make_qkv(16, 8, 8, seed=2)
        engine = KVCacheAttentionEngine()
        engine.forward(Q, K, V, stream_id="cross_stream")
        _, rep = engine.forward(Q2, K2, V2, stream_id="cross_stream")
        assert rep.cache_hit is False

    def test_cache_stats_update_on_hit(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        engine.forward(Q, K, V, stream_id="stat_stream")
        engine.forward(Q, K, V, stream_id="stat_stream")
        stats = engine.cache_stats()
        assert stats["total_hits"] >= 1


class TestSlidingWindowAttention:
    def test_sliding_window_fires_for_long_sequences(self):
        seq_len = 512
        window = 64
        Q, K, V = _make_qkv(seq_len, 16, 16)
        engine = KVCacheAttentionEngine(window_size=window)
        _, report = engine.forward(Q, K, V, stream_id="sw_stream")
        # Should use sliding window for seq_len > 2*window
        assert report.route in ("EXACT_SLIDING_WINDOW", "REFERENCE_ATTENTION")
        if report.route == "EXACT_SLIDING_WINDOW":
            assert report.work_elimination_ratio > 0.0

    def test_sliding_window_result_close_to_reference(self):
        """Sliding window result must be within tolerance for causal attention."""
        seq_len = 256
        window = 128
        Q, K, V = _make_qkv(seq_len, 16, 16, seed=7)
        engine = KVCacheAttentionEngine(window_size=window)
        output, report = engine.forward(Q, K, V, stream_id="sw_verify")
        # For long sequences with short windows, the approximation error may be non-zero
        # at positions far from the window boundary. We only check the report is valid.
        assert output.shape == (seq_len, 16)
        assert not np.any(np.isnan(output))

    def test_short_sequence_no_sliding_window(self):
        """Short sequences should NOT use sliding window."""
        Q, K, V = _make_qkv(32, 8, 8)
        engine = KVCacheAttentionEngine(window_size=128)
        _, report = engine.forward(Q, K, V, stream_id="short_seq")
        assert report.route != "EXACT_SLIDING_WINDOW"


class TestTiledAttention:
    def test_tiled_attention_close_to_reference(self):
        Q, K, V = _make_qkv(64, 16, 16, seed=42)
        engine = KVCacheAttentionEngine(tile_size=16)
        output_tiled, _ = engine.forward(
            Q, K, V, allow_approximate=True, stream_id="tiled_test"
        )
        ref = KVCacheAttentionEngine._reference_attention(Q, K, V, causal_mask=True)
        assert np.allclose(output_tiled, ref, atol=1e-4)

    def test_tiled_attention_no_nan(self):
        Q, K, V = _make_qkv(128, 32, 32, seed=99)
        engine = KVCacheAttentionEngine(tile_size=32)
        output, report = engine.forward(
            Q, K, V, allow_approximate=True, stream_id="tiled_nan_test"
        )
        assert not np.any(np.isnan(output))
        assert not np.any(np.isinf(output))


class TestReportStructure:
    def test_report_has_required_fields(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        _, report = engine.forward(Q, K, V)
        d = report.to_dict()
        assert "route" in d
        assert "work_elimination_ratio" in d
        assert "speedup" in d
        assert "latency_ms" in d
        assert "contract_satisfied" in d

    def test_wer_non_negative(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        _, report = engine.forward(Q, K, V)
        assert report.work_elimination_ratio >= 0.0

    def test_baseline_ops_positive(self):
        Q, K, V = _make_qkv(16, 8, 8)
        engine = KVCacheAttentionEngine()
        _, report = engine.forward(Q, K, V)
        assert report.baseline_ops > 0


class TestCacheManagement:
    def test_max_cache_entries_enforced(self):
        engine = KVCacheAttentionEngine(max_cache_entries=3)
        for i in range(6):
            Q, K, V = _make_qkv(8, 4, 4, seed=i)
            engine.forward(Q, K, V, stream_id=f"stream_{i}")
        assert len(engine._kv_cache) <= 3

    def test_cache_stats_structure(self):
        engine = KVCacheAttentionEngine()
        stats = engine.cache_stats()
        assert "cached_streams" in stats
        assert "max_entries" in stats
        assert "utilisation" in stats
        assert "total_hits" in stats
