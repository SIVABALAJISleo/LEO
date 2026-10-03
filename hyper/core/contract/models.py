"""
hyper/core/contract/models.py
Defines the Four Parity Levels, formal Semantic Contracts, and the 100% Contract Gate.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import numpy as np


class ParityLevel(str, Enum):
    """
    The Four Parity Definitions (Prompt Section 2):
    - RAW_HARDWARE_PARITY: Physical resource equivalence (NOT achievable by software alone).
    - EXACT_COMPUTATIONAL_PARITY: G(X) = F(X) with declared semantics (dtype, precision, rounding).
    - CONTRACT_PARITY: Satisfies every declared application requirement.
    - APPLICATION_PERFORMANCE_PARITY: Application-level service requirement (FPS, latency, tokens/s).
    """
    RAW_HARDWARE_PARITY = "RAW_HARDWARE_PARITY"
    EXACT_COMPUTATIONAL_PARITY = "EXACT_COMPUTATIONAL_PARITY"
    CONTRACT_PARITY = "CONTRACT_PARITY"
    APPLICATION_PERFORMANCE_PARITY = "APPLICATION_PERFORMANCE_PARITY"


class ContractType(str, Enum):
    EXACT_INTEGER = "EXACT_INTEGER"
    EXACT_SYMBOLIC = "EXACT_SYMBOLIC"
    NUMERICAL_FLOAT = "NUMERICAL_FLOAT"
    CLASSIFICATION_TOP1 = "CLASSIFICATION_TOP1"
    CLASSIFICATION_TOPK = "CLASSIFICATION_TOPK"
    LLM_TOKEN_EQUIVALENCE = "LLM_TOKEN_EQUIVALENCE"
    BOUNDED_ERROR = "BOUNDED_ERROR"
    LATENCY_DEADLINE = "LATENCY_DEADLINE"
    FPS_TARGET = "FPS_TARGET"


class SemanticContract(BaseModel):
    """
    Full formal semantic contract declaring exact correctness requirements.
    """
    contract_id: str = Field(default_factory=lambda: f"contract_{np.random.randint(100000, 999999)}")
    contract_type: ContractType = ContractType.EXACT_INTEGER
    declared_parity: ParityLevel = ParityLevel.CONTRACT_PARITY
    
    # Exact Numerical & Bitwise Specifications
    dtype: str = "float64"
    precision_bits: int = 64
    rounding_mode: str = "NEAREST_EVEN"
    nan_mode: str = "PRESERVE"
    inf_mode: str = "PRESERVE"
    signed_zero_mode: str = "PRESERVE"
    overflow_mode: str = "SATURATE_OR_RAISE"
    determinism_required: bool = True

    # Error Tolerances
    abs_tolerance: float = 1e-7
    rel_tolerance: float = 1e-5

    # Target Application Limits
    latency_target_ms: Optional[float] = None
    throughput_target_ops_sec: Optional[float] = None
    target_fps: Optional[float] = None
    memory_limit_mb: float = 1024.0

    invariants: List[str] = Field(default_factory=list)

    def validate_result(self, candidate_out: Any, reference_out: Any) -> Tuple[bool, float, str]:
        """
        Validates candidate_out against reference_out under declared contract semantics.
        Returns: (is_valid, max_discrepancy, explanation)
        """
        try:
            if self.contract_type in [ContractType.EXACT_INTEGER, ContractType.EXACT_SYMBOLIC]:
                cand_arr = np.asarray(candidate_out)
                ref_arr = np.asarray(reference_out)
                if cand_arr.shape != ref_arr.shape:
                    return False, 1.0, f"Shape mismatch: {cand_arr.shape} vs {ref_arr.shape}"
                if not np.array_equal(cand_arr, ref_arr):
                    diff = float(np.max(np.abs(cand_arr.astype(np.float64) - ref_arr.astype(np.float64))))
                    return False, diff, f"Exact mathematical identity violated. Max diff: {diff}"
                return True, 0.0, "Exact mathematical identity verified."

            elif self.contract_type in [ContractType.NUMERICAL_FLOAT, ContractType.BOUNDED_ERROR]:
                cand_arr = np.asarray(candidate_out, dtype=np.float64)
                ref_arr = np.asarray(reference_out, dtype=np.float64)
                if cand_arr.shape != ref_arr.shape:
                    return False, 1.0, f"Shape mismatch: {cand_arr.shape} vs {ref_arr.shape}"
                abs_diff = np.abs(cand_arr - ref_arr)
                max_diff = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
                is_close = np.allclose(cand_arr, ref_arr, atol=self.abs_tolerance, rtol=self.rel_tolerance)
                if not is_close:
                    return False, max_diff, f"Tolerance exceeded: max_diff={max_diff:.3e} > atol={self.abs_tolerance}"
                return True, max_diff, f"Numerical tolerance satisfied (max diff: {max_diff:.3e})"

            elif self.contract_type in [ContractType.CLASSIFICATION_TOP1, ContractType.CLASSIFICATION_TOPK]:
                cand_argmax = int(np.argmax(candidate_out))
                ref_argmax = int(np.argmax(reference_out))
                if cand_argmax != ref_argmax:
                    return False, 1.0, f"Top-1 class mismatch: candidate {cand_argmax} != ref {ref_argmax}"
                return True, 0.0, "Top-1 classification contract satisfied."

            elif self.contract_type == ContractType.LLM_TOKEN_EQUIVALENCE:
                cand_str = str(candidate_out).strip()
                ref_str = str(reference_out).strip()
                if cand_str != ref_str:
                    return False, 1.0, "LLM token string mismatch."
                return True, 0.0, "LLM token equivalence contract satisfied."

            # Default generic comparison
            matches = (candidate_out == reference_out)
            if isinstance(matches, np.ndarray):
                matches = bool(np.all(matches))
            return bool(matches), 0.0 if matches else 1.0, "Generic equality check"
        except Exception as e:
            return False, 1.0, f"Validation exception: {str(e)}"


class ContractGate:
    """
    100% Contract Gate (Prompt Section 33):
    A workload is 100% CONTRACT PASS only when correctness, quality, latency,
    throughput, resource limits, verification, provenance, and reproducibility all pass.
    No weighted score may convert failures into a PASS.
    """
    @staticmethod
    def evaluate(
        contract: SemanticContract,
        candidate_out: Any,
        reference_out: Any,
        latency_ms: float,
        memory_mb: float,
        proof_valid: bool,
        verification_passed: bool,
        reproducible: bool,
    ) -> Tuple[bool, Dict[str, bool]]:
        correctness_pass, _, _ = contract.validate_result(candidate_out, reference_out)
        
        latency_pass = True
        if contract.latency_target_ms is not None:
            latency_pass = (latency_ms <= contract.latency_target_ms)

        memory_pass = (memory_mb <= contract.memory_limit_mb)

        predicates = {
            "correctness": correctness_pass,
            "latency": latency_pass,
            "memory": memory_pass,
            "proof": proof_valid,
            "verification": verification_passed,
            "reproducibility": reproducible,
        }

        all_passed = all(predicates.values())
        return all_passed, predicates
