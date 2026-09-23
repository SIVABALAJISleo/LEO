"""
hyper/discovery/transformation_dsl.py
=====================================
Formal Transformation Domain-Specific Language (DSL) Engine.

Implements Section 14 of the Master Architecture:
Defines structured transformation specifications:
    TRANSFORM:
        INPUT_GRAPH
        OPERATION
        PRECONDITION
        POSTCONDITION
        COST_MODEL
        VERIFIER

Provides declarative schemas, precondition checks, postcondition validation,
cost estimation functions, and failure mode taxonomies.
"""

from __future__ import annotations
import inspect
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class TransformationFamilyType(Enum):
    MATHEMATICAL = "MATHEMATICAL"
    ALGORITHMIC = "ALGORITHMIC"
    STRUCTURAL = "STRUCTURAL"
    REPRESENTATION = "REPRESENTATION"
    MEMORY = "MEMORY"
    SCHEDULING = "SCHEDULING"
    COMPILER = "COMPILER"
    LOW_LEVEL = "LOW_LEVEL"


class FailureMode(Enum):
    PRECONDITION_VIOLATED = "PRECONDITION_VIOLATED"
    POSTCONDITION_VIOLATED = "POSTCONDITION_VIOLATED"
    NUMERICAL_DRIFT_EXCEEDED = "NUMERICAL_DRIFT_EXCEEDED"
    MEMORY_OVERFLOW = "MEMORY_OVERFLOW"
    TYPE_INCOMPATIBILITY = "TYPE_INCOMPATIBILITY"
    CONTRACT_REJECTED = "CONTRACT_REJECTED"


@dataclass
class TransformationCostEstimate:
    """Analytical cost estimate of applying a transformation."""
    estimated_flops_ratio: float = 1.0  # <1.0 means fewer operations
    estimated_memory_ratio: float = 1.0 # <1.0 means less memory
    estimated_bandwidth_ratio: float = 1.0
    estimated_speedup: float = 1.0
    complexity_class: str = "O(N)"


@dataclass
class DSLTransformationRule:
    """
    Structured definition of a transformation rule in the Transformation DSL.
    """
    rule_id: str
    name: str
    family: TransformationFamilyType
    description: str

    # Precondition: (input_state, metadata) -> (passed: bool, reason: str)
    precondition_fn: Callable[[Any, Dict[str, Any]], Tuple[bool, str]]

    # Operation: (input_state, metadata) -> transformed_state
    operation_fn: Callable[[Any, Dict[str, Any]], Any]

    # Postcondition: (original_state, transformed_state, metadata) -> (passed: bool, reason: str)
    postcondition_fn: Callable[[Any, Any, Dict[str, Any]], Tuple[bool, str]]

    # Verifier: (transformed_output, reference_output, tolerance) -> bool
    verifier_fn: Callable[[Any, Any, float], bool]

    # Cost model
    cost_model: TransformationCostEstimate

    # Applicable domains or operation types
    applicable_domains: Set[str] = field(default_factory=set)
    possible_failure_modes: List[FailureMode] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def check_precondition(self, state: Any, meta: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
        """Validates that all preconditions for the transformation are met."""
        meta = meta or {}
        try:
            return self.precondition_fn(state, meta)
        except Exception as e:
            return False, f"Precondition evaluation exception: {e}"

    def apply(self, state: Any, meta: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any, Optional[FailureMode], str]:
        """
        Executes the transformation pipeline:
        Precondition -> Operation -> Postcondition
        """
        meta = meta or {}

        # 1. Precondition
        ok, reason = self.check_precondition(state, meta)
        if not ok:
            return False, None, FailureMode.PRECONDITION_VIOLATED, f"Precondition failed: {reason}"

        # 2. Operation
        try:
            transformed = self.operation_fn(state, meta)
        except Exception as e:
            return False, None, FailureMode.TYPE_INCOMPATIBILITY, f"Operation execution error: {e}"

        # 3. Postcondition
        try:
            post_ok, post_reason = self.postcondition_fn(state, transformed, meta)
            if not post_ok:
                return False, transformed, FailureMode.POSTCONDITION_VIOLATED, f"Postcondition failed: {post_reason}"
        except Exception as e:
            return False, transformed, FailureMode.POSTCONDITION_VIOLATED, f"Postcondition evaluation error: {e}"

        return True, transformed, None, "Transformation applied successfully"


class TransformationDSLEngine:
    """
    Registry and compiler for Transformation DSL rules.
    """

    def __init__(self) -> None:
        self.rules: Dict[str, DSLTransformationRule] = {}
        self._register_built_in_rules()

    def register_rule(self, rule: DSLTransformationRule) -> None:
        self.rules[rule.rule_id] = rule

    def get_rule(self, rule_id: str) -> Optional[DSLTransformationRule]:
        return self.rules.get(rule_id)

    def find_applicable_rules(self, domain: str, state: Any, meta: Optional[Dict[str, Any]] = None) -> List[DSLTransformationRule]:
        """Finds all registered rules that are applicable and satisfy preconditions."""
        meta = meta or {}
        applicable = []
        for rule in self.rules.values():
            if domain in rule.applicable_domains or "*" in rule.applicable_domains:
                passed, _ = rule.check_precondition(state, meta)
                if passed:
                    applicable.append(rule)
        return applicable

    def _register_built_in_rules(self) -> None:
        """Initializes canonical built-in DSL transformation rules."""
        import numpy as np

        # Rule 1: Horner's Rule Factorization
        def horner_precondition(state: Any, meta: Dict[str, Any]) -> Tuple[bool, str]:
            coeffs = meta.get("coeffs")
            if coeffs is None or len(coeffs) < 2:
                return False, "Horner's rule requires a coefficient array with at least 2 elements"
            return True, "Valid polynomial coefficients present"

        def horner_op(state: Any, meta: Dict[str, Any]) -> Any:
            coeffs = meta["coeffs"]
            x = state
            res = coeffs[-1]
            for c in coeffs[-2::-1]:
                res = res * x + c
            return float(res)

        def horner_postcondition(orig_state: Any, transformed: Any, meta: Dict[str, Any]) -> Tuple[bool, str]:
            if not isinstance(transformed, (int, float, np.floating)):
                return False, "Output must be a numeric scalar"
            return True, "Valid scalar output generated"

        def horner_verifier(cand_out: Any, ref_out: Any, tol: float) -> bool:
            return abs(cand_out - ref_out) <= tol

        rule_horner = DSLTransformationRule(
            rule_id="dsl-math-horner",
            name="Horner's Polynomial Factorization",
            family=TransformationFamilyType.MATHEMATICAL,
            description="Transforms O(N^2) naive power sum into O(N) nested multiply-accumulate operations.",
            precondition_fn=horner_precondition,
            operation_fn=horner_op,
            postcondition_fn=horner_postcondition,
            verifier_fn=horner_verifier,
            cost_model=TransformationCostEstimate(
                estimated_flops_ratio=0.3,
                estimated_memory_ratio=1.0,
                estimated_speedup=3.5,
                complexity_class="O(N)",
            ),
            applicable_domains={"NUMERICAL", "POLYNOMIAL", "SCIENTIFIC"},
            possible_failure_modes=[FailureMode.PRECONDITION_VIOLATED, FailureMode.NUMERICAL_DRIFT_EXCEEDED],
        )
        self.register_rule(rule_horner)

        # Rule 2: Branch-Free Sort3 Network
        def sort3_precondition(state: Any, meta: Dict[str, Any]) -> Tuple[bool, str]:
            if not isinstance(state, list) or len(state) != 3:
                return False, "Sort3 requires a list of exactly 3 elements"
            return True, "Valid 3-element list"

        def sort3_op(state: Any, meta: Dict[str, Any]) -> Any:
            res = list(state)
            if res[0] > res[1]: res[0], res[1] = res[1], res[0]
            if res[1] > res[2]: res[1], res[2] = res[2], res[1]
            if res[0] > res[1]: res[0], res[1] = res[1], res[0]
            return res

        def sort3_postcondition(orig_state: Any, transformed: Any, meta: Dict[str, Any]) -> Tuple[bool, str]:
            if transformed[0] <= transformed[1] <= transformed[2]:
                return True, "Elements in monotonic ascending order"
            return False, "Elements not sorted"

        def sort3_verifier(cand_out: Any, ref_out: Any, tol: float) -> bool:
            return cand_out == ref_out

        rule_sort3 = DSLTransformationRule(
            rule_id="dsl-algo-sort3",
            name="AlphaDev Branch-Free Sort3 Network",
            family=TransformationFamilyType.LOW_LEVEL,
            description="Replaces comparative branching sort with optimal 3-instruction compare-and-swap network.",
            precondition_fn=sort3_precondition,
            operation_fn=sort3_op,
            postcondition_fn=sort3_postcondition,
            verifier_fn=sort3_verifier,
            cost_model=TransformationCostEstimate(
                estimated_flops_ratio=0.6,
                estimated_speedup=1.5,
                complexity_class="O(1)",
            ),
            applicable_domains={"SEARCH_SORTING", "SORTING", "BOUNDED_SORTING"},
            possible_failure_modes=[FailureMode.PRECONDITION_VIOLATED, FailureMode.POSTCONDITION_VIOLATED],
        )
        self.register_rule(rule_sort3)

        # Rule 3: Residual Delta Computation
        def delta_precondition(state: Any, meta: Dict[str, Any]) -> Tuple[bool, str]:
            prev_input = meta.get("prev_input")
            prev_output = meta.get("prev_output")
            if prev_input is None or prev_output is None:
                return False, "Requires previous frame input and output for delta accumulation"
            return True, "Previous state available"

        def delta_op(state: Any, meta: Dict[str, Any]) -> Any:
            prev_input = meta["prev_input"]
            prev_output = meta["prev_output"]
            delta = state - prev_input
            return prev_output + delta

        def delta_postcondition(orig: Any, trans: Any, meta: Dict[str, Any]) -> Tuple[bool, str]:
            return True, "Delta accumulated"

        def delta_verifier(cand_out: Any, ref_out: Any, tol: float) -> bool:
            return abs(cand_out - ref_out) <= tol

        rule_delta = DSLTransformationRule(
            rule_id="dsl-escape-delta",
            name="Incremental Residual Delta Accumulation",
            family=TransformationFamilyType.STRUCTURAL,
            description="Calculates only the output residual delta relative to prior state t-1.",
            precondition_fn=delta_precondition,
            operation_fn=delta_op,
            postcondition_fn=delta_postcondition,
            verifier_fn=delta_verifier,
            cost_model=TransformationCostEstimate(
                estimated_flops_ratio=0.1,
                estimated_speedup=8.0,
                complexity_class="O(Delta)",
            ),
            applicable_domains={"STREAMING", "ANIMATION", "VIDEO", "PHYSICS_SIMULATION"},
            possible_failure_modes=[FailureMode.PRECONDITION_VIOLATED],
        )
        self.register_rule(rule_delta)
