# OUT OF SCOPE: Explicit Boundaries and Physical Hardware Limits

**Project**: LEO / HYPER  
**Target Architecture**: Intel Core i5-12450H CPU, Intel UHD Integrated Graphics (48 EUs), 16 GB Unified System RAM, Windows 11  
**Declaration**: Software-Only Engine. No Dedicated GPU. No Hardware Upgrades. No Cloud Offloading.

---

## 1. Principles of Honest Engineering

A software system that claims to accelerate everything accelerates nothing.

HYPER's contract-driven optimization achieves parity **only** when a workload contains exploitable structure:
- **Redundancy** (memoization, caching)
- **Low-Rank Energy Concentration** (factorization, singular value decay)
- **Temporal Locality** (tile reprojection, delta computation)
- **Quantization Tolerance** (INT8/INT4 weight streaming, speculative verification)

When a workload lacks these properties—when it requires raw brute-force memory bandwidth, petascale matrix multiplication, or dedicated physical silicon accelerators—**HYPER cannot and does not achieve parity**.

Raw physical hardware parity against discrete GPUs (e.g. NVIDIA RTX 4090, H100) is **permanently claimed at 0.0%**.

Below is the authoritative list of workloads that are strictly **OUT OF SCOPE**.

---

## 2. Workload Classes Permanently Out of Scope

```
                    PHYSICAL HARDWARE SPECTRUM
┌─────────────────────────────────────────────────────────────┐
│  INTEL i5-12450H + UHD iGPU                                 │
│  • ~0.5 TFLOPS FP32                                         │
│  • ~30 GB/s DDR5 Shared Bandwidth                           │
│  • 16 GB Unified RAM                                        │
└──────────────────────────────┬──────────────────────────────┘
                               │   PHYSICAL GAP:
                               │   160x FLOPS, 33x Bandwidth
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  DISCRETE ACCELERATOR (RTX 4090 / H100)                     │
│  • 82.6 to 1000+ TFLOPS FP16/FP32                           │
│  • 1,008 to 3,350 GB/s Dedicated GDDR6X / HBM3 Bandwidth    │
│  • Dedicated Silicon: Tensor Cores, RT Cores, NVENC, NVLink │
└─────────────────────────────────────────────────────────────┘
```

---

### Class 1: Real-Time AAA 3D Gaming with Hardware Ray Tracing
*Examples: Cyberpunk 2077 (Ray Tracing Overdrive), Alan Wake 2, Unreal Engine 5 Lumen/Nanite at 4K Ultra 60+ FPS.*

- **Hardware Gap**:
  - Missing dedicated **Ray Tracing (RT) Cores** for hardware Bounding Volume Hierarchy (BVH) box/triangle intersection testing.
  - Missing **500–1000 GB/s dedicated GDDR6/GDDR7 VRAM bandwidth**. Intel UHD graphics shares ~30 GB/s system DDR5 with the CPU and operating system.
  - Missing physical **Tensor Cores** capable of running real-time neural optical flow frame generation (DLSS 3) at sub-millisecond latencies.
- **Why Software Cannot Substitute**:
  - BVH tree traversal for millions of dynamic primary, shadow, and reflection rays requires billions of non-linear pointer chases per frame. Software BVH traversal on CPU threads or integrated EU SIMD lanes saturates memory buses within 2–5 frames per second.
  - High-frequency dynamic geometry and procedural deformation invalidate temporal caching.

---

### Class 2: Frontier Foundation Model Training
*Examples: Pre-training or full fine-tuning of 7B, 13B, 70B, or 405B parameter models (e.g. LLaMA-3, DeepSeek, Mistral) in FP32, FP16, or BF16.*

- **Hardware Gap**:
  - Missing **multi-GPU high-speed interconnects** (NVLink 900 GB/s - 3.2 TB/s; NVSwitch fabrics; 800 Gbps InfiniBand).
  - Missing petascale dense matrix math units (e.g. 8x H100 SXM5 cluster delivering 16,000 TFLOPS FP8/FP16).
  - Missing high-bandwidth memory (HBM3) with multiple terabytes per second capacity.
- **Why Software Cannot Substitute**:
  - Distributed backpropagation requires continuous synchronization of dense gradient tensors across all layers.
  - Gradient accumulation cannot be memoized, factorized, or bypassed without fundamentally altering the stochastic gradient descent (SGD) trajectory and corrupting model convergence.
  - A training run that requires 100,000 GPU-hours on an H100 cluster would physically require centuries on a consumer 8-core CPU.

---

### Class 3: Multi-Stream 4K/8K 60fps Real-Time Video Transcoding
*Examples: Concurrent 4K HEVC / AV1 / ProRes broadcasting, multi-channel live streaming at 60 fps without hardware encoders.*

- **Hardware Gap**:
  - Missing dual or triple dedicated fixed-function video encoding ASICs (e.g. NVENC 8th Gen, Apple ProRes hardware engines).
- **Why Software Cannot Substitute**:
  - Entropy coding (CABAC), discrete cosine transforms (DCT), and motion search for 4K video at 60 fps require hundreds of billions of integer operations per second.
  - While Intel QuickSync provides basic fixed-function media capabilities for supported profiles, pure software encoding (`libx265` or `svt-av1` at high quality presets) operates at 5–12 fps on 8 CPU cores.

---

### Class 4: Fresh Unstructured Full-Rank Dense FP32 GEMM ($A \times B$)
*Examples: Cryptographic whitening, pseudo-random matrix multiplication, dense full-rank scientific Monte Carlo simulations without recurring matrices.*

- **Hardware Gap**:
  - Peak theoretical FP32 FLOPs on Intel Core i5-12450H is **~0.5 TFLOPS**. Peak FP32 on an RTX 4090 is **82.6 TFLOPS** ($165\times$ physical ratio).
  - DDR5 dual-channel system bandwidth is **~30 GB/s**. RTX 4090 memory bandwidth is **1,008 GB/s** ($33.6\times$ physical ratio).
- **Why Software Cannot Substitute**:
  - By the computational complexity of dense matrix multiplication, fresh dense matrices $A, B \in \mathbb{R}^{N \times N}$ without low-rank structure, sparsity, or reuse have a fixed arithmetic floor of $\Theta(N^3)$ operations and $\Theta(N^2)$ memory reads.
  - When every element is unique and non-recurring, no software compiler, cache hierarchy, or algorithm can overcome the physical memory bandwidth and ALU throughput limits of the silicon.

---

## 3. Summary Boundary Matrix

| Workload Domain | In Scope (Contract Parity) | Out of Scope (Hardware Parity) |
| :--- | :--- | :--- |
| **Large Language Models** | Streaming INT8/INT4 inference, speculative decoding with target verification, KV-cache compression. | Full FP32/FP16 70B+ pre-training, multi-GPU gradient backprop, zero-latency multi-token generation on unquantized weights. |
| **Information Retrieval & RAG** | Subspace clustering, semantic/exact caching, incremental vector retrieval for corpora $\le 10^7$ vectors. | Billion-scale brute-force linear search over unindexed high-entropy embeddings requiring terabytes of HBM. |
| **Scientific & Linear Algebra** | Low-rank factorized matrices, structured sparse matrices, PDE stencils with temporal reuse. | Fresh unstructured full-rank dense FP32 GEMM matching RTX 4090 FLOP rates. |
| **Computer Graphics & Vision** | Procedural tile reprojection, temporal frame reuse, perceptual equivalence ($\text{PSNR} \ge 40\text{ dB}$). | AAA real-time hardware ray tracing (DXR), 4K 144Hz path-traced rendering, real-time uncompressed 8K video encoding. |

---

## 4. Integrity Commitment

HYPER commits to the following standard:
1. **Never claim hardware parity**: When a benchmark compares against a dedicated GPU, it must explicitly state whether the comparison is **contract-level** (satisfying the application contract) or **raw hardware** (which remains 0.0%).
2. **Fail closed**: Any workload submitted to HYPER that falls into an out-of-scope class or fails contract thresholds must return `result.label = "EMULATED"` or `NOT_RUN` and fail the certification suite.
