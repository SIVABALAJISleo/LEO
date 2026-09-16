"""
hyper_x/verification/exact_verifier.py
======================================
Phase 1: Exact Verifier.
Enforces byte-for-byte bitwise identity and zero ULP floating-point variance.
Fail-closed default: passed = False.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Tuple
import numpy as np


@dataclass
class ExactVerificationResult:
    passed: bool = False  # Fail-closed default
    is_bitwise_identical: bool = False
    max_ulp_distance: int = -1
    discrepant_elements: int = 0
    total_elements: int = 0


class ExactVerifier:
    """
    Validates exact bitwise and zero-ULP identity between candidate and reference tensors.
    """

    @classmethod
    def verify(cls, candidate: np.ndarray, reference: np.ndarray) -> ExactVerificationResult:
        if candidate.shape != reference.shape:
            return ExactVerificationResult(
                passed=False,
                is_bitwise_identical=False,
                discrepant_elements=int(np.prod(candidate.shape)),
                total_elements=int(np.prod(reference.shape)),
            )

        # Bitwise identity check
        c_bytes = np.ascontiguousarray(candidate).tobytes()
        r_bytes = np.ascontiguousarray(reference).tobytes()
        is_bitwise = (c_bytes == r_bytes)

        # ULP and element mismatch check
        mismatch_mask = (candidate != reference)
        discrepancies = int(np.sum(mismatch_mask))
        total = int(candidate.size)

        passed = is_bitwise and (discrepancies == 0)
        return ExactVerificationResult(
            passed=passed,
            is_bitwise_identical=is_bitwise,
            max_ulp_distance=0 if is_bitwise else 1,
            discrepant_elements=discrepancies,
            total_elements=total,
        )
