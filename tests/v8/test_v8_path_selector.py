"""
tests/v8/test_v8_path_selector.py
=================================
Tests for CheapestValidPathSelector and ExecutionCertificate.
"""

import numpy as np
import pytest

from hyper.cache.exact_cache import ExactCache
from hyper.v8.contract import PathClassification, exact_contract, numerical_contract
from hyper.v8.path_selector import CheapestValidPathSelector
from hyper.v8.residual import ExactResidualEngine


def test_path_selector_returns_certificate():
    selector = CheapestValidPathSelector()
    contract = exact_contract("test_cert")

    A = np.eye(8, dtype=np.float32)
    B = np.ones((8, 8), dtype=np.float32)

    out, cert = selector.select_and_execute(A, B, contract)

    assert cert is not None
    assert cert.contract_passed
    assert cert.max_abs_error <= 1e-5
    assert isinstance(cert.speedup, float)
    assert np.allclose(out, A @ B)


def test_path_selector_cache_hit():
    cache = ExactCache(max_entries=10)
    selector = CheapestValidPathSelector(exact_cache=cache)
    contract = exact_contract("test_cache")

    A = np.random.randn(8, 8).astype(np.float32)
    B = np.random.randn(8, 8).astype(np.float32)

    # First run (populates cache)
    out1, cert1 = selector.select_and_execute(A, B, contract)

    # Second run with exact same inputs
    out2, cert2 = selector.select_and_execute(A, B, contract)

    assert cert2.path_type == PathClassification.EXACT_REUSED
    assert np.array_equal(out1, out2)


def test_path_selector_sparse_path():
    selector = CheapestValidPathSelector()
    contract = exact_contract("test_sparse")

    # 95% sparse inputs
    A = np.zeros((32, 32), dtype=np.float32)
    A[0, 0] = 5.0
    A[10, 10] = 2.0
    B = np.zeros((32, 32), dtype=np.float32)
    B[0, 5] = 3.0

    out, cert = selector.select_and_execute(A, B, contract)
    assert np.allclose(out, A @ B)
    assert cert.contract_passed
