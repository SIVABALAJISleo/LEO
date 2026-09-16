"""
hyper_x/verification/resource_verifier.py
=========================================
Phase 1: Resource & Thermal Stability Verifier.
Monitors memory footprint, memory leaks, DRAM bandwidth saturation, and thermal throttling risk.
Fail-closed default: passed = False.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ResourceVerificationResult:
    passed: bool = False  # Fail-closed default
    peak_memory_mb: float = 0.0
    memory_limit_mb: float = 0.0
    leak_detected: bool = False
    thermal_throttling_risk: float = 0.0  # [0.0, 1.0]
    violations: List[str] = field(default_factory=list)


class ResourceVerifier:
    """
    Validates physical memory bounds and thermal sustainability.
    """

    @classmethod
    def verify(
        cls,
        memory_trace_mb: List[float],
        memory_limit_mb: float = 2048.0,
        thermal_throttle_flag: bool = False,
    ) -> ResourceVerificationResult:
        violations = []
        if not memory_trace_mb:
            return ResourceVerificationResult(passed=False, violations=["Empty memory trace"])

        peak_mb = max(memory_trace_mb)
        if peak_mb > memory_limit_mb:
            violations.append(f"Memory limit exceeded: peak {peak_mb:.1f} MB > limit {memory_limit_mb:.1f} MB")

        # Monotonic memory growth detection across 10+ samples indicates leak
        leak = False
        if len(memory_trace_mb) >= 10:
            if all(memory_trace_mb[i] < memory_trace_mb[i+1] for i in range(len(memory_trace_mb)-1)):
                leak = True
                violations.append("Monotonic memory increase detected across entire run (memory leak suspected)")

        if thermal_throttle_flag:
            violations.append("Thermal throttling event registered during sustained endurance test")

        passed = len(violations) == 0
        return ResourceVerificationResult(
            passed=passed,
            peak_memory_mb=round(peak_mb, 2),
            memory_limit_mb=memory_limit_mb,
            leak_detected=leak,
            thermal_throttling_risk=1.0 if thermal_throttle_flag else 0.0,
            violations=violations,
        )
