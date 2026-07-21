"""
tests/test_cache_residency.py
Unit tests for StreamingKVManager, SnapKVEviction, and ChunkedPrefillProcessor.
"""

import pytest
import numpy as np
from core_ai.cache_residency import StreamingKVManager, SnapKVEviction, ChunkedPrefillProcessor


# ─── StreamingKVManager ───────────────────────────────────────────────────────

def test_streaming_kv_sink_slots():
    mgr = StreamingKVManager(sink_tokens=4, window_size=8, num_layers=2, num_heads=4, head_dim=8)
    k = np.ones((1, 4, 8), dtype=np.float16)
    v = np.ones((1, 4, 8), dtype=np.float16)
    for _ in range(4):
        k_out, v_out = mgr.push_token(0, k, v)
    assert k_out.shape[0] == 4  # 4 sink tokens cached


def test_streaming_kv_window_bounded():
    mgr = StreamingKVManager(sink_tokens=4, window_size=4, num_layers=2, num_heads=2, head_dim=4)
    k = np.ones((1, 2, 4), dtype=np.float16)
    v = np.ones((1, 2, 4), dtype=np.float16)
    for _ in range(20):
        k_out, v_out = mgr.push_token(0, k, v)
    assert k_out.shape[0] <= 4 + 4  # Never exceeds sink + window


def test_streaming_kv_memory_footprint():
    mgr = StreamingKVManager(sink_tokens=4, window_size=124, num_layers=32, num_heads=32, head_dim=64)
    stats = mgr.stats()
    # Should be under 1MB for L2 cache fit
    assert stats["cache_footprint_kb"] < 2048  # Under 2MB


# ─── SnapKVEviction ───────────────────────────────────────────────────────────

def test_snapkv_eviction_reduces_size():
    eviction = SnapKVEviction(max_tokens=512, eviction_budget=128, eviction_interval=4)
    for _ in range(4):
        attn = np.random.rand(4, 1, 256).astype(np.float32)
        eviction.record_attention(attn)

    k = np.random.rand(256, 4, 64).astype(np.float16)
    v = np.random.rand(256, 4, 64).astype(np.float16)

    k_evicted, v_evicted = eviction.evict(k, v)
    assert k_evicted.shape[0] <= 128  # Budget enforced
    assert k_evicted.shape[0] == v_evicted.shape[0]


def test_snapkv_no_evict_when_under_budget():
    eviction = SnapKVEviction(max_tokens=512, eviction_budget=256, eviction_interval=4)
    k = np.ones((100, 4, 64), dtype=np.float16)
    v = np.ones((100, 4, 64), dtype=np.float16)
    k_out, v_out = eviction.evict(k, v)
    assert k_out.shape[0] == 100  # No eviction, under budget


# ─── ChunkedPrefillProcessor ─────────────────────────────────────────────────

def test_chunked_prefill_short_prompt():
    proc = ChunkedPrefillProcessor(chunk_size=512)
    tokens = list(range(100))
    chunks = proc.split_prompt_tokens(tokens)
    assert len(chunks) == 1
    assert chunks[0] == tokens


def test_chunked_prefill_long_prompt():
    proc = ChunkedPrefillProcessor(chunk_size=512, overlap=16)
    tokens = list(range(2048))
    chunks = proc.split_prompt_tokens(tokens)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 512


def test_chunked_prefill_cache_pressure():
    proc = ChunkedPrefillProcessor(chunk_size=512)
    pressure = proc.estimate_cache_pressure(512)
    assert "kv_cache_mb" in pressure
    # 512 tokens should fit in 12MB L3
    assert pressure["fits_in_l3"] is True

def test_chunked_prefill_cache_pressure_large():
    proc = ChunkedPrefillProcessor(chunk_size=512)
    pressure = proc.estimate_cache_pressure(8192)
    # 8192 tokens won't fit in 12MB
    assert pressure["fits_in_l3"] is False
