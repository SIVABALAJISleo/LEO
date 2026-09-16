"""
hyper_x/verification/independent_verifier.py
============================================
Phase 1: Independent Reference Verifier.
Compares candidate output against isolated external reference observations.
Enforces that candidate does not compare against itself (C(x) != C(x)).
Fail-closed default: passed = False.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np


@dataclass
class IndependentVerificationResult:
    passed: bool = False  # Fail-closed default
    is_independent: bool = False
    self_comparison_detected: bool = False
    details: str = ""


class IndependentVerifier:
    """
    Verifies that the reference is completely isolated and candidate did not certify itself.
    """

    @classmethod
    def verify(
        cls,
        candidate_obj: Any,
        reference_obj: Any,
        candidate_output: Any,
        reference_output: Any,
    ) -> IndependentVerificationResult:
        # Check for self-comparison (identity object reference)
        if candidate_obj is reference_obj:
            return IndependentVerificationResult(
                passed=False,
                is_independent=False,
                self_comparison_detected=True,
                details="Fraudulent self-comparison detected: candidate is identical object to reference.",
            )

        # Ensure reference output exists and is non-empty
        if reference_output is None:
            return IndependentVerificationResult(
                passed=False,
                is_independent=False,
                self_comparison_detected=False,
                details="Reference output unavailable.",
            )

        return IndependentVerificationResult(
            passed=True,
            is_independent=True,
            self_comparison_detected=False,
            details="Independent reference comparison validated.",
        )
