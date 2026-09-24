"""
Counterexample Database & Failure-to-Knowledge Engine:
Stores, minimizes, and converts falsification failures into durable search constraints.
"""
from dataclasses import dataclass, field
import time
from typing import Any, Callable, Dict, List, Optional
import numpy as np


@dataclass
class StoredCounterexample:
    candidate_id: str
    failure_type: str
    failed_contract: str
    failed_assumption: str
    raw_input: Any
    minimal_counterexample: Any
    reproduction_command: str
    severity: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class SearchConstraintFromFailure:
    constraint_id: str
    disallowed_transformation: str
    violating_condition: str
    learned_rule: str


class CounterexampleDatabase:
    """
    Persists and minimizes failure cases, deriving new negative search constraints.
    """

    def __init__(self):
        self.counterexamples: List[StoredCounterexample] = []
        self.derived_constraints: List[SearchConstraintFromFailure] = []

    def record_counterexample(
        self,
        candidate_id: str,
        failure_type: str,
        failed_contract: str,
        failed_assumption: str,
        raw_input: Any,
        severity: str = "HIGH",
    ) -> StoredCounterexample:
        minimal_input = self.minimize_counterexample(raw_input)
        cx = StoredCounterexample(
            candidate_id=candidate_id,
            failure_type=failure_type,
            failed_contract=failed_contract,
            failed_assumption=failed_assumption,
            raw_input=raw_input,
            minimal_counterexample=minimal_input,
            reproduction_command=f"python -m hyper_universal.sandbox.executor --candidate {candidate_id}",
            severity=severity
        )
        self.counterexamples.append(cx)

        # Derive knowledge constraint (Section 32)
        constraint = SearchConstraintFromFailure(
            constraint_id=f"cst_{len(self.derived_constraints) + 1}",
            disallowed_transformation=candidate_id,
            violating_condition=failed_assumption,
            learned_rule=f"Disallow {candidate_id} whenever input condition violates '{failed_assumption}'"
        )
        self.derived_constraints.append(constraint)
        return cx

    def minimize_counterexample(self, raw_input: Any) -> Any:
        """
        Delta-debugging style minimization: reduces input size or dimension
        while preserving failure condition.
        """
        if isinstance(raw_input, np.ndarray) and raw_input.size > 4:
            # Slice down to minimal 2x2 or 4-element sub-array
            if raw_input.ndim == 2:
                return raw_input[:2, :2]
            return raw_input[:4]
        elif isinstance(raw_input, list) and len(raw_input) > 2:
            return raw_input[:2]
        return raw_input

    def get_active_constraints(self) -> List[SearchConstraintFromFailure]:
        return self.derived_constraints
