"""
hyper_x/leaf/symbolic/expression.py
===================================
Symbolic AST representation for EFSC (Execution-Free Symbolic Collapse).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np


class OpType(str, Enum):
    CONST = "CONST"
    VAR = "VAR"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    POW = "POW"
    SUMMATION = "SUMMATION"
    MATMUL = "MATMUL"
    CONV = "CONV"


@dataclass
class SymExpr:
    """Symbolic Expression node for mathematical AST analysis."""
    op: OpType
    val: Optional[Any] = None                    # For CONST or VAR name
    children: List["SymExpr"] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def const(cls, value: Union[int, float, np.ndarray]) -> "SymExpr":
        return cls(op=OpType.CONST, val=value)

    @classmethod
    def var(cls, name: str) -> "SymExpr":
        return cls(op=OpType.VAR, val=name)

    @classmethod
    def add(cls, left: "SymExpr", right: "SymExpr") -> "SymExpr":
        return cls(op=OpType.ADD, children=[left, right])

    @classmethod
    def sub(cls, left: "SymExpr", right: "SymExpr") -> "SymExpr":
        return cls(op=OpType.SUB, children=[left, right])

    @classmethod
    def mul(cls, left: "SymExpr", right: "SymExpr") -> "SymExpr":
        return cls(op=OpType.MUL, children=[left, right])

    @classmethod
    def div(cls, left: "SymExpr", right: "SymExpr") -> "SymExpr":
        return cls(op=OpType.DIV, children=[left, right])

    @classmethod
    def summation(cls, idx_var: str, lower: "SymExpr", upper: "SymExpr", body: "SymExpr") -> "SymExpr":
        expr = cls(op=OpType.SUMMATION, children=[lower, upper, body])
        expr.meta["idx_var"] = idx_var
        return expr

    @classmethod
    def matmul(cls, left: "SymExpr", right: "SymExpr") -> "SymExpr":
        return cls(op=OpType.MATMUL, children=[left, right])

    def evaluate(self, env: Dict[str, Any]) -> Any:
        """Evaluates expression recursively under variable environment."""
        if self.op == OpType.CONST:
            return self.val
        if self.op == OpType.VAR:
            if self.val not in env:
                raise KeyError(f"Variable {self.val} not found in evaluation environment.")
            return env[self.val]
        if self.op == OpType.ADD:
            return self.children[0].evaluate(env) + self.children[1].evaluate(env)
        if self.op == OpType.SUB:
            return self.children[0].evaluate(env) - self.children[1].evaluate(env)
        if self.op == OpType.MUL:
            return self.children[0].evaluate(env) * self.children[1].evaluate(env)
        if self.op == OpType.DIV:
            return self.children[0].evaluate(env) / self.children[1].evaluate(env)
        if self.op == OpType.MATMUL:
            A = self.children[0].evaluate(env)
            B = self.children[1].evaluate(env)
            return np.matmul(A, B)
        if self.op == OpType.SUMMATION:
            idx = self.meta["idx_var"]
            low = int(self.children[0].evaluate(env))
            high = int(self.children[1].evaluate(env))
            body = self.children[2]
            total = 0.0
            local_env = dict(env)
            for i in range(low, high + 1):
                local_env[idx] = i
                total += body.evaluate(local_env)
            return total
        raise NotImplementedError(f"Unsupported op: {self.op}")
