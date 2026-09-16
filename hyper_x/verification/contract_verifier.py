"""
hyper_x/verification/contract_verifier.py
=========================================
Phase 1: Contract Verifier.
Validates that candidate execution strictly complies with the immutable WorkloadContract.
Fail-closed default: passed = False.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List
from hyper_x.contract import WorkloadContract


@dataclass
class ContractVerificationResult:
    passed: bool = False  # Fail-closed default
    violations: List[str] = field(default_factory=list)
    contract_hash: str = ""


class ContractVerifier:
    """
    Validates execution telemetry and outputs against an immutable WorkloadContract.
    """

    @classmethod
    def verify(
        cls,
        contract: WorkloadContract,
        telemetry: Dict[str, Any],
        output: Any,
    ) -> ContractVerificationResult:
        violations: List[str] = []

        # Check external compute constraint
        if not contract.external_compute_allowed:
            if telemetry.get("external_compute_used", False):
                violations.append("Violation: External compute detected when forbidden by contract")

        # Check cache constraint
        if not contract.cache_allowed:
            if telemetry.get("cache_hit", False):
                violations.append("Violation: Cache hit utilized when forbidden by contract")

        # Check precomputation constraint
        if not contract.precomputation_allowed:
            if telemetry.get("precomputed_used", False):
                violations.append("Violation: Precomputed tables utilized when forbidden by contract")

        # Check approximation constraint
        if not contract.approximation_allowed:
            if telemetry.get("is_approximate", False):
                violations.append("Violation: Approximation used when exact execution required")

        # Check memory bounds
        peak_mb = telemetry.get("peak_memory_mb", 0.0)
        if peak_mb > contract.memory_limit_mb:
            violations.append(f"Violation: Peak memory ({peak_mb} MB) exceeded limit ({contract.memory_limit_mb} MB)")

        passed = len(violations) == 0
        return ContractVerificationResult(
            passed=passed,
            violations=violations,
            contract_hash=contract.compute_contract_hash(),
        )
