"""
hyper_x/verification/cache_integrity.py
=======================================
Phase 1: Cache Integrity Verifier.
Enforces absolute separation between cold execution, warm execution, and exact memoization.
Prevents semantic cache hits from being reported as exact computational speedups.
Fail-closed default: passed = False.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CacheIntegrityResult:
    passed: bool = False  # Fail-closed default
    is_cold_start_verified: bool = False
    is_warm_hit_properly_classified: bool = True
    violations: List[str] = field(default_factory=list)


class CacheIntegrityVerifier:
    """
    Verifies that cache states are not conflated with computational speedups.
    """

    @classmethod
    def verify(
        cls,
        cache_state: str,
        claimed_classification: str,
        reported_compute_speedup: float,
    ) -> CacheIntegrityResult:
        violations = []

        if cache_state in ("WARM_HIT", "EXACT_CACHE_HIT"):
            if "SPEEDUP" in claimed_classification or reported_compute_speedup > 1.0:
                violations.append(
                    "Violation: Cache hit reported as computational speedup rather than COMPUTATION_AVOIDED_BY_EXACT_REUSE"
                )

        passed = len(violations) == 0
        return CacheIntegrityResult(
            passed=passed,
            is_cold_start_verified=(cache_state == "COLD_START"),
            is_warm_hit_properly_classified=passed,
            violations=violations,
        )
