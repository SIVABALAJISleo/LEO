"""
hyper/universal/verification/verifier.py
========================================
Universal Multi-Strategy Independent Verifier.
Orchestrates independent checking across:
- Exact bitwise checking
- Differential relative/absolute bounds
- Freivalds O(k N^2) randomized matrix checks
- Structural invariant checking
Enforces: Zero Self-Confirmation. Candidate output is strictly verified against external reference.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .schema import UniversalVerificationResult, VerificationState, ScientificOutcome
from .exact_checker import ExactChecker
from .differential_checker import DifferentialChecker
from .freivalds import FreivaldsVerifier
from .invariant_checker import InvariantChecker
from ..contracts.universal_contract import UniversalContract


class UniversalVerifier:
    """Master independent verification engine."""

    @staticmethod
    def verify(
        candidate_output: Any,
        reference_output: Any,
        contract: UniversalContract,
        extra_inputs: Optional[Tuple[Any, ...]] = None,
    ) -> UniversalVerificationResult:
        method = contract.verification_method.upper()

        # 1. Freivalds check if specified or if matrix multiplication inputs are provided
        if method == "FREIVALDS" or (extra_inputs and len(extra_inputs) == 2 and isinstance(candidate_output, np.ndarray) and candidate_output.ndim == 2):
            if extra_inputs and len(extra_inputs) == 2:
                A, B = extra_inputs[0], extra_inputs[1]
                if isinstance(A, np.ndarray) and isinstance(B, np.ndarray) and A.ndim == 2 and B.ndim == 2:
                    return FreivaldsVerifier.verify(A, B, candidate_output, tolerance=contract.numeric_tolerance)

        # 2. Invariant checking
        if "INVARIANT" in method or "SORT" in contract.contract_id.upper():
            if isinstance(candidate_output, np.ndarray) and candidate_output.ndim == 1:
                v_inv = InvariantChecker.verify_sorted_monotonic(candidate_output)
                if not v_inv.is_valid:
                    return v_inv
                if reference_output is not None:
                    return InvariantChecker.verify_permutation(candidate_output, reference_output)
                return v_inv

        # 3. Exact bitwise check
        if contract.is_exact():
            return ExactChecker.verify(candidate_output, reference_output, contract)

        # 4. Differential numerical bounds
        return DifferentialChecker.verify(candidate_output, reference_output, contract)
