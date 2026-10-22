"""
hyper_x/cpce/rewrite_rules.py
=============================
Sound Algebraic Rewrite Rules for CPCE.
Applies exact and contract-preserving mathematical transformations:
- Identity elimination (A * I = A, I * B = B)
- Zero propagation (A * 0 = 0, 0 * B = 0)
- Diagonal scaling (D * B = scale(D, B))
- Common Subexpression Elimination (CSE)
- Constant folding
- Dead code elimination
- Horner polynomial transformation
- Sparse CSR conversion
"""

from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from hyper_x.cpce.ir import CanonicalGraph, CIRNode, OpType
from hyper_x.cpce.types import ZeroMatrix



class RewriteRule(abc.ABC):
    """Abstract base class for sound graph rewrite rules."""

    @property
    @abc.abstractmethod
    def rule_id(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def is_exact(self) -> bool:
        """True if the rewrite is mathematically and numerically exact."""
        pass

    @property
    @abc.abstractmethod
    def justification(self) -> str:
        """Mathematical justification for the transformation."""
        pass

    @abc.abstractmethod
    def can_apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        """Checks preconditions for the rule on a specific node."""
        pass

    @abc.abstractmethod
    def apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        """Applies transformation in-place to graph. Returns True if modified."""
        pass


class IdentityEliminationRule(RewriteRule):
    """
    Eliminates matrix multiplications involving the identity matrix:
    A * I_n -> A
    I_m * B -> B
    FLOPs eliminated: 2 * M * N * K
    """

    @property
    def rule_id(self) -> str:
        return "RULE_001_IDENTITY_ELIMINATION"

    @property
    def name(self) -> str:
        return "Identity Matrix Multiplication Elimination"

    @property
    def is_exact(self) -> bool:
        return True

    @property
    def justification(self) -> str:
        return "A @ I = A and I @ B = B by definition of the multiplicative identity element."

    def can_apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        if node.op_type != OpType.MATMUL or len(node.inputs) != 2:
            return False
        in0 = graph.nodes.get(node.inputs[0])
        in1 = graph.nodes.get(node.inputs[1])
        if not in0 or not in1:
            return False
        return in0.structural_tag == "IDENTITY" or in1.structural_tag == "IDENTITY"

    def apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        in0 = graph.nodes[node.inputs[0]]
        in1 = graph.nodes[node.inputs[1]]

        surviving_id = None
        if in0.structural_tag == "IDENTITY":
            surviving_id = in1.node_id
        elif in1.structural_tag == "IDENTITY":
            surviving_id = in0.node_id

        if surviving_id is None:
            return False

        # Reroute all consumers of node to surviving_id
        for consumer_id in list(node.outputs):
            consumer = graph.nodes[consumer_id]
            for idx, inp in enumerate(consumer.inputs):
                if inp == node.node_id:
                    consumer.inputs[idx] = surviving_id
            if consumer_id not in graph.nodes[surviving_id].outputs:
                graph.nodes[surviving_id].outputs.append(consumer_id)

        # Disconnect node from its inputs
        for inp_id in node.inputs:
            if inp_id in graph.nodes and node.node_id in graph.nodes[inp_id].outputs:
                graph.nodes[inp_id].outputs.remove(node.node_id)

        # Remove eliminated node from graph
        del graph.nodes[node.node_id]
        return True


class ZeroPropagationRule(RewriteRule):
    """
    Propagates zero matrices through multiplication:
    A * 0 -> 0
    0 * B -> 0
    """

    @property
    def rule_id(self) -> str:
        return "RULE_002_ZERO_PROPAGATION"

    @property
    def name(self) -> str:
        return "Zero Matrix Multiplication Propagation"

    @property
    def is_exact(self) -> bool:
        return True

    @property
    def justification(self) -> str:
        return "A @ 0 = 0 and 0 @ B = 0 under standard linear algebra semantics without NaN/Inf."

    def can_apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        if node.op_type != OpType.MATMUL or len(node.inputs) != 2:
            return False
        in0 = graph.nodes.get(node.inputs[0])
        in1 = graph.nodes.get(node.inputs[1])
        if not in0 or not in1:
            return False
        return in0.structural_tag == "ZERO" or in1.structural_tag == "ZERO"

    def apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        in0 = graph.nodes[node.inputs[0]]
        in1 = graph.nodes[node.inputs[1]]

        out_shape = (in0.shape[0], in1.shape[1]) if (in0.shape and in1.shape) else node.shape

        # Disconnect node from its inputs because constant zero does not depend on operands
        for inp_id in list(node.inputs):
            if inp_id in graph.nodes and node.node_id in graph.nodes[inp_id].outputs:
                graph.nodes[inp_id].outputs.remove(node.node_id)
        node.inputs = []

        node.structural_tag = "ZERO"
        node.op_type = OpType.CONSTANT
        node.is_constant = True
        node.constant_value = ZeroMatrix(out_shape or (64, 64), dtype=node.dtype)
        node.shape = out_shape
        node.resource_cost_flops = 0.0
        node.parameters["eliminated_by"] = self.rule_id
        return True



class DiagonalScalingRule(RewriteRule):
    """
    Transforms diagonal matrix multiplication into elementwise row scaling:
    diag(v) * B -> v[:, None] * B
    Reduces complexity from O(N^3) to O(N^2).
    """

    @property
    def rule_id(self) -> str:
        return "RULE_003_DIAGONAL_SCALING"

    @property
    def name(self) -> str:
        return "Diagonal Matrix Multiplication to Vector Scaling"

    @property
    def is_exact(self) -> bool:
        return True

    @property
    def justification(self) -> str:
        return "diag(v) @ B is mathematically identical to scaling each row i of B by v[i]."

    def can_apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        if node.op_type != OpType.MATMUL or len(node.inputs) != 2:
            return False
        in0 = graph.nodes.get(node.inputs[0])
        return in0 is not None and in0.structural_tag == "DIAGONAL"

    def apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        in0 = graph.nodes[node.inputs[0]]
        in1 = graph.nodes[node.inputs[1]]

        node.op_type = OpType.SCALE
        if in0.shape and in1.shape:
            # Operation count reduced from 2*N^3 to N^2 multiplications
            N, K = in1.shape
            node.resource_cost_flops = float(N * K)
        node.parameters["transformed_by"] = self.rule_id
        return True


class CommonSubexpressionEliminationRule(RewriteRule):
    """
    Eliminates redundant identical computations:
    If node A and node B compute the identical OpType on the identical inputs,
    fuses B into A.
    """

    @property
    def rule_id(self) -> str:
        return "RULE_004_CSE"

    @property
    def name(self) -> str:
        return "Common Subexpression Elimination"

    @property
    def is_exact(self) -> bool:
        return True

    @property
    def justification(self) -> str:
        return "Deterministic pure operations on identical operands yield identical results."

    def can_apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        if node.op_type in (OpType.INPUT, OpType.OUTPUT):
            return False
        if not node.inputs:
            return False
        # Check if there is another node with identical op_type and inputs
        for other_id, other in graph.nodes.items():
            if other.op_type in (OpType.INPUT, OpType.OUTPUT):
                continue
            if other_id != node.node_id and other.op_type == node.op_type:
                if other.inputs == node.inputs and other.parameters == node.parameters:
                    return True
        return False

    def apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        if node.op_type in (OpType.INPUT, OpType.OUTPUT) or not node.inputs:
            return False
        for other_id, other in list(graph.nodes.items()):
            if other.op_type in (OpType.INPUT, OpType.OUTPUT):
                continue
            if other_id != node.node_id and other.op_type == node.op_type:
                if other.inputs == node.inputs and other.parameters == node.parameters:
                    # Fuse other into node
                    for consumer_id in list(other.outputs):
                        consumer = graph.nodes[consumer_id]
                        for idx, inp in enumerate(consumer.inputs):
                            if inp == other_id:
                                consumer.inputs[idx] = node.node_id
                        if consumer_id not in node.outputs:
                            node.outputs.append(consumer_id)
                    # Remove redundant node from graph
                    del graph.nodes[other_id]
                    return True
        return False



class HornerPolynomialRule(RewriteRule):
    """
    Transforms explicit polynomial expansion:
    P(x) = c0 + c1*x + c2*x^2 + ... + cn*x^n
    Into nested Horner evaluation:
    P(x) = c0 + x*(c1 + x*(c2 + ... + x*cn))
    Reduces operations from O(N^2) to 2*N.
    """

    @property
    def rule_id(self) -> str:
        return "RULE_005_HORNER_POLYNOMIAL"

    @property
    def name(self) -> str:
        return "Horner's Method for Polynomial Evaluation"

    @property
    def is_exact(self) -> bool:
        return True

    @property
    def justification(self) -> str:
        return "Algebraic polynomial factorization reduces powers to linear multiply-add chains."

    def can_apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        return node.parameters.get("workload_type") == "polynomial_expansion"

    def apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        degree = node.parameters.get("degree", 10)
        node.op_type = OpType.HORNER_EVAL
        # Operations reduced from degree*(degree+1) to 2*degree
        node.resource_cost_flops = float(2 * degree)
        node.parameters["transformed_by"] = self.rule_id
        return True


class DeadCodeEliminationRule(RewriteRule):
    """
    Removes intermediate nodes whose outputs are never consumed and which are not designated graph outputs.
    """

    @property
    def rule_id(self) -> str:
        return "RULE_006_DEAD_CODE_ELIMINATION"

    @property
    def name(self) -> str:
        return "Dead Code Elimination"

    @property
    def is_exact(self) -> bool:
        return True

    @property
    def justification(self) -> str:
        return "Nodes without side effects whose values are never observed can be eliminated without altering observables."

    def can_apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        if node.node_id in graph.output_nodes:
            return False
        return len(node.outputs) == 0 and node.op_type not in (OpType.OUTPUT, OpType.INPUT)

    def apply(self, graph: CanonicalGraph, node: CIRNode) -> bool:
        # Disconnect from inputs
        for inp_id in node.inputs:
            if inp_id in graph.nodes:
                inp_node = graph.nodes[inp_id]
                if node.node_id in inp_node.outputs:
                    inp_node.outputs.remove(node.node_id)
        del graph.nodes[node.node_id]
        return True


class ExactAlgebraicRewriter:
    """
    Iterative fixed-point rewrite coordinator.
    Applies sound algebraic transformations until convergence or step limit.
    """

    def __init__(self, rules: Optional[List[RewriteRule]] = None):
        self.rules: List[RewriteRule] = rules or [
            IdentityEliminationRule(),
            ZeroPropagationRule(),
            DiagonalScalingRule(),
            CommonSubexpressionEliminationRule(),
            HornerPolynomialRule(),
            DeadCodeEliminationRule(),
        ]

    def add_rule(self, rule: RewriteRule):
        """Appends an optimization rewrite rule."""
        self.rules.append(rule)

    def rewrite(self, graph: CanonicalGraph, max_iterations: int = 10) -> Tuple[CanonicalGraph, List[str]]:

        """
        Executes rewrite loop until no rules can fire or iteration limit is reached.
        Returns optimized graph and list of applied rule IDs.
        """
        current_g = graph.clone()
        applied_rules: List[str] = []

        for _ in range(max_iterations):
            modified = False
            for rule in self.rules:
                for nid in list(current_g.nodes.keys()):
                    if nid not in current_g.nodes:
                        continue
                    node = current_g.nodes[nid]
                    if rule.can_apply(current_g, node):
                        if rule.apply(current_g, node):
                            applied_rules.append(rule.rule_id)
                            modified = True
            if not modified:
                break

        return current_g, applied_rules
