"""
hyper_v2/compiler/graph_optimizer.py
Applies graph-level optimizations, algebraic simplifications, and dead-code elimination on ComputationGraphIR.
"""

from typing import List, Dict, Any, Tuple
from hyper_v2.compiler.intermediate_representation import ComputationGraphIR, IRNode, OpCategory, DeviceTarget
from hyper_v2.compiler.contract_compiler import ExecutionContract


class GraphOptimizer:
    """Optimizes ComputationGraphIR based on contract permissions."""

    @staticmethod
    def optimize_graph(graph: ComputationGraphIR, contract: ExecutionContract) -> ComputationGraphIR:
        opt_graph = graph.clone()

        # Step 1: Detect fusible sequences (e.g. MATMUL + ELEMENTWISE BIAS + ACTIVATION)
        GraphOptimizer._fuse_linear_sequences(opt_graph, contract)

        # Step 2: Annotate candidate algorithm substitutions based on contract
        GraphOptimizer._annotate_substitutions(opt_graph, contract)

        opt_graph.recompute_totals()
        return opt_graph

    @staticmethod
    def _fuse_linear_sequences(graph: ComputationGraphIR, contract: ExecutionContract):
        if not contract.is_transformation_permitted("kernel_fusion"):
            return

        # Find adjacent nodes where output of node A is strictly single-use input to node B
        nodes_list = [graph.nodes[nid] for nid in graph.execution_order]
        for i in range(len(nodes_list) - 1):
            curr_node = nodes_list[i]
            next_node = nodes_list[i + 1]

            if curr_node.outputs and next_node.inputs and curr_node.outputs[0] in next_node.inputs:
                if curr_node.op_type == OpCategory.MATMUL and next_node.op_type == OpCategory.ELEMENTWISE:
                    curr_node.is_fused = True
                    curr_node.fused_nodes.append(next_node.id)
                    curr_node.bytes_written = next_node.bytes_written  # Eliminate intermediate write
                    next_node.can_eliminate = True
                    next_node.elimination_reason = f"Fused into {curr_node.id}"

    @staticmethod
    def _annotate_substitutions(graph: ComputationGraphIR, contract: ExecutionContract):
        for node in graph.nodes.values():
            if node.can_eliminate:
                continue

            if node.op_type == OpCategory.MATMUL:
                sparsity = node.attributes.get("sparsity", 0.0)
                if sparsity > 0.5 and contract.is_transformation_permitted("sparsity"):
                    node.substitute_algorithm = "BitNet_1.58b_Addition_Tree"
                    node.flop_cost = int(node.flop_cost * (1.0 - sparsity))
                elif not contract.exactness_required and contract.is_transformation_permitted("low_rank"):
                    node.substitute_algorithm = "Randomized_SVD_LowRank"
                    # O(N*k) vs O(N^3)
                    rank_ratio = 0.08
                    node.flop_cost = int(node.flop_cost * rank_ratio * 2)

            elif node.op_type == OpCategory.FFT:
                if not contract.exactness_required and contract.is_transformation_permitted("sparsity"):
                    k = node.attributes.get("sparsity_k", 16)
                    node.substitute_algorithm = "Sublinear_Sparse_FFT_O(k_log_N)"
                    # Drop FLOPs significantly
                    node.flop_cost = int(k * 1024)

            elif node.op_type == OpCategory.N_BODY_INTERACT:
                if not contract.exactness_required and contract.is_transformation_permitted("Barnes_Hut_expansion"):
                    node.substitute_algorithm = "Barnes_Hut_Octree_O(N_log_N)"
                    num_bodies = node.attributes.get("num_bodies", 4096)
                    import math
                    node.flop_cost = int(num_bodies * math.log2(num_bodies) * 40)
