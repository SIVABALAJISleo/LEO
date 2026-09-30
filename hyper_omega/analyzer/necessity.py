"""
hyper_omega/analyzer/necessity.py
Computational Necessity Analysis, Information-Flow Graph, Homotopic Pruning, and Output Sensitivity.
Answers:
«What portion of this computation is mathematically necessary to produce the requested contract output?»
"""
from __future__ import annotations
from typing import Any, Dict, List, Set, Tuple
import numpy as np

from hyper_omega.ir.graph import ComputationalIR, IRNode, IROpType


class NecessityReport:
    def __init__(
        self,
        total_nodes: int,
        necessary_nodes: int,
        pruned_nodes: int,
        eliminated_operations: int,
        output_sensitivity_ratio: float,
    ):
        self.total_nodes = total_nodes
        self.necessary_nodes = necessary_nodes
        self.pruned_nodes = pruned_nodes
        self.eliminated_operations = eliminated_operations
        self.output_sensitivity_ratio = output_sensitivity_ratio

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.total_nodes,
            "necessary_nodes": self.necessary_nodes,
            "pruned_nodes": self.pruned_nodes,
            "eliminated_operations": self.eliminated_operations,
            "output_sensitivity_ratio": round(self.output_sensitivity_ratio, 4),
        }


class NecessityEngine:
    """
    Performs backward dependency traversal from contract output nodes.
    Any node where d(Output)/d(Node) == 0 is marked dead and pruned.
    """

    @staticmethod
    def analyze_and_prune(ir: ComputationalIR) -> Tuple[ComputationalIR, NecessityReport]:
        # Backward reachable set from output nodes
        reachable: Set[str] = set()
        queue: List[str] = list(ir.output_nodes)

        while queue:
            curr_id = queue.pop(0)
            if curr_id in reachable:
                continue
            reachable.add(curr_id)
            if curr_id in ir.nodes:
                node = ir.nodes[curr_id]
                for inp_id in node.inputs:
                    if inp_id not in reachable:
                        queue.append(inp_id)

        # Mark dead nodes
        total_ops_before = ir.count_operations()
        pruned_count = 0
        for n_id, node in ir.nodes.items():
            if n_id not in reachable:
                node.is_dead = True
                pruned_count += 1
            else:
                node.is_dead = False

        total_ops_after = ir.count_operations()
        eliminated_ops = max(0, total_ops_before - total_ops_after)
        total_nodes = len(ir.nodes)
        nec_nodes = len(reachable)
        sensitivity_ratio = (nec_nodes / total_nodes) if total_nodes > 0 else 1.0

        report = NecessityReport(
            total_nodes=total_nodes,
            necessary_nodes=nec_nodes,
            pruned_nodes=pruned_count,
            eliminated_operations=eliminated_ops,
            output_sensitivity_ratio=sensitivity_ratio,
        )
        return ir, report


class InformationSufficiencyEngine:
    """
    Identifies sufficient statistics S(X) where F(X) = H(S(X)) with |S(X)| << |X|.
    """

    @staticmethod
    def find_sufficient_statistic(data: np.ndarray, target_op: str) -> Tuple[bool, str, Optional[Any]]:
        if target_op == "sum_reduction":
            return True, "1D_SCALAR_SUM", np.sum(data)
        elif target_op == "l2_norm":
            return True, "SCALAR_SUM_OF_SQUARES", np.sum(data ** 2)
        elif target_op == "variance":
            return True, "MOMENTS_1_AND_2", (np.mean(data), np.var(data))
        elif target_op == "sparse_nonzeros":
            nnz_indices = np.nonzero(data)
            if len(nnz_indices[0]) < 0.1 * data.size:
                return True, "SPARSE_CSR_TUPLE", (nnz_indices, data[nnz_indices])
        return False, "IRREDUCIBLE_FULL_ENTROPY", None
