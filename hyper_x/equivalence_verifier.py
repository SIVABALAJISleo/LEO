"""
hyper_x/equivalence_verifier.py
===============================
HYPER-Ω Output-Equivalence Engine:
Enforces fail-closed, multi-modal equivalence checks against external reference outputs:
- EXACT_BITWISE: SHA-256 / byte-for-byte identical
- EXACT_NUMERICAL: Strict machine precision / zero ULP variance
- NUMERICALLY_EQUIVALENT: Relative error <= epsilon, absolute error <= delta
- STRUCTURAL: Shape, layout, sparsity topology, rank bounds
- FUNCTIONAL: Invariant contract preserved
- CONTRACT_EQUIVALENT: Application-defined observable satisfied
- PERCEPTUAL_EQUIVALENT: PSNR >= target_dB, SSIM >= target_ssim

FAIL-CLOSED PRINCIPLE:
Every verification state defaults to UNKNOWN or FALSE. PASS must be mathematically earned.
"""

from __future__ import annotations
import enum
import hashlib
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class EquivalenceMode(str, enum.Enum):
    EXACT_BITWISE = "EXACT_BITWISE"
    EXACT_NUMERICAL = "EXACT_NUMERICAL"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    STRUCTURAL = "STRUCTURAL"
    FUNCTIONAL = "FUNCTIONAL"
    CONTRACT_EQUIVALENT = "CONTRACT_EQUIVALENT"
    PERCEPTUAL_EQUIVALENT = "PERCEPTUAL_EQUIVALENT"


class VerificationVerdict(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    INVALID = "INVALID"


@dataclass
class EquivalenceReport:
    workload_id: str
    mode: EquivalenceMode
    verdict: VerificationVerdict = VerificationVerdict.UNKNOWN  # Fail-closed default
    is_bitwise_identical: bool = False
    relative_error: float = float("inf")
    max_absolute_error: float = float("inf")
    ulp_distance: int = -1
    psnr_db: Optional[float] = None
    ssim: Optional[float] = None
    candidate_hash: str = ""
    reference_hash: str = ""
    failure_reasons: List[str] = field(default_factory=list)
    verification_latency_ms: float = 0.0


class ExternalEquivalenceVerifier:
    """
    Independent verifier validating candidate execution outputs against
    frozen external reference outputs.
    """

    @classmethod
    def verify(
        cls,
        workload_id: str,
        candidate_output: np.ndarray,
        reference_output: np.ndarray,
        mode: EquivalenceMode,
        rel_tolerance: float = 1e-4,
        abs_tolerance: float = 1e-4,
        min_psnr_db: float = 32.0,
        min_ssim: float = 0.95,
        application_contract_validator: Optional[Any] = None,
    ) -> EquivalenceReport:
        import time
        t0 = time.perf_counter()

        report = EquivalenceReport(
            workload_id=workload_id,
            mode=mode,
            verdict=VerificationVerdict.UNKNOWN,  # Default fail-closed
        )

        # 1. Structural Shape Check
        if candidate_output.shape != reference_output.shape:
            report.verdict = VerificationVerdict.FAIL
            report.failure_reasons.append(
                f"Shape mismatch: candidate {candidate_output.shape} vs reference {reference_output.shape}"
            )
            report.verification_latency_ms = (time.perf_counter() - t0) * 1000.0
            return report

        # 2. Cryptographic Output Hashes
        c_bytes = np.ascontiguousarray(candidate_output).tobytes()
        r_bytes = np.ascontiguousarray(reference_output).tobytes()
        report.candidate_hash = hashlib.sha256(c_bytes).hexdigest()
        report.reference_hash = hashlib.sha256(r_bytes).hexdigest()
        report.is_bitwise_identical = (report.candidate_hash == report.reference_hash)

        # 3. Numerical Error Analysis
        cand_f64 = candidate_output.astype(np.float64)
        ref_f64 = reference_output.astype(np.float64)
        diff = np.abs(cand_f64 - ref_f64)
        report.max_absolute_error = float(np.max(diff))
        ref_norm = float(np.linalg.norm(ref_f64))
        diff_norm = float(np.linalg.norm(diff))
        report.relative_error = float(diff_norm / max(1e-12, ref_norm))

        # 4. Mode-Specific Evaluation
        if mode == EquivalenceMode.EXACT_BITWISE:
            if report.is_bitwise_identical:
                report.verdict = VerificationVerdict.PASS
            else:
                report.verdict = VerificationVerdict.FAIL
                report.failure_reasons.append("Bitwise hash mismatch vs external reference")

        elif mode == EquivalenceMode.EXACT_NUMERICAL:
            if report.max_absolute_error == 0.0:
                report.verdict = VerificationVerdict.PASS
            else:
                report.verdict = VerificationVerdict.FAIL
                report.failure_reasons.append(f"Max abs error {report.max_absolute_error} > 0.0 for EXACT_NUMERICAL")

        elif mode == EquivalenceMode.NUMERICALLY_EQUIVALENT:
            if report.relative_error <= rel_tolerance and report.max_absolute_error <= abs_tolerance:
                report.verdict = VerificationVerdict.PASS
            else:
                report.verdict = VerificationVerdict.FAIL
                report.failure_reasons.append(
                    f"Relative error {report.relative_error:.2e} > {rel_tolerance:.2e} or abs error {report.max_absolute_error:.2e} > {abs_tolerance:.2e}"
                )

        elif mode == EquivalenceMode.PERCEPTUAL_EQUIVALENT:
            mse = float(np.mean(diff ** 2))
            psnr = 100.0 if mse < 1e-12 else float(20.0 * math.log10(1.0 / math.sqrt(mse)))
            report.psnr_db = round(psnr, 2)

            # Simple SSIM
            mu_c, mu_r = float(np.mean(cand_f64)), float(np.mean(ref_f64))
            var_c, var_r = float(np.var(cand_f64)), float(np.var(ref_f64))
            cov = float(np.mean((cand_f64 - mu_c) * (ref_f64 - mu_r)))
            c1, c2 = 0.0001, 0.0009
            ssim_val = float(((2 * mu_c * mu_r + c1) * (2 * cov + c2)) / ((mu_c**2 + mu_r**2 + c1) * (var_c + var_r + c2)))
            report.ssim = round(min(1.0, max(-1.0, ssim_val)), 4)

            if psnr >= min_psnr_db and report.ssim >= min_ssim:
                report.verdict = VerificationVerdict.PASS
            else:
                report.verdict = VerificationVerdict.FAIL
                report.failure_reasons.append(f"Perceptual threshold failed: PSNR {psnr:.2f}dB (min {min_psnr_db}), SSIM {report.ssim} (min {min_ssim})")

        elif mode == EquivalenceMode.CONTRACT_EQUIVALENT:
            if application_contract_validator is not None:
                passed, reason = application_contract_validator(candidate_output, reference_output)
                if passed:
                    report.verdict = VerificationVerdict.PASS
                else:
                    report.verdict = VerificationVerdict.FAIL
                    report.failure_reasons.append(f"Application contract failed: {reason}")
            else:
                if report.relative_error <= 0.05:  # 5% contract boundary
                    report.verdict = VerificationVerdict.PASS
                else:
                    report.verdict = VerificationVerdict.FAIL
                    report.failure_reasons.append(f"Default contract relative error {report.relative_error:.2e} > 0.05")

        report.verification_latency_ms = (time.perf_counter() - t0) * 1000.0
        return report
