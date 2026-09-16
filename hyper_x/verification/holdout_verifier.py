"""
hyper_x/verification/holdout_verifier.py
========================================
Phase 1: Holdout Generalization Verifier.
Validates candidate on strictly unseen, disjoint out-of-distribution datasets.
Candidate is NEVER tuned against the final holdout set.
Fail-closed default: passed = False.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class HoldoutVerificationResult:
    passed: bool = False  # Fail-closed default
    samples_evaluated: int = 0
    generalization_gap: float = float("inf")
    violations: List[str] = field(default_factory=list)


class HoldoutVerifier:
    """
    Evaluates candidate on unseen holdout distributions to measure generalization bounds.
    """

    @classmethod
    def verify(
        cls,
        candidate_fn: Callable[[Any], Any],
        reference_fn: Callable[[Any], Any],
        holdout_dataset: List[Any],
        comparator: Callable[[Any, Any], bool],
    ) -> HoldoutVerificationResult:
        if not holdout_dataset:
            return HoldoutVerificationResult(passed=False, violations=["Holdout dataset empty"])

        successes = 0
        violations = []

        for idx, sample in enumerate(holdout_dataset):
            try:
                ref_out = reference_fn(sample)
                cand_out = candidate_fn(sample)
                if comparator(cand_out, ref_out):
                    successes += 1
                else:
                    violations.append(f"Holdout sample {idx} failed equivalence")
            except Exception as e:
                violations.append(f"Holdout sample {idx} error: {str(e)}")

        pass_rate = successes / max(1, len(holdout_dataset))
        gen_gap = round(1.0 - pass_rate, 4)
        passed = (successes == len(holdout_dataset))

        return HoldoutVerificationResult(
            passed=passed,
            samples_evaluated=len(holdout_dataset),
            generalization_gap=gen_gap,
            violations=violations,
        )
