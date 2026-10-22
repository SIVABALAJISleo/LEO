"""
hyper_x/cpce/egraph.py
======================
Equality Saturation (E-Graph) Engine for Automated Algorithmic Discovery.
Applies rewrite rules simultaneously without fixed-order phase ordering biases.
Stores equivalent program representations in a compact e-graph with congruence closure,
then extracts the cost-optimal circuit via dynamic programming.

References:
- Willsey et al., "egg: Fast and Extensible Equality Saturation", POPL 2021.
- Tate et al., "Equality Saturation: A New Approach to Optimization", LMCS 2011.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np

from hyper_x.cpce.ir import CanonicalGraph, CIRNode, OpType


# ── E-Graph Node and Class Definitions ────────────────────────────────────── #

@dataclasses.dataclass(frozen=True)
class ENode:
    op: str
    children: Tuple[int, ...] = ()
    params: Tuple[Tuple[str, Any], ...] = ()

    @property
    def key(self) -> Tuple[str, Tuple[int, ...]]:
        return (self.op, self.children)


class EClass:
    """An equivalence class containing congruent expression nodes."""

    def __init__(self, class_id: int):
        self.class_id: int = class_id
        self.nodes: Set[ENode] = set()
        self.parents: List[Tuple[ENode, int]] = []  # (parent_node, parent_class_id)
        self.best_node: Optional[ENode] = None
        self.best_cost: float = float("inf")

    def __repr__(self) -> str:
        return f"EClass({self.class_id}, nodes={len(self.nodes)})"


class EGraph:
    """
    Equivalence Graph with Union-Find and Incremental Congruence Closure.
    """

    def __init__(self):
        self.union_find: Dict[int, int] = {}
        self.classes: Dict[int, EClass] = {}
        self.hashcons: Dict[Tuple[str, Tuple[int, ...]], int] = {}
        self._next_id: int = 0
        self._worklist: Set[int] = set()

    def find(self, class_id: int) -> int:
        """Finds root of class_id with path compression."""
        root = class_id
        while root in self.union_find and self.union_find[root] != root:
            root = self.union_find[root]

        curr = class_id
        while curr != root:
            parent = self.union_find.get(curr, curr)
            self.union_find[curr] = root
            curr = parent
        return root

    def canonicalize_node(self, node: ENode) -> ENode:
        """Returns node with all child class IDs mapped to their canonical roots."""
        canonical_children = tuple(self.find(c) for c in node.children)
        return ENode(op=node.op, children=canonical_children, params=node.params)

    def add(self, node: ENode) -> int:
        """Adds an ENode to the e-graph, returning its canonical EClass ID."""
        canonical = self.canonicalize_node(node)
        lookup_key = canonical.key

        if lookup_key in self.hashcons:
            return self.find(self.hashcons[lookup_key])

        new_id = self._next_id
        self._next_id += 1
        self.union_find[new_id] = new_id

        eclass = EClass(new_id)
        eclass.nodes.add(canonical)
        self.classes[new_id] = eclass
        self.hashcons[lookup_key] = new_id

        for child_id in canonical.children:
            self.classes[self.find(child_id)].parents.append((canonical, new_id))

        return new_id

    def union(self, id1: int, id2: int) -> int:
        """Merges two equivalence classes and enqueues parents for congruence closure."""
        root1 = self.find(id1)
        root2 = self.find(id2)
        if root1 == root2:
            return root1

        # Make root1 the new leader
        self.union_find[root2] = root1
        cls1 = self.classes[root1]
        cls2 = self.classes[root2]

        cls1.nodes.update(cls2.nodes)
        cls1.parents.extend(cls2.parents)
        self._worklist.add(root1)
        return root1

    def rebuild(self) -> None:
        """Restores congruence closure invariants."""
        while self._worklist:
            cid = self.find(self._worklist.pop())
            eclass = self.classes[cid]

            # Rehash all parents
            new_parents: List[Tuple[ENode, int]] = []
            for parent_node, parent_cid in eclass.parents:
                canon_parent = self.canonicalize_node(parent_node)
                p_root = self.find(parent_cid)
                lookup_key = canon_parent.key

                if lookup_key in self.hashcons and self.find(self.hashcons[lookup_key]) != p_root:
                    self.union(self.hashcons[lookup_key], p_root)
                self.hashcons[lookup_key] = p_root
                new_parents.append((canon_parent, p_root))

            eclass.parents = new_parents

    def total_nodes(self) -> int:
        """Returns total number of ENodes across all EClasses."""
        return sum(len(c.nodes) for c in self.classes.values())


# ── Rewrite Rules for Equality Saturation ─────────────────────────────────── #

class EGraphRule:
    """Base class for rewrite rules operating over E-Graphs."""

    def __init__(self, name: str):
        self.name = name

    def apply(self, egraph: EGraph) -> int:
        """Applies rule to egraph. Returns number of unions/nodes created."""
        raise NotImplementedError


class EGraphIdentityRule(EGraphRule):
    """A * I => A and I * A => A."""

    def __init__(self):
        super().__init__("EGRAPH_IDENTITY_ELIMINATION")

    def apply(self, egraph: EGraph) -> int:
        matches = 0
        for class_id, eclass in list(egraph.classes.items()):
            root_id = egraph.find(class_id)
            for node in list(eclass.nodes):
                if node.op == "MATMUL" and len(node.children) == 2:
                    left, right = node.children
                    left_nodes = egraph.classes[egraph.find(left)].nodes
                    right_nodes = egraph.classes[egraph.find(right)].nodes

                    # Case 1: left * IDENTITY => left
                    if any(n.op == "IDENTITY" for n in right_nodes):
                        egraph.union(root_id, left)
                        matches += 1
                    # Case 2: IDENTITY * right => right
                    elif any(n.op == "IDENTITY" for n in left_nodes):
                        egraph.union(root_id, right)
                        matches += 1
        return matches


class EGraphZeroRule(EGraphRule):
    """A * 0 => 0 and 0 * A => 0."""

    def __init__(self):
        super().__init__("EGRAPH_ZERO_PROPAGATION")

    def apply(self, egraph: EGraph) -> int:
        matches = 0
        for class_id, eclass in list(egraph.classes.items()):
            root_id = egraph.find(class_id)
            for node in list(eclass.nodes):
                if node.op == "MATMUL" and len(node.children) == 2:
                    left, right = node.children
                    left_nodes = egraph.classes[egraph.find(left)].nodes
                    right_nodes = egraph.classes[egraph.find(right)].nodes

                    zero_target = None
                    for n in right_nodes:
                        if n.op == "ZERO":
                            zero_target = right
                            break
                    if zero_target is None:
                        for n in left_nodes:
                            if n.op == "ZERO":
                                zero_target = left
                                break

                    if zero_target is not None:
                        egraph.union(root_id, zero_target)
                        matches += 1
        return matches


class EGraphDiagonalScalingRule(EGraphRule):
    """DIAGONAL(D) * B => SCALE(D, B)."""

    def __init__(self):
        super().__init__("EGRAPH_DIAGONAL_SCALING")

    def apply(self, egraph: EGraph) -> int:
        matches = 0
        for class_id, eclass in list(egraph.classes.items()):
            root_id = egraph.find(class_id)
            for node in list(eclass.nodes):
                if node.op == "MATMUL" and len(node.children) == 2:
                    left, right = node.children
                    left_nodes = egraph.classes[egraph.find(left)].nodes

                    for lnode in left_nodes:
                        if lnode.op == "DIAGONAL":
                            scale_node = ENode("SCALE", (left, right), params=node.params)
                            new_class = egraph.add(scale_node)
                            egraph.union(root_id, new_class)
                            matches += 1
                            break
        return matches


class EGraphHornerRule(EGraphRule):
    """Discovers polynomial chains and fuses into HORNER_EVAL."""

    def __init__(self):
        super().__init__("EGRAPH_HORNER_FUSION")

    def apply(self, egraph: EGraph) -> int:
        matches = 0
        for class_id, eclass in list(egraph.classes.items()):
            root_id = egraph.find(class_id)
            for node in list(eclass.nodes):
                if node.op == "POLYNOMIAL_EXPANDED":
                    horner_node = ENode("HORNER_EVAL", node.children, params=node.params)
                    new_cid = egraph.add(horner_node)
                    egraph.union(root_id, new_cid)
                    matches += 1
        return matches


# ── Equality Saturation Engine ────────────────────────────────────────────── #

class EqualitySaturationEngine:
    """
    Automated algorithmic search engine based on Equality Saturation.
    """

    def __init__(self, rules: Optional[List[EGraphRule]] = None):
        self.rules: List[EGraphRule] = rules or [
            EGraphIdentityRule(),
            EGraphZeroRule(),
            EGraphDiagonalScalingRule(),
            EGraphHornerRule(),
        ]

    def build_egraph(self, graph: CanonicalGraph) -> Tuple[EGraph, int]:
        """Translates a CanonicalGraph into an EGraph, returning (egraph, root_class_id)."""
        egraph = EGraph()
        node_to_class: Dict[str, int] = {}

        for node in graph.topological_sort():
            child_classes = tuple(node_to_class[inp] for inp in node.inputs)
            params = tuple(sorted(node.parameters.items())) if node.parameters else ()

            # Map op types
            op_str = node.op_type.value
            if "structure" in node.parameters:
                op_str = str(node.parameters["structure"]).upper()

            enode = ENode(op=op_str, children=child_classes, params=params)
            cid = egraph.add(enode)
            node_to_class[node.node_id] = cid

        out_node_id = graph.output_nodes[0] if graph.output_nodes else list(graph.nodes.keys())[-1]
        root_id = node_to_class[out_node_id]
        return egraph, root_id

    def saturate(
        self,
        egraph: EGraph,
        max_iterations: int = 8,
        node_budget: int = 1500,
    ) -> List[str]:
        """
        Runs equality saturation until convergence or budget depletion.
        Returns list of applied rule names that fired.
        """
        applied_rules: Set[str] = set()

        for _ in range(max_iterations):
            if egraph.total_nodes() >= node_budget:
                break

            total_matches = 0
            for rule in self.rules:
                matches = rule.apply(egraph)
                if matches > 0:
                    applied_rules.add(rule.name)
                    total_matches += matches

            egraph.rebuild()
            if total_matches == 0:
                # Saturated: no new equivalences discovered
                break

        return sorted(list(applied_rules))

    def extract_optimal_ast(
        self,
        egraph: EGraph,
        root_id: int,
    ) -> Tuple[CanonicalGraph, float]:
        """
        Extracts the lowest-cost equivalent CanonicalGraph from the saturated E-Graph
        using dynamic programming cost minimization.
        """
        cost_weights = {
            "IDENTITY": 0.0,
            "ZERO": 0.0,
            "INPUT": 0.0,
            "CONSTANT": 0.0,
            "SCALE": 1.0,         # O(MN)
            "HORNER_EVAL": 2.0,   # O(2N)
            "MATMUL": 100.0,      # O(2MNK)
            "ADD": 1.0,
        }

        # Dynamic programming bottom-up traversal with cycle breaking
        memo_cost: Dict[int, float] = {}
        memo_node: Dict[int, ENode] = {}
        in_progress: Set[int] = set()

        def get_class_cost(cid: int) -> float:
            canon_cid = egraph.find(cid)
            if canon_cid in memo_cost:
                return memo_cost[canon_cid]
            if canon_cid in in_progress:
                # Cycle detected: return inf so this loop is pruned
                return float("inf")

            in_progress.add(canon_cid)
            best_cost = float("inf")
            best_node = None

            for node in egraph.classes[canon_cid].nodes:
                canon_children = tuple(egraph.find(c) for c in node.children)
                if canon_cid in canon_children:
                    # Direct self-loop (e.g. A * I => A in same class)
                    continue

                op_cost = cost_weights.get(node.op, 10.0)
                children_costs = [get_class_cost(c) for c in canon_children]
                total = op_cost + sum(children_costs)
                if total < best_cost:
                    best_cost = total
                    best_node = node

            in_progress.remove(canon_cid)
            if best_node is None:
                # Fallback to any non-self-looping or base node
                for node in egraph.classes[canon_cid].nodes:
                    best_node = node
                    best_cost = cost_weights.get(node.op, 10.0)
                    break

            memo_cost[canon_cid] = best_cost
            memo_node[canon_cid] = best_node
            return best_cost

        root_cost = get_class_cost(root_id)

        # Reconstruct CanonicalGraph
        extracted_graph = CanonicalGraph()
        visited_classes: Dict[int, str] = {}

        def reconstruct(cid: int) -> str:
            canon_cid = egraph.find(cid)
            if canon_cid in visited_classes:
                return visited_classes[canon_cid]

            node = memo_node.get(canon_cid)
            if node is None:
                node = next(iter(egraph.classes[canon_cid].nodes))

            out_id = f"opt_node_{canon_cid}"
            visited_classes[canon_cid] = out_id

            child_node_ids = []
            for c in node.children:
                canon_c = egraph.find(c)
                if canon_c != canon_cid:
                    child_node_ids.append(reconstruct(canon_c))

            # Map back to OpType
            if node.op in ("IDENTITY", "ZERO", "INPUT"):
                op_t = OpType.INPUT
            elif node.op == "SCALE":
                op_t = OpType.SCALE
            elif node.op == "HORNER_EVAL":
                op_t = OpType.HORNER_EVAL
            elif node.op == "MATMUL":
                op_t = OpType.MATMUL
            else:
                op_t = OpType.CONSTANT

            extracted_graph.add_node(CIRNode(
                node_id=out_id,
                op_type=op_t,
                inputs=child_node_ids,
                parameters=dict(node.params),
            ))
            return out_id

        root_node_id = reconstruct(root_id)
        extracted_graph.add_node(CIRNode(
            node_id="opt_final_output",
            op_type=OpType.OUTPUT,
            inputs=[root_node_id],
        ))

        return extracted_graph, root_cost
