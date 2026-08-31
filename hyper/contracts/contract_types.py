"""
hyper/contracts/contract_types.py
==================================
Universal Contract Type Definitions for LEO/HYPER.
Enforces immutable, declarative application contracts.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Union


class ContractClass(str, Enum):
    EXACT = "EXACT"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    BOUNDED_ERROR = "BOUNDED_ERROR"
    PERCEPTUAL = "PERCEPTUAL"
    APPLICATION = "APPLICATION"
    PREDICTIVE = "PREDICTIVE"
    CACHED = "CACHED"
    REDUCED_WORK = "REDUCED_WORK"


class VerificationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNVERIFIED = "UNVERIFIED"


class ParityTier(str, Enum):
    TIER_A_RAW_HARDWARE = "RAW_HARDWARE_PARITY"
    TIER_B_EXACT_COMPUTATIONAL = "EXACT_COMPUTATIONAL_PARITY"
    TIER_C_CONTRACT = "CONTRACT_PARITY"
    TIER_D_APPLICATION = "APPLICATION_PARITY"


@dataclass(frozen=True)
class UniversalContract:
    """
    Immutable specification of an execution contract.
    The optimizer cannot secretly weaken this contract.
    """
    contract_id: str
    contract_class: ContractClass = ContractClass.BOUNDED_ERROR
    input_definition: str = "tensor"
    output_definition: str = "tensor"
    
    # Quantitative thresholds
    error_bound_eps: float = 0.01
    perceptual_ssim_min: float = 0.95
    perceptual_psnr_min: float = 30.0
    max_latency_ms: float = 50.0
    min_fps_requirement: float = 30.0
    min_throughput_tokens_sec: float = 20.0
    memory_limit_mb: float = 8192.0
    energy_drift_max: float = 0.001
    
    # Requirement flags
    require_determinism: bool = False
    allow_approximation: bool = True
    allow_cache_reuse: bool = True
    allow_speculative_draft: bool = True

    def dominates(self, other: "UniversalContract") -> bool:
        """
        Returns True if this contract is strictly equal to or tighter than 'other'.
        """
        if self.contract_class != other.contract_class:
            # EXACT dominates all
            if self.contract_class == ContractClass.EXACT:
                return True
            return False
            
        if self.error_bound_eps > other.error_bound_eps:
            return False
        if self.perceptual_ssim_min < other.perceptual_ssim_min:
            return False
        if self.max_latency_ms > other.max_latency_ms:
            return False
        return True
