"""
hyper/escape_engine/verification/verifier.py
============================================
VAEE Master Multi-Strategy Independent Verifier.

Coordinates Exact, Differential, Invariant, and Checksum verification strategies.
Ensures zero false positives and independent correctness validation.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np

from .schema import VerificationOutcome, VerificationTrustLevel
from .exact_verifier import ExactVerifier
from .differential_verifier import DifferentialVerifier
from .invariant_verifier import InvariantVerifier
from .checksum_verifier import ChecksumVerifier
from ..contracts.schema import ComputationalContract


class MasterVerifier:
    """Independent multi-strategy verification engine."""

    def __init__(self) -> None:
        self.exact = ExactVerifier()
        self.differential = DifferentialVerifier()
        self.invariant = InvariantVerifier()
        self.checksum = ChecksumVerifier()

    def verify_candidate(
        self,
        candidate_output: Any,
        reference_output: Any,
        contract: ComputationalContract,
        extra_inputs: Optional[Any] = None,
    ) -> VerificationOutcome:
        """
        Verify candidate output against contract specifications using the appropriate verifier.
        """
        method = contract.verification_method

        if method == "FREIVALDS" and isinstance(extra_inputs, tuple) and len(extra_inputs) == 2:
            A, B = extra_inputs
            return self.checksum.verify_freivalds_gemm(
                A, B, candidate_output,
                tolerance=contract.numeric_tolerance,
            )

        elif method == "INVARIANT_SORTED":
            return self.invariant.verify_sorting_invariant(candidate_output)

        elif method == "EXACT":
            return self.exact.verify(candidate_output, reference_output)

        else:
            # Default to differential verification
            return self.differential.verify(candidate_output, reference_output, contract)
