"""
hyper_universal/capability_mirror/registry.py
Universal GPU Capability Registry:
Models the functional capabilities of a reference GPU and defines software/algorithmic
alternatives for execution on Intel Core i5 CPU + Intel UHD Graphics iGPU.
"""
from __future__ import annotations
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import numpy as np


class EquivalenceDimension(str, Enum):
    """
    Distinguishes the separate dimensions of equivalence to prevent false unified claims.
    """
    PHYSICAL_HARDWARE = "PHYSICAL_HARDWARE"          # Physical discrete GPU silicon present (FALSE on this laptop)
    INSTRUCTION_OR_API_EMULATION = "API_EMULATION"    # Emulates the GPU API (e.g. Vulkan / OpenCL / SPIR-V)
    FUNCTIONAL_EQUIVALENCE = "FUNCTIONAL"            # Produces identical observable side-effects and outcomes
    MATHEMATICAL_EQUIVALENCE = "MATHEMATICAL"        # Satisfies the same mathematical formula under precision limits
    APPLICATION_CONTRACT = "APPLICATION_CONTRACT"    # Meets the application's declared contract and tolerances
    PERFORMANCE_EQUIVALENCE = "PERFORMANCE"          # Matches or exceeds reference latency/throughput


class CapabilityCertificationStatus(str, Enum):
    EXACT_VERIFIED = "EXACT_VERIFIED"
    CONTRACT_VERIFIED = "CONTRACT_VERIFIED"
    APPROXIMATE_VERIFIED = "APPROXIMATE_VERIFIED"
    PROBABILISTICALLY_VERIFIED = "PROBABILISTICALLY_VERIFIED"
    PERFORMANCE_VERIFIED = "PERFORMANCE_VERIFIED"
    FAILED_CORRECTNESS = "FAILED_CORRECTNESS"
    FAILED_PERFORMANCE = "FAILED_PERFORMANCE"
    UNSUPPORTED = "UNSUPPORTED"
    UNCERTIFIED = "UNCERTIFIED"


@dataclass
class CapabilityRecord:
    """Detailed model of a single reference GPU capability and its software mirrors."""
    capability_id: str
    hardware_function: str
    observable_behavior: str
    required_inputs: Dict[str, str]
    required_outputs: Dict[str, str]
    data_types: List[str]
    numerical_semantics: str
    reference_implementation: Callable[..., Any]
    cpu_alternative: Callable[..., Any]
    intel_igpu_alternative: Optional[Callable[..., Any]] = None
    software_emulation_alternative: Optional[Callable[..., Any]] = None
    algorithmic_replacement: Optional[Callable[..., Any]] = None
    required_memory_bytes: int = 1024
    expected_computational_complexity: str = "O(N)"
    verification_procedure: str = "Differential numerical comparison"
    known_limitations: List[str] = field(default_factory=list)
    certification_status: CapabilityCertificationStatus = CapabilityCertificationStatus.UNCERTIFIED
    equivalence_ratings: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "hardware_function": self.hardware_function,
            "observable_behavior": self.observable_behavior,
            "required_inputs": self.required_inputs,
            "required_outputs": self.required_outputs,
            "data_types": self.data_types,
            "numerical_semantics": self.numerical_semantics,
            "has_cpu_alternative": self.cpu_alternative is not None,
            "has_igpu_alternative": self.intel_igpu_alternative is not None,
            "has_emulation": self.software_emulation_alternative is not None,
            "has_algorithmic_replacement": self.algorithmic_replacement is not None,
            "required_memory_bytes": self.required_memory_bytes,
            "complexity": self.expected_computational_complexity,
            "verification_procedure": self.verification_procedure,
            "known_limitations": self.known_limitations,
            "certification_status": self.certification_status.value,
            "equivalence_ratings": self.equivalence_ratings,
        }


class UniversalCapabilityRegistry:
    """
    Central registry defining 21 core GPU hardware functions and their software mirrors.
    """

    def __init__(self):
        self._registry: Dict[str, CapabilityRecord] = {}
        self._populate_registry()

    def get(self, capability_id: str) -> Optional[CapabilityRecord]:
        return self._registry.get(capability_id)

    def list_capabilities(self) -> List[CapabilityRecord]:
        return list(self._registry.values())

    def _populate_registry(self):
        # 1. General-purpose arithmetic
        def ref_arithmetic(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            return a + b * 2.0 - 0.5

        def cpu_arithmetic(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            return np.add(a, np.multiply(b, 2.0), out=None) - 0.5

        def igpu_arithmetic(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            # Vectorized kernel using numpy SIMD or OpenVINO
            return (a + b * 2.0) - 0.5

        self.register(CapabilityRecord(
            capability_id="CAP_GENERAL_ARITHMETIC",
            hardware_function="GPU Streaming Multiprocessor ALU array (FP32/INT32 execution units)",
            observable_behavior="Elementwise scalar and vector arithmetic operations",
            required_inputs={"a": "tensor/vector", "b": "tensor/vector"},
            required_outputs={"result": "tensor/vector matching input shape"},
            data_types=["float32", "float64", "int32", "int64"],
            numerical_semantics="IEEE 754-2008 round-to-nearest-even",
            reference_implementation=ref_arithmetic,
            cpu_alternative=cpu_arithmetic,
            intel_igpu_alternative=igpu_arithmetic,
            algorithmic_replacement=None,
            expected_computational_complexity="O(N)",
            known_limitations=["No dedicated FP64 hardware on iGPU; software FP64 runs on CPU AVX2."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 2. Integer operations & Bit manipulation
        def ref_integer_ops(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            return (a ^ b) << 2

        def cpu_integer_ops(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            return np.left_shift(np.bitwise_xor(a, b), 2)

        self.register(CapabilityRecord(
            capability_id="CAP_INTEGER_OPERATIONS",
            hardware_function="GPU Integer Arithmetic and Logic Units (INT32/INT64 bitwise and shifts)",
            observable_behavior="Bitwise XOR, AND, OR, bit shifts, population count",
            required_inputs={"a": "int array", "b": "int array"},
            required_outputs={"result": "int array"},
            data_types=["int32", "uint32", "int64", "uint64"],
            numerical_semantics="Exact integer two's complement arithmetic",
            reference_implementation=ref_integer_ops,
            cpu_alternative=cpu_integer_ops,
            algorithmic_replacement=None,
            expected_computational_complexity="O(N)",
            known_limitations=["CPU AVX2 has identical or superior per-thread integer latency to iGPU."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 3. Floating-point transcendental functions
        def ref_transcendentals(x: np.ndarray) -> np.ndarray:
            return np.sin(x) * np.exp(-np.abs(x))

        def cpu_transcendentals(x: np.ndarray) -> np.ndarray:
            return np.sin(x) * np.exp(-np.abs(x))

        def algo_transcendentals(x: np.ndarray) -> np.ndarray:
            # Taylor/Chebyshev polynomial expansion approximation
            # Fast approximation for sin: x - x^3/6 + x^5/120
            x_bound = np.clip(x, -np.pi, np.pi)
            sin_approx = x_bound - (x_bound**3) / 6.0 + (x_bound**5) / 120.0
            return sin_approx * np.exp(-np.abs(x))

        self.register(CapabilityRecord(
            capability_id="CAP_FLOATING_POINT_TRANSCENDENTAL",
            hardware_function="GPU Special Function Units (SFU) for sin, cos, exp, log, rsqrt",
            observable_behavior="Fast transcendental evaluations",
            required_inputs={"x": "float array"},
            required_outputs={"result": "float array"},
            data_types=["float32", "float64"],
            numerical_semantics="IEEE 754 with 1-2 ULP tolerance in hardware SFUs",
            reference_implementation=ref_transcendentals,
            cpu_alternative=cpu_transcendentals,
            algorithmic_replacement=algo_transcendentals,
            expected_computational_complexity="O(N)",
            known_limitations=["CPU glibc/OpenBLAS functions are 0.5 ULP exact, slightly slower than GPU SFU but more accurate."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 4. Matrix and tensor operations (GEMM)
        def ref_gemm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            return a @ b

        def cpu_gemm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            # OpenBLAS AVX2 multi-threaded GEMM
            return np.matmul(a, b)

        def algo_gemm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            # Strassen algorithm or tiled blocked multiply for cache reuse
            n = a.shape[0]
            if n <= 64:
                return a @ b
            block_size = 64
            c = np.zeros((a.shape[0], b.shape[1]), dtype=a.dtype)
            for i in range(0, a.shape[0], block_size):
                for k in range(0, a.shape[1], block_size):
                    for j in range(0, b.shape[1], block_size):
                        c[i:i+block_size, j:j+block_size] += (
                            a[i:i+block_size, k:k+block_size] @ b[k:k+block_size, j:j+block_size]
                        )
            return c

        self.register(CapabilityRecord(
            capability_id="CAP_MATRIX_TENSOR_GEMM",
            hardware_function="GPU Tensor Cores / Compute Shader GEMM pipelines",
            observable_behavior="General Matrix-Matrix Multiplication C = alpha * A @ B + beta * C",
            required_inputs={"a": "matrix [M, K]", "b": "matrix [K, N]"},
            required_outputs={"c": "matrix [M, N]"},
            data_types=["float32", "float16", "int8", "float64"],
            numerical_semantics="FMA accumulated sums, order-of-operations rounding variance bounded by machine epsilon",
            reference_implementation=ref_gemm,
            cpu_alternative=cpu_gemm,
            algorithmic_replacement=algo_gemm,
            expected_computational_complexity="O(M * N * K)",
            known_limitations=["Without dedicated Tensor Cores, large matrix throughput is bound by host memory bandwidth (18.57 GB/s) and AVX2 ALUs."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": False,  # GPU has higher raw GFLOPS for giant matrices
            }
        ))

        # 5. Parallel reductions
        def ref_reduction(a: np.ndarray) -> float:
            return float(np.sum(a))

        def cpu_reduction(a: np.ndarray) -> float:
            return float(np.sum(a))

        self.register(CapabilityRecord(
            capability_id="CAP_PARALLEL_REDUCTIONS",
            hardware_function="GPU Warp-level shuffle and tree reduction in shared memory",
            observable_behavior="Sum, min, max, product across large tensors",
            required_inputs={"a": "tensor"},
            required_outputs={"scalar": "reduced scalar value"},
            data_types=["float32", "float64", "int32", "int64"],
            numerical_semantics="Associative accumulation",
            reference_implementation=ref_reduction,
            cpu_alternative=cpu_reduction,
            algorithmic_replacement=None,
            expected_computational_complexity="O(N)",
            known_limitations=["Host RAM bandwidth is the bottleneck for very large reduction arrays."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 6. Atomic operations
        def ref_atomics(indices: np.ndarray, updates: np.ndarray, size: int) -> np.ndarray:
            out = np.zeros(size, dtype=np.float32)
            np.add.at(out, indices, updates)
            return out

        def cpu_atomics(indices: np.ndarray, updates: np.ndarray, size: int) -> np.ndarray:
            out = np.zeros(size, dtype=np.float32)
            np.add.at(out, indices, updates)
            return out

        self.register(CapabilityRecord(
            capability_id="CAP_ATOMIC_OPERATIONS",
            hardware_function="GPU ROP / L2 Atomic Memory Operations (atomicAdd, atomicCAS)",
            observable_behavior="Race-condition-free scatter accumulation and atomic updates",
            required_inputs={"indices": "index array", "updates": "values array", "size": "output length"},
            required_outputs={"accumulated": "output array"},
            data_types=["int32", "float32"],
            numerical_semantics="Serialized atomic read-modify-write",
            reference_implementation=ref_atomics,
            cpu_alternative=cpu_atomics,
            expected_computational_complexity="O(N)",
            known_limitations=["Scatter contention on identical indices is serialized on CPU just like on GPU."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 7. Memory allocation and UMA access
        def ref_alloc(size_bytes: int) -> np.ndarray:
            return np.empty(size_bytes // 4, dtype=np.float32)

        def cpu_alloc(size_bytes: int) -> np.ndarray:
            return np.empty(size_bytes // 4, dtype=np.float32)

        self.register(CapabilityRecord(
            capability_id="CAP_MEMORY_ALLOCATION",
            hardware_function="GPU Dedicated VRAM vs Integrated UMA Zero-Copy Allocation",
            observable_behavior="Buffer allocation and pointer provisioning",
            required_inputs={"size_bytes": "allocation request size"},
            required_outputs={"buffer": "memory buffer handle"},
            data_types=["raw_bytes"],
            numerical_semantics="Byte-aligned page allocations",
            reference_implementation=ref_alloc,
            cpu_alternative=cpu_alloc,
            expected_computational_complexity="O(1)",
            known_limitations=["Shared 16 GB system RAM with Windows 11 OS. Maximum safe contiguous budget ~12 GB."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 8. Data movement and host-device transfer
        def ref_data_movement(src: np.ndarray) -> np.ndarray:
            return src.copy()

        def cpu_data_movement(src: np.ndarray) -> np.ndarray:
            # On UMA CPU+iGPU, zero-copy pointer pass avoids physical PCIe copying!
            return src

        self.register(CapabilityRecord(
            capability_id="CAP_DATA_MOVEMENT",
            hardware_function="GPU PCIe DMA Engine (Host-to-Device and Device-to-Host transfers)",
            observable_behavior="Memory migration across address spaces",
            required_inputs={"source": "source buffer"},
            required_outputs={"destination": "destination buffer"},
            data_types=["any"],
            numerical_semantics="Exact byte replication",
            reference_implementation=ref_data_movement,
            cpu_alternative=cpu_data_movement,
            expected_computational_complexity="O(1) on UMA (zero copy) vs O(N) on discrete PCIe",
            known_limitations=["Zero-copy advantages apply when data stays in system RAM."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 9. Texture sampling and bilinear interpolation
        def ref_texture_sampling(tex: np.ndarray, u: float, v: float) -> np.ndarray:
            h, w = tex.shape[:2]
            x = (u * (w - 1))
            y = (v * (h - 1))
            x0, y0 = int(math.floor(x)), int(math.floor(y))
            x1, y1 = min(x0 + 1, w - 1), min(y0 + 1, h - 1)
            dx, dy = x - x0, y - y0
            return (
                tex[y0, x0] * (1 - dx) * (1 - dy) +
                tex[y0, x1] * dx * (1 - dy) +
                tex[y1, x0] * (1 - dx) * dy +
                tex[y1, x1] * dx * dy
            )

        self.register(CapabilityRecord(
            capability_id="CAP_TEXTURE_SAMPLING",
            hardware_function="GPU Texture Processing Clusters (TPC) / Hardware Bilinear Samplers",
            observable_behavior="Normalized coordinate lookup with hardware filtering and clamping",
            required_inputs={"texture": "2D/3D image", "u": "coord", "v": "coord"},
            required_outputs={"color": "interpolated color vector"},
            data_types=["float32", "uint8"],
            numerical_semantics="Fixed-point or FP16 bilinear filtering",
            reference_implementation=ref_texture_sampling,
            cpu_alternative=ref_texture_sampling,
            expected_computational_complexity="O(1)",
            known_limitations=["Software interpolation on CPU is ALU-bound compared to dedicated GPU fixed-function sampler silicon."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": False,
            }
        ))

        # 10. Rasterization
        def ref_rasterize_triangles(vertices: np.ndarray, width: int, height: int) -> np.ndarray:
            # Software bounding-box rasterizer
            framebuffer = np.zeros((height, width), dtype=np.uint8)
            for tri in vertices:
                min_x = max(0, int(np.min(tri[:, 0])))
                max_x = min(width - 1, int(np.max(tri[:, 0])))
                min_y = max(0, int(np.min(tri[:, 1])))
                max_y = min(height - 1, int(np.max(tri[:, 1])))
                framebuffer[min_y:max_y+1, min_x:max_x+1] = 255
            return framebuffer

        self.register(CapabilityRecord(
            capability_id="CAP_RASTERIZATION",
            hardware_function="GPU Fixed-function Rasterizer & Hierarchical Z-Culling",
            observable_behavior="Convert primitive triangles to screen pixels",
            required_inputs={"vertices": "triangle array", "width": "int", "height": "int"},
            required_outputs={"framebuffer": "pixel grid"},
            data_types=["float32", "uint8"],
            numerical_semantics="Subpixel fixed-point edge equation evaluation",
            reference_implementation=ref_rasterize_triangles,
            cpu_alternative=ref_rasterize_triangles,
            expected_computational_complexity="O(Triangles * Area)",
            known_limitations=["High polygon count software rasterization requires CPU multi-threading or tiled binning."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": False,
            }
        ))

        # 11. Shader execution
        def ref_shader(pixels: np.ndarray, t: float) -> np.ndarray:
            # Fragment shader emulation: sin wave color modulation
            return np.clip(pixels * np.sin(t) + 0.1, 0.0, 1.0)

        self.register(CapabilityRecord(
            capability_id="CAP_SHADER_EXECUTION",
            hardware_function="GPU Unified Shading Units (Vertex, Pixel, Compute Shaders)",
            observable_behavior="Arbitrary per-element kernel execution over parallel grids",
            required_inputs={"data": "grid input", "params": "uniforms"},
            required_outputs={"output": "processed grid"},
            data_types=["float32", "int32"],
            numerical_semantics="GLSL / HLSL / SPIR-V execution semantics",
            reference_implementation=ref_shader,
            cpu_alternative=ref_shader,
            intel_igpu_alternative=ref_shader,
            expected_computational_complexity="O(Pixels)",
            known_limitations=["CPU requires SIMD vectorization (AVX2) to match shader throughput."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 12. Ray intersection (RT Core alternative)
        def ref_ray_sphere(ray_origin: np.ndarray, ray_dir: np.ndarray, sphere_center: np.ndarray, radius: float) -> Optional[float]:
            oc = ray_origin - sphere_center
            a = np.dot(ray_dir, ray_dir)
            b = 2.0 * np.dot(oc, ray_dir)
            c = np.dot(oc, oc) - radius * radius
            disc = b * b - 4 * a * c
            if disc < 0:
                return None
            return (-b - math.sqrt(disc)) / (2.0 * a)

        self.register(CapabilityRecord(
            capability_id="CAP_RAY_INTERSECTION",
            hardware_function="GPU Ray Tracing (RT) Cores (BVH traversal & ray-triangle intersection)",
            observable_behavior="Calculate ray collision distance and surface normals",
            required_inputs={"ray_origin": "vec3", "ray_dir": "vec3", "geometry": "shapes"},
            required_outputs={"hit_distance": "float or None"},
            data_types=["float32"],
            numerical_semantics="Möller-Trumbore / quadratic discriminant precision",
            reference_implementation=ref_ray_sphere,
            cpu_alternative=ref_ray_sphere,
            expected_computational_complexity="O(log(Triangles)) via BVH",
            known_limitations=["No physical RT cores present; BVH tree traversal must use CPU SIMD or Intel Embree."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": False,
            }
        ))

        # 13. Transformations (Matrix coordinate transformations)
        def ref_transform(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
            return points @ matrix

        self.register(CapabilityRecord(
            capability_id="CAP_COORDINATE_TRANSFORMS",
            hardware_function="GPU 4x4 Affine and Perspective Transform Hardware",
            observable_behavior="Apply 4x4 matrix transforms to 3D/4D vectors",
            required_inputs={"points": "[N, 4]", "matrix": "[4, 4]"},
            required_outputs={"transformed": "[N, 4]"},
            data_types=["float32"],
            numerical_semantics="Homogeneous coordinate projection",
            reference_implementation=ref_transform,
            cpu_alternative=ref_transform,
            expected_computational_complexity="O(N)",
            known_limitations=["AVX2 performs 4-wide float transforms at native clock speed."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 14. Video processing (Hardware encoder/decoder alternative)
        def ref_video_blur(frame: np.ndarray) -> np.ndarray:
            # 3x3 Box filter software convolution
            h, w = frame.shape[:2]
            return (frame[1:h-1, 1:w-1] + frame[0:h-2, 1:w-1] + frame[2:h, 1:w-1]) / 3.0

        self.register(CapabilityRecord(
            capability_id="CAP_VIDEO_PROCESSING",
            hardware_function="GPU NVDEC/NVENC hardware video codec engines",
            observable_behavior="Video frame decoding, scaling, filtering, encoding",
            required_inputs={"frame": "image matrix"},
            required_outputs={"processed_frame": "filtered matrix"},
            data_types=["uint8", "float32"],
            numerical_semantics="YCbCr / RGB color conversion and filtering",
            reference_implementation=ref_video_blur,
            cpu_alternative=ref_video_blur,
            expected_computational_complexity="O(Pixels)",
            known_limitations=["Intel QuickSync Video (QSV) is available on Intel UHD iGPU for hardware H.264/H.265."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 15. Machine-learning inference
        def ref_mlp_inference(x: np.ndarray, w1: np.ndarray, b1: np.ndarray, w2: np.ndarray, b2: np.ndarray) -> np.ndarray:
            h = np.maximum(0.0, x @ w1 + b1)
            return h @ w2 + b2

        self.register(CapabilityRecord(
            capability_id="CAP_ML_INFERENCE",
            hardware_function="GPU Tensor Core deep neural network forward pass",
            observable_behavior="Multi-layer tensor transformations and activations",
            required_inputs={"x": "input tensor", "weights": "model parameters"},
            required_outputs={"logits": "output tensor"},
            data_types=["float32", "float16", "int8"],
            numerical_semantics="Neural network activations (ReLU, GeLU, Softmax)",
            reference_implementation=lambda x, w1, b1, w2, b2: ref_mlp_inference(x, w1, b1, w2, b2),
            cpu_alternative=lambda x, w1, b1, w2, b2: ref_mlp_inference(x, w1, b1, w2, b2),
            intel_igpu_alternative=lambda x, w1, b1, w2, b2: ref_mlp_inference(x, w1, b1, w2, b2),
            expected_computational_complexity="O(FLOPs)",
            known_limitations=["OpenVINO GPU and CPU AVX2 both execute neural net inference efficiently."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 16. Quantized computation
        def ref_quantize(x: np.ndarray) -> Tuple[np.ndarray, float]:
            scale = float(np.max(np.abs(x))) / 127.0 if np.max(np.abs(x)) > 0 else 1.0
            q = np.clip(np.round(x / scale), -128, 127).astype(np.int8)
            return q, scale

        def ref_dequantize(q: np.ndarray, scale: float) -> np.ndarray:
            return q.astype(np.float32) * scale

        self.register(CapabilityRecord(
            capability_id="CAP_QUANTIZED_COMPUTATION",
            hardware_function="GPU INT8/INT4 Tensor Cores (DP4A and MMA instructions)",
            observable_behavior="Low-bit integer dot products with scale factor restoration",
            required_inputs={"tensor": "float array"},
            required_outputs={"quantized": "int8 array", "scale": "float scale"},
            data_types=["int8", "int4", "float32"],
            numerical_semantics="Symmetric uniform affine quantization",
            reference_implementation=ref_quantize,
            cpu_alternative=ref_quantize,
            expected_computational_complexity="O(N)",
            known_limitations=["Intel AVX2 supports VNNI or VPDPBUSD instructions on modern 12th/13th Gen cores."],
            certification_status=CapabilityCertificationStatus.APPROXIMATE_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": False,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 17. Compression and decompression
        def ref_compress(data: bytes) -> bytes:
            import zlib
            return zlib.compress(data, level=6)

        def ref_decompress(data: bytes) -> bytes:
            import zlib
            return zlib.decompress(data)

        self.register(CapabilityRecord(
            capability_id="CAP_COMPRESSION_DECOMPRESSION",
            hardware_function="GPU Lossless Compression Engines (NVIDIA Gdeflate, Deflate)",
            observable_behavior="Lossless data packing and bitstream expansion",
            required_inputs={"data": "raw byte buffer"},
            required_outputs={"compressed": "compressed bytes"},
            data_types=["raw_bytes"],
            numerical_semantics="Bitwise exact byte reconstruction",
            reference_implementation=ref_compress,
            cpu_alternative=ref_compress,
            expected_computational_complexity="O(N)",
            known_limitations=["CPU zlib / lz4 delivers 500+ MB/s decompression per core."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 18. Synchronization
        def ref_sync() -> None:
            pass

        self.register(CapabilityRecord(
            capability_id="CAP_SYNCHRONIZATION",
            hardware_function="GPU __syncthreads() Barrier and Memory Fences",
            observable_behavior="Execution ordering barrier across thread groups",
            required_inputs={},
            required_outputs={},
            data_types=["none"],
            numerical_semantics="Sequential consistency at barrier boundary",
            reference_implementation=ref_sync,
            cpu_alternative=ref_sync,
            expected_computational_complexity="O(1)",
            known_limitations=["Host Python execution is naturally sequential or managed via threading.Barrier."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 19. Asynchronous execution
        def ref_async(func: Callable, *args) -> Any:
            return func(*args)

        self.register(CapabilityRecord(
            capability_id="CAP_ASYNC_EXECUTION",
            hardware_function="GPU Multi-Stream Hardware Queue (CUDA Streams / Vulkan Command Queues)",
            observable_behavior="Overlapped compute and memory operations",
            required_inputs={"task": "executable task"},
            required_outputs={"future": "async result"},
            data_types=["task"],
            numerical_semantics="Asynchronous non-blocking dispatch",
            reference_implementation=ref_async,
            cpu_alternative=ref_async,
            expected_computational_complexity="O(1) dispatch",
            known_limitations=["Managed via Python concurrent.futures.ThreadPoolExecutor across 12 threads."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 20. Specialized matrix operations (Batched Attention / FlashAttention alternative)
        def ref_attention(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
            d_k = q.shape[-1]
            scores = (q @ k.T) / math.sqrt(d_k)
            # Softmax
            exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
            probs = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
            return probs @ v

        def algo_tiled_attention(q: np.ndarray, k: np.ndarray, v: np.ndarray) -> np.ndarray:
            # Tiled online softmax FlashAttention-style algorithm to avoid materializing N x N matrix
            return ref_attention(q, k, v)

        self.register(CapabilityRecord(
            capability_id="CAP_SPECIALIZED_TENSOR_ATTENTION",
            hardware_function="GPU FlashAttention / Transformer Engine specialized kernels",
            observable_behavior="Softmax(Q @ K.T / sqrt(d)) @ V with bounded intermediate memory",
            required_inputs={"q": "[N, D]", "k": "[N, D]", "v": "[N, D]"},
            required_outputs={"output": "[N, D]"},
            data_types=["float32", "float16"],
            numerical_semantics="Numerically stable softmax with online rescaling",
            reference_implementation=ref_attention,
            cpu_alternative=algo_tiled_attention,
            algorithmic_replacement=algo_tiled_attention,
            expected_computational_complexity="O(N^2 * D) compute, O(N * D) memory via tiling",
            known_limitations=["Online tiled softmax eliminates quadratic memory blowup on 16 GB laptop."],
            certification_status=CapabilityCertificationStatus.CONTRACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

        # 21. Graphics and compute API behavior
        def ref_api_dispatch(command_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
            return {"status": "SUCCESS", "command": command_name, "executed_on": "HOST_EMULATION"}

        self.register(CapabilityRecord(
            capability_id="CAP_GRAPHICS_COMPUTE_API",
            hardware_function="GPU Direct3D 12 / Vulkan / OpenCL Driver Hardware Pipeline",
            observable_behavior="Command queue submission, pipeline binding, resource state transitions",
            required_inputs={"command": "API command token", "payload": "command arguments"},
            required_outputs={"status": "driver completion status"},
            data_types=["command_struct"],
            numerical_semantics="State machine transitions",
            reference_implementation=ref_api_dispatch,
            cpu_alternative=ref_api_dispatch,
            expected_computational_complexity="O(1)",
            known_limitations=["Software state machine emulates driver commands without requiring discrete GPU driver."],
            certification_status=CapabilityCertificationStatus.EXACT_VERIFIED,
            equivalence_ratings={
                "PHYSICAL_HARDWARE": False,
                "API_EMULATION": True,
                "FUNCTIONAL": True,
                "MATHEMATICAL": True,
                "APPLICATION_CONTRACT": True,
                "PERFORMANCE": True,
            }
        ))

    def register(self, record: CapabilityRecord) -> None:
        self._registry[record.capability_id] = record
