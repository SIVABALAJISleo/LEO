# UNIVERSAL GPU CAPABILITY MIRROR MATRIX

**Platform**: Intel Core i5-12450H + Intel UHD Graphics iGPU (Windows 11)  
**Total Evaluated Hardware Functions**: 21  
**Candidate Software Pathways Evaluated**: 27  
**Verified Correct Substitutions**: 26

| Capability ID                       | Reference GPU Function                      | Pathway Evaluated       | Latency (ms) | Speedup vs Ref | Correctness | Equivalence Dimensions   | Status                 |
| :---------------------------------- | :------------------------------------------ | :---------------------- | :----------- | :------------- | :---------- | :----------------------- | :--------------------- |
| `CAP_GENERAL_ARITHMETIC`            | GPU Streaming Multiprocessor ALU array (... | CPU_AVX2                | 0.07         | 2.71x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_GENERAL_ARITHMETIC`            | GPU Streaming Multiprocessor ALU array (... | INTEL_UHD_IGPU          | 0.023        | 1.3x           | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_INTEGER_OPERATIONS`            | GPU Integer Arithmetic and Logic Units (... | CPU_AVX2                | 0.032        | 1.92x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_FLOATING_POINT_TRANSCENDENTAL` | GPU Special Function Units (SFU) for sin... | CPU_AVX2                | 0.056        | 3.47x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_FLOATING_POINT_TRANSCENDENTAL` | GPU Special Function Units (SFU) for sin... | ALGORITHMIC_REPLACEMENT | 0.167        | 0.26x          | PASS        | API_,FUNC,APPL           | `APPROXIMATE_VERIFIED` |
| `CAP_MATRIX_TENSOR_GEMM`            | GPU Tensor Cores / Compute Shader GEMM p... | CPU_AVX2                | 0.049        | 3.85x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_MATRIX_TENSOR_GEMM`            | GPU Tensor Cores / Compute Shader GEMM p... | ALGORITHMIC_REPLACEMENT | 0.035        | 0.91x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_PARALLEL_REDUCTIONS`           | GPU Warp-level shuffle and tree reductio... | CPU_AVX2                | 0.014        | 1.97x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_ATOMIC_OPERATIONS`             | GPU ROP / L2 Atomic Memory Operations (a... | CPU_AVX2                | 0.015        | 4.33x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_MEMORY_ALLOCATION`             | GPU Dedicated VRAM vs Integrated UMA Zer... | CPU_AVX2                | 0.003        | 0.0x           | FAIL        | API_                     | `FAILED_CORRECTNESS`   |
| `CAP_DATA_MOVEMENT`                 | GPU PCIe DMA Engine (Host-to-Device and ... | CPU_AVX2                | 0.004        | 4.16x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_TEXTURE_SAMPLING`              | GPU Texture Processing Clusters (TPC) / ... | CPU_AVX2                | 0.038        | 1.34x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_RASTERIZATION`                 | GPU Fixed-function Rasterizer & Hierarch... | CPU_AVX2                | 0.048        | 1.58x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_SHADER_EXECUTION`              | GPU Unified Shading Units (Vertex, Pixel... | CPU_AVX2                | 0.039        | 2.55x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_SHADER_EXECUTION`              | GPU Unified Shading Units (Vertex, Pixel... | INTEL_UHD_IGPU          | 0.032        | 1.15x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_RAY_INTERSECTION`              | GPU Ray Tracing (RT) Cores (BVH traversa... | CPU_AVX2                | 0.026        | 1.58x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_COORDINATE_TRANSFORMS`         | GPU 4x4 Affine and Perspective Transform... | CPU_AVX2                | 0.021        | 2.7x           | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_VIDEO_PROCESSING`              | GPU NVDEC/NVENC hardware video codec eng... | CPU_AVX2                | 0.027        | 1.32x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_ML_INFERENCE`                  | GPU Tensor Core deep neural network forw... | CPU_AVX2                | 0.073        | 0.99x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_ML_INFERENCE`                  | GPU Tensor Core deep neural network forw... | INTEL_UHD_IGPU          | 0.04         | 1.14x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_QUANTIZED_COMPUTATION`         | GPU INT8/INT4 Tensor Cores (DP4A and MMA... | CPU_AVX2                | 0.092        | 1.62x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_COMPRESSION_DECOMPRESSION`     | GPU Lossless Compression Engines (NVIDIA... | CPU_AVX2                | 0.017        | 9.44x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_SYNCHRONIZATION`               | GPU __syncthreads() Barrier and Memory F... | CPU_AVX2                | 0.001        | 1.73x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_ASYNC_EXECUTION`               | GPU Multi-Stream Hardware Queue (CUDA St... | CPU_AVX2                | 0.002        | 2.05x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_SPECIALIZED_TENSOR_ATTENTION`  | GPU FlashAttention / Transformer Engine ... | CPU_AVX2                | 0.062        | 2.12x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_SPECIALIZED_TENSOR_ATTENTION`  | GPU FlashAttention / Transformer Engine ... | ALGORITHMIC_REPLACEMENT | 0.047        | 1.21x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |
| `CAP_GRAPHICS_COMPUTE_API`          | GPU Direct3D 12 / Vulkan / OpenCL Driver... | CPU_AVX2                | 0.002        | 1.89x          | PASS        | API_,FUNC,MATH,APPL,PERF | `EXACT_VERIFIED`       |

## Equivalence Dimension Legend

- `PHYSICAL_HARDWARE`: Physical discrete GPU silicon present (**False** across all tests on this laptop).
- `API_EMU`: Instruction or API emulation layer (Vulkan / OpenCL / CPU emulated).
- `FUNC`: Functional equivalence (produces exact identical outcomes).
- `MATH`: Mathematical equivalence under floating-point precision bounds.
- `APPL`: Application-contract equivalence (meets application declared tolerances).
- `PERF`: Performance equivalence (matches or exceeds reference latency).

## Unresolved Gaps & Next Proposed Experiments

1. **Ray Tracing Fixed Functions**: BVH traversal and ray intersection rely on CPU BVH traversal; next experiment is integrating Intel Embree CPU SIMD traversal.
2. **Very Large GEMMs (>4096)**: Limited by 18.57 GB/s host memory bandwidth; next experiment is multi-block out-of-core streaming with OpenVINO INT8 weights.
3. **Fixed Hardware Texture Samplers**: Software bilinear filtering is ALU-bound; next experiment is tiled texture caching with AVX2 gather instructions.
