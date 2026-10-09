"""
hyper/workload_router/universal_router.py
=========================================
Universal Workload Router for HYPER-GODMODE.
Implements Section 22 of the HYPER-GODMODE specification:
- Classifies incoming workloads across 14 capability categories.
- Routes workloads to the most mathematically promising pathway family.
"""

from __future__ import annotations
import enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkloadCategory(str, enum.Enum):
    GRAPHICS = "GRAPHICS"
    RASTERIZATION = "RASTERIZATION"
    RAY_TRACING = "RAY_TRACING"
    AI = "AI"
    ML = "ML"
    SCIENTIFIC = "SCIENTIFIC"
    LINEAR_ALGEBRA = "LINEAR_ALGEBRA"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    COMPRESSION = "COMPRESSION"
    CRYPTOGRAPHY = "CRYPTOGRAPHY"
    SIMULATION = "SIMULATION"
    PHYSICS = "PHYSICS"
    GENERAL_COMPUTE = "GENERAL_COMPUTE"


class PathwayFamily(str, enum.Enum):
    SPECTRAL_FFT_DECOMPOSITION = "SPECTRAL_FFT_DECOMPOSITION"
    SPARSE_BLOCK_TILING = "SPARSE_BLOCK_TILING"
    RANK_ONE_DELTA_UPDATE = "RANK_ONE_DELTA_UPDATE"
    TEMPORAL_HISTORY_REPROJECTION = "TEMPORAL_HISTORY_REPROJECTION"
    SEPARABLE_FILTER_FACTORIZATION = "SEPARABLE_FILTER_FACTORIZATION"
    HIERARCHICAL_EARLY_PRUNING = "HIERARCHICAL_EARLY_PRUNING"
    LOSSLESS_BYTE_DELTA = "LOSSLESS_BYTE_DELTA"
    SYMMETRY_FORCE_HALVING = "SYMMETRY_FORCE_HALVING"
    EXACT_CONSTANT_TIME_ARITHMETIC = "EXACT_CONSTANT_TIME_ARITHMETIC"
    DIRECT_SIMD_FUSED_LOOP = "DIRECT_SIMD_FUSED_LOOP"


class RoutingDecision(BaseModel):
    workload_id: str
    workload_name: str
    detected_category: WorkloadCategory
    recommended_pathway_family: PathwayFamily
    recommended_hardware_target: str  # "CPU", "iGPU", or "CPU+iGPU_COOPERATIVE"
    confidence_score: float = 1.0
    candidate_transformations: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)


class UniversalWorkloadRouter:
    """
    Analyzes computational properties of an incoming workload and routes to the highest-probability pathway family.
    """

    CATEGORY_KEYWORDS = {
        WorkloadCategory.RAY_TRACING: ["ray", "bvh", "intersection", "shadow_ray", "pathtracing", "reflection"],
        WorkloadCategory.RASTERIZATION: ["raster", "depth", "early_z", "fragment", "triangle", "draw_quad"],
        WorkloadCategory.GRAPHICS: ["graphics", "color_buffer", "render", "post_process", "msaa"],
        WorkloadCategory.LINEAR_ALGEBRA: ["gemm", "matrix_mult", "matmul", "dot", "blas", "svd", "cholesky"],
        WorkloadCategory.AI: ["transformer", "attention", "sdpa", "embedding", "llm", "softmax"],
        WorkloadCategory.ML: ["convolution", "conv2d", "pooling", "layernorm", "linear", "inference"],
        WorkloadCategory.SCIENTIFIC: ["pde", "heat", "laplacian", "stencil", "finite_diff", "multigrid"],
        WorkloadCategory.PHYSICS: ["n_body", "nbody", "gravitation", "particle", "collision", "rigid_body"],
        WorkloadCategory.SIMULATION: ["fluid", "navier_stokes", "lattice", "monte_carlo"],
        WorkloadCategory.IMAGE: ["image", "blur", "gaussian", "sobel", "sharpen", "denoise"],
        WorkloadCategory.VIDEO: ["video", "optical_flow", "frame_diff", "motion_estimation", "h264"],
        WorkloadCategory.COMPRESSION: ["compression", "gzip", "lz4", "zstd", "entropy", "huffman", "delta_enc"],
        WorkloadCategory.CRYPTOGRAPHY: ["sha256", "aes", "rsa", "hash", "ecc", "modular", "crypto"],
        WorkloadCategory.GENERAL_COMPUTE: ["sort", "scan", "radix", "prefix_sum", "reduction", "graph"],
    }

    @classmethod
    def classify_and_route(
        cls,
        workload_name: str,
        workload_id: str = "WLD_AUTO",
        input_hints: Optional[Dict[str, Any]] = None,
    ) -> RoutingDecision:
        name_lower = workload_name.lower()
        matched_cat = WorkloadCategory.GENERAL_COMPUTE
        max_matches = 0

        for cat, keywords in cls.CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in name_lower)
            if matches > max_matches:
                max_matches = matches
                matched_cat = cat

        # Determine pathway family and hardware affinity
        if matched_cat in [WorkloadCategory.LINEAR_ALGEBRA, WorkloadCategory.AI]:
            family = PathwayFamily.SPARSE_BLOCK_TILING
            hw = "CPU+iGPU_COOPERATIVE"
            txs = ["AVX2 register tiling", "Cache-blocked GEMM", "Structured block pruning"]
        elif matched_cat == WorkloadCategory.SCIENTIFIC:
            family = PathwayFamily.SEPARABLE_FILTER_FACTORIZATION
            hw = "CPU"
            txs = ["Separable stencil factorization", "Wavefront active cell caching"]
        elif matched_cat == WorkloadCategory.PHYSICS:
            family = PathwayFamily.SYMMETRY_FORCE_HALVING
            hw = "CPU+iGPU_COOPERATIVE"
            txs = ["Newton's 3rd Law force halving", "SIMD vector distance softening"]
        elif matched_cat in [WorkloadCategory.RAY_TRACING, WorkloadCategory.RASTERIZATION]:
            family = PathwayFamily.HIERARCHICAL_EARLY_PRUNING
            hw = "CPU"
            txs = ["Early slab rejection", "Hierarchical dirty tile bounding box"]
        elif matched_cat in [WorkloadCategory.VIDEO, WorkloadCategory.GRAPHICS]:
            family = PathwayFamily.TEMPORAL_HISTORY_REPROJECTION
            hw = "iGPU"
            txs = ["Temporal reprojection", "Dirty-region bounding box bypass"]
        elif matched_cat == WorkloadCategory.COMPRESSION:
            family = PathwayFamily.LOSSLESS_BYTE_DELTA
            hw = "CPU"
            txs = ["Lossless byte delta encoding", "Dictionary prefix sharing"]
        elif matched_cat == WorkloadCategory.CRYPTOGRAPHY:
            family = PathwayFamily.EXACT_CONSTANT_TIME_ARITHMETIC
            hw = "CPU"
            txs = ["Strict exact constant-time bitwise operations", "Zero approximation"]
        else:
            family = PathwayFamily.DIRECT_SIMD_FUSED_LOOP
            hw = "CPU"
            txs = ["Loop fusion", "Vectorized accumulator"]

        return RoutingDecision(
            workload_id=workload_id,
            workload_name=workload_name,
            detected_category=matched_cat,
            recommended_pathway_family=family,
            recommended_hardware_target=hw,
            confidence_score=0.95 if max_matches > 0 else 0.70,
            candidate_transformations=txs,
        )
