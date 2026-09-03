"""
hyper_v3/intelligence/dependency.py
Analyzes dependency chains, critical path latency, and discovers parallelizable branches.
"""

from typing import Dict, Any, List, Set
from hyper_v3.ir.graph import ComputationGraphIR
from hyper_v3.ir.node import IRNode


class DependencyAnalyzer:
    """Analyzes the critical path and discovers independent concurrent branches."""

    @staticmethod
    def find_critical_path(graph: ComputationGraphIR) -> Dict[str, Any]:
        topo_nodes = graph.topological_sort()
        earliest_finish: Dict[str, float] = {}

        for node in topo_nodes:
            preds = [edge.source_node_id for edge in graph.edges if edge.target_node_id == node.node_id]
            max_pred_finish = max([earliest_finish.get(p, 0.0) for p in preds], default=0.0)
            earliest_finish[node.node_id] = max_pred_finish + max(node.latency_estimate_us, 1.0)

        critical_path_latency = max(earliest_finish.values(), default=0.0)
        return {
            "critical_path_latency_us": critical_path_latency,
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges)
        }

    @staticmethod
    def find_independent_nodes(graph: ComputationGraphIR) -> List[List[str]]:
        """Groups nodes into independent stages that can execute concurrently on CPU & iGPU."""
        adj = {nid: [] for nid in graph.nodes}
        in_degree = {nid: 0 for nid in graph.nodes}
        for edge in graph.edges:
            adj[edge.source_node_id].append(edge.target_node_id)
            in_degree[edge.target_node_id] += 1

        stages: List[List[str]] = []
        current_stage = [nid for nid, deg in in_degree.items() if deg == 0]

        while current_stage:
            stages.append(current_stage)
            next_stage = []
            for nid in current_stage:
                for neighbor in adj[nid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_stage.append(neighbor)
            current_stage = next_stage

        return stages
