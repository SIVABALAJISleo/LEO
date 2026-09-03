"""
hyper_v3/transforms/graph.py
Graph-level transformation passes (Dead-code elimination, Node clustering, Fusion).
"""

from typing import Set
from hyper_v3.ir.graph import ComputationGraphIR


class GraphTransformer:
    """Applies whole-graph structural transformations."""

    @staticmethod
    def run_dce_pass(graph: ComputationGraphIR, live_outputs: Set[str]) -> int:
        return graph.eliminate_dead_nodes(live_outputs)

    @staticmethod
    def run_cse_pass(graph: ComputationGraphIR) -> int:
        return graph.apply_common_subexpression_elimination()
