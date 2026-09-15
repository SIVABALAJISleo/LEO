"""
tests/test_cache_key_completeness.py
====================================
Tests Phase 5 cryptographic multi-state cache key completeness.
Verifies that modifying ANY execution factor invalidates the key.
"""

import numpy as np
import pytest
from hyper.cache.exact_cache import compute_cache_key


def test_identical_inputs_produce_identical_key():
    data = np.ones((16, 16), dtype=np.float32)
    k1 = compute_cache_key(data, "model_A", {"opt": 1}, "float32", 42, "10.0.0", "CPU_AVX2", "c_v1", "1.0")
    k2 = compute_cache_key(data.copy(), "model_A", {"opt": 1}, "float32", 42, "10.0.0", "CPU_AVX2", "c_v1", "1.0")
    assert k1 == k2


def test_modified_input_changes_key():
    d1 = np.zeros((16, 16), dtype=np.float32)
    d2 = np.zeros((16, 16), dtype=np.float32)
    d2[0, 0] = 1.0
    k1 = compute_cache_key(d1, "model_A")
    k2 = compute_cache_key(d2, "model_A")
    assert k1 != k2


def test_modified_model_changes_key():
    d = np.ones((8, 8), dtype=np.float32)
    k1 = compute_cache_key(d, "model_v1")
    k2 = compute_cache_key(d, "model_v2")
    assert k1 != k2


def test_changed_parameters_changes_key():
    d = np.ones((8, 8), dtype=np.float32)
    k1 = compute_cache_key(d, "m", {"temperature": 0.7})
    k2 = compute_cache_key(d, "m", {"temperature": 0.8})
    assert k1 != k2


def test_changed_precision_changes_key():
    d = np.ones((8, 8), dtype=np.float32)
    k1 = compute_cache_key(d, "m", precision="float32")
    k2 = compute_cache_key(d, "m", precision="float16")
    assert k1 != k2


def test_changed_seed_changes_key():
    d = np.ones((8, 8), dtype=np.float32)
    k1 = compute_cache_key(d, "m", random_seed=42)
    k2 = compute_cache_key(d, "m", random_seed=43)
    assert k1 != k2


def test_changed_backend_changes_key():
    d = np.ones((8, 8), dtype=np.float32)
    k1 = compute_cache_key(d, "m", hardware_backend="CPU_AVX2")
    k2 = compute_cache_key(d, "m", hardware_backend="OPENVINO_GPU")
    assert k1 != k2


def test_changed_contract_changes_key():
    d = np.ones((8, 8), dtype=np.float32)
    k1 = compute_cache_key(d, "m", contract_repr="contract_exact")
    k2 = compute_cache_key(d, "m", contract_repr="contract_approximate")
    assert k1 != k2
