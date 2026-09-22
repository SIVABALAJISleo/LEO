"""
hyper/discovery/capability_decomposer.py
=========================================
GPU Capability Decomposer for HYPER Universal Computational Pathway Discovery Engine.

Decomposes dedicated external GPU functionality into 7 capability families:
1. GRAPHICS
2. RAY_TRACING
3. AI_ML
4. SCIENTIFIC
5. MEDIA
6. MEMORY
7. GENERAL_COMPUTE

Rule: Never treat GPU as one monolithic workload. Every capability becomes an explicit contract.
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from hyper.universal.contracts.universal_contract import UniversalContract, ContractCorrectness, ExactnessTier


class CapabilityFamily(str, Enum):
    GRAPHICS = "GRAPHICS"
    RAY_TRACING = "RAY_TRACING"
    AI_ML = "AI_ML"
    SCIENTIFIC = "SCIENTIFIC"
    MEDIA = "MEDIA"
    MEMORY = "MEMORY"
    GENERAL_COMPUTE = "GENERAL_COMPUTE"


class CapabilityDetail(BaseModel):
    name: str
    family: CapabilityFamily
    sub_capabilities: List[str]
    reference_hardware_standard: str
    target_contract_type: str
    allows_approximation: bool = False
    default_tolerance: float = 0.0


class GPUCapabilityDecomposer:
    """
    Decomposes arbitrary computational requirements into GPU capability families
    and assigns formal capability contracts.
    """

    CAPABILITY_TAXONOMY: Dict[CapabilityFamily, List[CapabilityDetail]] = {
        CapabilityFamily.GRAPHICS: [
            CapabilityDetail(
                name="rasterization",
                family=CapabilityFamily.GRAPHICS,
                sub_capabilities=["vertex_processing", "primitive_assembly", "clipping", "triangle_rasterization", "fragment_shading", "depth_testing", "blending"],
                reference_hardware_standard="Hardware Rasterizer + ROPs",
                target_contract_type="PERCEPTUALLY_EQUIVALENT",
                allows_approximation=True,
                default_tolerance=0.01,
            ),
            CapabilityDetail(
                name="shading_and_texturing",
                family=CapabilityFamily.GRAPHICS,
                sub_capabilities=["compute_shaders", "texture_sampling", "anisotropic_filtering", "msaa", "hdr_tonemapping", "post_processing"],
                reference_hardware_standard="Texture Mapping Units (TMUs) + Unified Shaders",
                target_contract_type="PERCEPTUALLY_EQUIVALENT",
                allows_approximation=True,
                default_tolerance=0.02,
            ),
        ],
        CapabilityFamily.RAY_TRACING: [
            CapabilityDetail(
                name="bvh_acceleration",
                family=CapabilityFamily.RAY_TRACING,
                sub_capabilities=["bvh_construction", "bvh_traversal", "box_intersection", "triangle_intersection"],
                reference_hardware_standard="Dedicated RT Cores (BVH Traversal Engines)",
                target_contract_type="EXACT",
                allows_approximation=False,
                default_tolerance=0.0,
            ),
            CapabilityDetail(
                name="ray_generation_and_denoising",
                family=CapabilityFamily.RAY_TRACING,
                sub_capabilities=["ray_generation", "shadow_rays", "reflection_rays", "refraction", "temporal_denoising", "temporal_accumulation"],
                reference_hardware_standard="RT Cores + Tensor Denoising Units",
                target_contract_type="PERCEPTUALLY_EQUIVALENT",
                allows_approximation=True,
                default_tolerance=0.05,
            ),
        ],
        CapabilityFamily.AI_ML: [
            CapabilityDetail(
                name="gemm_and_convolution",
                family=CapabilityFamily.AI_ML,
                sub_capabilities=["dense_matrix_multiplication", "batched_gemm", "1d_2d_3d_convolution", "grouped_convolution", "depthwise_separable"],
                reference_hardware_standard="Tensor Cores (FP16/BF16/FP8/INT8 Matrix Units)",
                target_contract_type="NUMERICALLY_EQUIVALENT",
                allows_approximation=False,
                default_tolerance=1e-5,
            ),
            CapabilityDetail(
                name="attention_and_transformer",
                family=CapabilityFamily.AI_ML,
                sub_capabilities=["scaled_dot_product_attention", "flash_attention", "multi_head_attention", "kv_cache_paging", "rotary_positional_embeddings", "layernorm_rms"],
                reference_hardware_standard="High-Bandwidth Tensor Cores + FlashAttention Kernels",
                target_contract_type="NUMERICALLY_EQUIVALENT",
                allows_approximation=False,
                default_tolerance=1e-4,
            ),
            CapabilityDetail(
                name="quantization_and_sampling",
                family=CapabilityFamily.AI_ML,
                sub_capabilities=["1_bit_bitnet", "4_bit_gptq_awq", "8_bit_weight_only", "top_k_top_p_sampling", "speculative_drafting"],
                reference_hardware_standard="INT4/INT2 Matrix Execution Pipeline",
                target_contract_type="NUMERICALLY_EQUIVALENT",
                allows_approximation=True,
                default_tolerance=1e-3,
            ),
        ],
        CapabilityFamily.SCIENTIFIC: [
            CapabilityDetail(
                name="dense_and_sparse_linear_algebra",
                family=CapabilityFamily.SCIENTIFIC,
                sub_capabilities=["dense_cholesky_lu_qr", "sparse_matrix_vector", "krylov_subspace_solvers", "eigenvalue_decomposition"],
                reference_hardware_standard="FP64 High-Precision Compute Engines",
                target_contract_type="EXACT",
                allows_approximation=False,
                default_tolerance=1e-7,
            ),
            CapabilityDetail(
                name="pde_stencils_and_nbody",
                family=CapabilityFamily.SCIENTIFIC,
                sub_capabilities=["finite_difference_stencils", "finite_element_mesh", "n_body_gravitational", "monte_carlo_integration", "fast_fourier_transform"],
                reference_hardware_standard="Massively Parallel FP32/FP64 SIMD Grid",
                target_contract_type="NUMERICALLY_EQUIVALENT",
                allows_approximation=False,
                default_tolerance=1e-5,
            ),
        ],
        CapabilityFamily.MEDIA: [
            CapabilityDetail(
                name="video_codecs",
                family=CapabilityFamily.MEDIA,
                sub_capabilities=["h264_avc", "h265_hevc", "av1_decode_encode", "intra_inter_prediction", "dct_idct_transforms", "motion_estimation"],
                reference_hardware_standard="NVDEC / NVENC Hardware ASICs",
                target_contract_type="PERCEPTUALLY_EQUIVALENT",
                allows_approximation=True,
                default_tolerance=0.01,
            ),
            CapabilityDetail(
                name="image_processing",
                family=CapabilityFamily.MEDIA,
                sub_capabilities=["bilateral_filter", "gaussian_blur", "sobel_edge", "optical_flow", "frame_interpolation", "super_resolution"],
                reference_hardware_standard="CUDA Optical Flow Accelerator (OFA) + 2D Filter Units",
                target_contract_type="PERCEPTUALLY_EQUIVALENT",
                allows_approximation=True,
                default_tolerance=0.02,
            ),
        ],
        CapabilityFamily.MEMORY: [
            CapabilityDetail(
                name="high_bandwidth_transfers",
                family=CapabilityFamily.MEMORY,
                sub_capabilities=["memory_coalescing", "shared_memory_banking", "l2_cache_tiling", "asynchronous_copy", "unified_virtual_memory"],
                reference_hardware_standard="HBM3e / GDDR7 Memory Bus (1000+ GB/s)",
                target_contract_type="EXACT",
                allows_approximation=False,
                default_tolerance=0.0,
            ),
        ],
        CapabilityFamily.GENERAL_COMPUTE: [
            CapabilityDetail(
                name="parallel_primitives",
                family=CapabilityFamily.GENERAL_COMPUTE,
                sub_capabilities=["parallel_reduction", "prefix_scan_inclusive_exclusive", "radix_sort", "hash_table_probing", "graph_bfs_pagerank", "compression_deflate"],
                reference_hardware_standard="Warp-Level Shuffle / Ballot Execution Units",
                target_contract_type="EXACT",
                allows_approximation=False,
                default_tolerance=0.0,
            ),
        ],
    }

    def __init__(self) -> None:
        self.decomposed_cache: Dict[str, CapabilityDetail] = {}

    def decompose(self, capability_name: str, domain_hint: Optional[str] = None) -> CapabilityDetail:
        """
        Decomposes a capability string into a canonical CapabilityDetail with strict contract rules.
        """
        name_lower = capability_name.lower()
        hint_lower = (domain_hint or "").lower()

        # Check known mappings
        for family, details in self.CAPABILITY_TAXONOMY.items():
            for detail in details:
                if detail.name in name_lower or any(sub in name_lower or sub in hint_lower for sub in detail.sub_capabilities):
                    return detail

        # Heuristic fallback mapping
        if any(k in name_lower or k in hint_lower for k in ["render", "draw", "pixel", "raster", "frag", "vert", "shader"]):
            return self.CAPABILITY_TAXONOMY[CapabilityFamily.GRAPHICS][0]
        elif any(k in name_lower or k in hint_lower for k in ["ray", "bvh", "trace", "hit", "shadow_ray"]):
            return self.CAPABILITY_TAXONOMY[CapabilityFamily.RAY_TRACING][0]
        elif any(k in name_lower or k in hint_lower for k in ["gemm", "matmul", "attn", "attention", "transformer", "conv", "neural"]):
            return self.CAPABILITY_TAXONOMY[CapabilityFamily.AI_ML][0]
        elif any(k in name_lower or k in hint_lower for k in ["fft", "pde", "stencil", "nbody", "solve", "algebra", "cholesky"]):
            return self.CAPABILITY_TAXONOMY[CapabilityFamily.SCIENTIFIC][0]
        elif any(k in name_lower or k in hint_lower for k in ["video", "image", "blur", "filter", "encode", "decode", "flow"]):
            return self.CAPABILITY_TAXONOMY[CapabilityFamily.MEDIA][0]
        elif any(k in name_lower or k in hint_lower for k in ["bandwidth", "transfer", "coalesce", "tile", "dram", "cache"]):
            return self.CAPABILITY_TAXONOMY[CapabilityFamily.MEMORY][0]
        else:
            return self.CAPABILITY_TAXONOMY[CapabilityFamily.GENERAL_COMPUTE][0]

    def create_contract_for_capability(
        self,
        capability_name: str,
        workload_id: str,
        domain_hint: Optional[str] = None,
        custom_tolerance: Optional[float] = None,
    ) -> UniversalContract:
        """
        Creates a formal UniversalContract tailored to the decomposed capability.
        """
        detail = self.decompose(capability_name, domain_hint)
        tol = custom_tolerance if custom_tolerance is not None else detail.default_tolerance

        correctness_map = {
            "EXACT": ContractCorrectness.EXACT,
            "NUMERICALLY_EQUIVALENT": ContractCorrectness.NUMERICALLY_EQUIVALENT,
            "PERCEPTUALLY_EQUIVALENT": ContractCorrectness.PERCEPTUALLY_EQUIVALENT,
            "TOLERANCE_VALID": ContractCorrectness.TOLERANCE_VALID,
            "SEMANTICALLY_EQUIVALENT": ContractCorrectness.SEMANTICALLY_EQUIVALENT,
        }
        correctness = correctness_map.get(detail.target_contract_type, ContractCorrectness.EXACT)

        contract = UniversalContract(
            contract_id=f"cntr-{detail.family.value.lower()}-{workload_id}",
            workload_id=workload_id,
            exactness_tier=ExactnessTier.BIT_EXACT if detail.target_contract_type == "EXACT" else ExactnessTier.NUMERICALLY_EXACT,
            correctness=correctness,
            numeric_tolerance=tol,
            relative_tolerance=tol,
            allows_approximation=detail.allows_approximation,
            metadata={
                "capability_family": detail.family.value,
                "capability_name": detail.name,
                "reference_hardware_standard": detail.reference_hardware_standard,
            },
        )
        return contract

    def list_all_capabilities(self) -> List[Dict[str, Any]]:
        """Returns all capability families and sub-capabilities."""
        out = []
        for family, details in self.CAPABILITY_TAXONOMY.items():
            for detail in details:
                out.append({
                    "family": family.value,
                    "name": detail.name,
                    "sub_capabilities": detail.sub_capabilities,
                    "reference_hardware": detail.reference_hardware_standard,
                    "contract_type": detail.target_contract_type,
                    "allows_approximation": detail.allows_approximation,
                })
        return out
