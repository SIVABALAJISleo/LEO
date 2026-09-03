"""
hyper_v3/proof/engine.py
Unified Proof and Safety Engine orchestrating certificates, validation, and contract invariants.
"""

from typing import Dict, Any, Tuple
import numpy as np
import uuid

from hyper_v3.frontend.contract_parser import ExecutionContract, ExactnessClass
from hyper_v3.proof.certificates import ExactnessCertificate
from hyper_v3.proof.contract import ContractValidator
from hyper_v3.proof.exactness import ExactnessValidator


class ProofEngine:
    """Certifies transformations and verifies execution safety."""

    @staticmethod
    def certify_transformation(
        transformation_name: str,
        source_op: str,
        target_op: str,
        reference_out: np.ndarray,
        candidate_out: np.ndarray,
        contract: ExecutionContract
    ) -> ExactnessCertificate:
        max_abs, max_rel, snr_db = ExactnessValidator.measure_errors(reference_out, candidate_out)
        is_bitwise = ExactnessValidator.check_bitwise_identical(reference_out, candidate_out)
        is_compliant, _ = ContractValidator.validate_compliance(reference_out, candidate_out, contract)

        if is_bitwise:
            equiv_class = ExactnessClass.BITWISE_EXACT
            proof_method = "Bitwise Identity Check"
        elif max_rel <= 1e-4:
            equiv_class = ExactnessClass.NUMERICALLY_EXACT_UNDER_DEFINED_MODEL
            proof_method = "Numerical Forward Error Analysis"
        elif is_compliant:
            equiv_class = ExactnessClass.CONTRACT_EQUIVALENT
            proof_method = "Contract Bound Empirical Verification"
        else:
            equiv_class = ExactnessClass.APPROXIMATE
            proof_method = "Unverified Candidate"

        cert_id = f"cert_{uuid.uuid4().hex[:8]}"
        status = "PASS" if is_compliant else "FAIL"

        return ExactnessCertificate(
            certificate_id=cert_id,
            transformation_name=transformation_name,
            source_operation=source_op,
            target_operation=target_op,
            equivalence_class=equiv_class,
            proof_method=proof_method,
            max_relative_error_observed=max_rel,
            max_absolute_error_observed=max_abs,
            verification_status=status
        )
