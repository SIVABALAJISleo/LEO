"""
hyper_x/verification/realtime_verifier.py
=========================================
Phase 1: Real-Time Deadline Verifier.
Audits distribution latencies (P50, P90, P95, P99, worst-case) against hard real-time deadlines.
Fail-closed default: passed = False.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, List
import numpy as np


@dataclass
class RealtimeVerificationResult:
    passed: bool = False  # Fail-closed default
    p50_ms: float = float("inf")
    p90_ms: float = float("inf")
    p95_ms: float = float("inf")
    p99_ms: float = float("inf")
    worst_case_ms: float = float("inf")
    deadline_ms: float = 0.0
    deadline_violations: int = 0


class RealtimeVerifier:
    """
    Validates that latency distribution satisfies contract real-time deadlines.
    """

    @classmethod
    def verify(cls, latency_samples_ms: List[float], deadline_ms: float) -> RealtimeVerificationResult:
        if not latency_samples_ms:
            return RealtimeVerificationResult(passed=False, deadline_ms=deadline_ms)

        arr = np.array(latency_samples_ms, dtype=np.float64)
        p50 = float(np.percentile(arr, 50))
        p90 = float(np.percentile(arr, 90))
        p95 = float(np.percentile(arr, 95))
        p99 = float(np.percentile(arr, 99))
        worst = float(np.max(arr))

        violations = int(np.sum(arr > deadline_ms))
        # Hard real-time requirement: P99 and worst-case must meet deadline
        passed = (worst <= deadline_ms) and (violations == 0)

        return RealtimeVerificationResult(
            passed=passed,
            p50_ms=round(p50, 3),
            p90_ms=round(p90, 3),
            p95_ms=round(p95, 3),
            p99_ms=round(p99, 3),
            worst_case_ms=round(worst, 3),
            deadline_ms=deadline_ms,
            deadline_violations=violations,
        )
