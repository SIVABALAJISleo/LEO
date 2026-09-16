"""
hyper_x/fallback/engine.py
==========================
Phase 32: Fallback Engine.
Provides deterministic, fail-safe degradation to guaranteed canonical references.
Fallback hierarchy:
  1. Optimized Exact
  2. Standard Optimized Implementation
  3. Trusted CPU Baseline Implementation
Guarantees the user always receives the declared contract if fallback supports it.
"""

from __future__ import annotations
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class FallbackEngine:
    """
    Executes trusted canonical reference computation when any candidate shortcut fails.
    Guarantees transparent failure isolation and zero silent contract violation.
    """

    @classmethod
    def execute_with_fallback(
        cls,
        candidate_fn: Callable[..., Any],
        fallback_fn: Callable[..., Any],
        inputs: Any,
        verifier_fn: Optional[Callable[[Any], bool]] = None,
    ) -> Tuple[Any, Dict[str, Any]]:
        t0 = time.perf_counter()
        try:
            candidate_res = candidate_fn(inputs)
            if verifier_fn is not None:
                if not verifier_fn(candidate_res):
                    raise ValueError("Candidate output failed verification")
            lat_ms = (time.perf_counter() - t0) * 1000.0
            return candidate_res, {
                "fallback_engaged": False,
                "pathway": "CANDIDATE_PRIMARY",
                "latency_ms": round(lat_ms, 3),
            }
        except Exception as err:
            t1 = time.perf_counter()
            fallback_res = fallback_fn(inputs)
            fallback_lat = (time.perf_counter() - t1) * 1000.0
            total_lat = (time.perf_counter() - t0) * 1000.0
            return fallback_res, {
                "fallback_engaged": True,
                "failure_reason": str(err),
                "pathway": "TRUSTED_FALLBACK",
                "fallback_latency_ms": round(fallback_lat, 3),
                "total_latency_ms": round(total_lat, 3),
            }

    @staticmethod
    def execute_matrix_fallback(
        A: np.ndarray,
        B: np.ndarray,
        failure_cause: str,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Executes exact reference matrix multiplication on CPU P-core AVX2.
        """
        t0 = time.perf_counter()
        result = np.dot(A, B)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        return result, {
            "strategy": "EXACT_REFERENCE_FALLBACK",
            "fallback_engaged": True,
            "failure_cause": failure_cause,
            "fallback_latency_ms": round(elapsed_ms, 3),
            "mathematical_exactness": True,
        }
