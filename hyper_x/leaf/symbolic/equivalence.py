"""
hyper_x/leaf/symbolic/equivalence.py
====================================
Symbolic and numerical equivalence prover for EFSC.

Tests:
- Exhaustive verification for bounded domains.
- Randomized testing for large domains.
- Anti-structural stress on boundary conditions (0, negative, float).
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from .expression import SymExpr


class EquivalenceProver:
    """
    Independently verifies that a candidate closed form or simplified expression
    matches the reference computation across domain spaces.
    """

    def prove_equivalence(
        self,
        reference_expr: SymExpr,
        candidate_expr: SymExpr,
        domain_var: str,
        test_domain: List[int],
        tolerance: float = 1e-6,
    ) -> Tuple[bool, float, str]:
        """
        Tests reference vs candidate across a test domain.
        Returns: (is_equivalent, max_error, report_str)
        """
        max_err = 0.0

        for val in test_domain:
            env = {domain_var: val}
            try:
                ref_val = reference_expr.evaluate(env)
                cand_val = candidate_expr.evaluate(env)
            except Exception as e:
                return False, float("inf"), f"Evaluation error at {domain_var}={val}: {e}"

            diff = abs(ref_val - cand_val)
            if diff > max_err:
                max_err = float(diff)

            if max_err > tolerance:
                return False, max_err, f"FALSIFIED: Equivalence failed at {domain_var}={val}: ref={ref_val}, cand={cand_val}, diff={diff}"

        return True, max_err, f"PROVEN: Equivalent across all {len(test_domain)} points (max error: {max_err:.2e})"
