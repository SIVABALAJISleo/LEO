"""
hyper/core/fallback/engine.py
Canonical Exact Fallback Engine (Prompt Section 31 & 45).
Guarantees uncompromised mathematical ground truth when an optimization fails verification,
violates contract tolerances, or encounters unproven structures.
The fallback must NOT be hidden from timing.
"""
from __future__ import annotations
import time
from typing import Any, Callable, Dict, Optional, Tuple
from pydantic import BaseModel, Field

from hyper.core.contract.models import SemanticContract


class FallbackEvent(BaseModel):
    timestamp_ms: float
    trigger_reason: str
    fallback_execution_time_ms: float
    was_successful: bool
    details: Dict[str, Any] = Field(default_factory=dict)


class CanonicalFallbackEngine:
    """
    Manages safe, exact execution fallback to the ground-truth reference baseline.
    """

    @classmethod
    def execute_with_fallback(
        cls,
        candidate_fn: Callable[[], Any],
        reference_fn: Callable[[], Any],
        validator_fn: Callable[[Any], Tuple[bool, str]],
    ) -> Tuple[Any, Optional[FallbackEvent], float]:
        """
        Executes candidate; if validation fails or an exception occurs,
        falls back immediately to reference_fn.
        Returns: (result, fallback_event, total_elapsed_ms)
        """
        t0 = time.perf_counter()
        fallback_event: Optional[FallbackEvent] = None
        
        try:
            cand_res = candidate_fn()
            is_valid, reason = validator_fn(cand_res)
            if is_valid:
                total_ms = (time.perf_counter() - t0) * 1000.0
                return cand_res, None, total_ms
            
            # Validation failed, trigger fallback
            t_fb_start = time.perf_counter()
            ref_res = reference_fn()
            t_fb_ms = (time.perf_counter() - t_fb_start) * 1000.0
            total_ms = (time.perf_counter() - t0) * 1000.0
            
            fallback_event = FallbackEvent(
                timestamp_ms=t0,
                trigger_reason=f"Candidate validation failed: {reason}",
                fallback_execution_time_ms=t_fb_ms,
                was_successful=True,
                details={"fallback_type": "EXACT_CANONICAL"},
            )
            return ref_res, fallback_event, total_ms

        except Exception as e:
            # Exception raised by candidate, fall back
            t_fb_start = time.perf_counter()
            ref_res = reference_fn()
            t_fb_ms = (time.perf_counter() - t_fb_start) * 1000.0
            total_ms = (time.perf_counter() - t0) * 1000.0

            fallback_event = FallbackEvent(
                timestamp_ms=t0,
                trigger_reason=f"Candidate raised exception: {str(e)}",
                fallback_execution_time_ms=t_fb_ms,
                was_successful=True,
                details={"exception": str(e)},
            )
            return ref_res, fallback_event, total_ms
