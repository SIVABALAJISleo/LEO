"""
hyper_mvc_dar/contract.py
Multi-dimensional contract system controlling allowable mathematical and algorithmic transformations.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Any


class ContractClass(Enum):
    EXACT = "exact"                                  # Bit-level / standard roundoff identical
    NUMERICALLY_BOUNDED = "numerically_bounded"      # ||y - y*|| / ||y*|| <= epsilon
    PERCEPTUALLY_BOUNDED = "perceptually_bounded"    # SSIM >= Q_min, PSNR >= P_min
    STATISTICALLY_BOUNDED = "statistically_bounded"  # Confidence interval / standard error <= sigma
    APPLICATION_EQUIVALENT = "application_equivalent"# Same discrete action / top-1 label
    RESOURCE_CONSTRAINED = "resource_constrained"    # Strictly enforce memory/latency envelope


class ExecutionTrack(Enum):
    TRACK_A_EXACT = "TRACK_A_EXACT"        # Reference mathematical baseline
    TRACK_B_CONTRACT = "TRACK_B_CONTRACT"  # Minimum verified computation path


@dataclass
class ExecutionContract:
    contract_class: ContractClass = ContractClass.NUMERICALLY_BOUNDED
    track: ExecutionTrack = ExecutionTrack.TRACK_B_CONTRACT
    relative_error: float = 0.01
    quality_threshold: float = 0.95
    latency_limit_ms: float = 50.0
    throughput_limit_fps: float = 30.0
    memory_limit_mb: float = 2048.0
    verification_required: bool = True
    fallback_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_exact(self) -> bool:
        return self.contract_class == ContractClass.EXACT or self.track == ExecutionTrack.TRACK_A_EXACT

    def allows_low_rank(self) -> bool:
        return not self.is_exact() and self.relative_error > 0.0

    def allows_sparsity(self) -> bool:
        return True  # Sparsity can be exact (zeros) or bounded

    def allows_quantization(self) -> bool:
        return not self.is_exact()

    def allows_denoising(self) -> bool:
        return self.contract_class in (ContractClass.PERCEPTUALLY_BOUNDED, ContractClass.STATISTICALLY_BOUNDED)
