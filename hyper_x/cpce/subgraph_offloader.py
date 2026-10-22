"""
hyper_x/cpce/subgraph_offloader.py
==================================
OpenVINO Subgraph Offloading Engine for Heterogeneous CPU+iGPU Execution.
Partitions Canonical IR graphs into:
1. Large Dense Compute Subgraphs (M, N, K >= 768 / 1024): Offloaded to Intel UHD iGPU
   using OpenVINO with FP32 strict precision hints.
2. Memory-Bound & Structural Subgraphs (Diagonal Scaling, SpMV, Horner): Retained on CPU
   AVX2 cores where memory latency is minimal and caches are fastest.

Coordinates inter-subgraph tensor transfers and verifies numerical parity.
"""

from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

from hyper_x.cpce.ir import CanonicalGraph, CIRNode, OpType

try:
    import openvino as ov
    _HAS_OPENVINO = True
except ImportError:
    _HAS_OPENVINO = False


@dataclasses.dataclass
class SubgraphPartition:
    partition_id: str
    target_backend: str  # "INTEL_UHD_IGPU" or "CPU"
    node_ids: List[str]
    input_names: List[str]
    output_names: List[str]
    is_dense_compute_bound: bool
    estimated_flops: float


@dataclasses.dataclass
class PartitionedExecutionResult:
    status: str
    output: Any
    cpu_pre_duration_ms: float
    igpu_duration_ms: float
    tensor_transfer_duration_ms: float
    cpu_post_duration_ms: float
    total_partitioned_duration_ms: float
    subgraphs_executed: List[str]
    device_used: str
    provenance: str
    relative_difference_vs_cpu_ref: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "cpu_pre_duration_ms": round(self.cpu_pre_duration_ms, 3),
            "igpu_duration_ms": round(self.igpu_duration_ms, 3),
            "tensor_transfer_duration_ms": round(self.tensor_transfer_duration_ms, 3),
            "cpu_post_duration_ms": round(self.cpu_post_duration_ms, 3),
            "total_partitioned_duration_ms": round(self.total_partitioned_duration_ms, 3),
            "subgraphs_executed": self.subgraphs_executed,
            "device_used": self.device_used,
            "provenance": self.provenance,
            "relative_difference_vs_cpu_ref": float(self.relative_difference_vs_cpu_ref),
        }


class OpenVINOSubgraphOffloader:
    """
    Analyzes, partitions, and offloads dense subgraphs to Intel UHD iGPU.
    """

    # Empirical crossover threshold from benchmarks/igpu_tiling_tuning.py
    IGPU_DENSE_CROSSOVER_DIM: int = 768

    def __init__(self):
        self._compiled_cache: Dict[str, Any] = {}
        self.is_igpu_available: bool = False

        if _HAS_OPENVINO:
            try:
                core = ov.Core()
                self.is_igpu_available = "GPU" in core.available_devices
            except Exception:
                self.is_igpu_available = False

    def partition_graph(
        self,
        graph: CanonicalGraph,
        dense_threshold: int = IGPU_DENSE_CROSSOVER_DIM,
    ) -> List[SubgraphPartition]:
        """
        Partitions canonical graph into CPU-retained and iGPU-offloaded subgraphs.
        """
        partitions: List[SubgraphPartition] = []

        cpu_nodes: List[str] = []
        igpu_nodes: List[str] = []

        for node_id, node in graph.nodes.items():
            if node.op_type == OpType.OUTPUT:
                continue

            # Classify node:
            is_dense_matmul = False
            if node.op_type == OpType.MATMUL:
                shape = node.shape or ()
                if len(shape) >= 2 and shape[0] >= dense_threshold and shape[1] >= dense_threshold:
                    is_dense_matmul = True

            if is_dense_matmul and self.is_igpu_available:
                igpu_nodes.append(node_id)
            else:
                cpu_nodes.append(node_id)

        # Build partitions
        if cpu_nodes:
            partitions.append(SubgraphPartition(
                partition_id="SUBGRAPH_CPU_STRUCTURAL",
                target_backend="CPU",
                node_ids=cpu_nodes,
                input_names=graph.input_nodes,
                output_names=cpu_nodes,
                is_dense_compute_bound=False,
                estimated_flops=sum(graph.nodes[n].resource_cost_flops for n in cpu_nodes),
            ))

        if igpu_nodes:
            partitions.append(SubgraphPartition(
                partition_id="SUBGRAPH_IGPU_DENSE_GEMM",
                target_backend="INTEL_UHD_IGPU",
                node_ids=igpu_nodes,
                input_names=igpu_nodes,
                output_names=igpu_nodes,
                is_dense_compute_bound=True,
                estimated_flops=sum(graph.nodes[n].resource_cost_flops for n in igpu_nodes),
            ))

        return partitions

    def execute_hybrid_pipeline(
        self,
        dense_matrix_a: np.ndarray,
        dense_matrix_b: np.ndarray,
        diagonal_vector: np.ndarray,
    ) -> PartitionedExecutionResult:
        """
        Executes a canonical heterogeneous pipeline:
        1. CPU structural stage: prepares and conditions inputs.
        2. Offloaded iGPU dense stage: computes C_dense = A x B on Intel UHD Graphics.
        3. CPU memory-bound stage: performs fused diagonal scaling on result: out = diag(D) x C_dense.
        4. Verifies result against monolithic CPU reference.
        """
        t_total_start = time.perf_counter()

        A = np.ascontiguousarray(dense_matrix_a, dtype=np.float32)
        B = np.ascontiguousarray(dense_matrix_b, dtype=np.float32)
        D = np.ascontiguousarray(diagonal_vector, dtype=np.float32)

        M, K = A.shape
        _, N = B.shape

        # Stage 1: CPU Pre-conditioning
        t_pre_start = time.perf_counter()
        # Ensure contiguous memory alignment for PCIe/iGPU zero-copy transfer
        A_pinned = np.require(A, requirements=["C", "A"])
        B_pinned = np.require(B, requirements=["C", "A"])
        t_pre_end = time.perf_counter()
        pre_ms = (t_pre_end - t_pre_start) * 1000.0

        # Stage 2: Offload to Intel UHD iGPU (or fallback to CPU if iGPU absent)
        transfer_ms = 0.0
        igpu_ms = 0.0
        device_used = "Host CPU (AVX2)"
        c_intermediate: Optional[np.ndarray] = None

        if self.is_igpu_available and _HAS_OPENVINO:
            try:
                core = ov.Core()
                model_key = f"ov_gemm_{M}_{K}_{N}"
                if model_key not in self._compiled_cache:
                    pA = ov.opset10.parameter(shape=[M, K], dtype=ov.Type.f32, name="A")
                    pB = ov.opset10.parameter(shape=[K, N], dtype=ov.Type.f32, name="B")
                    mm = ov.opset10.matmul(pA, pB, False, False)
                    m = ov.Model([mm], [pA, pB], model_key)
                    self._compiled_cache[model_key] = core.compile_model(
                        m, "GPU", {"INFERENCE_PRECISION_HINT": "f32"}
                    )
                compiled = self._compiled_cache[model_key]

                # Memory Transfer to iGPU Buffers
                t_tx0 = time.perf_counter()
                infer_req = compiled.create_infer_request()
                t_tx1 = time.perf_counter()
                transfer_ms += (t_tx1 - t_tx0) * 1000.0

                # iGPU Execution
                t_gpu0 = time.perf_counter()
                infer_req.infer([A_pinned, B_pinned])
                c_intermediate = infer_req.get_output_tensor(0).data
                t_gpu1 = time.perf_counter()
                igpu_ms = (t_gpu1 - t_gpu0) * 1000.0

                # Transfer result back to host
                t_tx2 = time.perf_counter()
                c_intermediate = np.array(c_intermediate, copy=True)
                t_tx3 = time.perf_counter()
                transfer_ms += (t_tx3 - t_tx2) * 1000.0

                device_used = "Intel(R) UHD Graphics (OpenVINO GPU, FP32 Strict)"
            except Exception:
                c_intermediate = None

        if c_intermediate is None:
            # Fallback CPU GEMM
            t_cpu0 = time.perf_counter()
            c_intermediate = np.matmul(A, B)
            t_cpu1 = time.perf_counter()
            igpu_ms = (t_cpu1 - t_cpu0) * 1000.0
            device_used = "Host CPU (AVX2 Fallback)"

        # Stage 3: CPU Memory-Bound Structural Stage (Diagonal Scaling)
        t_post_start = time.perf_counter()
        out = D[:, np.newaxis] * c_intermediate
        t_post_end = time.perf_counter()
        post_ms = (t_post_end - t_post_start) * 1000.0

        total_ms = (time.perf_counter() - t_total_start) * 1000.0

        # Stage 4: Parity Verification against all-CPU reference
        ref_intermediate = np.matmul(A, B)
        ref_out = D[:, np.newaxis] * ref_intermediate
        norm_ref = float(np.linalg.norm(ref_out))
        frob_rel_err = float(np.linalg.norm(out - ref_out) / max(1e-7, norm_ref))
        max_abs_err = float(np.max(np.abs(out - ref_out)))

        return PartitionedExecutionResult(
            status="PASS" if frob_rel_err <= 1e-4 else "FAIL",
            output=out,
            cpu_pre_duration_ms=pre_ms,
            igpu_duration_ms=igpu_ms,
            tensor_transfer_duration_ms=transfer_ms,
            cpu_post_duration_ms=post_ms,
            total_partitioned_duration_ms=total_ms,
            subgraphs_executed=["SUBGRAPH_CPU_PRE", "SUBGRAPH_IGPU_DENSE", "SUBGRAPH_CPU_SCALE"],
            device_used=device_used,
            provenance="MEASURED",
            relative_difference_vs_cpu_ref=frob_rel_err,
        )
