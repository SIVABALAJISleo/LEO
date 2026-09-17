"""
hyper/v8/contract.py
====================
HYPER v8 — Formal Compute Contract Engine.

ComputeContractV2: every optimization must carry an explicit contract.
PathClassification: every execution result carries exactly one path label.
ContractValidator: rejects any result that cannot be proven contract-safe.

Scientific rules:
  - No optimization executes without a contract.
  - No result is accepted without verification against the contract.
  - Approximation is never silently labeled exact.
"""

from __future__ import annotations

import dataclasses
import enum
import time
from typing import Any, Dict, Optional

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# PATH CLASSIFICATION  (every result must carry exactly ONE)
# ─────────────────────────────────────────────────────────────────────────────

class PathClassification(enum.Enum):
    EXACT_FRESH         = "EXACT_FRESH"          # full recomputation, exact
    EXACT_REUSED        = "EXACT_REUSED"          # exact cache replay
    EXACT_RESIDUAL      = "EXACT_RESIDUAL"        # incremental exact update
    EXACT_REFORMULATED  = "EXACT_REFORMULATED"    # algebraically equivalent
    SPARSE_EXACT        = "SPARSE_EXACT"          # sparse but exact
    LOW_RANK_EXACT      = "LOW_RANK_EXACT"        # low-rank but exact
    APPROXIMATE         = "APPROXIMATE"            # bounded approximation
    PREDICTIVE          = "PREDICTIVE"             # predicted, not computed
    RECONSTRUCTED       = "RECONSTRUCTED"          # reconstructed from repr.
    CACHED              = "CACHED"                 # result from cache (any)
    FALLBACK            = "FALLBACK"               # fell back to safe path
    UNVERIFIED          = "UNVERIFIED"             # result not verified
    REJECTED            = "REJECTED"               # contract not satisfied


class VerificationStatus(enum.Enum):
    VERIFIED_EXACT      = "VERIFIED_EXACT"
    VERIFIED_NUMERICAL  = "VERIFIED_NUMERICAL"
    VERIFIED_PERCEPTUAL = "VERIFIED_PERCEPTUAL"
    UNVERIFIED          = "UNVERIFIED"
    REJECTED            = "REJECTED"


# ─────────────────────────────────────────────────────────────────────────────
# COMPUTE CONTRACT V2
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class NumericalTolerance:
    abs_error_max: float = 0.0
    rel_error_max: float = 0.0
    ulp_max: int = 0


@dataclasses.dataclass
class PerceptualTolerance:
    ssim_min: float = 1.0
    psnr_min: float = float("inf")
    lpips_max: float = 0.0


@dataclasses.dataclass
class PerformanceRequirement:
    latency_max_ms: float = float("inf")
    fps_min: float = 0.0
    throughput_min: float = 0.0


@dataclasses.dataclass
class MemoryRequirement:
    max_ram_mb: float = float("inf")


@dataclasses.dataclass
class ComputeContractV2:
    """
    Formal contract for a computation.

    Every field is explicit. No implicit defaults that hide intent.
    An optimization that cannot be proven to satisfy this contract
    must be rejected.
    """
    # Identification
    name: str = "unnamed"
    version: str = "1.0"

    # Correctness mode
    correctness_mode: str = "EXACT"   # EXACT | NUMERICAL | PERCEPTUAL

    # Numerical bounds (used when correctness_mode == NUMERICAL)
    numerical: NumericalTolerance = dataclasses.field(
        default_factory=NumericalTolerance
    )

    # Perceptual bounds (used when correctness_mode == PERCEPTUAL)
    perceptual: PerceptualTolerance = dataclasses.field(
        default_factory=PerceptualTolerance
    )

    # Performance requirements
    performance: PerformanceRequirement = dataclasses.field(
        default_factory=PerformanceRequirement
    )

    # Memory
    memory: MemoryRequirement = dataclasses.field(
        default_factory=MemoryRequirement
    )

    # Behavioral flags
    determinism_required: bool = True
    approximation_allowed: bool = False
    caching_allowed: bool = True
    prediction_allowed: bool = False

    # Strict mode
    strict_100_mode: bool = False   # if True, every field must pass or result=FAIL

    def is_exact(self) -> bool:
        return self.correctness_mode == "EXACT"

    def is_numerical(self) -> bool:
        return self.correctness_mode == "NUMERICAL"

    def allows_approximation(self) -> bool:
        return self.approximation_allowed

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "correctness_mode": self.correctness_mode,
            "abs_error_max": self.numerical.abs_error_max,
            "latency_max_ms": self.performance.latency_max_ms,
            "approximation_allowed": self.approximation_allowed,
            "caching_allowed": self.caching_allowed,
            "prediction_allowed": self.prediction_allowed,
            "strict_100_mode": self.strict_100_mode,
        }


# ─────────────────────────────────────────────────────────────────────────────
# PRE-BUILT CONTRACTS
# ─────────────────────────────────────────────────────────────────────────────

def exact_contract(name: str = "exact") -> ComputeContractV2:
    """Contract that requires exact computation. No approximation."""
    return ComputeContractV2(
        name=name,
        correctness_mode="EXACT",
        approximation_allowed=False,
        caching_allowed=True,
        prediction_allowed=False,
        strict_100_mode=True,
    )


def numerical_contract(
    name: str = "numerical",
    abs_tol: float = 1e-6,
    rel_tol: float = 1e-6,
    latency_ms: float = float("inf"),
) -> ComputeContractV2:
    """Contract allowing bounded numerical error."""
    return ComputeContractV2(
        name=name,
        correctness_mode="NUMERICAL",
        numerical=NumericalTolerance(
            abs_error_max=abs_tol,
            rel_error_max=rel_tol,
        ),
        performance=PerformanceRequirement(latency_max_ms=latency_ms),
        approximation_allowed=True,
        caching_allowed=True,
        prediction_allowed=False,
    )


def realtime_contract(fps: float = 60.0, abs_tol: float = 1e-3) -> ComputeContractV2:
    """Contract requiring real-time performance (FPS) with perceptual tolerance."""
    return ComputeContractV2(
        name="realtime",
        correctness_mode="NUMERICAL",
        numerical=NumericalTolerance(abs_error_max=abs_tol),
        performance=PerformanceRequirement(fps_min=fps, latency_max_ms=1000.0 / fps),
        approximation_allowed=True,
        caching_allowed=True,
        prediction_allowed=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# CONTRACT VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────

@dataclasses.dataclass
class ContractCheckResult:
    passed: bool
    path: PathClassification
    verification_status: VerificationStatus
    max_abs_error: float
    max_rel_error: float
    latency_ms: float
    failure_reasons: list
    notes: str = ""


class ContractValidator:
    """
    Validates an execution result against a contract.

    Never lowers verification to improve numbers.
    Never accepts an unverified result as VERIFIED.
    """

    def validate(
        self,
        contract: ComputeContractV2,
        reference: np.ndarray,
        candidate: np.ndarray,
        path: PathClassification,
        latency_ms: float,
    ) -> ContractCheckResult:
        failures = []
        max_abs = 0.0
        max_rel = 0.0

        # ── Shape check ──────────────────────────────────────────────────
        if reference.shape != candidate.shape:
            return ContractCheckResult(
                passed=False,
                path=path,
                verification_status=VerificationStatus.REJECTED,
                max_abs_error=float("inf"),
                max_rel_error=float("inf"),
                latency_ms=latency_ms,
                failure_reasons=["SHAPE_MISMATCH"],
            )

        # ── NaN/Inf check ─────────────────────────────────────────────────
        if np.any(np.isnan(candidate)) or np.any(np.isinf(candidate)):
            failures.append("NAN_OR_INF_IN_OUTPUT")

        # ── Numerical error ───────────────────────────────────────────────
        diff = np.abs(reference.astype(np.float64) - candidate.astype(np.float64))
        max_abs = float(diff.max()) if diff.size > 0 else 0.0
        ref_abs = np.abs(reference.astype(np.float64))
        with np.errstate(divide="ignore", invalid="ignore"):
            rel = np.where(ref_abs > 0, diff / ref_abs, diff)
        max_rel = float(rel.max()) if rel.size > 0 else 0.0

        if contract.is_exact():
            if max_abs > 0.0:
                failures.append(f"EXACT_VIOLATED: max_abs={max_abs:.3e}")
        elif contract.is_numerical():
            if max_abs > contract.numerical.abs_error_max:
                failures.append(
                    f"ABS_TOL_VIOLATED: {max_abs:.3e} > {contract.numerical.abs_error_max:.3e}"
                )
            if max_rel > contract.numerical.rel_error_max and contract.numerical.rel_error_max > 0:
                failures.append(
                    f"REL_TOL_VIOLATED: {max_rel:.3e} > {contract.numerical.rel_error_max:.3e}"
                )

        # ── Latency check ─────────────────────────────────────────────────
        if latency_ms > contract.performance.latency_max_ms:
            failures.append(
                f"LATENCY_VIOLATED: {latency_ms:.2f}ms > {contract.performance.latency_max_ms:.2f}ms"
            )

        # ── Path coherence check ──────────────────────────────────────────
        if not contract.approximation_allowed and path == PathClassification.APPROXIMATE:
            failures.append("APPROXIMATION_NOT_ALLOWED_BY_CONTRACT")

        if not contract.prediction_allowed and path == PathClassification.PREDICTIVE:
            failures.append("PREDICTION_NOT_ALLOWED_BY_CONTRACT")

        passed = len(failures) == 0

        if passed:
            if contract.is_exact() and max_abs == 0.0:
                vstatus = VerificationStatus.VERIFIED_EXACT
            else:
                vstatus = VerificationStatus.VERIFIED_NUMERICAL
        else:
            vstatus = VerificationStatus.REJECTED

        return ContractCheckResult(
            passed=passed,
            path=path,
            verification_status=vstatus,
            max_abs_error=max_abs,
            max_rel_error=max_rel,
            latency_ms=latency_ms,
            failure_reasons=failures,
        )
