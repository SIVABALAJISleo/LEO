"""
hyper/research_engine/minimal_sufficient_computation.py
======================================================
Minimal Sufficient Computation Engine.

Analyzes computational graphs and formal contracts to determine the exact minimum
computation and information materialization strictly required to produce the requested output.
"""

from __future__ import annotations
import copy
from typing import Any, Dict, List, Set, Tuple
import numpy as np

from hyper.discovery.cir import CIRGraph, CIRNode, CIREdge, OpType
from hyper.research_engine.contracts import ProblemContract


class MinimalSufficientComputationEngine:
    """
    Automated reasoning engine that discovers opportunities to eliminate unnecessary work,
    fuse operator pipelines, and avoid materializing intermediate tensor states.
    """

    @classmethod
    def analyze_graph(cls, graph: CIRGraph, contract: ProblemContract) -> Dict[str, Any]:
        """
        Conducts full sufficiency analysis on the input CIR graph.
        Returns detailed metrics on necessary vs. eliminable computation.
        """
        # 1. Reverse reachability from declared outputs
        reachable_nodes: Set[str] = set()
        worklist = list(graph.outputs)
        
        # Build reverse adjacency map (target -> sources)
        reverse_adj: Dict[str, List[str]] = {nid: [] for nid in graph.nodes}
        for edge in graph.edges:
            if edge.target_id in reverse_adj:
                reverse_adj[edge.target_id].append(edge.source_id)

        while worklist:
            curr = worklist.pop()
            if curr not in reachable_nodes:
                reachable_nodes.add(curr)
                for src in reverse_adj.get(curr, []):
                    worklist.append(src)

        unreachable_nodes = set(graph.nodes.keys()) - reachable_nodes
        
        # 2. Intermediate state materialization analysis
        intermediate_nodes = [
            nid for nid in reachable_nodes 
            if nid not in graph.inputs and nid not in graph.outputs
        ]
        
        total_intermediate_bytes = sum(
            graph.nodes[nid].output_meta.memory_bytes 
            for nid in intermediate_nodes 
            if graph.nodes[nid].output_meta
        )

        # 3. Fusion & Shortcut Opportunities
        fusible_pairs = []
        for edge in graph.edges:
            src = graph.nodes.get(edge.source_id)
            tgt = graph.nodes.get(edge.target_id)
            if src and tgt:
                # e.g., Matmul followed by Add or Relu
                if src.op_type in (OpType.MATMUL, OpType.CONV2D) and tgt.op_type in (OpType.ADD, OpType.RELU):
                    fusible_pairs.append((src.name, tgt.name, f"{src.op_type.value}_{tgt.op_type.value}_FUSION"))

        # 4. Projection Shortcut (Associativity reordering: (A @ B) @ v -> A @ (B @ v))
        vector_projection_opportunity = False
        for node in graph.nodes.values():
            if node.op_type == OpType.MATMUL and node.output_meta:
                # If output is a column vector or matrix with small dimension
                if len(node.output_meta.shape) >= 2 and (node.output_meta.shape[-1] == 1 or node.output_meta.shape[0] == 1):
                    vector_projection_opportunity = True

        elimination_potential_flops = sum(
            graph.nodes[nid].estimated_flops for nid in unreachable_nodes
        )

        return {
            "total_nodes": len(graph.nodes),
            "necessary_nodes": len(reachable_nodes),
            "unreachable_dead_nodes": len(unreachable_nodes),
            "dead_node_names": [graph.nodes[nid].name for nid in unreachable_nodes],
            "intermediate_nodes_count": len(intermediate_nodes),
            "total_intermediate_bytes": total_intermediate_bytes,
            "fusible_pairs": fusible_pairs,
            "vector_projection_shortcut_possible": vector_projection_opportunity,
            "elimination_potential_flops": elimination_potential_flops,
            "is_minimal": len(unreachable_nodes) == 0 and len(fusible_pairs) == 0,
        }

    @classmethod
    def optimize_graph(cls, graph: CIRGraph, contract: ProblemContract) -> Tuple[CIRGraph, Dict[str, Any]]:
        """
        Creates an optimized CIR graph where dead nodes are stripped,
        fusible operators are merged, and intermediate materializations are minimized.
        """
        opt_graph = copy.deepcopy(graph)
        analysis = cls.analyze_graph(opt_graph, contract)
        
        # 1. Eliminate dead nodes
        removed_count = opt_graph.eliminate_dead_nodes()

        # 2. Perform operator fusion where supported
        fused_count = 0
        nodes_to_remove = set()
        
        # Check for MatMul + Add -> Fused Gemm Add
        for edge in list(opt_graph.edges):
            src = opt_graph.nodes.get(edge.source_id)
            tgt = opt_graph.nodes.get(edge.target_id)
            if src and tgt and src.op_type == OpType.MATMUL and tgt.op_type == OpType.ADD:
                # Only fuse if src has no other consumers
                consumers = [e for e in opt_graph.edges if e.source_id == src.node_id]
                if len(consumers) == 1:
                    src.op_type = OpType.FUSED_GEMM_ADD
                    src.name = f"fused_{src.name}_{tgt.name}"
                    # Re-wire tgt's other input to src
                    other_inputs = [inp for inp in tgt.inputs if inp != src.node_id]
                    src.inputs.extend(other_inputs)
                    
                    # Update edges from tgt to its targets to come from src instead
                    for out_edge in opt_graph.edges:
                        if out_edge.source_id == tgt.node_id:
                            out_edge.source_id = src.node_id
                            
                    if tgt.node_id in opt_graph.outputs:
                        idx = opt_graph.outputs.index(tgt.node_id)
                        opt_graph.outputs[idx] = src.node_id
                        
                    nodes_to_remove.add(tgt.node_id)
                    fused_count += 1

        for nid in nodes_to_remove:
            if nid in opt_graph.nodes:
                del opt_graph.nodes[nid]
        opt_graph.edges = [e for e in opt_graph.edges if e.source_id not in nodes_to_remove and e.target_id not in nodes_to_remove]

        optimization_report = {
            "dead_nodes_removed": removed_count,
            "operators_fused": fused_count,
            "memory_saved_bytes": analysis["total_intermediate_bytes"] if fused_count > 0 else 0,
            "original_nodes": len(graph.nodes),
            "final_nodes": len(opt_graph.nodes),
        }
        return opt_graph, optimization_report
