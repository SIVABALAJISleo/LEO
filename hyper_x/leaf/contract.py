"""
hyper_x/leaf/contract.py
========================
Application Contract and Error Tolerance Specification for LEAF Engine.

Under the LEAF doctrine, the computational pathway is bounded strictly by
what the application contract demands:
- Exact contracts require exact mathematical parity (epsilon = 0 or relative diff <= 1e-7).
- Bounded contracts specify maximum allowable error (e.g. epsilon <= 1e-4).
- Perceptual contracts specify perceptual metrics (e.g. PSNR >= 40dB, SSIM >= 0.98).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np


class ContractTier(str, Enum):
    EXACT = "EXACT"                              # Zero mathematical tolerance
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"  # Machine epsilon tolerance (<= 1e-6)
    BOUNDED_APPROXIMATION = "BOUNDED_APPROXIMATION"    # Explicit delta bound (<= 1e-4)
    PERCEPTUAL_APPROXIMATION = "PERCEPTUAL_APPROXIMATION"  # PSNR / SSIM / LPIPS
    PREDICTIVE = "PREDICTIVE"                    # Statistical / heuristic with verifier fallback


@dataclass(frozen=True)
class LeafContract:
    """Formal contract specification for a computation."""
    name: str
    tier: ContractTier = ContractTier.EXACT
    max_relative_error: float = 1e-6
    max_absolute_error: float = 1e-6
    min_psnr_db: Optional[float] = None
    min_ssim: Optional[float] = None
    max_latency_ms: Optional[float] = None
    enforce_fail_closed: bool = True

    def validate(
        self,
        candidate_output: np.ndarray,
        reference_output: np.ndarray,
    ) -> Tuple[bool, float, str]:
        """
        Validates candidate output against reference output under this contract.
        Returns: (is_valid, measured_error, reason)
        """
        if candidate_output.shape != reference_output.shape:
            return False, 1.0, f"Shape mismatch: {candidate_output.shape} vs {reference_output.shape}"

        ref_norm = np.linalg.norm(reference_output)
        diff_norm = np.linalg.norm(candidate_output - reference_output)

        if ref_norm > 1e-12:
            rel_err = float(diff_norm / ref_norm)
        else:
            rel_err = float(np.max(np.abs(candidate_output - reference_output)))

        abs_err = float(np.max(np.abs(candidate_output - reference_output)))

        if self.tier == ContractTier.EXACT:
            if abs_err > 1e-7:
                return False, abs_err, f"EXACT tier failed: abs_err {abs_err:.2e} > 1e-7"
            return True, abs_err, "EXACT parity verified"

        if self.tier == ContractTier.NUMERICALLY_EQUIVALENT:
            if rel_err > self.max_relative_error:
                return False, rel_err, f"NUMERICALLY_EQUIVALENT failed: rel_err {rel_err:.2e} > {self.max_relative_error:.2e}"
            return True, rel_err, "Numerical equivalence verified"

        if self.tier == ContractTier.BOUNDED_APPROXIMATION:
            if rel_err > self.max_relative_error and abs_err > self.max_absolute_error:
                return False, rel_err, f"BOUNDED_APPROXIMATION failed: rel_err {rel_err:.2e} > {self.max_relative_error:.2e}"
            return True, rel_err, "Bounded approximation verified"

        # Perceptual / Predictive fallback checks
        if rel_err > 0.05:
            return False, rel_err, f"Error {rel_err:.2e} exceeds maximum allowable threshold"
        return True, rel_err, "Contract satisfied"
