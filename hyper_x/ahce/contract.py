"""
hyper_x/ahce/contract.py
========================
Formal AHCE Application Contract Specification (Section 9).

Explicitly defines contractual expectations:
- EXACT:                   Strict bitwise / zero error
- EXACT_REFORMULATION:     Exact output via lower-complexity mathematics
- NUMERICALLY_EQUIVALENT:  Relative/absolute numerical tolerance (e.g. eps <= 1e-4)
- BOUNDED_APPROXIMATION:   Mathematically bounded truncation
- PERCEPTUAL_APPROXIMATION: Psycho-visual bounds (e.g. SSIM >= 0.98, PSNR >= 38 dB)
- PREDICTIVE:              Speculative with fail-closed target verification
- CONTRACT_EQUIVALENT:     Output contract fully satisfied
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any, Optional


class CorrectnessClass(str, Enum):
    EXACT = "EXACT"
    EXACT_REFORMULATION = "EXACT_REFORMULATION"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    BOUNDED_APPROXIMATION = "BOUNDED_APPROXIMATION"
    PERCEPTUAL_APPROXIMATION = "PERCEPTUAL_APPROXIMATION"
    PREDICTIVE = "PREDICTIVE"
    CONTRACT_EQUIVALENT = "CONTRACT_EQUIVALENT"
    CACHED = "CACHED"
    REUSED = "REUSED"
    REDUCED_WORK = "REDUCED_WORK"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class AHCEContract:
    contract_id: str
    correctness_class: CorrectnessClass
    max_abs_error: Optional[float] = None
    max_relative_error: Optional[float] = None
    min_psnr: Optional[float] = None
    min_ssim: Optional[float] = None
    min_accuracy: Optional[float] = None
    min_tokens_per_sec: Optional[float] = None
    max_latency_ms: Optional[float] = None
    max_memory_mb: Optional[float] = None
    determinism_required: bool = True
    allow_cache: bool = True
    allow_approximation: bool = False
    allow_prediction: bool = False
    notes: str = ""

    def validate(self) -> None:
        """Fail-closed assertion of contract consistency."""
        if self.correctness_class == CorrectnessClass.EXACT:
            if self.max_abs_error not in (None, 0.0):
                raise ValueError("EXACT contract forbids non-zero max_abs_error.")
            if self.allow_approximation:
                raise ValueError("EXACT contract forbids approximation.")

        if self.correctness_class == CorrectnessClass.NUMERICALLY_EQUIVALENT:
            if self.max_relative_error is None and self.max_abs_error is None:
                raise ValueError("NUMERICALLY_EQUIVALENT contract must specify error bound.")

        if self.correctness_class == CorrectnessClass.PERCEPTUAL_APPROXIMATION:
            if self.min_psnr is None and self.min_ssim is None:
                raise ValueError("PERCEPTUAL_APPROXIMATION contract must specify min_psnr or min_ssim.")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["correctness_class"] = self.correctness_class.value
        return d
