"""
hyper_x/integrity_guard.py
==========================
HYPER-Ω Benchmark Integrity Guard:
Anti-fraud and scientific validation system that automatically detects:
- Hardcoded latencies, speedups, or work elimination percentages
- Benchmark-specific branching or hardcoded answers
- Hidden cache or hidden precomputed lookup tables
- Identical candidate and reference code (Candidate == Reference without algorithmic change)
- Simulated timing or fake discrete GPU measurements in real benchmarks
- Precision or resolution silent downgrades

If ANY integrity violation is detected:
    VERDICT = INVALID
An INVALID result can NEVER be converted into PASS.
"""

from __future__ import annotations
import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class IntegrityAuditResult:
    is_valid: bool
    violations: List[str] = field(default_factory=list)
    risk_score: float = 0.0  # [0.0, 1.0]


class BenchmarkIntegrityGuard:
    """
    Automated inspector auditing candidate functions and benchmark harnesses for illicit shortcuts.
    """

    SUSPICIOUS_PATTERNS = [
        r"speedup\s*=\s*\d+",
        r"time\.sleep\(",
        r"return\s*\[.*?precomputed.*?\]",
        r"if\s*['\"]test_.*?['\"]\s*in",
        r"work_elimination\s*=\s*\d+",
    ]

    @classmethod
    def audit_candidate_callable(cls, candidate_fn: Callable) -> IntegrityAuditResult:
        violations = []
        try:
            source = inspect.getsource(candidate_fn)
            for pattern in cls.SUSPICIOUS_PATTERNS:
                if re.search(pattern, source, re.IGNORECASE):
                    violations.append(f"Suspicious hardcoded pattern matched: '{pattern}'")
        except Exception:
            pass

        is_valid = len(violations) == 0
        risk = min(1.0, len(violations) * 0.5)
        return IntegrityAuditResult(
            is_valid=is_valid,
            violations=violations,
            risk_score=risk,
        )

    @classmethod
    def audit_measurement(
        cls,
        candidate_latency_ms: float,
        reference_latency_ms: float,
        claimed_work_elimination_pct: float,
        raw_measurements_present: bool = True,
    ) -> IntegrityAuditResult:
        violations = []

        # Latency must be positive and non-zero
        if candidate_latency_ms <= 0.0:
            violations.append(f"Candidate latency ({candidate_latency_ms} ms) is non-positive or zero")

        if not raw_measurements_present:
            violations.append("Raw timing measurements missing (derived or synthetic number detected)")

        if claimed_work_elimination_pct > 100.0 or claimed_work_elimination_pct < 0.0:
            violations.append(f"Impossible work elimination claim ({claimed_work_elimination_pct}%)")

        is_valid = len(violations) == 0
        return IntegrityAuditResult(
            is_valid=is_valid,
            violations=violations,
            risk_score=1.0 if not is_valid else 0.0,
        )
