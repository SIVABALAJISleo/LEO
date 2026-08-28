"""
hyper_cel/contract/verifier.py
=============================================================================
HYPER-CEL: Contract Verifier & Residual Guard
=============================================================================
Enforces non-negotiable verification.
If candidate output satisfies the contract -> EMIT (PASS).
If candidate output fails the contract -> TRIGGER EXACT FALLBACK (FAIL -> COMPUTE MORE).
"""

from typing import Dict, Any, Tuple, Callable, Optional
from hyper_cel.contract.contract import ComputationalContract, ExactContract

class ContractVerifier:
    """
    Verification guardian that checks candidates against contract tolerances.
    """

    def __init__(self, contract: Optional[ComputationalContract] = None):
        self.contract = contract or ExactContract()

    def verify_or_fallback(
        self,
        candidate_output: Any,
        reference_or_oracle: Any,
        exact_fallback_fn: Optional[Callable[[], Any]] = None
    ) -> Tuple[Any, bool, Dict[str, Any]]:
        """
        Verifies candidate against reference. If verification fails and exact_fallback_fn
        is provided, runs fallback and returns exact result.
        Returns: (final_output, verified_on_first_pass, verification_telemetry)
        """
        passed, quality, telemetry = self.contract.validate(candidate_output, reference_or_oracle)

        if passed:
            telemetry["status"] = "PASS"
            telemetry["fallback_triggered"] = False
            return candidate_output, True, telemetry
        
        # Verification failed -> Must compute more / run exact fallback
        telemetry["status"] = "FAIL"
        if exact_fallback_fn is not None:
            telemetry["fallback_triggered"] = True
            exact_result = exact_fallback_fn()
            return exact_result, False, telemetry
        else:
            telemetry["fallback_triggered"] = False
            return candidate_output, False, telemetry
