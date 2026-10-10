"""
hyper/hyper100_parity/taxonomy.py
==================================
Universal GPU Capability Taxonomy & Parity Hierarchy for HYPER (Sections 1-4).

Establishes:
1. Parity Taxonomy (8 formal levels):
   - Level 1: PHYSICAL_PARITY (OUT_OF_SCOPE)
   - Level 2: INTERFACE_PARITY
   - Level 3: FUNCTIONAL_PARITY
   - Level 4: EXACT_COMPUTATIONAL_PARITY
   - Level 5: NUMERICAL_PARITY
   - Level 6: GRAPHICS_PARITY
   - Level 7: APPLICATION_PARITY
   - Level 8: PERFORMANCE_CONTRACT_PARITY

2. Universal GPU Capability Taxonomy across 11 families:
   - GRAPHICS
   - RAY_TRACING
   - AI_ML
   - SCIENTIFIC
   - IMAGE
   - VIDEO
   - COMPRESSION
   - CRYPTOGRAPHY
   - GENERAL_COMPUTE
   - SIMULATION
   - MEMORY_BEHAVIOR

Every capability receives unique tracking IDs:
   - Capability ID
   - Workload ID
   - Contract ID
   - Verification ID
   - Benchmark ID
   - Evidence ID
"""

from __future__ import annotations
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ParityLevel(str, Enum):
    LEVEL_1_PHYSICAL = "LEVEL_1_PHYSICAL_PARITY (OUT_OF_SCOPE)"
    LEVEL_2_INTERFACE = "LEVEL_2_INTERFACE_PARITY"
    LEVEL_3_FUNCTIONAL = "LEVEL_3_FUNCTIONAL_PARITY"
    LEVEL_4_EXACT_COMPUTATIONAL = "LEVEL_4_EXACT_COMPUTATIONAL_PARITY"
    LEVEL_5_NUMERICAL = "LEVEL_5_NUMERICAL_PARITY"
    LEVEL_6_GRAPHICS = "LEVEL_6_GRAPHICS_PARITY"
    LEVEL_7_APPLICATION = "LEVEL_7_APPLICATION_PARITY"
    LEVEL_8_PERFORMANCE_CONTRACT = "LEVEL_8_PERFORMANCE_CONTRACT_PARITY"


class CapabilityFamily(str, Enum):
    GRAPHICS = "GRAPHICS"
    RAY_TRACING = "RAY_TRACING"
    AI_ML = "AI_ML"
    SCIENTIFIC = "SCIENTIFIC"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    COMPRESSION = "COMPRESSION"
    CRYPTOGRAPHY = "CRYPTOGRAPHY"
    GENERAL_COMPUTE = "GENERAL_COMPUTE"
    SIMULATION = "SIMULATION"
    MEMORY_BEHAVIOR = "MEMORY_BEHAVIOR"


class EquivalenceClass(str, Enum):
    EXACT = "EXACT"
    NUMERICALLY_EQUIVALENT = "NUMERICALLY_EQUIVALENT"
    PERCEPTUALLY_EQUIVALENT = "PERCEPTUALLY_EQUIVALENT"
    CONTRACT_EQUIVALENT = "CONTRACT_EQUIVALENT"


class EvidenceLevel(str, Enum):
    HYPOTHESIS = "HYPOTHESIS"
    UNVERIFIED = "UNVERIFIED"
    SIMULATED = "SIMULATED"
    ESTIMATED = "ESTIMATED"
    DERIVED = "DERIVED"
    MEASURED = "MEASURED"
    REPRODUCED = "REPRODUCED"
    VERIFIED = "VERIFIED"
    INDEPENDENTLY_VERIFIED = "INDEPENDENTLY_VERIFIED"


class CapabilityEntry(BaseModel):
    capability_id: str
    workload_id: str
    contract_id: str
    verification_id: str
    benchmark_id: str
    evidence_id: str
    name: str
    family: CapabilityFamily
    sub_capabilities: List[str]
    reference_hardware_subsystem: str
    equivalence_class: EquivalenceClass
    allows_approximation: bool
    default_abs_tolerance: float = 0.0
    default_rel_tolerance: float = 0.0
    evidence_level: EvidenceLevel = EvidenceLevel.MEASURED
    is_verified: bool = False
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class UniversalCapabilityRegistry:
    """
    Central registry cataloging external GPU capabilities mapped into software-only pathways.
    """

    def __init__(self) -> None:
        self._entries: Dict[str, CapabilityEntry] = {}
        self._populate_taxonomy()

    def register(self, entry: CapabilityEntry) -> None:
        self._entries[entry.capability_id] = entry

    def get(self, capability_id: str) -> Optional[CapabilityEntry]:
        return self._entries.get(capability_id)

    def get_by_family(self, family: CapabilityFamily) -> List[CapabilityEntry]:
        return [e for e in self._entries.values() if e.family == family]

    def all_capabilities(self) -> List[CapabilityEntry]:
        return list(self._entries.values())

    def _populate_taxonomy(self) -> None:
        taxonomy_specs: List[Dict[str, Any]] = [
            # 1. GRAPHICS
            {
                "cap_id": "CAP-GFX-001",
                "name": "vertex_and_geometry_processing",
                "family": CapabilityFamily.GRAPHICS,
                "sub": ["vertex_transform", "primitive_assembly", "clipping", "tessellation", "geometry_shading"],
                "hw": "SM Vertex Pipelines / Primitive Engines",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Transformation of 3D vertices, primitive setup, clipping, and tessellation.",
            },
            {
                "cap_id": "CAP-GFX-002",
                "name": "rasterization_and_fragment_shading",
                "family": CapabilityFamily.GRAPHICS,
                "sub": ["triangle_rasterization", "barycentric_interpolation", "fragment_shading", "depth_testing", "stencil", "blending", "msaa"],
                "hw": "Hardware Rasterizers + ROPs",
                "eq": EquivalenceClass.PERCEPTUALLY_EQUIVALENT,
                "approx": True,
                "abs_tol": 0.02,
                "desc": "Scanline/tile rasterization, fragment compute, z/stencil tests, and alpha blending.",
            },
            {
                "cap_id": "CAP-GFX-003",
                "name": "texture_sampling_and_post_processing",
                "family": CapabilityFamily.GRAPHICS,
                "sub": ["texture_sampling", "filtering_bilinear_trilinear", "anisotropic_filtering", "hdr_tonemapping", "post_processing", "compute_shaders"],
                "hw": "Texture Mapping Units (TMUs)",
                "eq": EquivalenceClass.PERCEPTUALLY_EQUIVALENT,
                "approx": True,
                "abs_tol": 0.02,
                "desc": "Texture addressing, mipmapping, anisotropic sampling, and HDR tone curve mapping.",
            },

            # 2. RAY TRACING
            {
                "cap_id": "CAP-RT-001",
                "name": "bvh_construction_and_traversal",
                "family": CapabilityFamily.RAY_TRACING,
                "sub": ["bvh_construction", "bvh_update", "ray_box_intersection", "ray_triangle_intersection", "ray_traversal"],
                "hw": "Dedicated RT Cores (BVH Traversal Engines)",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Bounding volume hierarchy building, update, ray-AABB and Moller-Trumbore intersection.",
            },
            {
                "cap_id": "CAP-RT-002",
                "name": "lighting_and_denoising",
                "family": CapabilityFamily.RAY_TRACING,
                "sub": ["ray_generation", "shadows", "reflections", "refractions", "global_illumination", "denoising", "temporal_accumulation"],
                "hw": "RT Cores + Tensor Denoising",
                "eq": EquivalenceClass.PERCEPTUALLY_EQUIVALENT,
                "approx": True,
                "abs_tol": 0.05,
                "desc": "Monte Carlo radiance transport, path tracing, irradiance caching, and spatio-temporal denoising.",
            },

            # 3. AI / ML
            {
                "cap_id": "CAP-AIML-001",
                "name": "matrix_multiplication_gemm",
                "family": CapabilityFamily.AI_ML,
                "sub": ["dense_gemm", "batched_gemm", "low_rank_gemm", "strassen_bilinear", "fused_matmul_bias"],
                "hw": "Tensor Cores (FP16/BF16/FP8/INT8/FP32)",
                "eq": EquivalenceClass.NUMERICALLY_EQUIVALENT,
                "approx": False,
                "abs_tol": 1e-4,
                "desc": "General matrix multiply with Strassen/tensor reduction, cache blocking, and fusion.",
            },
            {
                "cap_id": "CAP-AIML-002",
                "name": "convolution_and_tensor_ops",
                "family": CapabilityFamily.AI_ML,
                "sub": ["conv1d", "conv2d", "conv3d", "separable_convolution", "depthwise_convolution", "tensor_contractions"],
                "hw": "Tensor Cores + CUDA Core SIMD",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Multi-dimensional convolution via Winograd, FFT, or rank-1 separable decomposition.",
            },
            {
                "cap_id": "CAP-AIML-003",
                "name": "transformer_attention_and_kv_cache",
                "family": CapabilityFamily.AI_ML,
                "sub": ["scaled_dot_product_attention", "flash_attention", "kv_cache_ops", "speculative_decoding", "softmax", "layer_norm"],
                "hw": "Tensor Cores + High-Bandwidth Memory",
                "eq": EquivalenceClass.NUMERICALLY_EQUIVALENT,
                "approx": False,
                "abs_tol": 1e-3,
                "desc": "Multi-head attention, tiled softmax, KV-cache updates, and autoregressive speculation.",
            },
            {
                "cap_id": "CAP-AIML-004",
                "name": "quantization_and_embeddings",
                "family": CapabilityFamily.AI_ML,
                "sub": ["int8_quantization", "int4_quantization", "ternary_bitnet", "dequantization", "embedding_lookup", "reductions"],
                "hw": "Integer SIMD / Low-Precision Tensor Units",
                "eq": EquivalenceClass.NUMERICALLY_EQUIVALENT,
                "approx": True,
                "abs_tol": 0.05,
                "desc": "Affine/symmetric integer quantization, ternary BitNet b1.58, and sparse embedding tables.",
            },

            # 4. SCIENTIFIC COMPUTING
            {
                "cap_id": "CAP-SCI-001",
                "name": "linear_algebra_and_pde",
                "family": CapabilityFamily.SCIENTIFIC,
                "sub": ["dense_linear_algebra", "sparse_linear_algebra", "cholesky_lu", "pde_heat_stencil", "navier_stokes", "finite_difference"],
                "hw": "FP64 / FP32 Vector Compute Engines",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Dense/sparse solvers, matrix factorizations, and partial differential equation solvers.",
            },
            {
                "cap_id": "CAP-SCI-002",
                "name": "nbody_and_monte_carlo",
                "family": CapabilityFamily.SCIENTIFIC,
                "sub": ["n_body_simulation", "barnes_hut", "fast_multipole_method", "monte_carlo_integration", "fft_spectral"],
                "hw": "FP64/FP32 SM Compute",
                "eq": EquivalenceClass.NUMERICALLY_EQUIVALENT,
                "approx": False,
                "abs_tol": 1e-4,
                "desc": "Particle interactions via symmetric Newton 3rd law halving, FMM, and fast Fourier transforms.",
            },

            # 5. IMAGE PROCESSING
            {
                "cap_id": "CAP-IMG-001",
                "name": "image_filtering_and_transforms",
                "family": CapabilityFamily.IMAGE,
                "sub": ["resize", "separable_blur", "sharpen", "edge_detection_sobel", "morphology", "image_reconstruction"],
                "hw": "2D Image Processing Pipelines",
                "eq": EquivalenceClass.PERCEPTUALLY_EQUIVALENT,
                "approx": True,
                "abs_tol": 0.02,
                "desc": "Spatial spatial filters, separable kernel blur, Sobel gradient, and morphological operations.",
            },

            # 6. VIDEO PROCESSING
            {
                "cap_id": "CAP-VID-001",
                "name": "video_frame_processing_and_motion",
                "family": CapabilityFamily.VIDEO,
                "sub": ["frame_decoding", "frame_encoding", "motion_estimation", "temporal_reconstruction", "dirty_region_processing", "frame_interpolation"],
                "hw": "NVDEC / NVENC Hardware Codecs",
                "eq": EquivalenceClass.PERCEPTUALLY_EQUIVALENT,
                "approx": True,
                "abs_tol": 0.03,
                "desc": "Temporal dirty-region tracking, motion vector estimation, and frame delta compression.",
            },

            # 7. COMPRESSION
            {
                "cap_id": "CAP-CMP-001",
                "name": "lossless_and_entropy_compression",
                "family": CapabilityFamily.COMPRESSION,
                "sub": ["compression", "decompression", "entropy_coding", "dictionary_methods", "delta_encoding", "run_length_vectorized"],
                "hw": "High-Throughput Streaming Memory Subsystem",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Lossless delta state, vectorized run-length encoding, Huffman/LZ dictionary transforms.",
            },

            # 8. CRYPTOGRAPHY
            {
                "cap_id": "CAP-CRY-001",
                "name": "cryptographic_hashing_and_ciphers",
                "family": CapabilityFamily.CRYPTOGRAPHY,
                "sub": ["sha_families", "aes_primitives", "modular_arithmetic", "elliptic_curve_primitives", "parallel_hashing"],
                "hw": "Crypto Accelerator / Integer ALUs",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Bit-exact cryptographic hash chains, modular exponentiation, and symmetric ciphers.",
            },

            # 9. GENERAL COMPUTE
            {
                "cap_id": "CAP-GEN-001",
                "name": "parallel_sort_scan_and_reductions",
                "family": CapabilityFamily.GENERAL_COMPUTE,
                "sub": ["prefix_scan", "radix_sort", "parallel_reductions", "graph_traversal", "search_filtering"],
                "hw": "CUDA Core Warp Schedulers + Shared Memory",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Blelloch work-efficient tree scan, bitonic/radix sort, tree reductions, and graph search.",
            },

            # 10. SIMULATION
            {
                "cap_id": "CAP-SIM-001",
                "name": "physical_and_causal_simulation",
                "family": CapabilityFamily.SIMULATION,
                "sub": ["rigid_body_physics", "collision_detection", "causal_cloth_simulation", "particle_dynamics"],
                "hw": "PhysX / Compute Shaders",
                "eq": EquivalenceClass.NUMERICALLY_EQUIVALENT,
                "approx": True,
                "abs_tol": 0.01,
                "desc": "Symplectic integrators, causal simulation pruning, and spatial hash collisions.",
            },

            # 11. MEMORY BEHAVIOR
            {
                "cap_id": "CAP-MEM-001",
                "name": "memory_access_and_bandwidth_bypass",
                "family": CapabilityFamily.MEMORY_BEHAVIOR,
                "sub": ["cache_locality_tiling", "zero_copy_wormhole", "prefetching", "hot_cold_separation", "information_movement_minimization"],
                "hw": "HBM3 / GDDR6X Memory Bus & Crossbar",
                "eq": EquivalenceClass.EXACT,
                "approx": False,
                "desc": "Cache-aware memory hierarchy matching: Golden Cove L1/L2 tiling, UMA zero-copy bridge.",
            },
        ]

        for s in taxonomy_specs:
            cid = s["cap_id"]
            slug = s["name"]
            entry = CapabilityEntry(
                capability_id=cid,
                workload_id=f"WRK-{slug.upper()}",
                contract_id=f"CTR-{slug.upper()}",
                verification_id=f"VRF-{slug.upper()}",
                benchmark_id=f"BNCH-{slug.upper()}",
                evidence_id=f"EVD-{slug.upper()}",
                name=s["name"],
                family=s["family"],
                sub_capabilities=s["sub"],
                reference_hardware_subsystem=s["hw"],
                equivalence_class=s["eq"],
                allows_approximation=s["approx"],
                default_abs_tolerance=s.get("abs_tol", 0.0),
                default_rel_tolerance=s.get("rel_tol", 0.0),
                evidence_level=EvidenceLevel.MEASURED,
                is_verified=False,
                description=s["desc"],
            )
            self.register(entry)


# Singleton instance
GLOBAL_CAPABILITY_REGISTRY = UniversalCapabilityRegistry()
