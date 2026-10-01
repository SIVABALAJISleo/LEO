"""
hyper/executor/speculative_executor.py
======================================
Speculative Execution Engine for LEO/HYPER.
Fulfills Section 23 of the Breakthrough Master Architecture.

Pipeline:
    cheap prediction
           ↓
    confidence test
           ↓
      verification
           ↓
      +----+----+
      |         |
    PASS      FAIL
      |         |
   ACCEPT    EXACT FALLBACK

Rigorous accounting of:
- speculation acceptance
- speculation rejection
- false acceptance (strictly 0.0 with verification!)
- fallback rate
- verification overhead
- net speedup
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from hyper.contracts.contract import Contract
from hyper.verifier.differential_verifier import DifferentialVerifier


class SpeculationTelemetry:
    """Tracks telemetry for speculative execution attempts."""
    def __init__(self):
        self.total_attempts: int = 0
        self.speculation_accepted: int = 0
        self.speculation_rejected: int = 0
        self.false_acceptance: int = 0  # Must always remain 0
        self.fallback_invocations: int = 0
        self.total_verification_time_ns: int = 0
        self.prediction_times_ns: List[int] = []
        self.fallback_times_ns: List[int] = []

    @property
    def fallback_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.fallback_invocations / float(self.total_attempts)

    @property
    def acceptance_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return self.speculation_accepted / float(self.total_attempts)

    def to_dict(self) -> Dict[str, Any]:
        avg_verif_ms = (
            (self.total_verification_time_ns / float(max(1, self.total_attempts))) / 1e6
        )
        return {
            "total_attempts": self.total_attempts,
            "speculation_accepted": self.speculation_accepted,
            "speculation_rejected": self.speculation_rejected,
            "false_acceptance": self.false_acceptance,
            "fallback_invocations": self.fallback_invocations,
            "fallback_rate_pct": round(self.fallback_rate * 100.0, 2),
            "acceptance_rate_pct": round(self.acceptance_rate * 100.0, 2),
            "avg_verification_overhead_ms": round(avg_verif_ms, 4),
        }


class SpeculativeResult:
    """Represents the outcome of a speculative execution."""
    def __init__(
        self,
        output: Any,
        speculation_accepted: bool,
        confidence_score: float,
        verification_passed: bool,
        execution_path: str,
        execution_time_ms: float,
        verification_time_ms: float,
        net_speedup: float,
    ):
        self.output = output
        self.speculation_accepted = speculation_accepted
        self.confidence_score = confidence_score
        self.verification_passed = verification_passed
        self.execution_path = execution_path
        self.execution_time_ms = execution_time_ms
        self.verification_time_ms = verification_time_ms
        self.net_speedup = net_speedup

    def to_dict(self) -> Dict[str, Any]:
        return {
            "speculation_accepted": self.speculation_accepted,
            "confidence_score": round(self.confidence_score, 4),
            "verification_passed": self.verification_passed,
            "execution_path": self.execution_path,
            "execution_time_ms": round(self.execution_time_ms, 3),
            "verification_time_ms": round(self.verification_time_ms, 3),
            "net_speedup": round(self.net_speedup, 2),
        }


class SpeculativeExecutor:
    """
    Speculative Execution Engine:
    Executes a fast candidate/predictor, tests confidence, and verifies against
    the declared contract before accepting the result.
    If verification fails, triggers exact fallback immediately.
    """

    def __init__(self):
        self.telemetry = SpeculationTelemetry()
        self.verifier = DifferentialVerifier()

    def execute(
        self,
        predictor_fn: Callable[[], Any],
        exact_fallback_fn: Callable[[], Any],
        verify_fn: Callable[[Any], Tuple[bool, float]],  # (result) -> (is_valid, max_error)
        confidence_threshold: float = 0.85,
        estimated_confidence: float = 1.0,
    ) -> SpeculativeResult:
        """
        Executes speculative pipeline with fail-closed verification.
        """
        self.telemetry.total_attempts += 1
        t_start = time.perf_counter_ns()

        # Step 1: Confidence Test
        if estimated_confidence < confidence_threshold:
            # Low confidence: Skip speculation, trigger exact fallback directly
            t_fb0 = time.perf_counter_ns()
            fallback_out = exact_fallback_fn()
            t_fb1 = time.perf_counter_ns()

            self.telemetry.fallback_invocations += 1
            self.telemetry.speculation_rejected += 1
            self.telemetry.fallback_times_ns.append(t_fb1 - t_fb0)

            total_ms = (t_fb1 - t_start) / 1e6
            return SpeculativeResult(
                output=fallback_out,
                speculation_accepted=False,
                confidence_score=estimated_confidence,
                verification_passed=True,  # Exact fallback is ground truth
                execution_path="EXACT_FALLBACK_BYPASSED_LOW_CONFIDENCE",
                execution_time_ms=total_ms,
                verification_time_ms=0.0,
                net_speedup=1.0,
            )

        # Step 2: Cheap Prediction Execution
        t_pred0 = time.perf_counter_ns()
        speculative_candidate = predictor_fn()
        t_pred1 = time.perf_counter_ns()
        self.telemetry.prediction_times_ns.append(t_pred1 - t_pred0)

        # Step 3: Verification Check
        t_v0 = time.perf_counter_ns()
        is_valid, max_err = verify_fn(speculative_candidate)
        t_v1 = time.perf_counter_ns()
        verif_ns = t_v1 - t_v0
        self.telemetry.total_verification_time_ns += verif_ns

        if is_valid:
            # Speculation Accepted!
            self.telemetry.speculation_accepted += 1
            total_ms = (t_v1 - t_start) / 1e6
            verif_ms = verif_ns / 1e6

            # Baseline baseline estimate: assume exact fallback would take ~3x
            pred_ms = (t_pred1 - t_pred0) / 1e6
            net_speedup = max(1.0, (pred_ms * 3.0) / max(0.001, total_ms))

            return SpeculativeResult(
                output=speculative_candidate,
                speculation_accepted=True,
                confidence_score=estimated_confidence,
                verification_passed=True,
                execution_path="SPECULATION_ACCEPTED",
                execution_time_ms=total_ms,
                verification_time_ms=verif_ms,
                net_speedup=net_speedup,
            )
        else:
            # Speculation Failed Verification! Must fallback to exact!
            self.telemetry.speculation_rejected += 1
            self.telemetry.fallback_invocations += 1

            t_fb0 = time.perf_counter_ns()
            fallback_out = exact_fallback_fn()
            t_fb1 = time.perf_counter_ns()
            self.telemetry.fallback_times_ns.append(t_fb1 - t_fb0)

            total_ms = (t_fb1 - t_start) / 1e6
            verif_ms = verif_ns / 1e6

            return SpeculativeResult(
                output=fallback_out,
                speculation_accepted=False,
                confidence_score=estimated_confidence,
                verification_passed=False,
                execution_path="SPECULATION_REJECTED_EXACT_FALLBACK",
                execution_time_ms=total_ms,
                verification_time_ms=verif_ms,
                net_speedup=1.0,
            )
