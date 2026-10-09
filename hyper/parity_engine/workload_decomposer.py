"""
hyper/parity_engine/workload_decomposer.py
==========================================
GPU Capability Decomposer & Information Necessity Engine.
Implements Sections 5, 11, and 12 of the HYPER 100% Master Mission.

Decomposes:
GPU -> Capability -> Operation -> Sub-operation -> Dependency Graph -> Contract.

Evaluates the 10 Fundamental Information Necessity Questions:
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
import time
from typing import Any, Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field

from .capability_registry import GPUCapability
from .contract_engine import WorkloadContract


class SubOperation(BaseModel):
    sub_op_id: str = Field(default_factory=lambda: f"SUB_{uuid.uuid4().hex[:8]}")
    name: str
    description: str
    is_strictly_necessary: bool = True
    can_be_eliminated: bool = False
    can_be_reused: bool = False
    can_be_reconstructed: bool = False
    can_be_predicted: bool = False
    can_be_computed_incrementally: bool = False
    estimated_ops: float = 1.0
    dependencies: List[str] = Field(default_factory=list)


class NecessityAnalysis(BaseModel):
    must_happen: List[str] = Field(default_factory=list)
    does_not_need_to_happen: List[str] = Field(default_factory=list)
    reusable_elements: List[str] = Field(default_factory=list)
    eliminable_elements: List[str] = Field(default_factory=list)
    transformable_elements: List[str] = Field(default_factory=list)
    reconstructable_elements: List[str] = Field(default_factory=list)
    predictable_elements: List[str] = Field(default_factory=list)
    incremental_elements: List[str] = Field(default_factory=list)
    mathematical_shortcuts: List[str] = Field(default_factory=list)
    truly_necessary_information_bits: str = "Only outputs bounded by contract"
    theoretical_work_reduction: float = 0.0


class DecomposedWorkload(BaseModel):
    decomposition_id: str = Field(default_factory=lambda: f"DEC_{uuid.uuid4().hex[:8]}")
    workload_id: str
    capability_id: str
    operations: List[SubOperation] = Field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)
    necessity: NecessityAnalysis = Field(default_factory=NecessityAnalysis)
    total_original_ops: float = 0.0
    total_necessary_ops: float = 0.0
    created_at: float = Field(default_factory=time.time)


class WorkloadDecomposer:
    """
    Decomposes computational workloads into granular sub-operations, evaluates information sufficiency,
    and identifies mathematical redundancy.
    """

    @staticmethod
    def decompose(capability: GPUCapability, sample_input: Optional[Any] = None) -> DecomposedWorkload:
        cap_name = capability.name.lower()
        sub_ops: List[SubOperation] = []
        deps: Dict[str, List[str]] = {}
        necessity = NecessityAnalysis()

        # Domain-specific canonical decompositions
        if "matrix_multiplication" in cap_name or "gemm" in cap_name:
            op1 = SubOperation(name="Input Validation & Packing", description="Buffer bounds and memory alignment", is_strictly_necessary=False, can_be_eliminated=True, estimated_ops=100.0)
            op2 = SubOperation(name="Sparsity & Rank Inspection", description="Probe singular value spectrum or zero pattern", is_strictly_necessary=False, can_be_transformed=True, estimated_ops=500.0)
            op3 = SubOperation(name="Inner Product Summation", description="Pairwise MAC computations", is_strictly_necessary=True, estimated_ops=1e6)
            op4 = SubOperation(name="Output Normalization/Writeback", description="Accumulator store to destination buffer", is_strictly_necessary=True, dependencies=[op3.sub_op_id], estimated_ops=1e4)
            sub_ops.extend([op1, op2, op3, op4])
            deps[op4.sub_op_id] = [op3.sub_op_id]
            necessity.must_happen = ["Output linear combination specified by matrix dimensions"]
            necessity.does_not_need_to_happen = ["Zero-valued product evaluations in sparse blocks", "Full rank products if low-rank factorization exists"]
            necessity.reusable_elements = ["Stationary weights across batch/queries", "Repeated sub-block products"]
            necessity.eliminable_elements = ["Multiplications by zero", "Redundant memory copies across PCIe"]
            necessity.transformable_elements = ["A @ B -> (A @ U) @ (V.T @ B) (Low-rank SVD/CUR)", "Strassen-Winograd / blocked Winograd"]
            necessity.reconstructable_elements = ["Low-rank residual via error correction"]
            necessity.predictable_elements = ["Smooth drift in continuous neural activation streams"]
            necessity.incremental_elements = ["Delta-updates for rank-1 weight changes: A @ (B + d B) = A@B + A@dB"]
            necessity.mathematical_shortcuts = ["Freivalds O(N^2) randomized verification", "Fast Walsh-Hadamard transform"]
            necessity.theoretical_work_reduction = 0.65

        elif "rasterization" in cap_name or "graphics" in cap_name:
            op1 = SubOperation(name="Frustum & Occlusion Culling", description="Discard non-visible geometry", is_strictly_necessary=True, estimated_ops=5e4)
            op2 = SubOperation(name="Triangle Setup & Edge Functions", description="Compute barycentric coefficients", is_strictly_necessary=True, dependencies=[op1.sub_op_id], estimated_ops=2e5)
            op3 = SubOperation(name="Per-Pixel Fragment Shading", description="Evaluate BRDF, lighting, and texture", is_strictly_necessary=False, can_be_reused=True, can_be_reconstructed=True, dependencies=[op2.sub_op_id], estimated_ops=5e6)
            op4 = SubOperation(name="Depth Test & Blending", description="Z-buffer comparison and color write", is_strictly_necessary=True, dependencies=[op3.sub_op_id], estimated_ops=1e5)
            sub_ops.extend([op1, op2, op3, op4])
            deps[op2.sub_op_id] = [op1.sub_op_id]
            deps[op3.sub_op_id] = [op2.sub_op_id]
            deps[op4.sub_op_id] = [op3.sub_op_id]
            necessity.must_happen = ["Visibility boundary calculation and final perceptible pixels"]
            necessity.does_not_need_to_happen = ["Shading occluded pixels (overdraw)", "Re-shading static scene regions between frames"]
            necessity.reusable_elements = ["Previous frame shading via motion vector reprojection", "Irradiance cache"]
            necessity.eliminable_elements = ["Back-face primitives", "Sub-pixel triangles below Nyquist limit"]
            necessity.transformable_elements = ["Per-pixel brute force shading -> temporal accumulation + spatial denoising"]
            necessity.reconstructable_elements = ["High-frequency details via spatial-temporal reconstruction"]
            necessity.predictable_elements = ["Camera motion trajectory and object velocities"]
            necessity.incremental_elements = ["Dirty-tile rendering (only update tiles containing moving geometry)"]
            necessity.mathematical_shortcuts = ["Spherical harmonics for diffuse ambient lighting", "Hierarchical Z early rejection"]
            necessity.theoretical_work_reduction = 0.80

        elif "attention" in cap_name or "transformer" in cap_name:
            op1 = SubOperation(name="Q, K, V Projection", description="Linear projection from hidden state", is_strictly_necessary=True, estimated_ops=3e6)
            op2 = SubOperation(name="Q @ K.T Scaled Dot Product", description="Compute full sequence attention matrix", is_strictly_necessary=False, can_be_reused=True, estimated_ops=1e7)
            op3 = SubOperation(name="Softmax Normalization", description="Row-wise exponential and normalization", is_strictly_necessary=True, dependencies=[op2.sub_op_id], estimated_ops=1e6)
            op4 = SubOperation(name="Attn @ V Context Gather", description="Multiply attention weights by value vectors", is_strictly_necessary=True, dependencies=[op3.sub_op_id], estimated_ops=1e7)
            sub_ops.extend([op1, op2, op3, op4])
            deps[op3.sub_op_id] = [op2.sub_op_id]
            deps[op4.sub_op_id] = [op3.sub_op_id]
            necessity.must_happen = ["Tokens attending to context with high semantic weight"]
            necessity.does_not_need_to_happen = ["Computing quadratic attention for tokens with negligible softmax weight"]
            necessity.reusable_elements = ["KV cache for past prompt tokens", "Static system prompt attention prefixes"]
            necessity.eliminable_elements = ["Tokens below sparsity threshold epsilon < 1e-4"]
            necessity.transformable_elements = ["Dense attention -> Sliding window + dilated attention + low-rank flash attention"]
            necessity.reconstructable_elements = ["Pruned attention heads via low-rank cross-projection"]
            necessity.predictable_elements = ["Speculative draft token verification"]
            necessity.incremental_elements = ["Incremental single-token autoregressive decoding (O(N) instead of O(N^2))"]
            necessity.mathematical_shortcuts = ["Online softmax (FlashAttention tile fusion)", "Quantized INT4/FP8 KV-cache"]
            necessity.theoretical_work_reduction = 0.75

        elif "pde" in cap_name or "scientific" in cap_name:
            op1 = SubOperation(name="Grid Boundary Condition Setup", description="Apply Dirichlet/Neumann conditions", is_strictly_necessary=True, estimated_ops=1e4)
            op2 = SubOperation(name="Laplacian / Flux Stencil Evaluation", description="Compute spatial derivatives", is_strictly_necessary=True, dependencies=[op1.sub_op_id], estimated_ops=2e6)
            op3 = SubOperation(name="Time-step Integration (Euler/RK4)", description="Advance field in time", is_strictly_necessary=True, dependencies=[op2.sub_op_id], estimated_ops=5e5)
            sub_ops.extend([op1, op2, op3])
            deps[op2.sub_op_id] = [op1.sub_op_id]
            deps[op3.sub_op_id] = [op2.sub_op_id]
            necessity.must_happen = ["Conserving physical invariants (mass, energy, momentum)"]
            necessity.does_not_need_to_happen = ["Uniform dense grid updates in equilibrium/quiescent subdomains"]
            necessity.reusable_elements = ["Stationary state regions across time steps"]
            necessity.eliminable_elements = ["Quiescent grid cells with zero gradient"]
            necessity.transformable_elements = ["Spatial finite difference -> Spectral FFT domain or Multi-grid solver"]
            necessity.reconstructable_elements = ["Adaptive mesh refinement coarse-to-fine interpolation"]
            necessity.predictable_elements = ["Linear extrapolation for laminar flows"]
            necessity.incremental_elements = ["Active-set wavefront tracking"]
            necessity.mathematical_shortcuts = ["Separable dimension splitting (ADI method)", "FFT Poisson solver"]
            necessity.theoretical_work_reduction = 0.70

        else:
            # Generic compute decomposition
            op1 = SubOperation(name="Input Intake & Pre-check", description="Shape and type verification", is_strictly_necessary=False, can_be_eliminated=True, estimated_ops=100.0)
            op2 = SubOperation(name="Core Transformation Loop", description="Primary data-parallel execution", is_strictly_necessary=True, dependencies=[op1.sub_op_id], estimated_ops=1e6)
            op3 = SubOperation(name="Result Aggregation & Output", description="Collate final state", is_strictly_necessary=True, dependencies=[op2.sub_op_id], estimated_ops=1e4)
            sub_ops.extend([op1, op2, op3])
            deps[op2.sub_op_id] = [op1.sub_op_id]
            deps[op3.sub_op_id] = [op2.sub_op_id]
            necessity.must_happen = ["Output meeting contract specification"]
            necessity.does_not_need_to_happen = ["Redundant recomputation of unchanged values"]
            necessity.reusable_elements = ["Memoized results from identical input hashes"]
            necessity.eliminable_elements = ["Dead code branches and redundant memory transfers"]
            necessity.transformable_elements = ["Loop tiling and vectorization for AVX2/AVX-512"]
            necessity.reconstructable_elements = ["Interpolation where contract permits bounded error"]
            necessity.predictable_elements = ["Sequential access patterns"]
            necessity.incremental_elements = ["Delta processing on modified elements only"]
            necessity.mathematical_shortcuts = ["Strength reduction and algebraic identities"]
            necessity.theoretical_work_reduction = 0.50

        orig_ops = sum(op.estimated_ops for op in sub_ops)
        nec_ops = sum(op.estimated_ops for op in sub_ops if op.is_strictly_necessary)

        return DecomposedWorkload(
            workload_id=capability.workload_id,
            capability_id=capability.capability_id,
            operations=sub_ops,
            dependency_graph=deps,
            necessity=necessity,
            total_original_ops=orig_ops,
            total_necessary_ops=nec_ops,
        )
