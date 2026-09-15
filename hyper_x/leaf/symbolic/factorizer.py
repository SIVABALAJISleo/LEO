"""
hyper_x/leaf/symbolic/factorizer.py
==================================
Algebraic factorizer for EFSC: extracts common factors across sums.
"""

from typing import Any, Dict, List, Optional
from .expression import SymExpr, OpType


class AlgebraicFactorizer:
    """
    Factors distributive expressions:
    a * b + a * c -> a * (b + c)
    """

    def factor_distributive(self, expr: SymExpr) -> SymExpr:
        """Applies distributive factoring to addition of products."""
        if expr.op != OpType.ADD:
            return expr

        left, right = expr.children[0], expr.children[1]
        if left.op == OpType.MUL and right.op == OpType.MUL:
            # Check left-left vs right-left: a*b + a*c
            a1, b1 = left.children[0], left.children[1]
            a2, c2 = right.children[0], right.children[1]

            if a1.op == a2.op and a1.val == a2.val:
                # a * (b + c)
                b_plus_c = SymExpr.add(b1, c2)
                return SymExpr.mul(a1, b_plus_c)

        return expr
