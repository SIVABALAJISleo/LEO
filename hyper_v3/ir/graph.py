"""
hyper_v3/ir/graph.py
Universal Directed Acyclic Graph (DAG) computation graph IR for HYPER 3.0.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Set
from collections import deque
import hashlib
import json

from hyper_v3.ir.node import IRNode
from hyper_v3.ir.dependency import DependencyEdge, DependencyType
from hyper_v3.ir.operation import OpType, DeviceType, NecessityStatus
from hyper_v3.ir.tensor import TensorDescriptor


@dataclass
class ComputationGraphIR:
    """Universal DAG representation of computational workloads."""
    graph_id: str
    nodes: Dict[str, IRNode] = field(default_factory=dict)
    edges: List[DependencyEdge] = field(default_factory=list)
    input_tensors: Dict[str, TensorDescriptor] = field(default_factory=dict)
    output_tensors: Dict[str, TensorDescriptor] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: IRNode) -> str:
        self.nodes[node.node_id] = node
        return node.node_id

    def add_edge(self, source_id: str, target_id: str, dep_type: DependencyType = DependencyType.DATA_FLOW, tensor_name: str = ""):
        self.edges.append(DependencyEdge(source_id, target_id, dep_type, tensor_name))

    def topological_sort(self) -> List[IRNode]:
        """Returns nodes in topologically sorted execution order."""
        in_degree = {nid: 0 for nid in self.nodes}
        adj = {nid: [] for nid in self.nodes}
        for edge in self.edges:
            if edge.source_node_id in adj and edge.target_node_id in in_degree:
                adj[edge.source_node_id].append(edge.target_node_id)
                in_degree[edge.target_node_id] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        sorted_nodes = []

        while queue:
            curr = queue.popleft()
            sorted_nodes.append(self.nodes[curr])
            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Fallback if cycles or disconnected nodes
        if len(sorted_nodes) < len(self.nodes):
            for nid, node in self.nodes.items():
                if node not in sorted_nodes:
                    sorted_nodes.append(node)

        return sorted_nodes

    def total_reference_flops(self) -> int:
        return sum(node.flops for node in self.nodes.values() if not node.annotations.is_dead)

    def total_memory_traffic_bytes(self) -> int:
        return sum(node.calculate_memory_footprint() for node in self.nodes.values() if not node.annotations.is_dead)

    def eliminate_dead_nodes(self, live_outputs: Set[str]) -> int:
        """Dead code elimination (DCE): eliminates nodes whose outputs are not in live_outputs or consumed."""
        consumed_tensors = set(live_outputs)
        for node in self.nodes.values():
            for inp in node.inputs:
                consumed_tensors.add(inp.name)

        eliminated_count = 0
        for node_id, node in list(self.nodes.items()):
            produces_useful = any(out.name in consumed_tensors for out in node.outputs)
            if not produces_useful and node.outputs:
                node.annotations.is_dead = True
                node.annotations.necessity = NecessityStatus.ELIMINABLE
                eliminated_count += 1
        return eliminated_count

    def apply_common_subexpression_elimination(self) -> int:
        """Common Subexpression Elimination (CSE): merges nodes with identical op & input fingerprints."""
        fingerprint_map: Dict[str, str] = {}
        merged_count = 0
        for node in self.topological_sort():
            if node.annotations.is_dead:
                continue
            input_names = sorted([t.name for t in node.inputs])
            fp_str = f"{node.op_type.value}:{input_names}:{json.dumps(node.attributes, sort_keys=True)}"
            fp_hash = hashlib.sha256(fp_str.encode("utf-8")).hexdigest()
            node.annotations.fingerprint = fp_hash

            if fp_hash in fingerprint_map:
                # Duplicate subexpression!
                node.annotations.is_reused = True
                node.annotations.reuse_source_hash = fp_hash
                node.annotations.necessity = NecessityStatus.REDUNDANT
                merged_count += 1
            else:
                fingerprint_map[fp_hash] = node.node_id
        return merged_count


class GraphBuilder:
    """Builds standard ComputationGraphIR from workload descriptors."""

    @staticmethod
    def build_gemm_graph(m: int, n: int, k: int, dtype: str = "float32") -> ComputationGraphIR:
        graph = ComputationGraphIR(graph_id=f"gemm_{m}x{n}x{k}_{dtype}")
        t_a = TensorDescriptor(name="A", shape=[m, k], dtype=dtype)
        t_b = TensorDescriptor(name="B", shape=[k, n], dtype=dtype)
        t_c = TensorDescriptor(name="C", shape=[m, n], dtype=dtype)

        graph.input_tensors["A"] = t_a
        graph.input_tensors["B"] = t_b
        graph.output_tensors["C"] = t_c

        flops = 2 * m * n * k
        node = IRNode(
            node_id="matmul_0",
            op_type=OpType.MATMUL,
            name="dense_matmul",
            inputs=[t_a, t_b],
            outputs=[t_c],
            flops=flops,
            attributes={"m": m, "n": n, "k": k}
        )
        node.calculate_memory_footprint()
        graph.add_node(node)
        return graph

    @staticmethod
    def build_fft_graph(size: int, dtype: str = "float32") -> ComputationGraphIR:
        graph = ComputationGraphIR(graph_id=f"fft_{size}_{dtype}")
        t_in = TensorDescriptor(name="signal_in", shape=[size], dtype=dtype)
        t_out = TensorDescriptor(name="freq_out", shape=[size], dtype="complex64")

        graph.input_tensors["signal_in"] = t_in
        graph.output_tensors["freq_out"] = t_out

        import math
        flops = int(5 * size * math.log2(max(size, 2)))
        node = IRNode(
            node_id="fft_0",
            op_type=OpType.FFT,
            name="1d_fft",
            inputs=[t_in],
            outputs=[t_out],
            flops=flops,
            attributes={"size": size}
        )
        node.calculate_memory_footprint()
        graph.add_node(node)
        return graph

    @staticmethod
    def build_reduction_graph(size: int, dtype: str = "float32") -> ComputationGraphIR:
        graph = ComputationGraphIR(graph_id=f"reduction_{size}_{dtype}")
        t_in = TensorDescriptor(name="vec_in", shape=[size], dtype=dtype)
        t_out = TensorDescriptor(name="scalar_out", shape=[1], dtype=dtype)

        graph.input_tensors["vec_in"] = t_in
        graph.output_tensors["scalar_out"] = t_out

        flops = size
        node = IRNode(
            node_id="reduce_0",
            op_type=OpType.REDUCTION,
            name="sum_reduction",
            inputs=[t_in],
            outputs=[t_out],
            flops=flops,
            attributes={"size": size}
        )
        node.calculate_memory_footprint()
        graph.add_node(node)
        return graph
