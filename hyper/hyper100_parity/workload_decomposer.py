"""
hyper/hyper100_parity/workload_decomposer.py
============================================
GPU Capability & Workload Decomposer Engine (Section 5).

Transforms:
  GPU
   ↓
  Capability
   ↓
  Operation
   ↓
  Sub-operation
   ↓
  Dependency Graph (DAG)
   ↓
  Contract

For every capability, answers the 10 Core Questions:
1. What must happen?
2. What does not actually need to happen?
3. What can be reused?
4. What can be eliminated?
5. What can be transformed?
6. What can be reconstructed?
7. What can be predicted?
8. What can be computed incrementally?
9. What mathematical shortcuts exist?
10. What information is truly necessary?
"""

from __future__ import annotations
import uuid
from typing import Any, Dict, List, Optional, Set
import numpy as np
from pydantic import BaseModel, Field

from .taxonomy import CapabilityFamily, EquivalenceClass, UniversalCapabilityRegistry, GLOBAL_CAPABILITY_REGISTRY
from .contract_engine import PerformanceContract, PrecisionMode


class TenQuestionsAnalysis(BaseModel):
    must_happen: List[str]
    does_not_need_to_happen: List[str]
    can_be_reused: List[str]
    can_be_eliminated: List[str]
    can_be_transformed: List[str]
    can_be_reconstructed: List[str]
    can_be_predicted: List[str]
    can_be_computed_incrementally: List[str]
    mathematical_shortcuts: List[str]
    truly_necessary_information: List[str]


class DAGNode(BaseModel):
    node_id: str
    op_name: str
    sub_operation: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    estimated_flops: float = 0.0
    memory_traffic_bytes: int = 0
    is_eliminable: bool = False
    elimination_reason: Optional[str] = None


class WorkloadDAG(BaseModel):
    workload_id: str
    capability_family: CapabilityFamily
    nodes: Dict[str, DAGNode] = Field(default_factory=dict)
    edges: List[Dict[str, str]] = Field(default_factory=list)  # source -> target
    root_inputs: List[str] = Field(default_factory=list)
    terminal_outputs: List[str] = Field(default_factory=list)

    def total_flops(self) -> float:
        return sum(n.estimated_flops for n in self.nodes.values() if not n.is_eliminable)

    def original_flops(self) -> float:
        return sum(n.estimated_flops for n in self.nodes.values())

    def prune_dead_nodes(self) -> int:
        """Prunes nodes whose outputs are never read by terminal outputs or active nodes."""
        needed_outputs: Set[str] = set(self.terminal_outputs)
        # Traverse backwards
        reversed_order = list(reversed(list(self.nodes.values())))
        pruned_count = 0
        for node in reversed_order:
            produces_needed = any(out in needed_outputs for out in node.outputs)
            if not produces_needed and node.node_id not in self.terminal_outputs:
                node.is_eliminable = True
                node.elimination_reason = "Dead branch: output unreferenced by terminal contract."
                pruned_count += 1
            else:
                for inp in node.inputs:
                    needed_outputs.add(inp)
        return pruned_count


class DecompositionResult(BaseModel):
    workload_name: str
    capability_family: CapabilityFamily
    contract: PerformanceContract
    dag: WorkloadDAG
    analysis: TenQuestionsAnalysis


class GPUCapabilityDecomposer:
    """
    Decomposes arbitrary external GPU capabilities into fine-grained operation DAGs
    and formal 10-question sufficiency profiles.
    """

    def __init__(self, registry: Optional[UniversalCapabilityRegistry] = None) -> None:
        self.registry = registry or GLOBAL_CAPABILITY_REGISTRY

    def decompose(self, capability_name: str, sample_input: Optional[Any] = None) -> DecompositionResult:
        # Match capability in taxonomy
        norm_name = capability_name.lower().replace(" ", "_")
        matched = None
        for cap in self.registry.all_capabilities():
            if norm_name in cap.name.lower() or cap.name.lower() in norm_name:
                matched = cap
                break

        family = matched.family if matched else CapabilityFamily.GENERAL_COMPUTE
        contract = PerformanceContract(
            contract_id=f"CTR-{norm_name.upper()}",
            workload_name=norm_name,
            equivalence_class=matched.equivalence_class if matched else EquivalenceClass.EXACT,
            allows_approximation=matched.allows_approximation if matched else False,
            max_abs_error=matched.default_abs_tolerance if matched else 0.0,
            precision=PrecisionMode.FP32,
        )

        analysis = self._perform_ten_questions_analysis(norm_name, family)
        dag = self._build_workload_dag(norm_name, family, sample_input)
        dag.prune_dead_nodes()

        return DecompositionResult(
            workload_name=norm_name,
            capability_family=family,
            contract=contract,
            dag=dag,
            analysis=analysis,
        )

    def _perform_ten_questions_analysis(self, name: str, family: CapabilityFamily) -> TenQuestionsAnalysis:
        if family == CapabilityFamily.GRAPHICS:
            return TenQuestionsAnalysis(
                must_happen=["Final screen-space pixel projection", "Visible front-surface depth determination"],
                does_not_need_to_happen=["Occluded geometry rasterization", "Off-screen frustum triangles", "Static background redraw"],
                can_be_reused=["Static background shading from previous frame", "Unchanged material buffers", "Reprojected camera motion vectors"],
                can_be_eliminated=["Back-facing triangles", "Sub-pixel triangles below LOD threshold", "Zero-opacity transparent fragments"],
                can_be_transformed=["3D rasterization -> 2D dirty-bounding-box blit", "Full shading -> Spherical harmonic ambient cache"],
                can_be_reconstructed=["Pixel details from low-res pass via bilateral guided filter", "Motion-compensated temporal history"],
                can_be_predicted=["Object camera trajectory extrapolation", "Light probe changes"],
                can_be_computed_incrementally=["Dynamic actor dirty regions Delta(Frame)", "Moving light shadow map updates"],
                mathematical_shortcuts=["Barycentric edge functions inside AABB box", "Temporal motion vector reprojection p' = M * p"],
                truly_necessary_information=["RGB color of visible front-most surfaces", "Perceptually salient luminance edges"],
            )
        elif family == CapabilityFamily.AI_ML:
            return TenQuestionsAnalysis(
                must_happen=["Linear projection of active tokens", "Activation non-linearity"],
                does_not_need_to_happen=["Dense multiply across near-zero sparse activations", "Recomputation of previous token KV states"],
                can_be_reused=["KV-cache tensors from previous decoding steps", "Constant weight matrices"],
                can_be_eliminated=["Near-zero weight multiplications (< epsilon)", "Redundant activation re-computations"],
                can_be_transformed=["FP32 GEMM -> INT8 / BitNet ternary contraction", "Full GEMM -> Low-rank U @ V factor product"],
                can_be_reconstructed=["Compressed sparse attention distributions via top-k sampling"],
                can_be_predicted=["Draft tokens via small speculative model", "Early termination of deep layer residuals"],
                can_be_computed_incrementally=["KV-cache autoregressive token append", "Cumulative attention softmax normalizer"],
                mathematical_shortcuts=["Strassen bilinear tensor reduction", "FlashAttention online softmax tiling"],
                truly_necessary_information=["Top-1 argmax or top-p logit probability distribution"],
            )
        elif family == CapabilityFamily.SCIENTIFIC:
            return TenQuestionsAnalysis(
                must_happen=["Conservation law updates", "State convergence to declared epsilon"],
                does_not_need_to_happen=["Recalculation of symmetric opposing forces F_ji = -F_ij", "Updates to quiescent zero-gradient regions"],
                can_be_reused=["Invariant differential operators", "Preconditioned matrix factorizations"],
                can_be_eliminated=["50% pairwise force calculations via Newton's 3rd law", "Distant particle pairwise direct forces via FMM"],
                can_be_transformed=["Dense PDE stencil -> FFT spectral domain convolution", "Direct summation -> Barnes-Hut multipole expansion"],
                can_be_reconstructed=["Far-field potential from octree center-of-mass multipoles"],
                can_be_predicted=["Linear state trajectory step via symplectic extrapolation"],
                can_be_computed_incrementally=["Delta state time-stepper u(t+dt) = u(t) + dt * L(u)"],
                mathematical_shortcuts=["Action-reaction symmetry: F_ij = -F_ji", "Circulant convolution theorem C*x = IFFT(FFT(c).*FFT(x))"],
                truly_necessary_information=["Particle trajectories or field state within convergence tolerance"],
            )
        else:
            return TenQuestionsAnalysis(
                must_happen=["Contractual input-output transformation"],
                does_not_need_to_happen=["Full recomputation of unchanged inputs", "Branching across deterministic uniform loops"],
                can_be_reused=["Memoized intermediate results", "Pre-allocated working memory buffers"],
                can_be_eliminated=["Dead calculation branches unreferenced by contract"],
                can_be_transformed=["Sequential loops -> SIMD vector difference boundaries", "Double-buffered streaming"],
                can_be_reconstructed=["Outputs with compact degrees of freedom"],
                can_be_predicted=["Zero-residual delta state"],
                can_be_computed_incrementally=["Delta computation F(S + dS) = F(S) + dF"],
                mathematical_shortcuts=["Discrete difference boundary detection Delta(x)", "Freivalds randomized algebraic verification"],
                truly_necessary_information=["Declared contractual output bytes"],
            )

    def _build_workload_dag(self, name: str, family: CapabilityFamily, sample_input: Optional[Any]) -> WorkloadDAG:
        nodes: Dict[str, DAGNode] = {}
        edges: List[Dict[str, str]] = []

        # Common DAG construction
        nodes["n0_input_ingest"] = DAGNode(
            node_id="n0_input_ingest",
            op_name="Input_Ingest",
            sub_operation="Memory_Ingest",
            inputs=["raw_input"],
            outputs=["tensor_a", "tensor_b"],
            estimated_flops=100.0,
            memory_traffic_bytes=4096,
        )
        nodes["n1_core_compute"] = DAGNode(
            node_id="n1_core_compute",
            op_name="Core_Transformation",
            sub_operation=f"{family.value}_Kernel",
            inputs=["tensor_a", "tensor_b"],
            outputs=["intermediate_result"],
            estimated_flops=10000.0,
            memory_traffic_bytes=8192,
        )
        nodes["n2_unreferenced_dead_branch"] = DAGNode(
            node_id="n2_unreferenced_dead_branch",
            op_name="Auxiliary_Telemetry_Compute",
            sub_operation="Unneeded_Debug_Stats",
            inputs=["intermediate_result"],
            outputs=["dead_stat_metric"],
            estimated_flops=2000.0,
            memory_traffic_bytes=1024,
            is_eliminable=True,
            elimination_reason="Dead code: metric unrequested by application contract",
        )
        nodes["n3_terminal_projection"] = DAGNode(
            node_id="n3_terminal_projection",
            op_name="Terminal_Projection",
            sub_operation="Contract_Output_Packaging",
            inputs=["intermediate_result"],
            outputs=["final_output"],
            estimated_flops=500.0,
            memory_traffic_bytes=4096,
        )

        edges.append({"from": "n0_input_ingest", "to": "n1_core_compute"})
        edges.append({"from": "n1_core_compute", "to": "n2_unreferenced_dead_branch"})
        edges.append({"from": "n1_core_compute", "to": "n3_terminal_projection"})

        return WorkloadDAG(
            workload_id=f"DAG-{name.upper()}",
            capability_family=family,
            nodes=nodes,
            edges=edges,
            root_inputs=["raw_input"],
            terminal_outputs=["final_output"],
        )
