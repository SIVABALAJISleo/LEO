"""
hyper_x/wormhole_compiler/counterexample.py
=============================================================================
HYPER-X Counterexample Data Structures (Phase 12)
=============================================================================
Defines formal records of failure cases mined during verification and
falsification, used by the CEGIS (Counterexample-Guided Inductive Synthesis)
engine to repair candidate algorithms.
"""

from __future__ import annotations
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class Counterexample:
    """Formal record of an adversarial input that falsified a candidate."""
    case_id: str
    description: str
    input_A: np.ndarray
    input_B: np.ndarray
    condition_number: float
    effective_rank: int
    sparsity: float
    measured_error: float
    tolerance: float
    failure_mode: str
    diagnosis: str
    timestamp: float = field(default_factory=time.time)

    def compute_hash(self) -> str:
        s = f"{self.case_id}:{self.measured_error:.6e}:{self.condition_number:.2e}"
        return hashlib.sha256(s.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "condition_number": self.condition_number,
            "effective_rank": self.effective_rank,
            "sparsity": self.sparsity,
            "measured_error": self.measured_error,
            "tolerance": self.tolerance,
            "failure_mode": self.failure_mode,
            "diagnosis": self.diagnosis,
            "timestamp": self.timestamp,
        }


@dataclass
class CounterexampleRecord:
    """Formal audit record of a candidate falsification / counterexample."""
    counterexample_id: str
    candidate_id: str
    failure_reason: str
    input_signature: str
    reproduction_code: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counterexample_id": self.counterexample_id,
            "candidate_id": self.candidate_id,
            "failure_reason": self.failure_reason,
            "input_signature": self.input_signature,
            "reproduction_code": self.reproduction_code,
            "timestamp": self.timestamp,
        }

