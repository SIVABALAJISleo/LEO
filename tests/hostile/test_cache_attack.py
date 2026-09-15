"""
tests/hostile/test_cache_attack.py
==================================
Cache Elimination Attack (Phase 16).
Attacks memoization engines with unpredictable non-repeating high-entropy inputs.
Ensures zero false cache hits and measures true cache-off throughput.
"""

import numpy as np
import pytest
from hyper_x.leaf.verification import DECPVerifier
from hyper.extreme.cdre import CDREFramework


def test_cache_elimination_attack():
    cdre = CDREFramework()
    
    # Generate 20 distinct random inputs with high entropy
    hits = 0
    for i in range(20):
        A = np.random.randn(16, 16).astype(np.float32)
        B = np.random.randn(16, 16).astype(np.float32)
        _, telem = cdre.execute_under_contract(
            workload_id=f"workload_{i}",
            fast_fn=lambda: np.matmul(A, B),
            exact_fn=lambda: np.matmul(A, B),
            inputs=[A, B],
        )
        if telem.cache_hit:
            hits += 1

    # On non-repeating inputs, cache hit rate MUST be exactly 0
    assert hits == 0
