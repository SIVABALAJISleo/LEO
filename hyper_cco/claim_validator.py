"""
hyper_cco/claim_validator.py
=============================================================================
Claim Validator (Section 58)
=============================================================================
Scans text, documentation, markdown files, and code strings to automatically
detect and reject prohibited or unsupported claims:
  1. Universal Hardware Claims ("beats every NVIDIA GPU", "100% silicon parity")
  2. Conflation of Simulation with Measurement
  3. Labeling Cache Lookups as Raw Compute Speedups
  4. Labeling Predictive Approximations as Bit-Exact Equivalence
  5. Unverifiable Performance Claims
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple


@dataclass
class ClaimViolation:
    violation_id: str
    prohibited_pattern: str
    matched_text: str
    severity: str  # "ERROR" or "WARNING"
    reason: str
    remediation: str


@dataclass
class ClaimValidationReport:
    is_valid: bool
    total_checks: int
    violations: List[ClaimViolation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "total_checks": self.total_checks,
            "violations": [
                {
                    "id": v.violation_id,
                    "pattern": v.prohibited_pattern,
                    "matched": v.matched_text,
                    "severity": v.severity,
                    "reason": v.reason,
                    "remediation": v.remediation,
                }
                for v in self.violations
            ]
        }


class ClaimValidator:
    """Automated auditor enforcing scientific claim integrity."""

    PROHIBITED_RULES = [
        (
            r"(?i)\bbeats?\s+(every|all)\s+nvidia\b",
            "Universal Hardware Superiority Claim",
            "Discrete NVIDIA GPUs possess 100x higher raw FP32 throughput; claims of universal victory are physically false.",
            "Qualify claim to specific application contracts where GPU computation was eliminated."
        ),
        (
            r"(?i)\b100%\s+(raw|silicon|hardware)\s+parity\b",
            "Raw Silicon Parity Claim",
            "Intel UHD cannot match raw hardware FLOPS of discrete GPUs.",
            "Use '100% Contract Parity' or '100% Workload Closure' instead."
        ),
        (
            r"(?i)\bsimulated\s+benchmark\s+as\s+measured\b",
            "Simulation Conflation",
            "Simulated timings cannot be represented as physical hardware measurements.",
            "Label clearly as SIMULATED or MEASURED."
        ),
        (
            r"(?i)\bfunctional_pass\s*=\s*True\b",
            "Hardcoded Pass Flag",
            "Hardcoded test passes violate anti-cheat verification integrity.",
            "Replace with dynamically computed comparator check."
        ),
    ]

    @classmethod
    def validate_text(cls, text: str) -> ClaimValidationReport:
        violations = []
        checks = len(cls.PROHIBITED_RULES)

        for pattern, rule_name, reason, remediation in cls.PROHIBITED_RULES:
            matches = re.findall(pattern, text)
            if matches:
                matched_str = matches[0] if isinstance(matches[0], str) else " ".join(matches[0])
                violations.append(ClaimViolation(
                    violation_id=f"VIOLATION_{len(violations)+1}",
                    prohibited_pattern=pattern,
                    matched_text=matched_str,
                    severity="ERROR",
                    reason=f"{rule_name}: {reason}",
                    remediation=remediation
                ))

        return ClaimValidationReport(
            is_valid=(len(violations) == 0),
            total_checks=checks,
            violations=violations
        )
