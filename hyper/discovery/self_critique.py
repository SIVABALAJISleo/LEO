"""
hyper/discovery/self_critique.py
================================
Self-Critique Engine for UCTDE.

Attempts to disprove and scrutinize HYPER's own discovery claims:
  1. Did we silently alter the contract?
  2. Did we downsample the workload?
  3. Did we accidentally use cached data?
  4. Did we overfit to a benchmark-specific dimension?
  5. Was verification genuinely independent?
  6. Did it survive adversarial counterexample attacks?
  7. Is the measurement statistically reproducible (low variance)?
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SelfCritiqueReport(BaseModel):
    passed_all_scrutiny: bool
    risk_score: float                         # 0.0 (pristine) to 1.0 (contaminated)
    checks: Dict[str, bool] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    verdict: str                              # "RIGOROUS_DISCOVERY_CONFIRMED" or "POTENTIAL_CONTAMINATION"
    timestamp: float = Field(default_factory=float)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class SelfCritiqueEngine:
    """
    Hostile auditor that evaluates candidate improvements against falsification criteria.
    """

    def audit_discovery(
        self,
        contract_exactness: str,
        observed_error: float,
        allowed_tolerance: float,
        is_independent_verifier: bool,
        is_cache_flushed: bool,
        adversarial_counterexample_found: bool,
        trials_variance_ratio: float,          # std / mean
        dimension_generalized: bool,
    ) -> SelfCritiqueReport:
        checks: Dict[str, bool] = {}
        warnings: List[str] = []
        risk: float = 0.0

        # Check 1: Contract integrity
        contract_preserved = observed_error <= allowed_tolerance
        checks["contract_integrity"] = contract_preserved
        if not contract_preserved:
            warnings.append(f"Observed error {observed_error:.2e} exceeded contract tolerance {allowed_tolerance:.2e}.")
            risk += 0.40

        # Check 2: Cache independence (anti-cheating)
        checks["cache_cleanliness"] = is_cache_flushed
        if not is_cache_flushed:
            warnings.append("Cache was not explicitly flushed; speedup may reflect memory memoization.")
            risk += 0.25

        # Check 3: Independent verification
        checks["independent_verification"] = is_independent_verifier
        if not is_independent_verifier:
            warnings.append("Verification was self-reported; lacks independent multi-checker audit.")
            risk += 0.30

        # Check 4: Adversarial survival
        adversarial_survived = not adversarial_counterexample_found
        checks["adversarial_resilience"] = adversarial_survived
        if not adversarial_survived:
            warnings.append("An adversarial counterexample was discovered that breaks the candidate.")
            risk += 0.50

        # Check 5: Statistical reproducibility
        reproducible = trials_variance_ratio < 0.20
        checks["measurement_reproducibility"] = reproducible
        if not reproducible:
            warnings.append(f"High measurement variance (std/mean = {trials_variance_ratio:.2f} > 0.20).")
            risk += 0.15

        # Check 6: Dimension generalization
        checks["dimension_generalized"] = dimension_generalized
        if not dimension_generalized:
            warnings.append("Tested only on single fixed dimension; generality unverified.")
            risk += 0.10

        risk = min(1.0, risk)
        passed_all = (risk < 0.20) and contract_preserved and adversarial_survived and is_independent_verifier

        verdict = "RIGOROUS_DISCOVERY_CONFIRMED" if passed_all else "POTENTIAL_CONTAMINATION_DETECTED"

        return SelfCritiqueReport(
            passed_all_scrutiny=passed_all,
            risk_score=risk,
            checks=checks,
            warnings=warnings,
            verdict=verdict,
        )
