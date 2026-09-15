"""
hyper_x/ahce/candidate.py
=========================
Candidate pathway representation for AHCE.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from .contract import CorrectnessClass


@dataclass
class AHCECandidate:
    candidate_id: str
    strategy_name: str
    correctness_class: CorrectnessClass
    transformations: List[str] = field(default_factory=list)
    predicted_work_reduction: float = 0.0
    predicted_latency_ms: float = 0.0
    transformation_cost_ms: float = 0.0
    confidence: float = 0.5
    executable_target: str = "CPU_AVX2"
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["correctness_class"] = self.correctness_class.value
        return d


@dataclass
class AHCETrialResult:
    candidate_id: str
    strategy_name: str
    success: bool
    verified: bool
    output: Any
    trial_latency_ms: float
    transformation_latency_ms: float
    execution_latency_ms: float
    verification_latency_ms: float
    total_latency_ms: float
    measured_error: float
    necessary_work_units: float
    work_reduction_pct: float
    fallback_used: bool = False
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Avoid serializing raw output tensors if large
        if hasattr(self.output, "shape"):
            d["output_shape"] = list(self.output.shape)
            d["output"] = f"<tensor shape={self.output.shape} dtype={self.output.dtype}>"
        return d
