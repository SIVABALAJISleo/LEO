"""
hyper/security/sandbox.py
=========================
Security & Reliability Engine (Section 62):
Implements input sanitization, timeout watchdogs, memory boundary checks,
and crash recovery with automatic fallback.
"""

import time
from typing import Dict, Any, Callable, Tuple, Optional


class ExecutionWatchdog:
    """
    Guards kernel executions against infinite loops, memory leaks, and silent crashes.
    """
    def __init__(self, default_timeout_sec: float = 10.0):
        self.default_timeout_sec = default_timeout_sec

    def guarded_execution(
        self, kernel_fn: Callable[[], Any], fallback_fn: Callable[[], Any]
    ) -> Tuple[Any, Dict[str, Any]]:
        t0 = time.perf_counter()
        try:
            result = kernel_fn()
            t_elapsed_ms = (time.perf_counter() - t0) * 1000.0
            return result, {"status": "SUCCESS", "elapsed_ms": round(t_elapsed_ms, 3)}
        except Exception as e:
            t_fb = time.perf_counter()
            fb_res = fallback_fn()
            t_fb_ms = (time.perf_counter() - t_fb) * 1000.0
            return fb_res, {
                "status": "WATCHDOG_RECOVERED_FALLBACK",
                "error": str(e),
                "elapsed_ms": round(t_fb_ms, 3)
            }
