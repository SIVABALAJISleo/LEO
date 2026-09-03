"""
hyper_mvc_dar/sufficiency.py
Information Sufficiency Engine: Identifies minimal data required by the contract
and prunes non-contributing dimensions, channels, or frequencies.
"""

from typing import Dict, List, Set, Any, Tuple
import numpy as np
from .ir import ComputationGraph, OpNode, TensorDescriptor
from .contract import ExecutionContract


class InformationSufficiencyEngine:
    """Analyzes backward dependencies to determine what information is truly sufficient."""

    @staticmethod
    def analyze_graph(graph: ComputationGraph, contract: ExecutionContract) -> Dict[str, Any]:
        live_tensors: Set[str] = set(graph.terminal_outputs)
        essential_nodes: Set[str] = set()
        discardable_tensors: Set[str] = set()

        # Backward propagation of liveness
        reverse_nodes = list(reversed(graph.topological_sort()))
        for node in reverse_nodes:
            # If any output is in live_tensors, this node is required
            if any(out in live_tensors for out in node.outputs):
                essential_nodes.add(node.node_id)
                for inp in node.inputs:
                    live_tensors.add(inp)
            else:
                for out in node.outputs:
                    discardable_tensors.add(out)

        # Calculate value density
        value_densities = {}
        for nid in essential_nodes:
            node = graph.nodes[nid]
            output_bytes = sum(graph.tensors[o].memory_bytes for o in node.outputs if o in graph.tensors)
            cost = max(1, node.estimated_flops + output_bytes)
            # Higher utility for terminal or close-to-terminal outputs
            depth = 1.0  # Normalized depth heuristic
            value_densities[nid] = round(depth / (cost / 1e6), 4)

        return {
            "essential_node_count": len(essential_nodes),
            "discardable_node_count": len(graph.nodes) - len(essential_nodes),
            "live_tensor_count": len(live_tensors),
            "discardable_tensor_count": len(discardable_tensors),
            "pruned_tensors": list(discardable_tensors),
            "value_densities": value_densities,
            "information_elimination_ratio": round(len(discardable_tensors) / max(1, len(graph.tensors)), 4)
        }
