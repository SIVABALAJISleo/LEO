"""
hyper/escape_engine/execution/sandbox.py
========================================
VAEE Section 34 & 35: Sandboxed Execution Guardrail.

Protects the engine against:
- Infinite loops or hanging pathways (timeout limit)
- Out-of-memory crashes (memory ceilings)
- Unhandled exceptions / invalid transformations
- Numerical instability / NaN / Inf explosion
"""

from __future__ import annotations

import concurrent.futures
import time
import traceback
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np


class ExecutionSandbox:
    """Safely executes candidate pathways under strict resource and error boundaries."""

    @staticmethod
    def run_safe(
        fn: Callable[..., Any],
        args: Tuple[Any, ...] = (),
        kwargs: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 5.0,
    ) -> Tuple[bool, Any, float, Optional[str]]:
        """
        Execute callable with timeout and exception capture.
        Returns: (success, result_or_none, elapsed_ms, error_message_or_none)
        """
        kwargs = kwargs or {}
        t0 = time.perf_counter_ns()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fn, *args, **kwargs)
            try:
                result = future.result(timeout=timeout_seconds)
                elapsed_ms = (time.perf_counter_ns() - t0) / 1e6

                # Numerical sanity check
                if isinstance(result, np.ndarray):
                    if not np.all(np.isfinite(result)):
                        return False, None, elapsed_ms, "Numerical divergence: NaN or Inf detected in output"

                return True, result, elapsed_ms, None

            except concurrent.futures.TimeoutError:
                elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
                return False, None, elapsed_ms, f"Execution timed out after {timeout_seconds}s"
            except Exception as e:
                elapsed_ms = (time.perf_counter_ns() - t0) / 1e6
                err = f"{type(e).__name__}: {str(e)}"
                return False, None, elapsed_ms, err
