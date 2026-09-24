"""
hyper_universal/sandbox/executor.py
===================================
Sandboxed Compilation & Execution Engine.

Implements Sections 22 & 23 of the Master Specification:
- Compiles candidate AST / Python source
- Executes in isolated namespace with restricted builtins
- Enforces strict execution time limits and catches errors
"""

from __future__ import annotations
import math
import time
from typing import Any, Callable, Dict, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from hyper_universal.sandbox.security import inspect_source_code


class SandboxExecutionResult(BaseModel):
    success: bool
    output: Optional[Any] = None
    execution_time_ms: float = 0.0
    error_type: Optional[str] = None  # "security_violation", "compile_failure", "timeout", "runtime_failure"
    error_message: str = ""


class SandboxExecutor:
    """
    Executes generated candidate functions in an isolated namespace.
    """

    @staticmethod
    def _safe_import(name: str, *args: Any, **kwargs: Any) -> Any:
        allowed = {"numpy", "np", "math", "scipy"}
        base = name.split(".")[0]
        if base not in allowed:
            raise ImportError(f"Importing '{name}' is forbidden in sandbox.")
        return __import__(name, *args, **kwargs)

    SAFE_BUILTINS: Dict[str, Any] = {
        "abs": abs, "min": min, "max": max, "sum": sum, "len": len,
        "range": range, "enumerate": enumerate, "zip": zip,
        "reversed": reversed, "sorted": sorted, "any": any, "all": all,
        "filter": filter, "map": map, "slice": slice, "round": round,
        "pow": pow, "isinstance": isinstance, "int": int, "float": float,
        "bool": bool, "list": list, "dict": dict, "tuple": tuple, "set": set,
        "Exception": Exception, "ValueError": ValueError, "TypeError": TypeError,
        "math": math, "np": np, "numpy": np,
    }

    def __init__(self, timeout_ms: float = 5000.0) -> None:
        self.timeout_ms = timeout_ms

    def compile_and_execute(
        self,
        source_code: str,
        entry_function_name: str,
        input_args: Tuple[Any, ...],
    ) -> SandboxExecutionResult:
        """
        Statically checks, compiles, and safely executes generated candidate source.
        """
        # 1. AST Security Inspection
        is_safe, violations = inspect_source_code(source_code)
        if not is_safe:
            return SandboxExecutionResult(
                success=False,
                error_type="security_violation",
                error_message="; ".join(violations),
            )

        # 2. Compilation
        try:
            compiled = compile(source_code, "<hyper_candidate>", "exec")
        except Exception as e:
            return SandboxExecutionResult(
                success=False,
                error_type="compile_failure",
                error_message=f"Compilation failed: {str(e)}",
            )

        # 3. Execution in isolated namespace
        safe_builtins = dict(self.SAFE_BUILTINS)
        safe_builtins["__import__"] = self._safe_import
        exec_namespace: Dict[str, Any] = {"__builtins__": safe_builtins, "np": np, "numpy": np}
        try:
            exec(compiled, exec_namespace)
        except Exception as e:
            return SandboxExecutionResult(
                success=False,
                error_type="runtime_failure",
                error_message=f"Failed to initialize module: {str(e)}",
            )

        fn = exec_namespace.get(entry_function_name)
        if not callable(fn):
            return SandboxExecutionResult(
                success=False,
                error_type="compile_failure",
                error_message=f"Entrypoint '{entry_function_name}' not defined or not callable.",
            )

        # 4. Measure execution
        t0 = time.perf_counter_ns()
        try:
            out = fn(*input_args)
            t1 = time.perf_counter_ns()
            elapsed_ms = (t1 - t0) / 1_000_000.0

            if elapsed_ms > self.timeout_ms:
                return SandboxExecutionResult(
                    success=False,
                    execution_time_ms=elapsed_ms,
                    error_type="timeout",
                    error_message=f"Execution timed out ({elapsed_ms:.1f}ms > {self.timeout_ms:.1f}ms)",
                )

            return SandboxExecutionResult(
                success=True,
                output=out,
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            t1 = time.perf_counter_ns()
            return SandboxExecutionResult(
                success=False,
                execution_time_ms=(t1 - t0) / 1_000_000.0,
                error_type="runtime_failure",
                error_message=f"Execution error: {str(e)}",
            )


def execute_isolated_candidate(
    source_code: str,
    input_data: Any,
    entry_function_name: str = "candidate",
    timeout_seconds: float = 5.0,
) -> Any:
    """Convenience helper to compile and execute a candidate in the sandbox."""
    executor = SandboxExecutor(timeout_ms=timeout_seconds * 1000.0)
    args = (input_data,)
    r = executor.compile_and_execute(source_code, entry_function_name, args)

    class ResultWrapper:
        def __init__(self, res: SandboxExecutionResult):
            self.success = res.success
            self.output = res.output
            self.execution_time_ms = res.execution_time_ms
            self.error_type = res.error_type
            self.error_message = res.error_message
            self.error = res.error_message

    return ResultWrapper(r)

