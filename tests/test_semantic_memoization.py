"""
tests/test_semantic_memoization.py
==================================
Unit tests for Multi-Level Semantic Memoization & Irreducible Entropy Detection.
"""

import numpy as np
import pytest

from hyper.research_engine.semantic_memoization import (
    EntropyDetector,
    LSHSemanticCache,
)


def test_entropy_detector_structured_vs_random():
    # Structured signal: Constant or low frequency sine wave
    structured = np.sin(np.linspace(0, 4 * np.pi, 1024)).astype(np.float32)
    e_struct = EntropyDetector.compute_entropy_ratio(structured)
    assert not EntropyDetector.is_irreducible(structured, threshold=0.65)

    # Pure high-entropy uniform noise: K(x) ~ |x|
    rng = np.random.default_rng(42)
    noise = rng.uniform(-1.0, 1.0, size=2048).astype(np.float32)
    e_noise = EntropyDetector.compute_entropy_ratio(noise)
    assert e_noise > e_struct
    assert EntropyDetector.is_irreducible(noise, threshold=0.65)


def test_lsh_cache_hit_and_miss():
    in_dim = 64
    cache = LSHSemanticCache(in_dim=in_dim, num_hyperplanes=16, max_entries=100)

    # Structured pattern
    x = np.linspace(-1.0, 1.0, in_dim, dtype=np.float32)
    y_expected = np.sum(x) * 2.0

    # First lookup: Miss
    out = cache.lookup(x)
    assert out is None

    # Insert
    cache.insert(x, np.array([y_expected], dtype=np.float32))

    # Second lookup: Instant Hit
    hit_out = cache.lookup(x)
    assert hit_out is not None
    assert np.allclose(hit_out[0], y_expected)

    stats = cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_lsh_entropy_bypass():
    in_dim = 64
    cache = LSHSemanticCache(in_dim=in_dim, num_hyperplanes=16)

    # Pure random noise with K(x) ~ |x|
    noise = np.random.uniform(-100.0, 100.0, size=in_dim).astype(np.float32)

    # Lookup should bypass cache due to irreducible entropy
    out = cache.lookup(noise)
    assert out is None
    stats = cache.get_stats()
    assert stats["bypassed_entropy"] >= 1
