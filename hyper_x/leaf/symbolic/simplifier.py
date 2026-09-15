"""
hyper_x/leaf/symbolic/simplifier.py
==================================
Algebraic simplifier, constant folding, and identity cancellation for EFSC.
"""

from typing import Any, Dict, List, Optional
from .expression import SymExpr, OpType


class AlgebraicSimplifier:
    """
    Applies mathematical identity rules to simplify SymExpr trees.
    - Constant folding: 2 + 3 -> 5
    - Multiplicative identities: x * 1 -> x, x * 0 -> 0
    - Additive identities: x + 0 -> x, x - 0 -> x
    - Self-cancellation: x - x -> 0, x / x -> 1
    """

    def simplify(self, expr: SymExpr) -> SymExpr:
        """Recursively simplifies an expression tree."""
        if expr.op in (OpType.CONST, OpType.VAR):
            return expr

        simplified_children = [self.simplify(c) for c in expr.children]

        # 1. Constant folding
        if all(c.op == OpType.CONST for c in simplified_children):
            if expr.op == OpType.ADD:
                return SymExpr.const(simplified_children[0].val + simplified_children[1].val)
            elif expr.op == OpType.SUB:
                return SymExpr.const(simplified_children[0].val - simplified_children[1].val)
            elif expr.op == OpType.MUL:
                return SymExpr.const(simplified_children[0].val * simplified_children[1].val)
            elif expr.op == OpType.DIV:
                if simplified_children[1].val != 0:
                    return SymExpr.const(simplified_children[0].val / simplified_children[1].val)

        # 2. Additive identities: x + 0 -> x, 0 + x -> x
        if expr.op == OpType.ADD:
            left, right = simplified_children[0], simplified_children[1]
            if left.op == OpType.CONST and left.val == 0:
                return right
            if right.op == OpType.CONST and right.val == 0:
                return left

        # 3. Subtractive identities: x - 0 -> x, x - x -> 0
        if expr.op == OpType.SUB:
            left, right = simplified_children[0], simplified_children[1]
            if right.op == OpType.CONST and right.val == 0:
                return left
            if left.op == OpType.VAR and right.op == OpType.VAR and left.val == right.val:
                return SymExpr.const(0)

        # 4. Multiplicative identities: x * 0 -> 0, x * 1 -> x
        if expr.op == OpType.MUL:
            left, right = simplified_children[0], simplified_children[1]
            if (left.op == OpType.CONST and left.val == 0) or (right.op == OpType.CONST and right.val == 0):
                return SymExpr.const(0)
            if left.op == OpType.CONST and left.val == 1:
                return right
            if right.op == OpType.CONST and right.val == 1:
                return left

        return SymExpr(op=expr.op, val=expr.val, children=simplified_children, meta=expr.meta)
