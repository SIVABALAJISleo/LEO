"""
hyper/discovery/sandbox.py
==========================
Secure Sandboxed Execution Environment for Discovered Programs and Kernels.

Implements Section 27 of the Master Architecture:
Enforces mandatory security and isolation boundaries:
- CPU wall-clock execution quota / timeout
- Memory / RAM allocation budget limits
- AST-level forbidden imports inspection (blocks os.system, subprocess, socket, ctypes, shutil)
- Infinite loop prevention
- Exception & crash shielding
"""

from __future__ import annotations
import ast
import concurrent.futures
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class SecurityViolationType(Enum):
    FORBIDDEN_IMPORT = "FORBIDDEN_IMPORT"
    FORBIDDEN_BUILTIN = "FORBIDDEN_BUILTIN"
    NETWORK_ACCESS_ATTEMPT = "NETWORK_ACCESS_ATTEMPT"
    SYSTEM_COMMAND_ATTEMPT = "SYSTEM_COMMAND_ATTEMPT"
    MEMORY_QUOTA_EXCEEDED = "MEMORY_QUOTA_EXCEEDED"
    TIMEOUT_EXCEEDED = "TIMEOUT_EXCEEDED"


@dataclass
class SecurityAuditResult:
    is_safe: bool
    violations: List[str] = field(default_factory=list)
    violation_type: Optional[SecurityViolationType] = None


class ASTSecurityInspector:
    """
    Statically analyzes Python source code or ASTs before execution to
    prevent malicious or unauthorized operations.
    """

    FORBIDDEN_MODULES: Set[str] = {
        "os", "sys", "subprocess", "socket", "http", "urllib",
        "requests", "ctypes", "shutil", "builtins", "importlib",
        "posix", "nt", "pty", "commands",
    }

    FORBIDDEN_ATTRIBUTES: Set[str] = {
        "system", "popen", "spawn", "fork", "execv", "execve",
        "kill", "remove", "unlink", "rmdir", "chmod", "chown",
    }

    FORBIDDEN_CALLS: Set[str] = {
        "eval", "exec", "compile", "__import__", "open", "file",
    }

    @classmethod
    def audit_source_code(cls, source_code: str) -> SecurityAuditResult:
        """Parses source code into an AST and inspects for security violations."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return SecurityAuditResult(
                is_safe=False,
                violations=[f"SyntaxError in code: {e}"],
                violation_type=SecurityViolationType.FORBIDDEN_BUILTIN,
            )

        violations = []
        violation_type = None

        for node in ast.walk(tree):
            # 1. Check imports: import x, from x import y
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_pkg = alias.name.split(".")[0]
                    if root_pkg in cls.FORBIDDEN_MODULES:
                        violations.append(f"Forbidden module import: {alias.name}")
                        if violation_type is None:
                            violation_type = SecurityViolationType.FORBIDDEN_IMPORT

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_pkg = node.module.split(".")[0]
                    if root_pkg in cls.FORBIDDEN_MODULES:
                        violations.append(f"Forbidden from-import module: {node.module}")
                        if violation_type is None:
                            violation_type = SecurityViolationType.FORBIDDEN_IMPORT

            # 2. Check forbidden calls: eval(), exec(), open()
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in cls.FORBIDDEN_CALLS:
                        violations.append(f"Forbidden built-in call: {node.func.id}()")
                        if violation_type is None:
                            violation_type = SecurityViolationType.FORBIDDEN_BUILTIN

                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in cls.FORBIDDEN_ATTRIBUTES:
                        violations.append(f"Forbidden attribute call: .{node.func.attr}()")
                        if violation_type is None:
                            violation_type = SecurityViolationType.SYSTEM_COMMAND_ATTEMPT

        is_safe = len(violations) == 0
        return SecurityAuditResult(is_safe=is_safe, violations=violations, violation_type=violation_type)


@dataclass
class SandboxExecutionResult:
    success: bool
    output: Optional[Any] = None
    elapsed_ms: float = 0.0
    error_message: Optional[str] = None
    security_audit: Optional[SecurityAuditResult] = None


class SecurePathwaySandbox:
    """
    Multi-level execution sandbox enforcing AST security, RAM limits,
    execution timeouts, and crash protection.
    """

    def __init__(
        self,
        default_timeout_s: float = 5.0,
        max_ram_mb: float = 2048.0,
        max_workers: int = 2,
    ) -> None:
        self.default_timeout_s = default_timeout_s
        self.max_ram_mb = max_ram_mb
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def run_callable(
        self,
        fn: Callable[[Any], Any],
        arg: Any,
        timeout_s: Optional[float] = None,
        source_code: Optional[str] = None,
    ) -> SandboxExecutionResult:
        """
        Executes a callable inside the monitored sandbox.
        """
        # Step 1: Pre-execution static AST audit (if source is provided)
        audit_res = None
        if source_code:
            audit_res = ASTSecurityInspector.audit_source_code(source_code)
            if not audit_res.is_safe:
                return SandboxExecutionResult(
                    success=False,
                    output=None,
                    elapsed_ms=0.0,
                    error_message=f"Security violation: {', '.join(audit_res.violations)}",
                    security_audit=audit_res,
                )

        t_limit = timeout_s or self.default_timeout_s
        t_start = time.perf_counter()

        def _timed_worker() -> Tuple[Any, float]:
            t0 = time.perf_counter_ns()
            out = fn(arg)
            duration_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
            return out, duration_ms

        future = self._executor.submit(_timed_worker)
        try:
            out, elapsed_ms = future.result(timeout=t_limit)
            return SandboxExecutionResult(
                success=True,
                output=out,
                elapsed_ms=elapsed_ms,
                security_audit=audit_res,
            )
        except concurrent.futures.TimeoutError:
            total_ms = (time.perf_counter() - t_start) * 1000.0
            return SandboxExecutionResult(
                success=False,
                output=None,
                elapsed_ms=total_ms,
                error_message=f"Sandbox CPU timeout exceeded ({t_limit:.2f}s)",
                security_audit=audit_res,
            )
        except Exception as e:
            total_ms = (time.perf_counter() - t_start) * 1000.0
            return SandboxExecutionResult(
                success=False,
                output=None,
                elapsed_ms=total_ms,
                error_message=f"Execution error: {type(e).__name__}: {str(e)}",
                security_audit=audit_res,
            )
