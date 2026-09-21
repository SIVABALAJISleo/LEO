"""
hyper/discovery/counterexample_engine.py
========================================
Counterexample Discovery Engine for UCTDE.

Mandatory Adversarial Attack Subsystem:
  For every proposed transformation, pathway, or hypothesis: TRY TO BREAK IT.
  Generates pathological edge cases, ill-conditioned distributions, anti-structural noise,
  minimizes failing inputs via delta-debugging, and records them in a persistent database.
"""

from __future__ import annotations
import uuid
import time
import json
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field


class Counterexample(BaseModel):
    counterexample_id: str = Field(default_factory=lambda: f"cx-{uuid.uuid4().hex[:8]}")
    hypothesis_id: str
    workload_domain: str
    failure_mode: str                       # e.g., "NUMERICAL_DIVERGENCE", "INVARIANT_VIOLATION", "NAN_OVERFLOW"
    input_summary: str
    minimal_input_repr: str
    error_magnitude: float
    explanation: str
    timestamp: float = Field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class CounterexampleDatabase:
    """Persistent storage for discovered counterexamples."""

    def __init__(self) -> None:
        self.counterexamples: Dict[str, Counterexample] = {}
        self.by_hypothesis: Dict[str, List[str]] = {}

    def record(self, cx: Counterexample) -> None:
        self.counterexamples[cx.counterexample_id] = cx
        if cx.hypothesis_id not in self.by_hypothesis:
            self.by_hypothesis[cx.hypothesis_id] = []
        self.by_hypothesis[cx.hypothesis_id].append(cx.counterexample_id)

    def get_by_hypothesis(self, hypothesis_id: str) -> List[Counterexample]:
        cx_ids = self.by_hypothesis.get(hypothesis_id, [])
        return [self.counterexamples[cid] for cid in cx_ids if cid in self.counterexamples]

    def all(self) -> List[Counterexample]:
        return list(self.counterexamples.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_count": len(self.counterexamples),
            "items": [cx.to_dict() for cx in self.counterexamples.values()],
        }

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


class CounterexampleDiscoveryEngine:
    """
    Actively hunts for counterexamples to disprove candidate general principles.
    """

    def __init__(self, db: Optional[CounterexampleDatabase] = None) -> None:
        self.db = db or CounterexampleDatabase()

    def generate_adversarial_inputs(self, domain: str, base_len: int = 100) -> List[Tuple[str, Any]]:
        """
        Generates adversarial input variants:
          1. Empty / single-element / tiny scale
          2. Pathological dynamic range (1e-30 to 1e30)
          3. Ill-conditioned / duplicate / singular cases
          4. Anti-structure high-entropy Cauchy noise
          5. Extremal integers (INT_MIN, INT_MAX)
        """
        tests: List[Tuple[str, Any]] = []

        if domain in ("NUMERICAL_POLYNOMIAL", "NUMERICAL", "ARITHMETIC"):
            # Extreme range
            tests.append(("extreme_dynamic_range", np.array([1e-25, -1e25, 1e20, -1e20, 0.0], dtype=np.float64)))
            # Large coordinates
            tests.append(("large_values", np.linspace(1e5, 1e7, base_len, dtype=np.float64)))
            # Cauchy heavy-tailed distribution (no finite variance)
            rng = np.random.default_rng(42)
            cauchy = rng.standard_cauchy(base_len)
            tests.append(("cauchy_noise", cauchy))
            # Subnormal numbers
            tests.append(("subnormal_tiny", np.array([1e-38, 1e-45, 0.0, -1e-45], dtype=np.float32)))

        elif domain in ("SORTING", "BOUNDED_SORTING"):
            # All duplicates
            tests.append(("all_duplicates", np.full(base_len, 42, dtype=np.int32)))
            # Reverse sorted worst case
            tests.append(("reverse_sorted", np.arange(base_len, 0, -1, dtype=np.int32)))
            # Extremal range beyond small key bounds (K > 10000)
            tests.append(("out_of_bound_keys", np.array([0, -100, 50000, 1000000, -5], dtype=np.int32)))
            # Single element
            tests.append(("single_element", np.array([7], dtype=np.int32)))
            # Alternating oscillation
            tests.append(("oscillating", np.array([1, 1000] * (base_len // 2), dtype=np.int32)))

        elif domain in ("MATRIX", "LINEAR_ALGEBRA"):
            # Singular rank-1 matrix
            tests.append(("rank_1_singular", np.ones((base_len, base_len), dtype=np.float32)))
            # Ill-conditioned Hilbert-style matrix
            i, j = np.meshgrid(np.arange(1, min(base_len, 10) + 1), np.arange(1, min(base_len, 10) + 1))
            hilbert = 1.0 / (i + j - 1.0)
            tests.append(("ill_conditioned_hilbert", hilbert.astype(np.float32)))
            # Sparse zero matrix
            tests.append(("all_zeros", np.zeros((min(base_len, 16), min(base_len, 16)), dtype=np.float32)))

        else:
            # Generic adversarial arrays
            tests.append(("zeros", np.zeros(base_len, dtype=np.float32)))
            tests.append(("alternating_signs", np.array([(-1) ** i for i in range(base_len)], dtype=np.float32)))

        return tests

    def attack_pathway(
        self,
        candidate_callable: Callable[[Any], Any],
        reference_callable: Callable[[Any], Any],
        domain: str,
        hypothesis_id: str,
        atol: float = 1e-4,
        rtol: float = 1e-3,
    ) -> Optional[Counterexample]:
        """
        Executes the adversarial gauntlet. If divergence or unhandled exception occurs,
        minimizes the failing case and records the counterexample.
        """
        suite = self.generate_adversarial_inputs(domain)

        for test_name, adv_input in suite:
            try:
                ref_out = reference_callable(adv_input)
            except Exception as ref_err:
                # If reference fails as well on pathological input, this is not a candidate fault
                continue

            try:
                cand_out = candidate_callable(adv_input)
            except Exception as cand_err:
                # Candidate crashed where reference survived -> Counterexample!
                cx = Counterexample(
                    hypothesis_id=hypothesis_id,
                    workload_domain=domain,
                    failure_mode="CANDIDATE_CRASH",
                    input_summary=f"Test '{test_name}' crashed candidate: {str(cand_err)}",
                    minimal_input_repr=str(adv_input[:5] if hasattr(adv_input, '__len__') else adv_input),
                    error_magnitude=float("inf"),
                    explanation=f"Candidate raised exception '{cand_err}' on input variant '{test_name}'.",
                )
                self.db.record(cx)
                return cx

            # Check correctness against reference
            if isinstance(ref_out, np.ndarray) and isinstance(cand_out, np.ndarray):
                if ref_out.shape != cand_out.shape:
                    cx = Counterexample(
                        hypothesis_id=hypothesis_id,
                        workload_domain=domain,
                        failure_mode="SHAPE_MISMATCH",
                        input_summary=f"Test '{test_name}' output shape mismatch: {cand_out.shape} vs {ref_out.shape}",
                        minimal_input_repr=str(adv_input[:5] if hasattr(adv_input, '__len__') else adv_input),
                        error_magnitude=1.0,
                        explanation=f"Candidate returned shape {cand_out.shape}, reference produced {ref_out.shape}.",
                    )
                    self.db.record(cx)
                    return cx

                diff = np.abs(cand_out - ref_out)
                max_diff = float(np.max(diff)) if diff.size > 0 else 0.0
                allowed_tol = atol + rtol * float(np.max(np.abs(ref_out))) if ref_out.size > 0 else atol

                if max_diff > allowed_tol or np.isnan(max_diff):
                    # Numerical break found! Minimize failing slice via delta-debugging
                    min_repr = self._minimize_array_input(
                        candidate_callable, reference_callable, adv_input, atol, rtol
                    )
                    cx = Counterexample(
                        hypothesis_id=hypothesis_id,
                        workload_domain=domain,
                        failure_mode="NUMERICAL_DIVERGENCE",
                        input_summary=f"Test '{test_name}' diverged: max_diff={max_diff:.3e} > tol={allowed_tol:.3e}",
                        minimal_input_repr=min_repr,
                        error_magnitude=max_diff,
                        explanation=f"Candidate violated error tolerance on '{test_name}'.",
                    )
                    self.db.record(cx)
                    return cx
            else:
                if cand_out != ref_out:
                    cx = Counterexample(
                        hypothesis_id=hypothesis_id,
                        workload_domain=domain,
                        failure_mode="VALUE_INEQUALITY",
                        input_summary=f"Test '{test_name}' scalar mismatch",
                        minimal_input_repr=str(adv_input),
                        error_magnitude=1.0,
                        explanation=f"Candidate value {cand_out} != reference {ref_out}.",
                    )
                    self.db.record(cx)
                    return cx

        # Survived all adversarial gauntlet attacks
        return None

    def _minimize_array_input(
        self,
        cand_fn: Callable[[Any], Any],
        ref_fn: Callable[[Any], Any],
        failing_input: Any,
        atol: float,
        rtol: float,
    ) -> str:
        """Delta-debugging style reduction to find smaller failing array slice."""
        if not isinstance(failing_input, np.ndarray) or len(failing_input) <= 2:
            return str(failing_input)

        current = failing_input
        # Try binary halving
        for _ in range(4):
            mid = len(current) // 2
            if mid < 2:
                break
            half = current[:mid]
            try:
                r = ref_fn(half)
                c = cand_fn(half)
                d = np.abs(c - r)
                tol = atol + rtol * float(np.max(np.abs(r)))
                if np.max(d) > tol:
                    current = half
                else:
                    break
            except Exception:
                break

        return f"Array(len={len(current)}, sample={current[:3]}...)"
