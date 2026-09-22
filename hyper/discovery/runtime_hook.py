"""
hyper/discovery/runtime_hook.py
===============================
Runtime Opportunity Detection & Safe Promotion Hook for UCTDE (Phase 15).

Implements Section 33 specifications:
Observes live workload execution patterns safely without blocking production latency:
    RUN WORKLOAD -> OBSERVE STRUCTURE -> DETECT OPPORTUNITY -> GENERATE ALTERNATIVE ->
    VERIFY -> BENCHMARK -> PROMOTE IF SAFE

Rule: Never silently replace production computation without explicit formal verification.
"""

from __future__ import annotations
import hashlib
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from hyper.universal.contracts.universal_contract import UniversalContract
from hyper.universal.verification.verifier import UniversalVerifier


class RuntimeObservation(BaseModel):
    workload_id: str
    call_count: int = 0
    total_latency_ms: float = 0.0
    average_latency_ms: float = 0.0
    last_input_hash: str = ""
    identical_input_streak: int = 0
    detected_structures: List[str] = Field(default_factory=list)


class RuntimeOpportunity(BaseModel):
    opportunity_id: str = Field(default_factory=lambda: f"opp-{uuid.uuid4().hex[:8]}")
    workload_id: str
    recommended_transformation: str
    expected_speedup: float
    confidence: float
    status: str = "OPPORTUNITY_DETECTED"  # "OPPORTUNITY_DETECTED", "PROMOTED", "REJECTED"
    rationale: str = ""
    timestamp: float = Field(default_factory=time.time)


class RuntimeDiscoveryHook:
    """
    Non-disruptive telemetry observer that detects algorithmic optimization opportunities.
    """

    def __init__(self) -> None:
        self.observations: Dict[str, RuntimeObservation] = {}
        self.opportunities: List[RuntimeOpportunity] = []
        self.verifier = UniversalVerifier()

    @staticmethod
    def _compute_hash(val: Any) -> str:
        try:
            return hashlib.sha256(repr(val).encode("utf-8")).hexdigest()[:16]
        except Exception:
            return "unknown"

    def observe(
        self,
        workload_id: str,
        sample_input: Any,
        latency_ms: float,
    ) -> Optional[RuntimeOpportunity]:
        """
        Records a telemetry event and evaluates opportunities.
        """
        obs = self.observations.get(workload_id)
        if not obs:
            obs = RuntimeObservation(workload_id=workload_id)
            self.observations[workload_id] = obs

        obs.call_count += 1
        obs.total_latency_ms += latency_ms
        obs.average_latency_ms = obs.total_latency_ms / obs.call_count

        cur_hash = self._compute_hash(sample_input)
        if cur_hash == obs.last_input_hash:
            obs.identical_input_streak += 1
        else:
            obs.identical_input_streak = 0
        obs.last_input_hash = cur_hash

        # Detection logic
        # 1. High repetition -> Exact caching opportunity
        if obs.identical_input_streak >= 2 and "EXACT_CACHE" not in obs.detected_structures:
            obs.detected_structures.append("EXACT_CACHE")
            opp = RuntimeOpportunity(
                workload_id=workload_id,
                recommended_transformation="EXACT_CACHE_LOOKUP",
                expected_speedup=10.0,
                confidence=0.92,
                rationale=f"Workload {workload_id} exhibited {obs.identical_input_streak} repeated identical invocations.",
            )
            self.opportunities.append(opp)
            return opp

        # 2. Heavy execution time -> Algorithmic rewrite opportunity
        if obs.call_count >= 5 and obs.average_latency_ms > 10.0 and "ALGORITHMIC_REWRITE" not in obs.detected_structures:
            obs.detected_structures.append("ALGORITHMIC_REWRITE")
            opp = RuntimeOpportunity(
                workload_id=workload_id,
                recommended_transformation="ALGORITHMIC_HORNER_OR_SPARSE",
                expected_speedup=3.5,
                confidence=0.85,
                rationale=f"Workload {workload_id} has high average latency ({obs.average_latency_ms:.2f}ms); candidate for algorithmic work reduction.",
            )
            self.opportunities.append(opp)
            return opp

        return None

    def attempt_promotion(
        self,
        workload_fn: Callable[[Any], Any],
        candidate_fn: Callable[[Any], Any],
        sample_input: Any,
        contract: UniversalContract,
    ) -> Tuple[bool, str]:
        """
        Attempts safe promotion by verifying the candidate before activation.
        """
        try:
            # 1. Evaluate candidate
            ref_out = workload_fn(sample_input)
            cand_out = candidate_fn(sample_input)

            # 2. Strict verification check
            res = self.verifier.verify(candidate_fn, workload_fn, sample_input, contract)
            if not res.is_valid:
                return False, f"Promotion rejected: verification failed ({res.error_message})"

            return True, "Promotion verified and safe for production routing."
        except Exception as exc:
            return False, f"Promotion error: {exc}"
