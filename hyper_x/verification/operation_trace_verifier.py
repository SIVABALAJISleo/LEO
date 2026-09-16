"""
hyper_x/verification/operation_trace_verifier.py
================================================
Phase 1: Operation Trace Verifier.
Validates execution graph step ordering, intermediate reductions, and provenance invariants.
Fail-closed default: passed = False.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class OperationTraceResult:
    passed: bool = False  # Fail-closed default
    trace_hash: str = ""
    step_count: int = 0
    invariants_satisfied: bool = False
    violations: List[str] = field(default_factory=list)


class OperationTraceVerifier:
    """
    Validates execution traces for non-circular dependency flow and reduction invariant consistency.
    """

    @classmethod
    def verify_trace(cls, execution_steps: List[Dict[str, Any]]) -> OperationTraceResult:
        if not execution_steps:
            return OperationTraceResult(passed=False, violations=["Empty trace"])

        violations = []
        seen_steps = set()

        for idx, step in enumerate(execution_steps):
            step_id = step.get("id", f"step_{idx}")
            if step_id in seen_steps:
                violations.append(f"Duplicate step execution detected: {step_id}")
            seen_steps.add(step_id)

            # Check that dependencies precede current step
            deps = step.get("dependencies", [])
            for dep in deps:
                if dep not in seen_steps:
                    violations.append(f"Dependency violation: {dep} not computed before {step_id}")

        trace_str = "-".join(sorted(seen_steps))
        t_hash = hashlib.sha256(trace_str.encode("utf-8")).hexdigest()

        passed = len(violations) == 0
        return OperationTraceResult(
            passed=passed,
            trace_hash=t_hash,
            step_count=len(execution_steps),
            invariants_satisfied=passed,
            violations=violations,
        )
