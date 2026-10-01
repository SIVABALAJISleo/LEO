"""
hyper/semantics/control_flow.py
===============================
Structured Control Flow Primitives for Universal Exact Semantic Machine.
Implements Sections 19 & 20:
- Bounded Loops: LOOP_INIT, LOOP_CONDITION, LOOP_BODY, LOOP_UPDATE
- Branches: IF, ELSE, MERGE, PHI
"""

from __future__ import annotations
import enum
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class LoopKind(str, enum.Enum):
    FOR_BOUNDED = "FOR_BOUNDED"
    WHILE_BOUNDED = "WHILE_BOUNDED"
    DO_WHILE_BOUNDED = "DO_WHILE_BOUNDED"


@dataclass
class StructuredLoop:
    """
    Formally defined bounded loop primitive with deterministic upper bound.
    """
    loop_id: str
    kind: LoopKind
    max_iterations: int
    induction_var: str
    lower_bound: int
    upper_bound: int
    step: int = 1
    carried_vars: List[str] = field(default_factory=list)
    condition_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    body_fn: Optional[Callable[[Dict[str, Any], int], Dict[str, Any]]] = None

    def execute_bounded(self, initial_env: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes bounded loop with hard iteration limit ensuring termination.
        """
        env = dict(initial_env)
        curr = self.lower_bound
        iters = 0

        while curr < self.upper_bound and iters < self.max_iterations:
            env[self.induction_var] = curr
            if self.condition_fn and not self.condition_fn(env):
                break
            if self.body_fn:
                env = self.body_fn(env, curr)
            curr += self.step
            iters += 1

        return env


@dataclass
class StructuredBranch:
    """
    Formally defined two-way branch with explicit merge and PHI nodes.
    """
    branch_id: str
    condition_var: str
    then_vars: List[str]
    else_vars: List[str]
    merge_vars: List[str]
    phi_mappings: Dict[str, Tuple[str, str]] = field(default_factory=dict)

    def evaluate_phi(
        self,
        condition_val: np.ndarray | bool,
        then_env: Dict[str, np.ndarray],
        else_env: Dict[str, np.ndarray],
    ) -> Dict[str, np.ndarray]:
        """
        Computes merge output tensors by selecting between then_env and else_env via condition_val.
        """
        merged: Dict[str, np.ndarray] = {}
        for out_var, (then_src, else_src) in self.phi_mappings.items():
            t_val = then_env[then_src]
            e_val = else_env[else_src]
            if isinstance(condition_val, bool):
                merged[out_var] = t_val if condition_val else e_val
            else:
                merged[out_var] = np.where(condition_val, t_val, e_val)
        return merged
