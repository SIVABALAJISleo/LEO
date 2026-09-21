"""
hyper/universal/contracts/contract_validator.py
===============================================
Validates whether a computational result and execution profile satisfy a UniversalContract.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from .universal_contract import UniversalContract, ContractCorrectness


class ContractValidator:
    """Validates contract satisfaction without compromises or silent precision downgrades."""

    @staticmethod
    def validate(
        candidate_output: Any,
        reference_output: Any,
        contract: UniversalContract,
        execution_profile: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, List[str]]:
        violations: List[str] = []

        # 1. Output existence & structure
        if candidate_output is None and reference_output is not None:
            violations.append("Candidate output is None but reference output exists.")
            return False, violations

        # 2. Shape and type check for ndarray
        if isinstance(candidate_output, np.ndarray) and isinstance(reference_output, np.ndarray):
            if candidate_output.shape != reference_output.shape:
                violations.append(f"Shape mismatch: candidate {candidate_output.shape} != reference {reference_output.shape}")
                return False, violations

            diff = np.abs(candidate_output - reference_output)
            abs_err = float(np.max(diff)) if diff.size > 0 else 0.0
            ref_mag = np.abs(reference_output)
            with np.errstate(divide="ignore", invalid="ignore"):
                rel_err_arr = np.where(ref_mag > 1e-12, diff / ref_mag, diff)
            rel_err = float(np.max(rel_err_arr)) if rel_err_arr.size > 0 else 0.0

            if contract.is_exact():
                if abs_err > 0.0:
                    violations.append(f"Contract requires EXACT result, but max abs error is {abs_err:.4e}")
            else:
                if contract.numeric_tolerance > 0 and abs_err > contract.numeric_tolerance:
                    violations.append(f"Max abs error {abs_err:.4e} exceeds tolerance {contract.numeric_tolerance:.4e}")
                if contract.relative_tolerance > 0 and rel_err > contract.relative_tolerance:
                    violations.append(f"Max relative error {rel_err:.4e} exceeds relative tolerance {contract.relative_tolerance:.4e}")

        elif isinstance(candidate_output, (int, float, complex)) and isinstance(reference_output, (int, float, complex)):
            diff = abs(candidate_output - reference_output)
            if contract.is_exact() and diff != 0:
                violations.append(f"Exact match required, got difference {diff}")
            elif contract.numeric_tolerance > 0 and diff > contract.numeric_tolerance:
                violations.append(f"Scalar difference {diff} exceeds tolerance {contract.numeric_tolerance}")

        elif candidate_output != reference_output:
            violations.append("Candidate output does not match reference output.")

        # 3. Execution profile constraints (latency, memory, energy)
        if execution_profile:
            latency_ms = execution_profile.get("latency_ms")
            if contract.latency_requirement_ms and latency_ms and latency_ms > contract.latency_requirement_ms:
                violations.append(f"Latency {latency_ms:.2f}ms exceeds requirement {contract.latency_requirement_ms:.2f}ms")

            mem_mb = execution_profile.get("memory_mb")
            if contract.memory_requirement_mb and mem_mb and mem_mb > contract.memory_requirement_mb:
                violations.append(f"Peak memory {mem_mb:.2f}MB exceeds requirement {contract.memory_requirement_mb:.2f}MB")

        is_satisfied = len(violations) == 0
        return is_satisfied, violations
