"""
hyper/parity_engine/capability_registry.py
==========================================
Universal GPU Capability Taxonomy and Registry.
Implements Section 4 specifications of the HYPER 100% Master Mission:
Defines complete capability taxonomy across all 9 universal GPU domains:
- Graphics
- Ray Tracing
- AI / ML
- Scientific Computing
- Image Processing
- Video Processing
- Compression
- Cryptography
- General Compute

Every capability receives unique IDs:
Capability ID, Workload ID, Contract ID, Verification ID, Benchmark ID, Evidence ID.
"""

from __future__ import annotations
import enum
import json
import os
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GPUDomain(str, enum.Enum):
    GRAPHICS = "GRAPHICS"
    RAY_TRACING = "RAY_TRACING"
    AI_ML = "AI_ML"
    SCIENTIFIC_COMPUTING = "SCIENTIFIC_COMPUTING"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    COMPRESSION = "COMPRESSION"
    CRYPTOGRAPHY = "CRYPTOGRAPHY"
    GENERAL_COMPUTE = "GENERAL_COMPUTE"


class CapabilityStatus(str, enum.Enum):
    UNEXPLORED = "UNEXPLORED"
    EXPLORING = "EXPLORING"
    PATHWAY_FOUND = "PATHWAY_FOUND"
    VERIFIED = "VERIFIED"
    BLIND_HOLDOUT_PASSED = "BLIND_HOLDOUT_PASSED"
    PARITY_ACHIEVED = "PARITY_ACHIEVED"
    FAILED = "FAILED"


class GPUCapability(BaseModel):
    domain: GPUDomain
    name: str
    description: str
    capability_id: str
    workload_id: str
    contract_id: str
    verification_id: str
    benchmark_id: str
    evidence_id: str
    status: CapabilityStatus = CapabilityStatus.UNEXPLORED
    primary_hardware_subsystem: str = "COMPUTE"  # Shader cores, Tensor cores, RT cores, Texture units, ROPs, Video encoder/decoder
    physical_parity_excluded: bool = True  # ALWAYS True per Level 1 exclusion
    verified_non_physical_pathway_id: Optional[str] = None
    parity_percentage: float = 0.0
    last_updated: float = Field(default_factory=time.time)


class CapabilityRegistry:
    """
    Central authoritative capability registry for HYPER 100%.
    Holds all canonical capabilities required from external GPU hardware.
    """

    def __init__(self, storage_path: str = "reports/parity_capability_registry.json") -> None:
        self.storage_path = storage_path
        self._capabilities: Dict[str, GPUCapability] = {}
        self._initialize_canonical_taxonomy()
        self._load_state()

    def _generate_ids(self, domain_prefix: str, slug: str) -> Dict[str, str]:
        code = f"{domain_prefix}_{slug.upper().replace('-', '_')}"
        return {
            "capability_id": f"CAP_{code}",
            "workload_id": f"WLD_{code}",
            "contract_id": f"CTR_{code}",
            "verification_id": f"VRF_{code}",
            "benchmark_id": f"BMK_{code}",
            "evidence_id": f"EVD_{code}",
        }

    def _register(self, domain: GPUDomain, name: str, desc: str, hw: str) -> None:
        prefix = domain.value[:3]
        slug = name.replace(" ", "_")
        ids = self._generate_ids(prefix, slug)
        cap = GPUCapability(
            domain=domain,
            name=name,
            description=desc,
            capability_id=ids["capability_id"],
            workload_id=ids["workload_id"],
            contract_id=ids["contract_id"],
            verification_id=ids["verification_id"],
            benchmark_id=ids["benchmark_id"],
            evidence_id=ids["evidence_id"],
            primary_hardware_subsystem=hw,
        )
        self._capabilities[cap.capability_id] = cap

    def _initialize_canonical_taxonomy(self) -> None:
        # 1. Graphics (14 capabilities)
        graphics_ops = [
            ("vertex_processing", "Transform, skinning, and vertex attribute calculation", "VERTEX_PIPELINE"),
            ("rasterization", "Triangle setup, clipping, and pixel coverage determination", "RASTER_UNIT"),
            ("tessellation", "Hull/domain shading and patch subdivision", "TESSELLATION_UNIT"),
            ("geometry_processing", "Primitive assembly and geometry shader generation", "GEOMETRY_PIPELINE"),
            ("fragment_processing", "Pixel shading, color evaluation, and interpolation", "SHADER_CORES"),
            ("texture_sampling", "UV lookup, address wrapping, and mipmap calculation", "TMU"),
            ("filtering", "Bilinear, trilinear, and anisotropic texture filtering", "TMU"),
            ("blending", "Alpha compositing, additive blending, and dual-source blending", "ROP"),
            ("depth_testing", "Z-buffering, early-Z rejection, and hierarchical depth", "ROP"),
            ("stencil_testing", "Masking, portal clipping, and volumetric shadows", "ROP"),
            ("msaa", "Multi-sample anti-aliasing and sample resolving", "ROP"),
            ("hdr_tone_mapping", "High-dynamic range color grading and exposure adjustment", "SHADER_CORES"),
            ("post_processing", "Bloom, motion blur, SSAO, and depth-of-field filters", "SHADER_CORES"),
            ("compute_shaders", "General purpose massively parallel compute dispatch", "COMPUTE_UNITS"),
        ]
        for name, desc, hw in graphics_ops:
            self._register(GPUDomain.GRAPHICS, name, desc, hw)

        # 2. Ray Tracing (12 capabilities)
        rt_ops = [
            ("ray_generation", "Primary ray spawning and camera projection", "COMPUTE_UNITS"),
            ("ray_traversal", "BVH hierarchy walking and tree search", "RT_CORES"),
            ("bvh_construction", "Bottom-up and top-down bounding volume hierarchy building", "COMPUTE_UNITS"),
            ("bvh_update", "Dynamic BLAS refitting and scene hierarchy morphing", "COMPUTE_UNITS"),
            ("ray_box_intersection", "Axis-aligned bounding box slab testing", "RT_CORES"),
            ("ray_triangle_intersection", "Möller-Trumbore / watertight barycentric hit testing", "RT_CORES"),
            ("shadow_rays", "Binary visibility query for direct illuminators", "RT_CORES"),
            ("reflections", "Specular bounce ray tracing and Fresnel evaluation", "RT_CORES"),
            ("refractions", "Dielectric Snell-law transmission ray tracing", "RT_CORES"),
            ("global_illumination", "Multi-bounce diffuse indirect irradiance gathering", "RT_CORES"),
            ("denoising", "Spatial-temporal path-tracing noise filtering (SVGF/BM3D)", "TENSOR_CORES"),
            ("temporal_accumulation", "History buffer reprojection and variance estimation", "SHADER_CORES"),
        ]
        for name, desc, hw in rt_ops:
            self._register(GPUDomain.RAY_TRACING, name, desc, hw)

        # 3. AI / ML (14 capabilities)
        ai_ops = [
            ("matrix_multiplication", "GEMM, blocked BLAS, and quantized matrix products", "TENSOR_CORES"),
            ("convolution", "1D/2D/3D spatial, depthwise, and grouped convolutions", "TENSOR_CORES"),
            ("attention", "FlashAttention, scaled dot-product, and multi-head attention", "TENSOR_CORES"),
            ("transformer_inference", "Autoregressive generation and encoder-decoder pipelines", "TENSOR_CORES"),
            ("embeddings", "Token lookup, positional encoding, and sparse embedding gather", "MEMORY_BUS"),
            ("normalization", "LayerNorm, RMSNorm, BatchNorm, and GroupNorm", "SHADER_CORES"),
            ("softmax", "LogSoftmax, online stable softmax, and causal masking", "SHADER_CORES"),
            ("reductions", "Tree reductions, sum, max, argmax, and norm operations", "SHADER_CORES"),
            ("quantization", "FP32/FP16 to INT8/INT4/FP8/FP4 compression", "TENSOR_CORES"),
            ("dequantization", "Weight unpacking and dynamic scale multiplication", "TENSOR_CORES"),
            ("tensor_operations", "Permute, transpose, slice, concatenate, and broadcast", "MEMORY_CONTROLLER"),
            ("batching", "Batched execution and dynamic batch coalescing", "SCHEDULER"),
            ("speculative_decoding", "Draft model generation and target verifier check", "COMPUTE_UNITS"),
            ("kv_cache_operations", "PagedAttention, ring-buffer caching, and eviction", "VRAM_MANAGEMENT"),
        ]
        for name, desc, hw in ai_ops:
            self._register(GPUDomain.AI_ML, name, desc, hw)

        # 4. Scientific Computing (11 capabilities)
        sci_ops = [
            ("dense_linear_algebra", "LU, Cholesky, QR, and SVD decomposition", "FP64_CORES"),
            ("sparse_linear_algebra", "SpMV, SpMM, and iterative conjugate gradient solvers", "MEMORY_COALESCING"),
            ("fft", "1D/2D Fast Fourier Transform and spectral convolution", "COMPUTE_UNITS"),
            ("pde", "Finite difference, finite element, and stencil Navier-Stokes", "COMPUTE_UNITS"),
            ("numerical_integration", "Runge-Kutta, symplectic integrators, and quadrature", "COMPUTE_UNITS"),
            ("monte_carlo", "High-throughput pseudo/quasi-random sampling walks", "COMPUTE_UNITS"),
            ("n_body", "Gravitational and electrostatic pair-wise interaction force", "COMPUTE_UNITS"),
            ("optimization", "L-BFGS, SGD, Nelder-Mead, and gradient descent", "COMPUTE_UNITS"),
            ("simulation", "Molecular dynamics, particle fluids, and rigid bodies", "COMPUTE_UNITS"),
            ("differential_equations", "Ordinary and stochastic differential equation solvers", "COMPUTE_UNITS"),
            ("scientific_visualization", "Isosurface extraction, marching cubes, and volume rendering", "RASTER_UNIT"),
        ]
        for name, desc, hw in sci_ops:
            self._register(GPUDomain.SCIENTIFIC_COMPUTING, name, desc, hw)

        # 5. Image (10 capabilities)
        img_ops = [
            ("resize", "Bilinear, bicubic, and Lanczos spatial image resampling", "TMU"),
            ("convolution_filters", "Gaussian blur, Sobel, Laplacian, and custom kernels", "COMPUTE_UNITS"),
            ("blur", "Box blur, separable Gaussian, and dual-filtering blur", "COMPUTE_UNITS"),
            ("sharpen", "Unsharp masking, high-pass filtering, and contrast enhancement", "COMPUTE_UNITS"),
            ("edge_detection", "Canny edge detection and gradient magnitude", "COMPUTE_UNITS"),
            ("morphology", "Dilation, erosion, opening, and closing structuring elements", "COMPUTE_UNITS"),
            ("segmentation", "Thresholding, watershed, and semantic mask generation", "COMPUTE_UNITS"),
            ("optical_flow", "Lucas-Kanade and Farneback dense motion field extraction", "COMPUTE_UNITS"),
            ("feature_extraction", "Harris corners, FAST, ORB, and descriptor pooling", "COMPUTE_UNITS"),
            ("image_reconstruction", "Inpainting, super-resolution, and denoising", "TENSOR_CORES"),
        ]
        for name, desc, hw in img_ops:
            self._register(GPUDomain.IMAGE, name, desc, hw)

        # 6. Video (10 capabilities)
        vid_ops = [
            ("decoding", "H.264, HEVC, AV1 hardware bitstream entropy decoding and IDCT", "NVDEC"),
            ("encoding", "Hardware macroblock rate control, CABAC, and packetizing", "NVENC"),
            ("frame_processing", "Color space conversion (YUV420 to RGB), deinterlacing", "VIDEO_ENGINE"),
            ("frame_interpolation", "Optical flow guided intermediate frame generation", "OPTICAL_FLOW_ACCEL"),
            ("optical_flow_video", "Temporal block matching and hierarchical motion vectors", "OPTICAL_FLOW_ACCEL"),
            ("motion_estimation", "Diamond search, full search, and sub-pixel displacement", "NVENC"),
            ("temporal_reconstruction", "Multi-frame super-resolution and temporal anti-aliasing", "TENSOR_CORES"),
            ("video_filtering", "Denoising, artifact removal, and deblocking filter", "VIDEO_ENGINE"),
            ("scaling", "Dynamic hardware video scaler and color gamut remapping", "VIDEO_ENGINE"),
            ("compression_video", "Intra/inter-frame prediction, residual quantization", "NVENC"),
        ]
        for name, desc, hw in vid_ops:
            self._register(GPUDomain.VIDEO, name, desc, hw)

        # 7. Compression (6 capabilities)
        cmp_ops = [
            ("compression_lossless", "LZ4, Snappy, Zstandard parallel GPU-accelerated compression", "COMPUTE_UNITS"),
            ("decompression_lossless", "GpuDecompress parallel block decompression", "COMPUTE_UNITS"),
            ("entropy_coding", "Huffman, ANS (Asymmetric Numeral Systems), Arithmetic coding", "COMPUTE_UNITS"),
            ("dictionary_methods", "Sliding window string matching and hash chains", "SHARED_MEMORY"),
            ("transforms_compression", "Discrete Cosine Transform and Discrete Wavelet Transform", "COMPUTE_UNITS"),
            ("parallel_compression", "Chunked multi-stream independent pipeline compaction", "COMPUTE_UNITS"),
        ]
        for name, desc, hw in cmp_ops:
            self._register(GPUDomain.COMPRESSION, name, desc, hw)

        # 8. Cryptography (6 capabilities)
        cry_ops = [
            ("hashing", "Massive parallel hashing (MD5, Blake2b, Keccak)", "BIT_MANIP_CORES"),
            ("sha_families", "SHA-256 and SHA-512 state transforms and message schedules", "BIT_MANIP_CORES"),
            ("aes", "AES-128/256 Galois counter mode and SubBytes/MixColumns", "AES_UNITS"),
            ("modular_arithmetic", "Big-integer Montgomery multiplication and modular exponentiation", "COMPUTE_UNITS"),
            ("elliptic_curve_workloads", "Secp256k1 and Ed25519 point multiplication and scalar mult", "COMPUTE_UNITS"),
            ("cryptographic_primitives", "ChaCha20, Poly1305, and lattice-based post-quantum lattices", "COMPUTE_UNITS"),
        ]
        for name, desc, hw in cry_ops:
            self._register(GPUDomain.CRYPTOGRAPHY, name, desc, hw)

        # 9. General Compute (8 capabilities)
        gen_ops = [
            ("sorting", "Radix sort, bitonic sort, and merge sort for massive key-value pairs", "SHARED_MEMORY"),
            ("scanning", "Inclusive/exclusive parallel prefix sum (Blelloch scan)", "SHARED_MEMORY"),
            ("reductions_general", "Parallel tree reduction and warp shuffle summation", "WARP_SHUFFLE"),
            ("graph_algorithms", "Breadth-first search, PageRank, and shortest path traversal", "ATOMIC_UNITS"),
            ("search_algorithms", "Binary search, hash table lookup, and spatial indexing", "MEMORY_CONTROLLER"),
            ("filtering_general", "Stream compaction, predicate filtering, and gather-scatter", "WARP_SHUFFLE"),
            ("aggregation", "Group-by, histogram generation, and binning", "ATOMIC_UNITS"),
            ("simulation_general", "Cellular automata, agent systems, and grid propagation", "COMPUTE_UNITS"),
        ]
        for name, desc, hw in gen_ops:
            self._register(GPUDomain.GENERAL_COMPUTE, name, desc, hw)

    def _load_state(self) -> None:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data.get("capabilities", []):
                        cid = item.get("capability_id")
                        if cid in self._capabilities:
                            self._capabilities[cid].status = CapabilityStatus(item.get("status", "UNEXPLORED"))
                            self._capabilities[cid].parity_percentage = float(item.get("parity_percentage", 0.0))
                            self._capabilities[cid].verified_non_physical_pathway_id = item.get("verified_non_physical_pathway_id")
            except Exception:
                pass

    def save_state(self) -> None:
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        payload = {
            "total_capabilities": len(self._capabilities),
            "updated_at": time.time(),
            "capabilities": [c.model_dump() for c in self._capabilities.values()],
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def get_capability(self, capability_id: str) -> Optional[GPUCapability]:
        return self._capabilities.get(capability_id)

    def get_by_name(self, name: str) -> Optional[GPUCapability]:
        name_clean = name.lower().replace(" ", "_").replace("-", "_")
        for cap in self._capabilities.values():
            if cap.name.lower().replace(" ", "_") == name_clean:
                return cap
        return None

    def list_capabilities(self, domain: Optional[GPUDomain] = None) -> List[GPUCapability]:
        if domain is None:
            return list(self._capabilities.values())
        return [c for c in self._capabilities.values() if c.domain == domain]

    def update_status(
        self,
        capability_id: str,
        status: CapabilityStatus,
        parity_pct: float,
        pathway_id: Optional[str] = None,
    ) -> None:
        if capability_id in self._capabilities:
            cap = self._capabilities[capability_id]
            cap.status = status
            cap.parity_percentage = max(0.0, min(100.0, parity_pct))
            if pathway_id:
                cap.verified_non_physical_pathway_id = pathway_id
            cap.last_updated = time.time()
            self.save_state()

    def get_coverage_summary(self) -> Dict[str, Any]:
        total = len(self._capabilities)
        verified = sum(1 for c in self._capabilities.values() if c.status in [CapabilityStatus.VERIFIED, CapabilityStatus.PARITY_ACHIEVED])
        by_domain: Dict[str, Dict[str, Any]] = {}
        for dom in GPUDomain:
            dom_caps = self.list_capabilities(dom)
            dom_total = len(dom_caps)
            dom_verified = sum(1 for c in dom_caps if c.status in [CapabilityStatus.VERIFIED, CapabilityStatus.PARITY_ACHIEVED])
            dom_pct = round((dom_verified / max(dom_total, 1)) * 100.0, 2)
            by_domain[dom.value] = {
                "total": dom_total,
                "verified": dom_verified,
                "percentage": dom_pct,
            }
        return {
            "total_capabilities": total,
            "verified_capabilities": verified,
            "global_parity_percentage": round((verified / max(total, 1)) * 100.0, 2),
            "by_domain": by_domain,
        }
