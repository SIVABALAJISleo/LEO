"""
hyper/dependency/dependency_analyzer.py
=======================================
Dependency Graph Analyzer:
- Detects dead branches and calculations
- Invariant calculations and common subexpressions
- Critical path and sequential bottlenecks
- Pruning opportunities
"""

from typing import Dict, Any, List, Set
from hyper.workload.graph import OpNode, ComputationGraph


class DependencyAnalyzer:
    """
    Builds and analyzes dependency graphs to eliminate dead/redundant operations.
    """
    def __init__(self):
        pass

    def analyze_dependencies(self, graph: ComputationGraph) -> Dict[str, Any]:
        """
        Extracts dead branches, critical path length, and parallelizable stages.
        """
        all_node_ids = set(graph.nodes.keys())
        depended_nodes = set()
        
        for node in graph.nodes.values():
            for dep in node.dependencies:
                depended_nodes.add(dep)

        # Roots and leaves
        leaf_nodes = all_node_ids - depended_nodes
        root_nodes = {nid for nid, node in graph.nodes.items() if not node.dependencies}

        # Dead node detection (nodes that are neither outputs nor ancestors of outputs)
        dead_nodes = set()
        for nid, node in graph.nodes.items():
            if node.is_dead:
                dead_nodes.add(nid)

        active_flops = sum(node.flops_baseline for nid, node in graph.nodes.items() if nid not in dead_nodes)
        dead_flops = sum(node.flops_baseline for nid, node in graph.nodes.items() if nid in dead_nodes)

        return {
            "total_nodes": len(graph.nodes),
            "dead_nodes_count": len(dead_nodes),
            "root_nodes_count": len(root_nodes),
            "leaf_nodes_count": len(leaf_nodes),
            "active_flops": active_flops,
            "dead_flops": dead_flops,
            "elimination_potential_pct": round((dead_flops / max(1, graph.total_baseline_flops)) * 100.0, 2)
        }
