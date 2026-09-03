"""
hyper_v3/proof/contract.py
Validates candidate outputs against the immutable bounds in an ExecutionContract.
"""

from typing import Dict, Any, Tuple
import numpy as np

from hyper_v3.frontend.contract_parser import ExecutionContract, ExecutionTrack
from hyper_v3.proof.exactness import ExactnessValidator


class ContractValidator:
    """Verifies that candidate outputs strictly comply with contract limits."""

    @staticmethod
    def validate_compliance(reference: np.ndarray, candidate: np.ndarray, contract: ExecutionContract) -> Tuple[bool, Dict[str, Any]]:
        max_abs, max_rel, snr_db = ExactnessValidator.measure_errors(reference, candidate)

        if contract.track == ExecutionTrack.EXACT:
            # Exact track requires strict error <= 1e-4 or bitwise
            is_valid = (max_rel <= 1e-4) or (max_abs <= 1e-4)
        else:
            is_valid = (max_rel <= contract.max_relative_error) and (max_abs <= contract.max_absolute_error) and (snr_db >= contract.min_snr_db)

        details = {
            "workload_name": contract.workload_name,
            "track": contract.track.value,
            "max_absolute_error": max_abs,
            "max_relative_error": max_rel,
            "snr_db": snr_db,
            "allowed_max_rel_error": contract.max_relative_error,
            "is_compliant": is_valid
        }
        return is_valid, details
