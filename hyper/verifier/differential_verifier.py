"""
hyper/verifier/differential_verifier.py
=======================================
Differential Verifier for LEO/HYPER.
Directly executes CandidateExecutor vs UniversalReferenceExecutor,
evaluating bitwise identity, exact semantic equality, Freivalds randomized matrix check,
and contract-specified tolerance bounds.
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
import numpy as np

from hyper.universal_ir.program import UniversalIRProgram
from hyper.executor.reference_executor import UniversalReferenceExecutor
from hyper.semantics.types import ExactnessLevel, VerificationVerdict


@dataclass
class DifferentialReport:
    verdict: VerificationVerdict
    exactness_level: ExactnessLevel
    max_absolute_error: float
    max_relative_error: float
    bitwise_identical: bool
    freivalds_passed: Optional[bool] = None
    freivalds_rounds: int = 0
    mismatched_outputs: List[str] = field(default_factory=list)
    failure_reason: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


class DifferentialVerifier:
    """
    Segregated, independent differential verifier.
    Compares candidate output against the canonical UniversalReferenceExecutor.
    """

    def __init__(self, freivalds_rounds: int = 15) -> None:
        self.reference_executor = UniversalReferenceExecutor()
        self.freivalds_rounds = freivalds_rounds

    def verify(
        self,
        program: UniversalIRProgram,
        candidate_outputs: Dict[str, np.ndarray],
        inputs: Dict[str, np.ndarray],
        exactness_level: ExactnessLevel = ExactnessLevel.EXACT_SEMANTIC,
        abs_tolerance: float = 1e-7,
        rel_tolerance: float = 1e-5,
    ) -> DifferentialReport:
        """
        Executes reference program on inputs, then differentially checks candidate outputs.
        """
        try:
            ref_outputs = self.reference_executor.execute(program, inputs)
        except Exception as e:
            return DifferentialReport(
                verdict=VerificationVerdict.FAIL,
                exactness_level=exactness_level,
                max_absolute_error=float("inf"),
                max_relative_error=float("inf"),
                bitwise_identical=False,
                failure_reason=f"Reference executor crashed: {str(e)}",
            )

        max_abs = 0.0
        max_rel = 0.0
        all_bitwise = True
        mismatched: List[str] = []
        details: Dict[str, Any] = {}

        for out_name in program.outputs:
            if out_name not in candidate_outputs:
                return DifferentialReport(
                    verdict=VerificationVerdict.FAIL,
                    exactness_level=exactness_level,
                    max_absolute_error=float("inf"),
                    max_relative_error=float("inf"),
                    bitwise_identical=False,
                    failure_reason=f"Candidate missing output '{out_name}'",
                )

            cand = candidate_outputs[out_name]
            ref = ref_outputs[out_name]

            if cand.shape != ref.shape:
                return DifferentialReport(
                    verdict=VerificationVerdict.FAIL,
                    exactness_level=exactness_level,
                    max_absolute_error=float("inf"),
                    max_relative_error=float("inf"),
                    bitwise_identical=False,
                    mismatched_outputs=[out_name],
                    failure_reason=f"Shape mismatch on '{out_name}': candidate {cand.shape} != reference {ref.shape}",
                )

            # Check bitwise identity
            is_bitwise = bool(np.array_equal(cand, ref, equal_nan=True))
            if not is_bitwise:
                all_bitwise = False

            # Error calculation
            if np.iscomplexobj(cand) or np.iscomplexobj(ref):
                abs_diff = np.abs(cand - ref)
                ref_mag = np.abs(ref)
            else:
                abs_diff = np.abs(cand.astype(np.float64) - ref.astype(np.float64))
                ref_mag = np.abs(ref.astype(np.float64))
            curr_max_abs = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
            rel_diff = abs_diff / np.maximum(ref_mag, 1e-12)
            curr_max_rel = float(np.max(rel_diff)) if rel_diff.size > 0 else 0.0

            if curr_max_abs > max_abs:
                max_abs = curr_max_abs
            if curr_max_rel > max_rel:
                max_rel = curr_max_rel

            details[out_name] = {
                "max_abs": curr_max_abs,
                "max_rel": curr_max_rel,
                "bitwise": is_bitwise,
            }

            # Level check
            if exactness_level == ExactnessLevel.EXACT_BITWISE:
                if not is_bitwise:
                    mismatched.append(out_name)
            elif exactness_level == ExactnessLevel.EXACT_SEMANTIC:
                # Semantic equality requires zero numerical drift or <= 1e-7
                if curr_max_abs > 1e-7 and not is_bitwise:
                    mismatched.append(out_name)
            elif exactness_level == ExactnessLevel.NUMERIC_TOLERANCE:
                if curr_max_abs > abs_tolerance and curr_max_rel > rel_tolerance:
                    mismatched.append(out_name)

        verdict = VerificationVerdict.PASS if not mismatched else VerificationVerdict.FAIL
        failure_msg = None
        if verdict == VerificationVerdict.FAIL:
            failure_msg = f"Tolerances exceeded for outputs: {mismatched}. Max abs={max_abs:.3e}, max rel={max_rel:.3e}"

        return DifferentialReport(
            verdict=verdict,
            exactness_level=exactness_level,
            max_absolute_error=max_abs,
            max_relative_error=max_rel,
            bitwise_identical=all_bitwise,
            mismatched_outputs=mismatched,
            failure_reason=failure_msg,
            details=details,
        )

    def verify_freivalds_matmul(
        self,
        A: np.ndarray,
        B: np.ndarray,
        C_candidate: np.ndarray,
        rounds: int = 15,
        tolerance: float = 1e-5,
    ) -> Tuple[bool, float, Dict[str, Any]]:
        """
        Freivalds O(k*N^2) randomized matrix multiplication verifier.
        Tests: A @ (B @ r) == C_candidate @ r for random vectors r in {-1, 1}^N.
        Probability of false acceptance: 2^(-k) (for k=15: < 0.00003).
        """
        M, K = A.shape
        K2, N = B.shape
        if K != K2 or C_candidate.shape != (M, N):
            return False, 1.0, {"reason": f"Dimension mismatch: A({A.shape}) @ B({B.shape}) vs C({C_candidate.shape})"}

        max_err = 0.0
        for r_idx in range(rounds):
            r = np.random.choice([-1.0, 1.0], size=(N, 1)).astype(np.float64)
            Br = np.matmul(B.astype(np.float64), r)
            ABr = np.matmul(A.astype(np.float64), Br)
            Cr = np.matmul(C_candidate.astype(np.float64), r)

            diff = float(np.max(np.abs(ABr - Cr)))
            scale = max(float(np.max(np.abs(ABr))), 1e-9)
            rel_err = diff / scale

            if rel_err > max_err:
                max_err = rel_err
            if rel_err > tolerance:
                return False, max_err, {
                    "failed_round": r_idx + 1,
                    "rel_err": rel_err,
                    "tolerance": tolerance,
                }

        confidence = 1.0 - (0.5 ** rounds)
        return True, max_err, {
            "rounds_passed": rounds,
            "confidence": confidence,
            "max_rel_error": max_err,
        }
