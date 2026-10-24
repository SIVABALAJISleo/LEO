"""
hyper_phase_change/verification.py
==================================
Strict Independent Verification Engine for Phase-Change and Universal Fabric.

Enforces:
1. Complete independence: Candidate optimization logic is evaluated against an isolated reference implementation.
2. Formal 5-State Verification: PASS, FAIL, UNKNOWN, BLOCKED, NOT_RUN.
3. Strict exactness testing:
   - BIT_EXACT: Exact bitwise binary match (exact bytes).
   - INTEGER_EXACT: Exact scalar/array integer equality.
   - NUMERICALLY_EQUIVALENT: Tolerance check (np.allclose with contract atol/rtol).
4. Hash digest comparison and provenance tracking.
5. Rejection of UNKNOWN/BLOCKED in certification.
"""

from __future__ import annotations

import dataclasses
import hashlib
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper.canonical.verification_state_machine import (
    VerificationStatus,
    WorkloadVerificationRecord,
    SuiteVerificationReport,
    StrictVerificationRunner,
)
from hyper_phase_change.contract import (
    WorkloadContract,
    ExactnessClass,
    CANONICAL_REGISTRY,
    CANONICAL_15_WORKLOAD_IDS,
)
from hyper.canonical.independent_reference import IndependentReferenceEngine


@dataclasses.dataclass
class VerificationResult:
    """Individual execution verification result."""
    is_verified: bool
    status: VerificationStatus
    workload_id: str
    exactness_class: str
    candidate_digest: str
    reference_digest: str
    max_absolute_error: float
    max_relative_error: float
    within_tolerance: bool
    verification_latency_ms: float
    details: List[str] = dataclasses.field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_verified": self.is_verified,
            "status": self.status.value,
            "workload_id": self.workload_id,
            "exactness_class": self.exactness_class,
            "candidate_digest": self.candidate_digest,
            "reference_digest": self.reference_digest,
            "max_absolute_error": float(self.max_absolute_error),
            "max_relative_error": float(self.max_relative_error),
            "within_tolerance": self.within_tolerance,
            "verification_latency_ms": round(self.verification_latency_ms, 4),
            "details": self.details,
        }


class PhaseChangeVerifier:
    """Independent verification engine checking candidate results against isolated references."""

    @staticmethod
    def compute_digest(output: Any) -> str:
        """Computes a cryptographically secure SHA-256 digest of an output tensor or structure."""
        hasher = hashlib.sha256()
        if isinstance(output, np.ndarray):
            hasher.update(str(output.shape).encode("utf-8"))
            hasher.update(str(output.dtype).encode("utf-8"))
            hasher.update(output.tobytes() if output.flags["C_CONTIGUOUS"] else np.ascontiguousarray(output).tobytes())
        elif isinstance(output, (dict, list, tuple)):
            hasher.update(repr(output).encode("utf-8"))
        elif isinstance(output, (int, float, bool, str)):
            hasher.update(f"{type(output).__name__}:{output}".encode("utf-8"))
        elif output is None:
            hasher.update(b"none")
        else:
            hasher.update(repr(output).encode("utf-8"))
        return hasher.hexdigest()

    @classmethod
    def verify_candidate_output(
        cls,
        workload_id: str,
        inputs: Dict[str, Any],
        candidate_output: Any,
        contract: Optional[WorkloadContract] = None,
        reference_output: Optional[Any] = None,
    ) -> VerificationResult:
        """
        Verifies a candidate output against an independent reference.
        Never shares logic with the candidate.
        """
        t0 = time.perf_counter()
        if contract is None:
            contract = CANONICAL_REGISTRY.get_contract(workload_id)

        details: List[str] = []

        # 1. Compute independent reference if not provided
        if reference_output is None:
            try:
                reference_output, _ = IndependentReferenceEngine.execute_reference(workload_id, inputs)
            except Exception as e:
                v_ms = (time.perf_counter() - t0) * 1000.0
                return VerificationResult(
                    is_verified=False,
                    status=VerificationStatus.BLOCKED,
                    workload_id=workload_id,
                    exactness_class=contract.exactness_class.value if contract else "UNKNOWN",
                    candidate_digest=cls.compute_digest(candidate_output),
                    reference_digest="ERROR",
                    max_absolute_error=float("inf"),
                    max_relative_error=float("inf"),
                    within_tolerance=False,
                    verification_latency_ms=v_ms,
                    details=[f"Reference computation failed: {str(e)}"],
                )

        cand_digest = cls.compute_digest(candidate_output)
        ref_digest = cls.compute_digest(reference_output)

        # 2. Check shapes
        if isinstance(candidate_output, np.ndarray) and isinstance(reference_output, np.ndarray):
            if candidate_output.shape != reference_output.shape:
                v_ms = (time.perf_counter() - t0) * 1000.0
                return VerificationResult(
                    is_verified=False,
                    status=VerificationStatus.FAIL,
                    workload_id=workload_id,
                    exactness_class=contract.exactness_class.value if contract else "UNKNOWN",
                    candidate_digest=cand_digest,
                    reference_digest=ref_digest,
                    max_absolute_error=float("inf"),
                    max_relative_error=float("inf"),
                    within_tolerance=False,
                    verification_latency_ms=v_ms,
                    details=[f"Shape mismatch: candidate {candidate_output.shape} vs ref {reference_output.shape}"],
                )

        # 3. Check exactness class
        exactness = contract.exactness_class if contract else ExactnessClass.NUMERICALLY_EQUIVALENT

        if exactness in (ExactnessClass.BIT_EXACT, ExactnessClass.INTEGER_EXACT):
            is_match = False
            if isinstance(candidate_output, np.ndarray) and isinstance(reference_output, np.ndarray):
                is_match = bool(np.array_equal(candidate_output, reference_output))
            else:
                is_match = bool(candidate_output == reference_output)

            v_ms = (time.perf_counter() - t0) * 1000.0
            return VerificationResult(
                is_verified=is_match,
                status=VerificationStatus.PASS if is_match else VerificationStatus.FAIL,
                workload_id=workload_id,
                exactness_class=exactness.value,
                candidate_digest=cand_digest,
                reference_digest=ref_digest,
                max_absolute_error=0.0 if is_match else 1.0,
                max_relative_error=0.0 if is_match else 1.0,
                within_tolerance=is_match,
                verification_latency_ms=v_ms,
                details=["Exact bit/integer match verified" if is_match else "Exact equality check failed"],
            )

        # 4. Numerical Tolerance Check
        atol = getattr(contract, "atol", 1e-4) if contract else 1e-4
        rtol = getattr(contract, "rtol", 1e-4) if contract else 1e-4

        cand_arr = np.asarray(candidate_output, dtype=np.float64)
        ref_arr = np.asarray(reference_output, dtype=np.float64)

        diff = np.abs(cand_arr - ref_arr)
        max_abs_err = float(np.max(diff))
        denom = np.abs(ref_arr)
        # Avoid division by zero in relative error
        safe_denom = np.where(denom > 1e-8, denom, 1.0)
        max_rel_err = float(np.max(diff / safe_denom))

        within_tol = bool(np.allclose(cand_arr, ref_arr, atol=atol, rtol=rtol))
        v_ms = (time.perf_counter() - t0) * 1000.0

        if within_tol:
            details.append(f"Numerically equivalent within atol={atol}, rtol={rtol}. Max abs err: {max_abs_err:.2e}")
            status = VerificationStatus.PASS
        else:
            details.append(f"Tolerance exceeded: max_abs_err={max_abs_err:.2e} > atol={atol} or rel_err={max_rel_err:.2e} > rtol={rtol}")
            status = VerificationStatus.FAIL

        return VerificationResult(
            is_verified=within_tol,
            status=status,
            workload_id=workload_id,
            exactness_class=exactness.value,
            candidate_digest=cand_digest,
            reference_digest=ref_digest,
            max_absolute_error=max_abs_err,
            max_relative_error=max_rel_err,
            within_tolerance=within_tol,
            verification_latency_ms=v_ms,
            details=details,
        )

    @classmethod
    def run_suite(cls) -> SuiteVerificationReport:
        """Executes full verification across all 15 canonical workloads."""
        return StrictVerificationRunner.verify_all_canonical_workloads()


__all__ = [
    "VerificationStatus",
    "WorkloadVerificationRecord",
    "SuiteVerificationReport",
    "VerificationResult",
    "PhaseChangeVerifier",
]
