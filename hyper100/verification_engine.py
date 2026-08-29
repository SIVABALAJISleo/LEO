"""
hyper100/verification_engine.py
===============================
Mathematical Verification Engine.
Validates transformed and optimized computational outputs against declared contracts,
calculating exact absolute error, relative Frobenius error, residual bounds, and perceptual metrics.
"""

from typing import Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass
import numpy as np

from .contract_engine import ExecutionContract, VerificationStatus, ContractExactness


@dataclass
class VerificationReport:
    """Complete mathematical audit of an execution result."""
    status: VerificationStatus
    is_valid: bool
    absolute_error_max: float
    relative_error_norm: float
    psnr_db: float
    ssim: float
    residual_norm: float
    passed_invariants: bool
    diagnostic_details: str


class VerificationEngine:
    """Executes formal verification checks on computed outputs."""

    @staticmethod
    def verify(
        candidate: Any,
        baseline: Optional[Any],
        contract: ExecutionContract,
        invariants_fn: Optional[Any] = None
    ) -> VerificationReport:
        """
        Validates candidate against baseline and contract rules.
        """
        # 1. Base validation
        valid, status, metrics = contract.validate_output(candidate, baseline)

        # 2. Invariant verification
        passed_inv = True
        diag = "Verification passed successfully"
        res_norm = 0.0

        if invariants_fn is not None:
            try:
                passed_inv, res_norm = invariants_fn(candidate)
                if not passed_inv:
                    valid = False
                    status = VerificationStatus.VIOLATION
                    diag = f"Invariant check failed (residual={res_norm:.2e})"
            except Exception as e:
                passed_inv = False
                valid = False
                status = VerificationStatus.VIOLATION
                diag = f"Invariant evaluation error: {e}"

        if not valid:
            diag = metrics.get("violation_reason", "Contract constraint violated")

        return VerificationReport(
            status=status,
            is_valid=valid,
            absolute_error_max=metrics.get("error_l_inf", 0.0),
            relative_error_norm=metrics.get("error_relative", 0.0),
            psnr_db=metrics.get("psnr_db", float("inf")),
            ssim=metrics.get("ssim", 1.0),
            residual_norm=res_norm,
            passed_invariants=passed_inv,
            diagnostic_details=diag
        )
