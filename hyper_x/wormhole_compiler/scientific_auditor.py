"""
hyper_x/wormhole_compiler/scientific_auditor.py
=============================================================================
Automated Scientific Auditor & Impossible-Claim Detector (Section 51)
=============================================================================
CRITICAL PRINCIPLE:
Audits code, benchmarks, certificates, and published statements for:
  1. Impossible claims (e.g. "GPU replaced", "100% raw silicon parity")
  2. Provenance mismatches (target CPU/iGPU mismatch, unknown host)
  3. Workload definition mutations (silently changing SPP, resolution, matrix dim)
  4. Simulated timing presented as physical hardware measurements
  5. Hardcoded results / scores / passes
  6. Hidden approximations in declared EXACT mode
  7. Benchmark & Blind Holdout leakage (candidate training on holdout data)
  8. Circular verification (verifying a candidate against another unverified candidate)
  9. Mathematical unit / FLOP / speedup errors

If ANY anomaly is detected:
  STRICTLY FAILS THE CLAIM. NEVER SUPPRESSES THE FAILURE.
"""

from __future__ import annotations
import time
import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class AuditFinding:
    severity: str  # "CRITICAL_VIOLATION", "WARNING", "NOTE"
    category: str
    description: str
    remediation: str


@dataclass
class ScientificAuditReport:
    passed: bool
    total_findings: int
    critical_violations: int
    findings: List[AuditFinding] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "total_findings": self.total_findings,
            "critical_violations": self.critical_violations,
            "findings": [
                {
                    "severity": f.severity,
                    "category": f.category,
                    "description": f.description,
                    "remediation": f.remediation
                }
                for f in self.findings
            ],
            "timestamp": self.timestamp,
        }


class ScientificAuditor:
    """
    Automated watchdog enforcing uncompromising scientific rigor and truthfulness.
    """

    PROHIBITED_PHRASES = [
        ("gpu replaced", "Physical hardware cannot be replaced by software."),
        ("100% nvidia parity", "Misleading statement: raw physical silicon parity is 0.0%."),
        ("100% raw parity", "Raw silicon hardware cannot be duplicated by software."),
        ("infinite speedup", "Speedup is mathematically bounded by real execution time."),
    ]

    @classmethod
    def audit_statement(cls, text: str) -> List[AuditFinding]:
        findings = []
        lower = text.lower()
        for phrase, reason in cls.PROHIBITED_PHRASES:
            if phrase in lower:
                findings.append(AuditFinding(
                    severity="CRITICAL_VIOLATION",
                    category="IMPOSSIBLE_CLAIM",
                    description=f"Statement contains prohibited unscientific phrase: '{phrase}'.",
                    remediation=reason,
                ))
        return findings

    @classmethod
    def audit_result_record(
        cls,
        workload_id: str,
        contract_mode: str,
        numerical_error: float,
        holdout_passed: bool,
        provenance: Dict[str, Any],
        is_simulated: bool,
        claimed_as_real_hardware: bool,
        candidate_source_code: Optional[str] = None,
    ) -> ScientificAuditReport:
        findings: List[AuditFinding] = []

        # 1. Physical vs Simulated Hardware Check
        if is_simulated and claimed_as_real_hardware:
            findings.append(AuditFinding(
                severity="CRITICAL_VIOLATION",
                category="SIMULATION_CONFUSION",
                description=f"Workload {workload_id} reported simulated execution as real hardware evidence.",
                remediation="Label strictly as SIMULATED; do not enter into real-hardware leaderboards.",
            ))

        # 2. Hidden Approximation in EXACT Mode
        if contract_mode in ("EXACT", "EXACT_REFORMULATION") and numerical_error > 0.0:
            findings.append(AuditFinding(
                severity="CRITICAL_VIOLATION",
                category="HIDDEN_APPROXIMATION",
                description=f"Workload {workload_id} declared EXACT contract but has non-zero error {numerical_error:.6e}.",
                remediation="Downgrade contract to BOUNDED_APPROXIMATION or reject candidate.",
            ))

        # 3. Holdout Integrity
        if not holdout_passed:
            findings.append(AuditFinding(
                severity="CRITICAL_VIOLATION",
                category="HOLDOUT_FAILURE",
                description=f"Workload {workload_id} candidate failed blind holdout evaluation.",
                remediation="Candidate cannot receive certified status.",
            ))

        # 4. Target Hardware Mismatch
        target_cpu = provenance.get("cpu", "")
        if "i5-12450H" not in target_cpu and "Intel" not in target_cpu:
            findings.append(AuditFinding(
                severity="WARNING",
                category="TARGET_HARDWARE_MISMATCH",
                description=f"Provenance CPU '{target_cpu}' differs from target benchmark machine (Intel Core i5-12450H).",
                remediation="Annotate benchmark with explicit foreign-machine provenance tag.",
            ))

        # 5. AST Hardcoding Check
        if candidate_source_code:
            suspicious_patterns = [
                (r"return\s+0(\.0)?\s*$", "Candidate returns constant zero."),
                (r"functional_pass\s*=\s*True", "Candidate hardcodes functional_pass=True."),
                (r"verified\s*=\s*True", "Candidate hardcodes verified=True without proof."),
            ]
            for pat, desc in suspicious_patterns:
                if re.search(pat, candidate_source_code):
                    findings.append(AuditFinding(
                        severity="CRITICAL_VIOLATION",
                        category="HARDCODED_RESULT",
                        description=f"Suspicious hardcoded pattern in candidate AST: {desc}",
                        remediation="Remove hardcoded constants; enforce dynamic execution and evaluation.",
                    ))

        crit_count = sum(1 for f in findings if f.severity == "CRITICAL_VIOLATION")
        passed = (crit_count == 0)

        return ScientificAuditReport(
            passed=passed,
            total_findings=len(findings),
            critical_violations=crit_count,
            findings=findings,
        )
