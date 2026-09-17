"""
tests/v8/test_v8_cache_collision.py
===================================
Tests for SHA-256 hash collision resistance in exact cache.
"""

import numpy as np
import pytest

from hyper.cache.exact_cache import ExactCache, compute_cache_key


def test_different_arrays_produce_different_keys():
    N = 64
    A1 = np.zeros((N, N), dtype=np.float32)
    A1[0, 0] = 1.0
    A1[0, 1] = -1.0

    # Same sum, same mean, same variance, different location
    A2 = np.zeros((N, N), dtype=np.float32)
    A2[1, 0] = -1.0
    A2[1, 1] = 1.0

    key1 = compute_cache_key(A1, "TEST_MODEL")
    key2 = compute_cache_key(A2, "TEST_MODEL")

    assert key1 != key2


def test_cache_never_returns_stale_data_for_different_input():
    cache = ExactCache(max_entries=10)
    A1 = np.ones((8, 8), dtype=np.float32)
    A2 = np.ones((8, 8), dtype=np.float32) * 2.0

    key1 = compute_cache_key(A1, "TEST")
    key2 = compute_cache_key(A2, "TEST")

    res1 = np.array([[1.0]])
    cache.put(key1, res1)

    val, hit, _ = cache.get(key2)
    assert not hit
    assert val is None
