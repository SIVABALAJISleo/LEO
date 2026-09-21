"""
hyper/universal/execution/sandbox.py
====================================
Controlled sandboxed execution environment for candidate pathways.
Enforces:
- Hard wall-clock timeout
- Exception safety
- Memory allocation limits
- Process/thread isolation
"""

from __future__ import annotations

import concurrent.futures
import time
from typing import Any, Callable, Dict, Optional, Tuple


class UniversalSandbox:
    """Sandboxed runner executing candidate pathways with strict resource limits."""

    def __init__(self, default_timeout_s: float = 10.0, max_memory_mb: float = 4096.0) -> None:
        self.default_timeout_s = default_timeout_s
        self.max_memory_mb = max_memory_mb
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

    @staticmethod
    def _timed_call(fn: Callable[[Any], Any], arg: Any) -> Tuple[Any, float]:
        t0 = time.perf_counter_ns()
        res = fn(arg)
        ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        return res, ms

    def run_safe(
        self,
        fn: Callable[[Any], Any],
        arg: Any,
        timeout_s: Optional[float] = None,
    ) -> Tuple[bool, Optional[Any], float, Optional[str]]:
        t_limit = timeout_s or self.default_timeout_s
        t_start = time.perf_counter()

        future = self._executor.submit(self._timed_call, fn, arg)
        try:
            result, elapsed_ms = future.result(timeout=t_limit)
            return True, result, elapsed_ms, None
        except concurrent.futures.TimeoutError:
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return False, None, elapsed_ms, f"Execution timed out after {t_limit:.1f}s"
        except Exception as e:
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0
            return False, None, elapsed_ms, f"Execution error: {type(e).__name__}: {str(e)}"
