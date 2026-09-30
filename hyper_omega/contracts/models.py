"""
hyper_omega/contracts/models.py
Defines formal workload contracts, parity levels, and contract firewall validation.
"""
from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import numpy as np


class ParityLevel(str, Enum):
    LEVEL_A = "LEVEL_A_RAW_HARDWARE"          # Physical silicon resource parity (NOT claimed)
    LEVEL_B = "LEVEL_B_EXACT_COMPUTATIONAL"    # G(X) = F(X) zero-approximation mathematical parity
    LEVEL_C = "LEVEL_C_CONTRACT"               # Application tolerance, invariant, accuracy parity
    LEVEL_D = "LEVEL_D_APPLICATION_PERFORMANCE"# Latency, throughput, FPS target satisfaction


class ContractType(str, Enum):
    EXACT_INTEGER = "EXACT_INTEGER"
    EXACT_SYMBOLIC = "EXACT_SYMBOLIC"
    NUMERICAL_FLOAT = "NUMERICAL_FLOAT"
    PERCEPTUAL = "PERCEPTUAL"
    CLASSIFICATION_TOP1 = "CLASSIFICATION_TOP1"
    CLASSIFICATION_TOPK = "CLASSIFICATION_TOPK"
    LLM_TOKEN_EQUIVALENCE = "LLM_TOKEN_EQUIVALENCE"
    LATENCY_DEADLINE = "LATENCY_DEADLINE"


class WorkloadContract(BaseModel):
    """Formal mathematical and operational contract for any computational workload."""
    contract_id: str = Field(default_factory=lambda: f"contract_{np.random.randint(100000, 999999)}")
    contract_type: ContractType = ContractType.EXACT_INTEGER
    parity_level: ParityLevel = ParityLevel.LEVEL_B
    exact_match_required: bool = True
    abs_tolerance: float = 1e-7
    rel_tolerance: float = 1e-5
    output_shape: Optional[Tuple[int, ...]] = None
    output_dtype: Optional[str] = "float64"
    invariants: List[str] = Field(default_factory=list)
    latency_target_ms: Optional[float] = None
    throughput_target_ops_sec: Optional[float] = None
    memory_limit_mb: Optional[float] = 1024.0

    def validate_output(self, candidate_out: Any, reference_out: Any) -> Tuple[bool, float, str]:
        """
        Validates whether candidate_out satisfies this contract against reference_out.
        Returns: (is_valid, max_discrepancy, reason_string)
        """
        try:
            if self.contract_type in [ContractType.EXACT_INTEGER, ContractType.EXACT_SYMBOLIC]:
                cand_arr = np.asarray(candidate_out)
                ref_arr = np.asarray(reference_out)
                if cand_arr.shape != ref_arr.shape:
                    return False, 1.0, f"Shape mismatch: {cand_arr.shape} vs {ref_arr.shape}"
                if not np.array_equal(cand_arr, ref_arr):
                    diff = np.max(np.abs(cand_arr.astype(np.float64) - ref_arr.astype(np.float64)))
                    return False, float(diff), f"Exact match failed. Max diff: {diff}"
                return True, 0.0, "Exact mathematical identity verified."

            elif self.contract_type == ContractType.NUMERICAL_FLOAT:
                cand_arr = np.asarray(candidate_out, dtype=np.float64)
                ref_arr = np.asarray(reference_out, dtype=np.float64)
                if cand_arr.shape != ref_arr.shape:
                    return False, 1.0, f"Shape mismatch: {cand_arr.shape} vs {ref_arr.shape}"
                
                abs_diff = np.abs(cand_arr - ref_arr)
                max_abs = float(np.max(abs_diff)) if abs_diff.size > 0 else 0.0
                
                is_close = np.allclose(cand_arr, ref_arr, atol=self.abs_tolerance, rtol=self.rel_tolerance)
                if not is_close:
                    return False, max_abs, f"Numerical tolerance exceeded: max abs diff {max_abs} > atol {self.abs_tolerance}"
                return True, max_abs, f"Numerical tolerance satisfied (max diff: {max_abs:.3e})"

            elif self.contract_type in [ContractType.CLASSIFICATION_TOP1, ContractType.CLASSIFICATION_TOPK]:
                cand_argmax = int(np.argmax(candidate_out))
                ref_argmax = int(np.argmax(reference_out))
                if cand_argmax != ref_argmax:
                    return False, 1.0, f"Argmax class mismatch: candidate {cand_argmax} vs ref {ref_argmax}"
                return True, 0.0, "Classification contract satisfied."

            elif self.contract_type == ContractType.LLM_TOKEN_EQUIVALENCE:
                cand_str = str(candidate_out).strip()
                ref_str = str(reference_out).strip()
                if cand_str != ref_str:
                    return False, 1.0, f"Token output string mismatch."
                return True, 0.0, "Token equivalence contract satisfied."

            # Default general equality fallback
            matches = (candidate_out == reference_out)
            if isinstance(matches, np.ndarray):
                matches = bool(np.all(matches))
            return bool(matches), 0.0 if matches else 1.0, "Generic equality check"
        except Exception as e:
            return False, 1.0, f"Validation exception: {str(e)}"


class ContractFirewall:
    """Firewall ensuring no unproven shortcut bypasses contract constraints."""
    @staticmethod
    def enforce(contract: WorkloadContract, candidate_output: Any, reference_output: Any) -> bool:
        valid, _, _ = contract.validate_output(candidate_output, reference_output)
        return valid
