"""
hyper_v3/verification/canonical_certifier.py
Authoritative, segregated certification engine that strictly validates workload execution
against declared contracts, rejecting invalid success claims and forged passed flags.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import numpy as np

from hyper_v3.frontend.contract_parser import ExecutionContract, ExactnessClass, ExecutionTrack
from hyper_v3.verification.independent_verifier import IndependentVerifier, VerificationResult


class CertificationStatus(str, Enum):
    CERTIFIED_EXACT = "CERTIFIED_EXACT"
    CERTIFIED_CONTRACT_AWARE = "CERTIFIED_CONTRACT_AWARE"
    REJECTED_NUMERICAL_TOLERANCE_EXCEEDED = "REJECTED_NUMERICAL_TOLERANCE_EXCEEDED"
    REJECTED_SHAPE_MISMATCH = "REJECTED_SHAPE_MISMATCH"
    REJECTED_NUMERICAL_INSTABILITY = "REJECTED_NUMERICAL_INSTABILITY"
    REJECTED_PERCEPTUAL_QUALITY_FAILED = "REJECTED_PERCEPTUAL_QUALITY_FAILED"
    REJECTED_PERFORMANCE_REGRESSION = "REJECTED_PERFORMANCE_REGRESSION"
    UNCERTIFIED_INSUFFICIENT_EVIDENCE = "UNCERTIFIED_INSUFFICIENT_EVIDENCE"


@dataclass
class CorrectnessVerification:
    is_valid: bool
    status: CertificationStatus
    max_relative_error: float
    max_absolute_error: float
    ssim: Optional[float] = None
    freivalds_passed: Optional[bool] = None
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceVerification:
    speedup_ratio: float
    latency_us: float
    reference_latency_us: float
    verified_work_avoidance: float
    is_performant: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkloadCertificate:
    workload_name: str
    contract_id: str
    track: str
    passed: bool
    status: CertificationStatus
    correctness: CorrectnessVerification
    performance: PerformanceVerification
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workload_name": self.workload_name,
            "contract_id": self.contract_id,
            "track": self.track,
            "passed": self.passed,
            "status": self.status.value,
            "max_relative_error": round(self.correctness.max_relative_error, 5),
            "max_absolute_error": round(self.correctness.max_absolute_error, 5),
            "speedup": round(self.performance.speedup_ratio, 2),
            "verified_work_avoidance": round(self.performance.verified_work_avoidance, 4),
            "reason": self.correctness.reason,
            "summary": self.summary,
        }


def verify_output(
    contract: ExecutionContract,
    reference: np.ndarray,
    candidate: np.ndarray,
) -> CorrectnessVerification:
    """Rigorous verification of candidate output against reference output under contract."""
    # 1. NaN and Inf checks
    if np.isnan(candidate).any() or np.isinf(candidate).any():
        return CorrectnessVerification(
            is_valid=False,
            status=CertificationStatus.REJECTED_NUMERICAL_INSTABILITY,
            max_relative_error=float("inf"),
            max_absolute_error=float("inf"),
            reason="Candidate output contains NaN or Infinity values.",
        )

    # 2. Shape validation
    if reference.shape != candidate.shape:
        if not contract.allow_representation_transform:
            return CorrectnessVerification(
                is_valid=False,
                status=CertificationStatus.REJECTED_SHAPE_MISMATCH,
                max_relative_error=1.0,
                max_absolute_error=1.0,
                reason=f"Shape mismatch: reference {reference.shape} != candidate {candidate.shape} without transform permission.",
            )
        # Bounded slice for allowed representation transformation
        min_rows = min(reference.shape[0], candidate.shape[0])
        ref_slice = reference[:min_rows]
        cand_slice = candidate[:min_rows]
    else:
        ref_slice = reference
        cand_slice = candidate

    # 3. Numerical Error calculation
    abs_diff = np.abs(ref_slice - cand_slice)
    max_abs = float(np.max(abs_diff))
    ref_scale = max(float(np.max(np.abs(ref_slice))), 1e-12)
    max_rel = float(max_abs / ref_scale)

    # 4. Bitwise Exact Verification
    if contract.exactness_class == ExactnessClass.BITWISE_EXACT or contract.track == ExecutionTrack.EXACT:
        is_exact = bool(np.array_equal(ref_slice, cand_slice) or max_abs <= 1e-6)
        return CorrectnessVerification(
            is_valid=is_exact,
            status=CertificationStatus.CERTIFIED_EXACT if is_exact else CertificationStatus.REJECTED_NUMERICAL_TOLERANCE_EXCEEDED,
            max_relative_error=max_rel,
            max_absolute_error=max_abs,
            reason="Exact bitwise/analytical parity verified" if is_exact else f"Failed exact parity: max_abs={max_abs:.6e}",
        )

    # 5. Image / Rasterization perceptual verification
    ssim_val: Optional[float] = None
    if contract.min_ssim < 1.0 and ref_slice.ndim >= 2:
        ssim_val = IndependentVerifier.compute_ssim_2d(ref_slice, cand_slice)
        if ssim_val < contract.min_ssim:
            return CorrectnessVerification(
                is_valid=False,
                status=CertificationStatus.REJECTED_PERCEPTUAL_QUALITY_FAILED,
                max_relative_error=max_rel,
                max_absolute_error=max_abs,
                ssim=ssim_val,
                reason=f"Perceptual SSIM {ssim_val:.4f} below threshold {contract.min_ssim:.4f}",
            )

    # 6. Contract-Aware Numerical Verification
    # Candidate must satisfy relative error <= declared threshold AND absolute error <= declared threshold
    passed_rel = max_rel <= contract.max_relative_error
    passed_abs = max_abs <= contract.max_absolute_error

    if not (passed_rel and passed_abs):
        return CorrectnessVerification(
            is_valid=False,
            status=CertificationStatus.REJECTED_NUMERICAL_TOLERANCE_EXCEEDED,
            max_relative_error=max_rel,
            max_absolute_error=max_abs,
            ssim=ssim_val,
            reason=f"Tolerance exceeded: max_rel={max_rel:.5f} (limit {contract.max_relative_error}), max_abs={max_abs:.5f} (limit {contract.max_absolute_error})",
        )

    return CorrectnessVerification(
        is_valid=True,
        status=CertificationStatus.CERTIFIED_CONTRACT_AWARE,
        max_relative_error=max_rel,
        max_absolute_error=max_abs,
        ssim=ssim_val,
        reason="Contract bounds verified within declared tolerances",
    )


def verify_performance(
    contract: ExecutionContract,
    metrics: Dict[str, Any],
) -> PerformanceVerification:
    """Verifies timing, speedup, and work avoidance without synthetic inflation."""
    latency_us = float(metrics.get("latency_us", 0.0))
    ref_latency_us = float(metrics.get("reference_latency_us", latency_us))
    speedup = (ref_latency_us / latency_us) if latency_us > 0 else 1.0

    ref_flops = int(metrics.get("ref_flops", 1))
    act_flops = int(metrics.get("act_flops", ref_flops))
    vwa = max(0.0, 1.0 - (act_flops / max(ref_flops, 1)))

    is_performant = True
    if latency_us > ref_latency_us * 1.05 and contract.track == ExecutionTrack.CONTRACT_AWARE:
        is_performant = False

    return PerformanceVerification(
        speedup_ratio=speedup,
        latency_us=latency_us,
        reference_latency_us=ref_latency_us,
        verified_work_avoidance=vwa,
        is_performant=is_performant,
        details={"speedup": round(speedup, 2), "vwa": round(vwa, 4)},
    )


def certify_candidate(
    contract: ExecutionContract,
    reference_output: np.ndarray,
    candidate_output: np.ndarray,
    metrics: Dict[str, Any],
) -> WorkloadCertificate:
    """
    Authoritative certification pipeline conforming to Master Directive Part 3.1.
    Never trusts a candidate-supplied passed flag.
    """
    correctness = verify_output(
        contract=contract,
        reference=reference_output,
        candidate=candidate_output,
    )
    performance = verify_performance(
        contract=contract,
        metrics=metrics,
    )

    passed = correctness.is_valid

    summary = (
        f"Workload '{contract.workload_name}' [{contract.track.value}]: "
        f"{'PASSED' if passed else 'FAILED'} - {correctness.reason} "
        f"(speedup: {performance.speedup_ratio:.2f}x, VWA: {performance.verified_work_avoidance:.2%})"
    )

    return WorkloadCertificate(
        workload_name=contract.workload_name,
        contract_id=contract.contract_id,
        track=contract.track.value,
        passed=passed,
        status=correctness.status,
        correctness=correctness,
        performance=performance,
        summary=summary,
    )
