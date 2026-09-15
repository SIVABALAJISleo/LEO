"""
tests/test_cache_invalidation.py
================================
Tests Phase 5 cache invalidation, cache disabling, eviction,
and concurrent thread-safety.
"""

import concurrent.futures
import numpy as np
import pytest
from hyper.cache.exact_cache import ExactCache, compute_cache_key


def test_cache_hit_and_invalidation():
    cache = ExactCache()
    k = compute_cache_key("test_input", "model1")
    val = np.array([1.0, 2.0, 3.0])

    # Miss initially
    res, hit, _ = cache.get(k)
    assert hit is False
    assert res is None

    # Put and get
    cache.put(k, val)
    res, hit, _ = cache.get(k)
    assert hit is True
    assert np.array_equal(res, val)

    # Invalidate
    evicted = cache.invalidate(k)
    assert evicted is True

    # Miss after invalidation
    res, hit, _ = cache.get(k)
    assert hit is False


def test_disabled_cache():
    cache = ExactCache(is_enabled=False)
    k = "some_key"
    cache.put(k, "some_value")
    res, hit, _ = cache.get(k)
    assert hit is False
    assert res is None


def test_clear_cache():
    cache = ExactCache()
    cache.put("k1", "v1")
    cache.put("k2", "v2")
    cache.clear()
    assert cache.report_metrics()["entry_count"] == 0
    _, hit, _ = cache.get("k1")
    assert hit is False


def test_concurrent_access_safety():
    cache = ExactCache()

    def worker(idx: int):
        k = f"key_{idx % 10}"
        cache.put(k, idx)
        v, _, _ = cache.get(k)
        if idx % 5 == 0:
            cache.invalidate(k)
        return v

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker, i) for i in range(100)]
        for f in concurrent.futures.as_completed(futures):
            _ = f.result()

    metrics = cache.report_metrics()
    assert metrics["total_queries"] == 100
