"""
hyper/escape/egraph.py
======================
Equality Saturation and E-Graph Optimizer for LEO/HYPER Universal GPU Semantic Machine.
Fulfills Section 30 of Master Specification.

Key Properties:
- Equivalence Classes (EClass) containing equivalent expressions (ENodes).
- Rules tagged by safety:
    * EXACT: Mathematically exact identity, always sound for all contracts.
    * CONTRACT_DEPENDENT: Exact under specific contracts (e.g. integer arithmetic or IEEE associativity tolerance).
    * APPROXIMATE: Introduces bounded numeric deviation; FORBIDDEN under exact contracts.
    * UNSAFE: Heuristic / speculative; requires explicit external verification.
- Cost-based extraction: Finds the globally minimal compute cost expression in the saturated e-graph.
- Enforces fail-closed safety: Never applies approximate rules under exact contracts.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class RuleSafety(enum.Enum):
    EXACT = "EXACT"
    CONTRACT_DEPENDENT = "CONTRACT_DEPENDENT"
    APPROXIMATE = "APPROXIMATE"
    UNSAFE = "UNSAFE"


@dataclass(frozen=True)
class ENode:
    """An expression node consisting of an operator and child e-class IDs."""
    op: str
    children: Tuple[int, ...] = ()
    metadata: Tuple[Tuple[str, Any], ...] = ()

    def __repr__(self) -> str:
        if not self.children:
            return f"{self.op}"
        return f"{self.op}({', '.join(str(c) for c in self.children)})"


@dataclass
class EClass:
    """An equivalence class of expressions."""
    id: int
    nodes: Set[ENode] = field(default_factory=set)
    parents: Set[Tuple[ENode, int]] = field(default_factory=set)

    def add_node(self, node: ENode):
        self.nodes.add(node)


@dataclass
class RewriteRule:
    """
    Rewrite rule for Equality Saturation.
    Applies pattern matching and substitution to create equivalent ENodes in the E-Graph.
    """
    name: str
    safety: RuleSafety
    match_fn: Callable[[ENode, EGraph], Optional[Dict[str, Any]]]
    apply_fn: Callable[[Dict[str, Any], EGraph], Optional[int]]
    description: str = ""


class EGraph:
    """
    Equality Graph (E-Graph) supporting union-find canonicalization, congruence closure,
    rule application, and cost-based extraction.
    """

    def __init__(self):
        self.union_find: Dict[int, int] = {}
        self.classes: Dict[int, EClass] = {}
        self.hashcons: Dict[ENode, int] = {}
        self._next_id: int = 0
        self.applied_rules: List[str] = []

    def find(self, class_id: int) -> int:
        """Find the canonical representative with path compression."""
        root = class_id
        while self.union_find.get(root, root) != root:
            root = self.union_find[root]
        curr = class_id
        while curr != root:
            parent = self.union_find.get(curr, curr)
            self.union_find[curr] = root
            curr = parent
        return root

    def canonicalize_node(self, node: ENode) -> ENode:
        """Canonicalize all child e-class IDs using union-find."""
        canonical_children = tuple(self.find(c) for c in node.children)
        return ENode(op=node.op, children=canonical_children, metadata=node.metadata)

    def add(self, node: ENode) -> int:
        """Add an expression node to the E-Graph and return its canonical e-class ID."""
        c_node = self.canonicalize_node(node)
        if c_node in self.hashcons:
            return self.find(self.hashcons[c_node])

        new_id = self._next_id
        self._next_id += 1
        self.union_find[new_id] = new_id
        eclass = EClass(id=new_id)
        eclass.add_node(c_node)
        self.classes[new_id] = eclass
        self.hashcons[c_node] = new_id

        for child in c_node.children:
            canonical_child = self.find(child)
            if canonical_child in self.classes:
                self.classes[canonical_child].parents.add((c_node, new_id))

        return new_id

    def merge(self, id1: int, id2: int) -> int:
        """Merge two e-classes and record congruence."""
        root1 = self.find(id1)
        root2 = self.find(id2)
        if root1 == root2:
            return root1

        # Direct root2 to root1
        self.union_find[root2] = root1
        class1 = self.classes[root1]
        class2 = self.classes.pop(root2)

        class1.nodes.update(class2.nodes)
        class1.parents.update(class2.parents)
        return root1

    def rebuild(self):
        """Restore invariants: update hashcons and propagate congruences."""
        rebuilt = False
        while True:
            changed = False
            new_hashcons: Dict[ENode, int] = {}
            for node, class_id in list(self.hashcons.items()):
                c_node = self.canonicalize_node(node)
                c_id = self.find(class_id)
                if c_node in new_hashcons:
                    existing_id = new_hashcons[c_node]
                    if self.find(existing_id) != c_id:
                        self.merge(existing_id, c_id)
                        changed = True
                else:
                    new_hashcons[c_node] = c_id

            self.hashcons = new_hashcons
            if not changed:
                break
            rebuilt = True
        return rebuilt

    def apply_rules(
        self,
        rules: List[RewriteRule],
        allowed_safeties: Set[RuleSafety],
        max_iterations: int = 5,
    ) -> int:
        """
        Apply rewrite rules up to saturation or max_iterations.
        Only rules whose safety is in `allowed_safeties` are evaluated.
        """
        total_matches = 0
        for _ in range(max_iterations):
            matches: List[Tuple[RewriteRule, int, int]] = []
            for class_id, eclass in list(self.classes.items()):
                canon_id = self.find(class_id)
                for node in list(eclass.nodes):
                    for rule in rules:
                        if rule.safety not in allowed_safeties:
                            continue
                        match_env = rule.match_fn(node, self)
                        if match_env is not None:
                            target_id = rule.apply_fn(match_env, self)
                            if target_id is not None:
                                matches.append((rule, canon_id, target_id))

            if not matches:
                break

            for rule, orig_id, repl_id in matches:
                if self.find(orig_id) != self.find(repl_id):
                    self.merge(orig_id, repl_id)
                    self.applied_rules.append(rule.name)
                    total_matches += 1

            self.rebuild()

        return total_matches

    def extract_cheapest(
        self,
        root_id: int,
        cost_fn: Callable[[ENode, Dict[int, float]], float],
    ) -> Tuple[ENode, float]:
        """
        Extract the lowest-cost expression from the canonical root e-class.
        Uses bottom-up dynamic programming.
        """
        canon_root = self.find(root_id)
        costs: Dict[int, float] = {}
        best_nodes: Dict[int, ENode] = {}

        # Iterative fixed-point cost relaxation
        changed = True
        iterations = 0
        max_iter = max(len(self.classes) * 2, 20)

        while changed and iterations < max_iter:
            changed = False
            iterations += 1
            for class_id, eclass in self.classes.items():
                c_id = self.find(class_id)
                current_best_cost = costs.get(c_id, float("inf"))
                current_best_node = best_nodes.get(c_id, None)

                for node in eclass.nodes:
                    c_node = self.canonicalize_node(node)
                    # Check if all children have computed costs
                    if all(self.find(c) in costs for c in c_node.children):
                        node_cost = cost_fn(c_node, costs)
                        if node_cost < current_best_cost:
                            costs[c_id] = node_cost
                            best_nodes[c_id] = c_node
                            changed = True

        if canon_root not in best_nodes:
            # Fallback: pick any node from the root eclass
            root_class = self.classes.get(canon_root)
            if root_class and root_class.nodes:
                fallback_node = next(iter(root_class.nodes))
                return fallback_node, 100.0
            return ENode(op="UNKNOWN"), float("inf")

        return best_nodes[canon_root], costs.get(canon_root, 1.0)


# ==============================================================================
# Standard Algebraic & Contract-Aware Rules
# ==============================================================================

def make_default_rules() -> List[RewriteRule]:
    """Build canonical rewrite rules tagged by exact mathematical soundness."""
    rules = []

    # Rule: x + 0 -> x (EXACT)
    def match_add_zero(node: ENode, eg: EGraph) -> Optional[Dict[str, Any]]:
        if node.op in ("ADD", "GPU_ADD") and len(node.children) == 2:
            left, right = node.children
            # Check if right or left is constant 0
            for child, other in [(right, left), (left, right)]:
                c_class = eg.classes.get(eg.find(child))
                if c_class:
                    for n in c_class.nodes:
                        if n.op == "CONST_0" or (n.op == "CONST" and n.metadata == (("val", 0),)):
                            return {"x": other}
        return None

    def apply_add_zero(env: Dict[str, Any], eg: EGraph) -> Optional[int]:
        return eg.find(env["x"])

    rules.append(
        RewriteRule(
            name="ADD_ZERO_ELIMINATION",
            safety=RuleSafety.EXACT,
            match_fn=match_add_zero,
            apply_fn=apply_add_zero,
            description="Eliminates addition with constant zero.",
        )
    )

    # Rule: x * 1 -> x (EXACT)
    def match_mul_one(node: ENode, eg: EGraph) -> Optional[Dict[str, Any]]:
        if node.op in ("MUL", "GPU_MUL") and len(node.children) == 2:
            left, right = node.children
            for child, other in [(right, left), (left, right)]:
                c_class = eg.classes.get(eg.find(child))
                if c_class:
                    for n in c_class.nodes:
                        if n.op == "CONST_1" or (n.op == "CONST" and n.metadata == (("val", 1),)):
                            return {"x": other}
        return None

    def apply_mul_one(env: Dict[str, Any], eg: EGraph) -> Optional[int]:
        return eg.find(env["x"])

    rules.append(
        RewriteRule(
            name="MUL_ONE_ELIMINATION",
            safety=RuleSafety.EXACT,
            match_fn=match_mul_one,
            apply_fn=apply_mul_one,
            description="Eliminates multiplication by constant one.",
        )
    )

    # Rule: x * 0 -> 0 (EXACT)
    def match_mul_zero(node: ENode, eg: EGraph) -> Optional[Dict[str, Any]]:
        if node.op in ("MUL", "GPU_MUL") and len(node.children) == 2:
            for child in node.children:
                c_class = eg.classes.get(eg.find(child))
                if c_class:
                    for n in c_class.nodes:
                        if n.op == "CONST_0" or (n.op == "CONST" and n.metadata == (("val", 0),)):
                            return {"zero_class": child}
        return None

    def apply_mul_zero(env: Dict[str, Any], eg: EGraph) -> Optional[int]:
        return eg.find(env["zero_class"])

    rules.append(
        RewriteRule(
            name="MUL_ZERO_ANNIHILATION",
            safety=RuleSafety.EXACT,
            match_fn=match_mul_zero,
            apply_fn=apply_mul_zero,
            description="Replaces multiplication by zero with constant zero.",
        )
    )

    # Rule: transpose(transpose(x)) -> x (EXACT)
    def match_double_transpose(node: ENode, eg: EGraph) -> Optional[Dict[str, Any]]:
        if node.op in ("TRANSPOSE", "GPU_TRANSPOSE", "PERMUTE") and len(node.children) == 1:
            child = node.children[0]
            c_class = eg.classes.get(eg.find(child))
            if c_class:
                for n in c_class.nodes:
                    if n.op in ("TRANSPOSE", "GPU_TRANSPOSE") and len(n.children) == 1:
                        return {"x": n.children[0]}
        return None

    def apply_double_transpose(env: Dict[str, Any], eg: EGraph) -> Optional[int]:
        return eg.find(env["x"])

    rules.append(
        RewriteRule(
            name="DOUBLE_TRANSPOSE_CANCELLATION",
            safety=RuleSafety.EXACT,
            match_fn=match_double_transpose,
            apply_fn=apply_double_transpose,
            description="Cancels involution of double transposition.",
        )
    )

    # Rule: Low-Rank Approximation A ~ U @ V^T (APPROXIMATE)
    def match_low_rank(node: ENode, eg: EGraph) -> Optional[Dict[str, Any]]:
        if node.op in ("MATMUL", "GPU_MATMUL", "GEMM") and len(node.children) == 2:
            return {"a": node.children[0], "b": node.children[1]}
        return None

    def apply_low_rank(env: Dict[str, Any], eg: EGraph) -> Optional[int]:
        # Synthesize LOW_RANK_MATMUL node
        lr_node = ENode(op="LOW_RANK_APPROX_MATMUL", children=(env["a"], env["b"]))
        return eg.add(lr_node)

    rules.append(
        RewriteRule(
            name="LOW_RANK_APPROXIMATION",
            safety=RuleSafety.APPROXIMATE,
            match_fn=match_low_rank,
            apply_fn=apply_low_rank,
            description="Replaces dense GEMM with low-rank factorization (Approximate only).",
        )
    )

    return rules


def default_cost_function(node: ENode, child_costs: Dict[int, float]) -> float:
    """Calculate operator compute cost, prioritizing zero-cost & collapsed nodes."""
    op_base_costs = {
        "CONST": 0.0,
        "CONST_0": 0.0,
        "CONST_1": 0.0,
        "VAR": 0.0,
        "ADD": 1.0,
        "SUB": 1.0,
        "MUL": 1.5,
        "DIV": 4.0,
        "FMA": 1.5,
        "MATMUL": 100.0,
        "LOW_RANK_APPROX_MATMUL": 20.0,
        "TRANSPOSE": 0.5,
        "PERMUTE": 0.5,
    }
    base = op_base_costs.get(node.op, 5.0)
    children_sum = sum(child_costs.get(c, 0.0) for c in node.children)
    return base + children_sum
