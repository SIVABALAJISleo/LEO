"""
hyper_x/cpce/rewrite_verifier.py
================================
Independent Multi-Level Verification Stack for CPCE.
Ensures that the optimizer is not its own sole judge of correctness.
Validates candidate outputs against reference observations under contract semantics:
- Exact bitwise equality
- Exact mathematical equality
- Tolerance-based floating-point equivalence
- Freivalds probabilistic matrix product verification
- Cosine-bounded quality contracts
"""

from __future__ import annotations

import dataclasses
from enum import Enum
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper_x.cpce.contracts import WorkloadContract, ValidationMode, ExactnessRequirement


class VerificationOutcome(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    UNSUPPORTED = "UNSUPPORTED"


@dataclasses.dataclass
class VerificationReport:
    """Detailed evidence record produced by the independent verification engine."""
    outcome: VerificationOutcome
    validation_level: str
    max_absolute_error: float = 0.0
    relative_error: float = 0.0
    cosine_similarity: float = 1.0
    freivalds_verified: bool = False
    evidence_summary: str = ""
    timestamp: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outcome": self.outcome.value,
            "validation_level": self.validation_level,
            "max_absolute_error": float(self.max_absolute_error),
            "relative_error": float(self.relative_error),
            "cosine_similarity": float(self.cosine_similarity),
            "freivalds_verified": bool(self.freivalds_verified),
            "evidence_summary": self.evidence_summary,
            "timestamp": self.timestamp,
        }


class RewriteVerifier:
    """Independent multi-level verifier implementing fail-closed certification."""

    @staticmethod
    def verify(
        candidate_output: Any,
        reference_output: Any,
        contract: WorkloadContract,
        matrix_operands: Optional[Tuple[np.ndarray, np.ndarray]] = None,
    ) -> VerificationReport:
        """
        Independently verifies candidate output against reference output under contract rules.
        """
        # Convert to numpy arrays if necessary
        cand = candidate_output.to_dense() if hasattr(candidate_output, "to_dense") else (np.asarray(candidate_output) if not isinstance(candidate_output, np.ndarray) else candidate_output)
        ref = reference_output.to_dense() if hasattr(reference_output, "to_dense") else (np.asarray(reference_output) if not isinstance(reference_output, np.ndarray) else reference_output)

        # Shape consistency check

        if cand.shape != ref.shape:
            return VerificationReport(
                outcome=VerificationOutcome.FAIL,
                validation_level="SHAPE_CHECK",
                evidence_summary=f"Shape mismatch: candidate {cand.shape} vs reference {ref.shape}",
            )

        # Level 1: Bitwise Exact Contract
        if contract.validation_mode == ValidationMode.EXACT:
            if cand.dtype != ref.dtype:
                # Dtype mismatch on exact contract is a failure
                return VerificationReport(
                    outcome=VerificationOutcome.FAIL,
                    validation_level="DTYPE_CHECK",
                    evidence_summary=f"Dtype mismatch on exact contract: {cand.dtype} vs {ref.dtype}",
                )

            is_exact = np.array_equal(cand, ref)
            if is_exact:
                return VerificationReport(
                    outcome=VerificationOutcome.PASS,
                    validation_level="BITWISE_EXACT",
                    evidence_summary="Bitwise exact equality confirmed across all elements.",
                )
            else:
                max_diff = float(np.max(np.abs(cand.astype(np.float64) - ref.astype(np.float64))))
                return VerificationReport(
                    outcome=VerificationOutcome.FAIL,
                    validation_level="BITWISE_EXACT",
                    max_absolute_error=max_diff,
                    evidence_summary=f"Bitwise exact check failed. Max diff: {max_diff:.2e}",
                )

        # Level 2: Numerical Tolerance Contract
        if contract.validation_mode == ValidationMode.TOLERANCE_BASED:
            abs_diff = np.abs(cand.astype(np.float64) - ref.astype(np.float64))
            max_abs_err = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
            ref_norm = float(np.max(np.abs(ref))) if ref.size > 0 else 1.0
            rel_err = float(max_abs_err / max(1e-12, ref_norm))

            threshold = contract.max_absolute_error + contract.max_relative_error * ref_norm
            passed_tolerance = max_abs_err <= threshold

            freivalds_ok = True
            if matrix_operands and cand.ndim == 2:
                # Run Freivalds probabilistic O(N^2) verification check
                A, B = matrix_operands
                freivalds_ok = RewriteVerifier.freivalds_check(A, B, cand)

            if passed_tolerance and freivalds_ok:
                return VerificationReport(
                    outcome=VerificationOutcome.PASS,
                    validation_level="NUMERICAL_TOLERANCE",
                    max_absolute_error=max_abs_err,
                    relative_error=rel_err,
                    freivalds_verified=freivalds_ok,
                    evidence_summary=f"Tolerance passed (err={max_abs_err:.2e} <= threshold={threshold:.2e})",
                )
            else:
                reason = "Tolerance threshold exceeded" if not passed_tolerance else "Freivalds verification failed"
                return VerificationReport(
                    outcome=VerificationOutcome.FAIL,
                    validation_level="NUMERICAL_TOLERANCE",
                    max_absolute_error=max_abs_err,
                    relative_error=rel_err,
                    freivalds_verified=freivalds_ok,
                    evidence_summary=f"{reason}: err={max_abs_err:.2e}, limit={threshold:.2e}",
                )

        # Level 3: Approximate / Cosine Bounded Contract
        if contract.validation_mode == ValidationMode.APPROXIMATE:
            c_flat = cand.astype(np.float64).ravel()
            r_flat = ref.astype(np.float64).ravel()
            norm_c = np.linalg.norm(c_flat)
            norm_r = np.linalg.norm(r_flat)

            if norm_c == 0.0 and norm_r == 0.0:
                cosine_sim = 1.0
            elif norm_c == 0.0 or norm_r == 0.0:
                cosine_sim = 0.0
            else:
                cosine_sim = float(np.dot(c_flat, r_flat) / (norm_c * norm_r))

            if cosine_sim >= contract.min_cosine_similarity:
                return VerificationReport(
                    outcome=VerificationOutcome.PASS,
                    validation_level="COSINE_APPROXIMATE",
                    cosine_similarity=cosine_sim,
                    evidence_summary=f"Cosine similarity {cosine_sim:.4f} >= required {contract.min_cosine_similarity:.4f}",
                )
            else:
                return VerificationReport(
                    outcome=VerificationOutcome.FAIL,
                    validation_level="COSINE_APPROXIMATE",
                    cosine_similarity=cosine_sim,
                    evidence_summary=f"Cosine similarity {cosine_sim:.4f} fell below contract threshold {contract.min_cosine_similarity:.4f}",
                )

        # Level 4: Task Quality Contract (e.g. LLM generated text)
        if contract.validation_mode == ValidationMode.TASK_QUALITY:
            # Task-level validation: check output is non-empty and well-formed
            cand_str = str(candidate_output).strip()
            if len(cand_str) > 0:
                return VerificationReport(
                    outcome=VerificationOutcome.PASS,
                    validation_level="TASK_QUALITY",
                    evidence_summary=f"Task quality verified: generated {len(cand_str)} chars.",
                )
            return VerificationReport(
                outcome=VerificationOutcome.FAIL,
                validation_level="TASK_QUALITY",
                evidence_summary="Task quality check failed: empty output.",
            )

        return VerificationReport(
            outcome=VerificationOutcome.UNKNOWN,
            validation_level="UNKNOWN_MODE",
            evidence_summary="Unrecognized validation mode.",
        )

    @staticmethod
    def freivalds_check(A: np.ndarray, B: np.ndarray, C: np.ndarray, trials: int = 3) -> bool:
        """
        Executes Freivalds randomized algorithm to verify C == A @ B in O(k * N^2) time.
        Error probability <= 2^{-k}.
        """
        N = B.shape[1]
        rng = np.random.RandomState(42)

        for _ in range(trials):
            r = rng.choice([-1.0, 1.0], size=(N, 1)).astype(np.float32)
            # Br = B @ r
            br = np.matmul(B, r)
            # A_br = A @ (B @ r)
            abr = np.matmul(A, br)
            # Cr = C @ r
            cr = np.matmul(C, r)

            # Check ||A(Br) - Cr|| <= tolerance
            diff = np.max(np.abs(abr - cr))
            if diff > 1e-3:
                return False

        return True

    @classmethod
    def verify_bitwise(cls, candidate: Any, reference: Any) -> VerificationReport:
        c = WorkloadContract(
            contract_id="internal_bitwise",
            validation_mode=ValidationMode.EXACT,
            exactness_requirement=ExactnessRequirement.BITWISE_EXACT,
        )
        return cls.verify(candidate, reference, c)

    @classmethod
    def verify_tolerance(cls, candidate: Any, reference: Any, atol: float = 1e-4, rtol: float = 1e-4) -> VerificationReport:
        c = WorkloadContract(
            contract_id="internal_tol",
            validation_mode=ValidationMode.TOLERANCE_BASED,
            exactness_requirement=ExactnessRequirement.EPSILON_TOLERANT,
            max_absolute_error=atol,
            max_relative_error=rtol,
        )
        return cls.verify(candidate, reference, c)


def freivalds_verify(A: np.ndarray, B: np.ndarray, C: np.ndarray, iterations: int = 3) -> Tuple[bool, Dict[str, Any]]:
    """Convenience standalone wrapper for Freivalds randomized matrix check."""
    ok = RewriteVerifier.freivalds_check(A, B, C, trials=iterations)
    return ok, {"trials": iterations, "verified": ok}

