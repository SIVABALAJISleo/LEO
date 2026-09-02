"""
hyper_v2/compiler/graph_builder.py
Constructs DAG Computation Graph IR from workload definitions or tensor descriptors.
"""

from typing import Dict, Any, List
from hyper_v2.compiler.intermediate_representation import (
    ComputationGraphIR, IRNode, TensorSpec, OpCategory, DeviceTarget
)
from hyper_v2.compiler.contract_compiler import ExecutionContract


class GraphBuilder:
    """Builds DAG computation graphs for computational workloads."""

    @staticmethod
    def build_gemm_graph(M: int, N: int, K: int, dtype: str = "float32", sparsity: float = 0.0) -> ComputationGraphIR:
        graph = ComputationGraphIR(graph_id=f"gemm_{M}x{K}x{N}")
        graph.add_tensor(TensorSpec(name="A", shape=(M, K), dtype=dtype, sparsity_ratio=sparsity))
        graph.add_tensor(TensorSpec(name="B", shape=(K, N), dtype=dtype, sparsity_ratio=sparsity))
        graph.add_tensor(TensorSpec(name="C", shape=(M, N), dtype=dtype))

        flop_count = 2 * M * N * K
        bytes_read = (M * K + K * N) * (4 if "32" in dtype else 2)
        bytes_written = (M * N) * (4 if "32" in dtype else 2)

        matmul_node = IRNode(
            id="matmul_0",
            op_type=OpCategory.MATMUL,
            inputs=["A", "B"],
            outputs=["C"],
            attributes={"M": M, "N": N, "K": K, "sparsity": sparsity},
            flop_cost=flop_count,
            bytes_read=bytes_read,
            bytes_written=bytes_written,
            device_placement=DeviceTarget.CPU_PCORE
        )
        graph.add_node(matmul_node)
        return graph

    @staticmethod
    def build_fft_graph(N: int, is_2d: bool = True, sparsity_k: int = 16) -> ComputationGraphIR:
        size = N * N if is_2d else N
        graph = ComputationGraphIR(graph_id=f"fft_{'2d_' if is_2d else ''}{N}")
        graph.add_tensor(TensorSpec(name="signal_in", shape=(N, N) if is_2d else (N,), dtype="complex64"))
        graph.add_tensor(TensorSpec(name="spectrum_out", shape=(N, N) if is_2d else (N,), dtype="complex64"))

        # 5 * N * log2(N) per dimension
        import math
        flops = int(5 * size * math.log2(max(2, size)))
        bytes_io = size * 8

        fft_node = IRNode(
            id="fft_0",
            op_type=OpCategory.FFT,
            inputs=["signal_in"],
            outputs=["spectrum_out"],
            attributes={"N": N, "is_2d": is_2d, "sparsity_k": sparsity_k},
            flop_cost=flops,
            bytes_read=bytes_io,
            bytes_written=bytes_io,
            device_placement=DeviceTarget.INTEL_IGPU
        )
        graph.add_node(fft_node)
        return graph

    @staticmethod
    def build_nbody_graph(num_bodies: int) -> ComputationGraphIR:
        graph = ComputationGraphIR(graph_id=f"nbody_{num_bodies}")
        graph.add_tensor(TensorSpec(name="positions", shape=(num_bodies, 3), dtype="float32"))
        graph.add_tensor(TensorSpec(name="velocities", shape=(num_bodies, 3), dtype="float32"))
        graph.add_tensor(TensorSpec(name="forces", shape=(num_bodies, 3), dtype="float32"))

        # Direct pairwise N^2 interactions
        flops = num_bodies * num_bodies * 20
        bytes_io = num_bodies * 12

        nbody_node = IRNode(
            id="nbody_pairwise_0",
            op_type=OpCategory.N_BODY_INTERACT,
            inputs=["positions", "velocities"],
            outputs=["forces"],
            attributes={"num_bodies": num_bodies},
            flop_cost=flops,
            bytes_read=bytes_io * 2,
            bytes_written=bytes_io,
            device_placement=DeviceTarget.HYBRID_CPU_IGPU
        )
        graph.add_node(nbody_node)
        return graph

    @staticmethod
    def build_generic_workload_graph(workload_id: str, params: Dict[str, Any]) -> ComputationGraphIR:
        if "gemm" in workload_id.lower():
            M = params.get("M", 2048)
            N = params.get("N", 2048)
            K = params.get("K", 2048)
            return GraphBuilder.build_gemm_graph(M, N, K, dtype=params.get("dtype", "float32"), sparsity=params.get("sparsity", 0.0))
        elif "fft" in workload_id.lower():
            N = params.get("N", 2048)
            return GraphBuilder.build_fft_graph(N, is_2d=params.get("is_2d", True), sparsity_k=params.get("k", 16))
        elif "nbody" in workload_id.lower():
            N = params.get("N", 4096)
            return GraphBuilder.build_nbody_graph(N)
        else:
            # Fallback generic graph
            graph = ComputationGraphIR(graph_id=workload_id)
            node = IRNode(
                id=f"{workload_id}_node",
                op_type=OpCategory.ELEMENTWISE,
                inputs=["in_tensor"],
                outputs=["out_tensor"],
                attributes=params,
                flop_cost=params.get("flops", 10_000_000),
                bytes_read=params.get("bytes_read", 4_000_000),
                bytes_written=params.get("bytes_written", 4_000_000)
            )
            graph.add_node(node)
            return graph
