# HARDWARE LIMITATIONS AND PLATFORM REALITIES

**Host Device:** Lenovo IdeaPad Slim 3 15IAH8  
**SoC:** Intel Core i5 (8 Cores, 12 Threads)  
**Graphics:** Intel integrated UHD Graphics (OpenVINO iGPU)  
**RAM:** 16 GB Shared System DDR4/DDR5  
**OS:** Microsoft Windows 11  

---

## 1. Physical Hardware Boundaries

### 1.1 Memory Architecture
- **Unified / Shared Memory Architecture**: System RAM (16 GB) is shared between the CPU and the Intel UHD integrated GPU.
- **Memory Bandwidth**: System memory provides approximately **40–60 GB/s** of bandwidth. In comparison, dedicated discrete GPUs (such as the NVIDIA RTX 4090 or RTX 5090) feature dedicated GDDR6X/GDDR7 VRAM delivering **1,000 to 1,792 GB/s** (a 25x–40x physical hardware bandwidth difference).
- **Zero-Copy Transfers**: The shared physical bus allows CPU and iGPU to access unified buffers via OpenVINO without PCIe serialization bottlenecks, but memory bandwidth contention remains when both devices access RAM concurrently.

### 1.2 Thermal & Power Dissipation Limits
- **Package TDP**: The Intel Core i5 SoC operates within a **45W** thermal envelope (pl2 boost up to ~95W for short bursts).
- **Flagship GPU Comparison**: Flagship desktop GPUs draw **450W to 600W** dedicated power. Sustained brute-force arithmetic density cannot bridge a 10x–13x physical energy gap without algorithmic work elimination.

### 1.3 Execution Unit Density
- **Intel UHD iGPU**: Features **48 Execution Units (EUs)**.
- **CUDA / Tensor Density**: Flagship discrete GPUs feature thousands of specialized FP16/INT8/FP8 Tensor Cores. On the Intel UHD iGPU, matrix multiplications are executed across general SIMD EUs via OpenVINO or Intel oneAPI.

---

## 2. Engineering Implications

1. **When iGPU Is Beneficial**: Large, regular, dense tensor operations (> 256K elements) where matrix compute intensity overcomes OpenVINO dispatch, shader compilation, and synchronization overhead.
2. **When CPU AVX2 Is Faster**: Small to medium matrices, irregular sparse graphs, tree traversals, hash table lookups, and branchy control flow, where CPU branch predictors and high single-core P-core clocks outperform iGPU dispatch latency.
3. **The Only Viable Strategy**: Eliminate unnecessary computation via caching, low-rank factorization, delta updates, and precision reduction before dispatching remaining necessary work to the host silicon.
