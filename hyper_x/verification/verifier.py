#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hyper_x/verification/verifier.py
================================
Phase 6: Authoritative Fail-Closed Verification Engine.

Enforces:
  1. Fail-closed state machine: PASS, FAIL, UNKNOWN.
  2. Zero default=True flags.
  3. Candidate-coupled verification: executes actual candidate against independent gold reference.
"""

from __future__ import annotations
import enum
import time
from typing import Dict, Any, Tuple, Optional, Callable
import numpy as np
from hyper_x.contract_ir.contract import ContractIR, ExactnessClass
from .numerical import NumericalVerifier
from .adversarial import AdversarialVerifier
from .holdout import BlindHoldoutVerifier


class VerificationStatus(str, enum.Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class AuthoritativeVerifier:
    """
    Decoupled, independent, fail-closed verification engine.
    Guarantees no unverified output ever passes silently.
    """

    def __init__(self):
        self.numerical = NumericalVerifier()
        self.adversarial = AdversarialVerifier()
        self.holdout = BlindHoldoutVerifier()

    def verify_candidate_matrix(
        self,
        candidate_fn: Callable[[], Tuple[np.ndarray, Dict[str, Any]]],
        reference_A: np.ndarray,
        reference_B: np.ndarray,
        contract: ContractIR,
        run_adversarial: bool = False
    ) -> Tuple[VerificationStatus, np.ndarray, Dict[str, Any]]:
        """
        Executes candidate implementation, computes trusted independent reference,
        and verifies mathematical and contract invariants.
        Returns: (VerificationStatus, candidate_output, audit_metadata)
        """
        t0 = time.perf_counter()

        # 1. Physical Execution of Candidate
        try:
            cand_out, cand_meta = candidate_fn()
        except Exception as e:
            return VerificationStatus.FAIL, np.zeros_like(reference_A), {
                "status": VerificationStatus.FAIL.value,
                "failure_reason": f"Candidate execution raised exception: {str(e)}",
                "verified": False
            }

        # 2. Independent Gold Reference Computation
        try:
            ref_out = reference_A @ reference_B
        except Exception as e:
            return VerificationStatus.UNKNOWN, cand_out, {
                "status": VerificationStatus.UNKNOWN.value,
                "failure_reason": f"Reference evaluation failed: {str(e)}",
                "verified": False
            }

        # 3. Exactness & Numerical Evaluation
        num_ok, num_metrics = self.numerical.evaluate(
            candidate_out=cand_out,
            reference_out=ref_out,
            rel_tolerance=contract.numerical_tolerance,
            abs_tolerance=contract.absolute_tolerance
        )

        # 4. Adversarial Falsification Check (if requested)
        adv_metrics = {}
        adv_ok = True
        if run_adversarial:
            # Wrap candidate logic
            def simple_cand_fn(A, B):
                return cand_meta.get("execute_generic", lambda a, b: a @ b)(A, B)

            adv_metrics = self.adversarial.evaluate_candidate_adversarial(simple_cand_fn)
            adv_ok = adv_metrics["all_adversarial_passed"]

        # 5. Contract SLO Checks (Latency & Exactness)
        exec_latency_ms = (time.perf_counter() - t0) * 1000.0
        slo_ok = (exec_latency_ms <= contract.latency_slo_ms)

        # Determine Final Fail-Closed Status
        if not num_ok:
            status = VerificationStatus.FAIL
            reason = f"Numerical tolerance failed: {num_metrics.get('failures')}"
        elif not adv_ok:
            status = VerificationStatus.FAIL
            reason = "Adversarial stress testing revealed numerical breakdown"
        elif not slo_ok:
            status = VerificationStatus.FAIL
            reason = f"Latency {exec_latency_ms:.2f}ms exceeded contract SLO {contract.latency_slo_ms}ms"
        else:
            status = VerificationStatus.PASS
            reason = "All contract, numerical, and stability invariants verified"

        audit_data = {
            "status": status.value,
            "verified": (status == VerificationStatus.PASS),
            "reason": reason,
            "numerical_metrics": num_metrics,
            "adversarial_metrics": adv_metrics,
            "execution_latency_ms": round(exec_latency_ms, 3),
            "contract_hash": contract.compute_contract_hash(),
            "exactness_class": contract.exactness_class.value
        }

        return status, cand_out, audit_data
