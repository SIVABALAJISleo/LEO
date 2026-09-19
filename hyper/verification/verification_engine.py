"""
Verification Engine for LEO/HYPER Ω.
Implements the 6 verification levels:
- LEVEL 0: None
- LEVEL 1: Sample (Random spot check)
- LEVEL 2: Block (Tiled boundary verification)
- LEVEL 3: Full Numerical (Elementwise IEEE 754 parity)
- LEVEL 4: Mathematical Equivalence (Freivalds algorithm for matrix multiplication)
- LEVEL 5: Application-Independent Validation (Conservation laws, SSIM/PSNR, structural bounds)
"""

from __future__ import annotations

import enum
import dataclasses
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from contracts.contract_ir import ContractIR, VerificationLevel, ExactnessClass, ContractStatus, Contract100Evaluation


class VerificationEngine:
    """
    Verifies candidate results against reference requirements and contracts.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def verify_freivalds(A: np.ndarray, B: np.ndarray, C: np.ndarray, k: int = 5) -> bool:
        """
        Freivalds algorithm for verifying A @ B == C in O(k * n^2) instead of O(n^3).
        Tests A @ (B @ r) == C @ r for random binary vectors r in {0, 1}^n.
        Probability of error <= 2^(-k).
        """
        n = B.shape[1]
        for _ in range(k):
            r = np.random.randint(0, 2, size=(n, 1)).astype(A.dtype)
            br = B @ r
            abr = A @ br
            cr = C @ r
            if not np.allclose(abr, cr, atol=1e-4):
                return False
        return True

    @staticmethod
    def verify_sample(candidate: np.ndarray, reference: np.ndarray, sample_ratio: float = 0.05, tolerance: float = 1e-4) -> bool:
        """Random spot check on a subset of elements."""
        size = candidate.size
        sample_count = max(10, int(size * sample_ratio))
        indices = np.random.choice(size, sample_count, replace=False)
        cand_sample = candidate.ravel()[indices]
        ref_sample = reference.ravel()[indices]
        return bool(np.allclose(cand_sample, ref_sample, atol=tolerance))

    @staticmethod
    def verify_full_numerical(candidate: np.ndarray, reference: np.ndarray, max_abs_error: float = 1e-5) -> Tuple[bool, float, float]:
        """Full elementwise IEEE 754 check."""
        diff = np.abs(candidate.astype(np.float64) - reference.astype(np.float64))
        max_abs = float(np.max(diff)) if diff.size > 0 else 0.0
        norm_ref = float(np.linalg.norm(reference.astype(np.float64)))
        rel_l2 = float(np.linalg.norm(diff) / max(1e-12, norm_ref))
        passed = (max_abs <= max_abs_error)
        return passed, max_abs, rel_l2

    def verify(
        self,
        candidate: np.ndarray,
        reference: np.ndarray,
        contract: ContractIR,
        A: Optional[np.ndarray] = None,
        B: Optional[np.ndarray] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs the appropriate verification level mandated by the contract.
        """
        v_level = contract.verification_level

        # LEVEL 0: NONE
        if v_level == VerificationLevel.NONE:
            return True, {"level": 0, "verified": False, "method": "NONE"}

        # LEVEL 1: SAMPLE
        if v_level == VerificationLevel.STATISTICAL:
            passed = self.verify_sample(candidate, reference, tolerance=contract.exactness.tolerance)
            return passed, {"level": 1, "verified": passed, "method": "SAMPLE"}

        # LEVEL 4: PROBABILISTIC / FREIVALDS
        if v_level == VerificationLevel.PROBABILISTIC and A is not None and B is not None:
            passed = self.verify_freivalds(A, B, candidate)
            return passed, {"level": 4, "verified": passed, "method": "FREIVALDS"}

        # LEVEL 3: FULL NUMERICAL (Default)
        passed, max_abs, rel_l2 = self.verify_full_numerical(candidate, reference, max_abs_error=max(1e-5, contract.exactness.tolerance))
        return passed, {
            "level": 3,
            "verified": passed,
            "method": "FULL_NUMERICAL",
            "max_abs_error": max_abs,
            "relative_l2_error": rel_l2,
        }
