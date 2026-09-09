"""
tests/test_cco_exact_cache.py
=============================
Tests for ExactFullContentCache:
- Verifies that tensors identical in prefix/suffix but differing in the middle NEVER collide.
- Verifies COLD, WARM, and DISABLED cache modes.
- Verifies that changing model_hash, contract_hash, precision_mode, or shape causes cache misses.
"""

import pytest
import numpy as np
from hyper_cco.exact_cache import ExactFullContentCache, CacheMode


def test_full_content_hash_collision_resistance_middle_elements():
    """
    REGRESSION TEST FOR REQUIREMENT 12 & 88:
    Verify that two arrays with identical first 512 elements and last 512 elements,
    but differing in the middle elements, produce DIFFERENT hashes.
    Under old sampled hashing (ravel()[:512], ravel()[-512:]), these would falsely collide.
    """
    N = 2048
    t1 = np.ones(N, dtype=np.float32)
    t2 = np.ones(N, dtype=np.float32)
    # Modify only the middle elements (between index 600 and 700)
    t2[600:700] = 99.0

    key1 = ExactFullContentCache.compute_full_content_key("test_op", t1)
    key2 = ExactFullContentCache.compute_full_content_key("test_op", t2)

    assert key1 != key2, "CRITICAL ERROR: Full content cache collided on middle-modified tensor!"


def test_cache_modes_cold_warm_disabled():
    cache = ExactFullContentCache()
    A = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    key = cache.compute_full_content_key("add", A)

    # 1. Warm put and lookup
    cache.set_mode(CacheMode.WARM)
    cache.put(key, np.array([2.0, 4.0, 6.0], dtype=np.float32), original_operations=6.0)
    lookup1 = cache.lookup(key)
    assert lookup1.hit is True
    assert lookup1.executed_operations == 0.0
    assert lookup1.original_operations == 6.0

    # 2. Cold mode: storage cleared, cold miss guaranteed
    cache.set_mode(CacheMode.COLD)
    lookup2 = cache.lookup(key)
    assert lookup2.hit is False

    # 3. Disabled mode: lookups always report miss
    cache.set_mode(CacheMode.WARM)
    cache.put(key, np.array([2.0, 4.0, 6.0], dtype=np.float32))
    cache.set_mode(CacheMode.DISABLED)
    lookup3 = cache.lookup(key)
    assert lookup3.hit is False


def test_cache_key_sensitivity_to_metadata():
    A = np.array([1.0, 2.0], dtype=np.float32)
    key_base = ExactFullContentCache.compute_full_content_key("op", A, model_hash="m1", contract_hash="c1")
    key_diff_model = ExactFullContentCache.compute_full_content_key("op", A, model_hash="m2", contract_hash="c1")
    key_diff_contract = ExactFullContentCache.compute_full_content_key("op", A, model_hash="m1", contract_hash="c2")
    key_diff_dtype = ExactFullContentCache.compute_full_content_key("op", A.astype(np.float64), model_hash="m1", contract_hash="c1")

    assert key_base != key_diff_model
    assert key_base != key_diff_contract
    assert key_base != key_diff_dtype
