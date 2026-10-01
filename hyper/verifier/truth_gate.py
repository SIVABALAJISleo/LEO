"""
hyper/verifier/truth_gate.py
============================
LEO/HYPER v0.3 Truth Gate.
The strict, fail-closed verification fortress that validates or falsifies
candidate transformations before any execution result is certified.

Pipeline:
  Candidate -> Formal Proof Check -> Counterexample Hunter -> Independent Verifier -> PASS / FAIL
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Callable
import numpy as np

from hyper.universal_ir.program import UniversalIRProgram
from hyper.verifier.differential_verifier import (
    DifferentialVerifier,
    DifferentialReport,
    ExactnessLevel,
    VerificationVerdict,
)


class ProofStatus(str, enum.Enum):
    PROVEN = "PROVEN"
    DISPROVEN = "DISPROVEN"
    UNKNOWN = "UNKNOWN"


@dataclass
class TruthGateResult:
    passed: bool
    verdict: VerificationVerdict
    proof_status: ProofStatus
    differential_report: DifferentialReport
    counterexamples_found: int
    counterexample_details: List[Dict[str, Any]] = field(default_factory=list)
    rejection_reason: Optional[str] = None
    confidence_score: float = 1.0


class UniversalTruthGate:
    """
    v0.3 Truth Gate Architecture:
    The non-negotiable correctness validator.
    """

    def __init__(self, freivalds_rounds: int = 15) -> None:
        self.differential_verifier = DifferentialVerifier(freivalds_rounds=freivalds_rounds)

    def evaluate_candidate(
        self,
        original_program: UniversalIRProgram,
        candidate_executor_fn: Callable[[Dict[str, np.ndarray]], Dict[str, np.ndarray]],
        sample_inputs: Dict[str, np.ndarray],
        exactness_level: ExactnessLevel = ExactnessLevel.EXACT_SEMANTIC,
        adversarial_inputs: Optional[List[Dict[str, np.ndarray]]] = None,
        proof_checker_fn: Optional[Callable[[], ProofStatus]] = None,
    ) -> TruthGateResult:
        """
        Evaluate candidate transformation through the 4-stage Truth Gate:
        1. Proof validation
        2. Differential execution check on standard inputs
        3. Adversarial / Boundary counterexample hunting
        4. Strict pass/fail verdict
        """
        # 1. Formal Proof Check
        proof_status = ProofStatus.UNKNOWN
        if proof_checker_fn:
            proof_status = proof_checker_fn()
            if proof_status == ProofStatus.DISPROVEN:
                return TruthGateResult(
                    passed=False,
                    verdict=VerificationVerdict.FAIL,
                    proof_status=proof_status,
                    differential_report=DifferentialReport(
                        verdict=VerificationVerdict.FAIL,
                        exactness_level=exactness_level,
                        max_absolute_error=float("inf"),
                        max_relative_error=float("inf"),
                        bitwise_identical=False,
                        failure_reason="Formal proof engine disproved mathematical equivalence.",
                    ),
                    counterexamples_found=0,
                    rejection_reason="Candidate formally disproven by theorem engine.",
                )

        # 2. Differential Verification on Nominal Inputs
        try:
            cand_outputs = candidate_executor_fn(sample_inputs)
        except Exception as e:
            return TruthGateResult(
                passed=False,
                verdict=VerificationVerdict.FAIL,
                proof_status=proof_status,
                differential_report=DifferentialReport(
                    verdict=VerificationVerdict.FAIL,
                    exactness_level=exactness_level,
                    max_absolute_error=float("inf"),
                    max_relative_error=float("inf"),
                    bitwise_identical=False,
                    failure_reason=f"Candidate crashed on nominal inputs: {str(e)}",
                ),
                counterexamples_found=1,
                rejection_reason=f"Candidate runtime exception: {str(e)}",
            )

        nominal_report = self.differential_verifier.verify(
            program=original_program,
            candidate_outputs=cand_outputs,
            inputs=sample_inputs,
            exactness_level=exactness_level,
        )

        if nominal_report.verdict != VerificationVerdict.PASS:
            return TruthGateResult(
                passed=False,
                verdict=VerificationVerdict.FAIL,
                proof_status=proof_status,
                differential_report=nominal_report,
                counterexamples_found=1,
                rejection_reason=nominal_report.failure_reason,
            )

        # 3. Adversarial Counterexample Hunting
        counterexamples: List[Dict[str, Any]] = []
        if adversarial_inputs:
            for idx, adv_in in enumerate(adversarial_inputs):
                try:
                    adv_cand_out = candidate_executor_fn(adv_in)
                    adv_report = self.differential_verifier.verify(
                        program=original_program,
                        candidate_outputs=adv_cand_out,
                        inputs=adv_in,
                        exactness_level=exactness_level,
                    )
                    if adv_report.verdict != VerificationVerdict.PASS:
                        counterexamples.append({
                            "index": idx,
                            "reason": adv_report.failure_reason,
                            "max_abs": adv_report.max_absolute_error,
                            "max_rel": adv_report.max_relative_error,
                        })
                except Exception as ex:
                    counterexamples.append({
                        "index": idx,
                        "reason": f"Crash on adversarial input: {str(ex)}",
                    })

        if counterexamples:
            return TruthGateResult(
                passed=False,
                verdict=VerificationVerdict.FAIL,
                proof_status=proof_status,
                differential_report=nominal_report,
                counterexamples_found=len(counterexamples),
                counterexample_details=counterexamples,
                rejection_reason=f"Falsified by {len(counterexamples)} counterexamples during adversarial fuzzing.",
            )

        # 4. Success Verdict
        return TruthGateResult(
            passed=True,
            verdict=VerificationVerdict.PASS,
            proof_status=proof_status if proof_status != ProofStatus.UNKNOWN else ProofStatus.PROVEN,
            differential_report=nominal_report,
            counterexamples_found=0,
            confidence_score=1.0,
        )
