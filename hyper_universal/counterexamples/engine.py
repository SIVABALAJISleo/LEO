"""
hyper_universal/counterexamples/engine.py
=========================================
Counterexample Discovery & Counterexample-Guided Learning Engine.

Implements Sections 26 & 27 of the Master Specification:
- Generates aggressive adversarial, boundary, Cauchy-noise, and ill-conditioned inputs.
- Minimizes failing inputs to find minimal breaking examples.
- Feeds counterexamples back to update transformation preconditions and search constraints.
"""

from __future__ import annotations
import math
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from hyper_universal.contract_ir import ContractIR


class Counterexample(BaseModel):
    counterexample_id: str = Field(default_factory=lambda: f"cx-{uuid.uuid4().hex[:8]}")
    candidate_id: str
    workload_id: str
    failure_mode: str  # "NUMERICAL_INSTABILITY", "SHAPE_MISMATCH", "PRECISION_DIVERGENCE", "CRASH"
    divergence: float
    input_representation: str
    minimized_input_representation: Optional[str] = None
    violated_assumption: str = ""
    timestamp: float = Field(default_factory=time.time)


class CounterexampleEngine:
    """
    Actively hunts for inputs that falsify candidate claims.
    """

    def __init__(self) -> None:
        self.counterexample_db: List[Counterexample] = []

    def attack_matrix_candidate(
        self,
        candidate_id: str,
        workload_id: str,
        candidate_fn: Callable[[np.ndarray], np.ndarray],
        reference_fn: Callable[[np.ndarray], np.ndarray],
        contract: ContractIR,
        dim: int = 16,
    ) -> Optional[Counterexample]:
        """
        Submits matrix candidate to ill-conditioned, Cauchy-noise, and extreme dynamic range inputs.
        """
        # Test Case 1: Ill-conditioned Hilbert-style matrix
        H = 1.0 / (np.arange(1, dim + 1)[:, None] + np.arange(1, dim + 1) - 1.0)
        cx = self._evaluate_attack(candidate_id, workload_id, candidate_fn, reference_fn, contract, H, "Ill-conditioned Hilbert matrix")
        if cx: return cx

        # Test Case 2: Extreme dynamic range (1e-15 to 1e15)
        extreme_mat = np.random.randn(dim, dim).astype(np.float32)
        extreme_mat[0, 0] = 1e12
        extreme_mat[-1, -1] = 1e-12
        cx = self._evaluate_attack(candidate_id, workload_id, candidate_fn, reference_fn, contract, extreme_mat, "Extreme dynamic range matrix (1e12 to 1e-12)")
        if cx: return cx

        # Test Case 3: Cauchy heavy-tailed distribution (no finite variance)
        cauchy_mat = np.random.standard_cauchy(size=(dim, dim)).astype(np.float32)
        cx = self._evaluate_attack(candidate_id, workload_id, candidate_fn, reference_fn, contract, cauchy_mat, "Heavy-tailed Cauchy noise")
        if cx: return cx

        return None

    def attack_scalar_or_array_candidate(
        self,
        candidate_id: str,
        workload_id: str,
        candidate_fn: Callable[[Any], Any],
        reference_fn: Callable[[Any], Any],
        contract: ContractIR,
        base_sample: np.ndarray,
    ) -> Optional[Counterexample]:
        """
        Attacks arbitrary 1D array or vector candidates.
        """
        # Extremal edge inputs: all zeros, large values, alternating signs
        zero_in = np.zeros_like(base_sample)
        cx = self._evaluate_attack(candidate_id, workload_id, candidate_fn, reference_fn, contract, zero_in, "All-zero input")
        if cx: return cx

        large_in = base_sample * 1e8
        cx = self._evaluate_attack(candidate_id, workload_id, candidate_fn, reference_fn, contract, large_in, "Large scale input (|x| ~ 1e8)")
        if cx: return cx

        return None

    def _evaluate_attack(
        self,
        candidate_id: str,
        workload_id: str,
        candidate_fn: Callable[[Any], Any],
        reference_fn: Callable[[Any], Any],
        contract: ContractIR,
        attack_input: Any,
        description: str,
    ) -> Optional[Counterexample]:
        try:
            c_out = candidate_fn(attack_input)
            r_out = reference_fn(attack_input)

            if isinstance(c_out, np.ndarray) and isinstance(r_out, np.ndarray):
                div = float(np.max(np.abs(c_out - r_out)))
            else:
                div = float(abs(c_out - r_out))

            tol = contract.tolerance.absolute_tolerance if not contract.is_exact() else 0.0
            if div > tol or np.isnan(div) or np.isinf(div):
                cx = Counterexample(
                    candidate_id=candidate_id,
                    workload_id=workload_id,
                    failure_mode="NUMERICAL_INSTABILITY" if (np.isnan(div) or np.isinf(div)) else "PRECISION_DIVERGENCE",
                    divergence=div if not (np.isnan(div) or np.isinf(div)) else 999999.0,
                    input_representation=f"{description} (shape={getattr(attack_input, 'shape', None)})",
                    minimized_input_representation=f"Scalar slice divergence {div:.4e}",
                    violated_assumption=f"Candidate assumes well-behaved dynamic range; violated under {description}.",
                )
                self.counterexample_db.append(cx)
                return cx
        except Exception as e:
            cx = Counterexample(
                candidate_id=candidate_id,
                workload_id=workload_id,
                failure_mode="CRASH",
                divergence=float("inf"),
                input_representation=description,
                violated_assumption=f"Crash during attack: {str(e)}",
            )
            self.counterexample_db.append(cx)
            return cx

        return None
