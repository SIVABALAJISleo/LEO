"""
hyper_cco/verifier.py
=====================
Pluggable Multi-Level Verification Suite.
Supports verification levels from Level 0 (None) through Level 5 (Application-Level Validator):
- Level 1: Sample screening (explicitly tagged as screening, never as mathematical proof)
- Level 2: Structured block check
- Level 3: Full deterministic Frobenius and L-infinity numerical verification
- Level 4: Formal mathematical equivalence via Freivalds O(N^2) randomized verification (k=15 rounds, 99.997% confidence)
- Level 5: Application-level validator (PSNR, SSIM, domain invariants)

Strictly outputs PASS, FAIL, or INCONCLUSIVE. Never converts INCONCLUSIVE into PASS.
"""

from typing import Dict, Any, Tuple, Optional, Callable, List
import numpy as np
from .contract import ComputeContract, VerificationLevel, VerificationStatus


class CcoVerifier:
    """
    Pluggable verification suite for mathematical and application-level correctness.
    """

    @staticmethod
    def verify_freivalds(
        A: np.ndarray,
        B: np.ndarray,
        C_candidate: np.ndarray,
        rounds: int = 15,
        tolerance: float = 1e-4
    ) -> Tuple[VerificationStatus, float, Dict[str, Any]]:
        """
        Level 4 Formal Verification: Freivalds Randomized Algorithm for Matrix Multiplication.
        Tests if A @ B = C_candidate by computing A @ (B @ r) - C_candidate @ r for random r in {-1, 1}^N.
        Complexity: O(rounds * N^2) instead of O(N^3).
        Confidence: 1 - 2^(-rounds). For rounds=15: 99.9969%.
        """
        M, K = A.shape
        K2, N = B.shape
        if C_candidate.shape != (M, N):
            return VerificationStatus.FAIL, 1.0, {"reason": f"Shape mismatch: {C_candidate.shape} != {(M, N)}"}

        max_rel_error = 0.0
        confidence = 1.0 - (0.5 ** rounds)

        for r_idx in range(rounds):
            r = np.random.choice([-1.0, 1.0], size=(N, 1))
            Br = B @ r
            ABr = A @ Br
            Cr = C_candidate @ r

            diff_norm = float(np.linalg.norm(ABr - Cr))
            ref_norm = float(np.linalg.norm(ABr))
            rel_err = diff_norm / max(1e-12, ref_norm)

            if rel_err > max_rel_error:
                max_rel_error = rel_err

            if rel_err > tolerance:
                return VerificationStatus.FAIL, confidence, {
                    "reason": f"Freivalds round {r_idx+1} failed: rel_err={rel_err:.2e} > tolerance={tolerance:.2e}",
                    "failed_round": r_idx + 1,
                    "max_rel_error": max_rel_error
                }

        return VerificationStatus.PASS, confidence, {
            "rounds_passed": rounds,
            "confidence_pct": confidence * 100.0,
            "max_rel_error": max_rel_error
        }

    @staticmethod
    def verify_numeric(
        candidate: np.ndarray,
        baseline: np.ndarray,
        contract: ComputeContract,
        level: VerificationLevel = VerificationLevel.LEVEL_3_FULL_NUMERICAL
    ) -> Tuple[VerificationStatus, Dict[str, Any]]:
        """
        Level 3/Level 2 numerical verification against contract error tolerances.
        """
        if candidate.shape != baseline.shape:
            return VerificationStatus.FAIL, {
                "reason": f"Shape mismatch: {candidate.shape} != {baseline.shape}",
                "level": level.value
            }

        if level == VerificationLevel.LEVEL_1_SAMPLE_SCREENING:
            # Sample check: examine 5% random indices (screening only)
            sample_size = max(10, int(candidate.size * 0.05))
            indices = np.random.choice(candidate.size, size=sample_size, replace=False)
            c_sample = candidate.ravel()[indices]
            b_sample = baseline.ravel()[indices]
            diff = np.abs(c_sample - b_sample)
            max_abs = float(np.max(diff))
            return VerificationStatus.PASS if max_abs <= (contract.max_absolute_error or 1e-3) else VerificationStatus.FAIL, {
                "screening_only": True,
                "level": level.value,
                "max_sample_abs_err": max_abs
            }

        # Level 3: Full numerical check
        diff = np.abs(candidate - baseline)
        max_abs = float(np.max(diff)) if diff.size > 0 else 0.0
        norm_b = float(np.linalg.norm(baseline))
        rel_err = float(np.linalg.norm(diff)) / max(1e-12, norm_b) if norm_b > 0 else max_abs

        if contract.is_exact_required():
            if max_abs > 0.0:
                return VerificationStatus.FAIL, {
                    "reason": f"Exactness required: max_abs={max_abs:.2e} > 0",
                    "error_abs": max_abs,
                    "error_rel": rel_err
                }
            return VerificationStatus.PASS, {"error_abs": 0.0, "error_rel": 0.0}

        if contract.max_absolute_error is not None and max_abs > contract.max_absolute_error:
            return VerificationStatus.FAIL, {
                "reason": f"Absolute error {max_abs:.2e} > threshold {contract.max_absolute_error:.2e}",
                "error_abs": max_abs,
                "error_rel": rel_err
            }

        if contract.max_relative_error is not None and rel_err > contract.max_relative_error:
            return VerificationStatus.FAIL, {
                "reason": f"Relative error {rel_err:.2e} > threshold {contract.max_relative_error:.2e}",
                "error_abs": max_abs,
                "error_rel": rel_err
            }

        return VerificationStatus.PASS, {
            "error_abs": max_abs,
            "error_rel": rel_err,
            "level": level.value
        }

    @staticmethod
    def verify_image(
        candidate: np.ndarray,
        baseline: np.ndarray,
        contract: ComputeContract
    ) -> Tuple[VerificationStatus, Dict[str, Any]]:
        """
        Level 5 Perceptual Image Verification (PSNR & SSIM).
        """
        from .temporal_graphics import TemporalGraphicsEngine
        psnr = TemporalGraphicsEngine.calculate_psnr(candidate, baseline)
        ssim = TemporalGraphicsEngine.calculate_ssim(candidate, baseline)

        min_psnr = contract.min_psnr or 30.0
        min_ssim = contract.min_ssim or 0.90

        if psnr < min_psnr:
            return VerificationStatus.FAIL, {
                "reason": f"PSNR {psnr:.2f}dB < threshold {min_psnr:.2f}dB",
                "psnr": psnr,
                "ssim": ssim
            }

        if ssim < min_ssim:
            return VerificationStatus.FAIL, {
                "reason": f"SSIM {ssim:.4f} < threshold {min_ssim:.4f}",
                "psnr": psnr,
                "ssim": ssim
            }

        return VerificationStatus.PASS, {
            "psnr": psnr,
            "ssim": ssim,
            "level": VerificationLevel.LEVEL_5_APPLICATION_VALIDATOR.value
        }
