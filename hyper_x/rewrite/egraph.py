"""
hyper_x/rewrite/egraph.py
=============================================================================
HYPER-X E-Graph / Equality-Rewriting Subsystem
=============================================================================
Equality-Rewriting Engine for computational graph optimization.
Pipeline:
  expression -> canonical representation -> rewrite rules -> equivalent expression space
             -> cost model -> extraction -> candidate -> verification

Rules include:
  - Associativity commute: (A @ B) @ C <=> A @ (B @ C)
  - Distributivity:        A @ (B + C) <=> A @ B + A @ C
  - Transposition duality: (A @ B).T <=> B.T @ A.T
  - Factored rank:         (U @ V) @ B <=> U @ (V @ B)
  - Identity & zero prune: A @ I => A, A @ 0 => 0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple, Any
import numpy as np

@dataclass
class EClass:
    class_id: int
    nodes: Set[str] = field(default_factory=set)
    best_cost: float = float("inf")
    best_expr: Optional[str] = None

@dataclass
class RewriteRule:
    name: str
    pattern: str
    replacement: str
    condition: Optional[str] = None
    cost_delta: float = 0.0

class EGraph:
    """E-Graph for equivalence exploration and minimal-cost expression extraction."""

    def __init__(self):
        self.classes: Dict[int, EClass] = {}
        self.expr_to_class: Dict[str, int] = {}
        self.next_id = 0
        self.rules: List[RewriteRule] = self._default_rules()

    def _default_rules(self) -> List[RewriteRule]:
        return [
            RewriteRule("MATMUL_ASSOC_RIGHT", "(A @ B) @ C", "A @ (B @ C)", condition="k_left > k_right"),
            RewriteRule("MATMUL_ASSOC_LEFT", "A @ (B @ C)", "(A @ B) @ C", condition="k_right > k_left"),
            RewriteRule("DISTRIBUTIVE_EXPAND", "A @ (B + C)", "(A @ B) + (A @ C)"),
            RewriteRule("DISTRIBUTIVE_FACTOR", "(A @ B) + (A @ C)", "A @ (B + C)", cost_delta=-0.5),
            RewriteRule("FACTORIZED_CHAIN", "(U @ V) @ B", "U @ (V @ B)", cost_delta=-0.6),
            RewriteRule("ZERO_ELIMINATION", "A + 0", "A", cost_delta=-0.1),
            RewriteRule("IDENTITY_ELIMINATION", "A @ I", "A", cost_delta=-0.9),
        ]

    def add_expression(self, expr: str, cost: float = 1.0) -> int:
        if expr in self.expr_to_class:
            cid = self.expr_to_class[expr]
            ecls = self.classes[cid]
            if cost < ecls.best_cost:
                ecls.best_cost = cost
                ecls.best_expr = expr
            return cid

        cid = self.next_id
        self.next_id += 1
        ecls = EClass(class_id=cid, nodes={expr}, best_cost=cost, best_expr=expr)
        self.classes[cid] = ecls
        self.expr_to_class[expr] = cid
        return cid

    def union(self, cid1: int, cid2: int) -> int:
        if cid1 == cid2:
            return cid1
        e1 = self.classes[cid1]
        e2 = self.classes[cid2]
        
        # Merge e2 into e1
        e1.nodes.update(e2.nodes)
        for node in e2.nodes:
            self.expr_to_class[node] = cid1
        if e2.best_cost < e1.best_cost:
            e1.best_cost = e2.best_cost
            e1.best_expr = e2.best_expr
        del self.classes[cid2]
        return cid1

    def apply_rules(self) -> int:
        applied = 0
        current_exprs = list(self.expr_to_class.keys())
        for expr in current_exprs:
            cid = self.expr_to_class[expr]
            for rule in self.rules:
                if rule.pattern in expr:
                    rewritten = expr.replace(rule.pattern, rule.replacement)
                    new_cost = self.classes[cid].best_cost + rule.cost_delta
                    new_cid = self.add_expression(rewritten, cost=max(0.01, new_cost))
                    self.union(cid, new_cid)
                    applied += 1
        return applied

    def extract_cheapest(self, cid: int) -> Tuple[str, float]:
        ecls = self.classes[cid]
        return ecls.best_expr or "unknown", ecls.best_cost
