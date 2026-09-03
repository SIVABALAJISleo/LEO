"""
hyper_mvc_dar/dead_work.py
Dead-Work Elimination Engine: Performs graph-level liveness analysis to eliminate
operations whose outputs do not contribute to the final contract-verified output.
"""

from typing import Set, List, Dict, Any
from .ir import ComputationGraph, OpNode


class DeadWorkEliminator:
    """Prunes dead nodes and unreferenced buffers from the ComputationGraph."""

    @staticmethod
    def eliminate_dead_work(graph: ComputationGraph) -> Dict[str, Any]:
        live_tensors: Set[str] = set(graph.terminal_outputs)
        initial_node_count = len(graph.nodes)
        initial_flops = graph.total_estimated_flops()

        # Iterate until fixpoint
        changed = True
        while changed:
            changed = False
            for node_id, node in list(graph.nodes.items()):
                # Node is live if any output is live
                if any(out in live_tensors for out in node.outputs):
                    for inp in node.inputs:
                        if inp not in live_tensors:
                            live_tensors.add(inp)
                            changed = True

        # Remove dead nodes
        dead_nodes: List[str] = []
        for node_id, node in list(graph.nodes.items()):
            if not any(out in live_tensors for out in node.outputs):
                dead_nodes.append(node_id)
                del graph.nodes[node_id]

        final_flops = graph.total_estimated_flops()
        flops_saved = initial_flops - final_flops

        return {
            "initial_node_count": initial_node_count,
            "final_node_count": len(graph.nodes),
            "eliminated_node_count": len(dead_nodes),
            "eliminated_nodes": dead_nodes,
            "flops_saved": flops_saved,
            "flops_elimination_ratio": round(flops_saved / max(1, initial_flops), 4)
        }
