"""
hyper_x/verification/benchmark_integrity.py
===========================================
Phase 1: Benchmark Integrity Verifier.
Inspects benchmark harnesses and measurements for fraud, simulated timing, or hardcoded constants.
Fail-closed default: passed = False.
"""

from __future__ import annotations
import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class BenchmarkIntegrityResult:
    passed: bool = False  # Fail-closed default
    violations: List[str] = field(default_factory=list)
    risk_score: float = 1.0


class BenchmarkIntegrityVerifier:
    """
    Automated inspector auditing benchmarks for fraudulent shortcuts.
    """

    SUSPICIOUS_PATTERNS = [
        r"speedup\s*=\s*\d+",
        r"time\.sleep\(",
        r"return\s*\[.*?precomputed.*?\]",
        r"if\s*['\"]test_.*?['\"]\s*in",
        r"work_elimination\s*=\s*\d+",
    ]

    @classmethod
    def verify_callable(cls, candidate_fn: Callable) -> BenchmarkIntegrityResult:
        violations = []
        try:
            source = inspect.getsource(candidate_fn)
            for pattern in cls.SUSPICIOUS_PATTERNS:
                if re.search(pattern, source, re.IGNORECASE):
                    violations.append(f"Forbidden hardcoded pattern detected: '{pattern}'")
        except Exception:
            pass

        passed = len(violations) == 0
        return BenchmarkIntegrityResult(
            passed=passed,
            violations=violations,
            risk_score=0.0 if passed else 1.0,
        )

    @classmethod
    def verify_telemetry(
        cls,
        candidate_latency_ms: float,
        reference_latency_ms: float,
        claimed_elimination_pct: float,
        raw_clock_samples_present: bool = True,
    ) -> BenchmarkIntegrityResult:
        violations = []
        if candidate_latency_ms <= 0.0:
            violations.append(f"Invalid non-positive candidate latency: {candidate_latency_ms} ms")
        if not raw_clock_samples_present:
            violations.append("Raw timing clock samples missing (synthetic timing suspected)")
        if claimed_elimination_pct < 0.0 or claimed_elimination_pct > 100.0:
            violations.append(f"Impossible work elimination claim: {claimed_elimination_pct}%")

        passed = len(violations) == 0
        return BenchmarkIntegrityResult(
            passed=passed,
            violations=violations,
            risk_score=0.0 if passed else 1.0,
        )
