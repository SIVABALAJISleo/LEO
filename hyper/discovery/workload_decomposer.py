"""
hyper/discovery/workload_decomposer.py
======================================
Workload Decomposer & Dependency Graph Engine for HYPER.

Transforms arbitrary workloads into:
  INPUT → STATE → OPERATIONS → DEPENDENCIES → INTERMEDIATE DATA → OUTPUT

Analyzes computational necessity:
- what must be computed
- what can be reused
- what can be eliminated
- what can be reconstructed
- what can be transformed
- what can be computed incrementally
- what can be compressed
- what can be reordered
- what can be fused
- what cannot be changed
"""

from __future__ import annotations
import uuid
import hashlib
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np
from pydantic import BaseModel, Field

from hyper.universal.contracts.universal_contract import InformationNecessityClass, WorkNecessityClass


class OperationType(str, Enum):
    ARITHMETIC = "ARITHMETIC"
    MEMORY_LOAD = "MEMORY_LOAD"
    MEMORY_STORE = "MEMORY_STORE"
    SYNC = "SYNC"
    REDUCTION = "REDUCTION"
    PERMUTATION = "PERMUTATION"
    LOOKUP = "LOOKUP"
    BRANCH = "BRANCH"


class ComputationalNode(BaseModel):
    node_id: str
    name: str
    op_type: OperationType
    input_ids: List[str] = Field(default_factory=list)
    output_ids: List[str] = Field(default_factory=list)
    estimated_flops: float = 0.0
    estimated_bytes_in: int = 0
    estimated_bytes_out: int = 0
    can_be_eliminated: bool = False
    can_be_reused: bool = False
    can_be_reconstructed: bool = False
    can_be_computed_incrementally: bool = False
    can_be_fused_with: List[str] = Field(default_factory=list)
    is_critical_path: bool = False
    necessity_class: WorkNecessityClass = WorkNecessityClass.NECESSARY_WORK_ESTIMATE


class WorkloadDependencyGraph(BaseModel):
    graph_id: str = Field(default_factory=lambda: f"dag-{uuid.uuid4().hex[:8]}")
    workload_name: str
    nodes: Dict[str, ComputationalNode] = Field(default_factory=dict)
    state_variables: List[str] = Field(default_factory=list)
    input_variables: List[str] = Field(default_factory=list)
    output_variables: List[str] = Field(default_factory=list)
    intermediate_variables: List[str] = Field(default_factory=list)

    total_flops: float = 0.0
    total_bytes_moved: int = 0
    critical_path_length: int = 0
    potential_elimination_flops: float = 0.0
    potential_reuse_flops: float = 0.0

    def add_node(self, node: ComputationalNode) -> None:
        self.nodes[node.node_id] = node
        self.total_flops += node.estimated_flops
        self.total_bytes_moved += node.estimated_bytes_in + node.estimated_bytes_out
        if node.can_be_eliminated:
            self.potential_elimination_flops += node.estimated_flops
        if node.can_be_reused:
            self.potential_reuse_flops += node.estimated_flops


class WorkloadDecompositionResult(BaseModel):
    workload_name: str
    dag: WorkloadDependencyGraph
    essential_operations_count: int
    eliminable_operations_count: int
    reusable_operations_count: int
    fusible_groups_count: int
    estimated_information_entropy_bits: float
    work_reduction_opportunity_ratio: float


class WorkloadDecomposer:
    """
    Analyzes and decomposes computational workloads into an explicit dependency DAG
    and evaluates necessity classes for operation elimination and reuse.
    """

    def decompose_workload(
        self,
        workload_name: str,
        sample_input: Any,
        workload_fn: Optional[Callable[[Any], Any]] = None,
        operations_spec: Optional[List[Dict[str, Any]]] = None,
    ) -> WorkloadDecompositionResult:
        dag = WorkloadDependencyGraph(workload_name=workload_name)
        dag.input_variables = ["input_tensor_0"]
        dag.output_variables = ["output_tensor_0"]

        if operations_spec:
            # Build from explicit specification
            prev_id: Optional[str] = None
            for idx, op in enumerate(operations_spec):
                nid = op.get("node_id", f"node_{idx}")
                node = ComputationalNode(
                    node_id=nid,
                    name=op.get("name", f"op_{idx}"),
                    op_type=OperationType(op.get("op_type", OperationType.ARITHMETIC.value)),
                    input_ids=[prev_id] if prev_id else ["input_tensor_0"],
                    output_ids=[f"inter_{idx}"],
                    estimated_flops=float(op.get("flops", 100.0)),
                    estimated_bytes_in=int(op.get("bytes_in", 64)),
                    estimated_bytes_out=int(op.get("bytes_out", 64)),
                    can_be_eliminated=bool(op.get("can_eliminate", False)),
                    can_be_reused=bool(op.get("can_reuse", False)),
                    can_be_reconstructed=bool(op.get("can_reconstruct", False)),
                    can_be_computed_incrementally=bool(op.get("can_incremental", False)),
                    necessity_class=WorkNecessityClass.NECESSARY_WORK_ESTIMATE if not op.get("can_eliminate", False) else WorkNecessityClass.REMOVED_WORK,
                )
                dag.add_node(node)
                prev_id = nid
        else:
            # Synthetic structured analysis based on workload_name heuristics
            name_lower = workload_name.lower()
            if "matmul" in name_lower or "gemm" in name_lower:
                n = 64
                if isinstance(sample_input, np.ndarray) and sample_input.ndim >= 2:
                    n = sample_input.shape[0]
                elif isinstance(sample_input, (tuple, list)) and len(sample_input) > 0 and isinstance(sample_input[0], np.ndarray):
                    n = sample_input[0].shape[0]

                flops = 2.0 * (n ** 3)
                bytes_io = 3 * (n ** 2) * 4

                n1 = ComputationalNode(
                    node_id="load_operands",
                    name="load_matrices_A_B",
                    op_type=OperationType.MEMORY_LOAD,
                    input_ids=["input_tensor_0"],
                    output_ids=["tile_A", "tile_B"],
                    estimated_flops=0,
                    estimated_bytes_in=bytes_io,
                    can_be_reused=True,
                )
                n2 = ComputationalNode(
                    node_id="bilinear_contract",
                    name="fused_multiply_accumulate",
                    op_type=OperationType.ARITHMETIC,
                    input_ids=["tile_A", "tile_B"],
                    output_ids=["inter_accum"],
                    estimated_flops=flops,
                    estimated_bytes_in=bytes_io,
                    estimated_bytes_out=int(n * n * 4),
                    can_be_fused_with=["write_result"],
                    necessity_class=WorkNecessityClass.NECESSARY_WORK_ESTIMATE,
                )
                n3 = ComputationalNode(
                    node_id="write_result",
                    name="store_matrix_C",
                    op_type=OperationType.MEMORY_STORE,
                    input_ids=["inter_accum"],
                    output_ids=["output_tensor_0"],
                    estimated_bytes_out=int(n * n * 4),
                    necessity_class=WorkNecessityClass.NECESSARY_WORK_ESTIMATE,
                )
                dag.add_node(n1)
                dag.add_node(n2)
                dag.add_node(n3)

            elif "attention" in name_lower or "transformer" in name_lower:
                dag.add_node(ComputationalNode(node_id="qkv_proj", name="linear_qkv_projection", op_type=OperationType.ARITHMETIC, estimated_flops=10000, can_be_reused=True))
                dag.add_node(ComputationalNode(node_id="qk_dot", name="scaled_dot_product", op_type=OperationType.ARITHMETIC, estimated_flops=20000, can_be_reused=True))
                dag.add_node(ComputationalNode(node_id="softmax", name="attention_softmax", op_type=OperationType.REDUCTION, estimated_flops=5000))
                dag.add_node(ComputationalNode(node_id="attn_v", name="attention_weighted_values", op_type=OperationType.ARITHMETIC, estimated_flops=20000, can_be_fused_with=["out_proj"]))
                dag.add_node(ComputationalNode(node_id="out_proj", name="output_linear_projection", op_type=OperationType.ARITHMETIC, estimated_flops=10000))

            elif "raster" in name_lower or "graphics" in name_lower or "render" in name_lower:
                dag.add_node(ComputationalNode(node_id="geom_xform", name="vertex_transformation", op_type=OperationType.ARITHMETIC, estimated_flops=50000, can_be_reused=True))
                dag.add_node(ComputationalNode(node_id="culling", name="frustum_and_occlusion_cull", op_type=OperationType.BRANCH, estimated_flops=5000, can_be_eliminated=True))
                dag.add_node(ComputationalNode(node_id="rasterize", name="triangle_raster_traversal", op_type=OperationType.ARITHMETIC, estimated_flops=200000, can_be_computed_incrementally=True))
                dag.add_node(ComputationalNode(node_id="depth_test", name="early_z_depth_stencil", op_type=OperationType.BRANCH, estimated_flops=20000, can_be_eliminated=True))
                dag.add_node(ComputationalNode(node_id="shading", name="pixel_fragment_shading", op_type=OperationType.ARITHMETIC, estimated_flops=500000, can_be_reused=True, can_be_reconstructed=True))

            else:
                # Default generic pipeline
                dag.add_node(ComputationalNode(node_id="step_prepare", name="input_transformation", op_type=OperationType.MEMORY_LOAD, estimated_flops=100, can_be_reused=True))
                dag.add_node(ComputationalNode(node_id="step_compute", name="core_arithmetic_kernel", op_type=OperationType.ARITHMETIC, estimated_flops=1000, can_be_computed_incrementally=True))
                dag.add_node(ComputationalNode(node_id="step_finalize", name="output_reduction_store", op_type=OperationType.MEMORY_STORE, estimated_flops=200))

        # Compute summary metrics
        dag.critical_path_length = len(dag.nodes)
        essential = sum(1 for n in dag.nodes.values() if not n.can_be_eliminated)
        eliminable = sum(1 for n in dag.nodes.values() if n.can_be_eliminated)
        reusable = sum(1 for n in dag.nodes.values() if n.can_be_reused)
        fusible = sum(1 for n in dag.nodes.values() if len(n.can_be_fused_with) > 0)

        reduction_opp = (dag.potential_elimination_flops + dag.potential_reuse_flops) / max(dag.total_flops, 1.0)
        entropy_est = float(np.log2(max(len(dag.nodes) * 8, 2.0)))

        return WorkloadDecompositionResult(
            workload_name=workload_name,
            dag=dag,
            essential_operations_count=essential,
            eliminable_operations_count=eliminable,
            reusable_operations_count=reusable,
            fusible_groups_count=fusible,
            estimated_information_entropy_bits=entropy_est,
            work_reduction_opportunity_ratio=min(reduction_opp, 0.99),
        )
