# HYPER Heterogeneous CPU + Intel UHD iGPU Fabric

## 1. Heterogeneous Silicon Topology

Target System: **Lenovo IdeaPad Slim 3 15IAH8**
- **CPU:** Intel Core i5-12450H (Alder Lake-H)
  - 4 Golden Cove Performance Cores (8 threads, AVX2, FMA3, 4.4 GHz max turbo)
  - 4 Gracemont Efficient Cores (4 threads, high energy-efficiency, 3.3 GHz max turbo)
- **iGPU:** Intel UHD Graphics Xe G4
  - 48 Execution Units (384 ALUs, FP32/FP16 SIMD, OpenVINO / DirectX 12)
- **Memory Architecture:** Unified System RAM (16 GB DDR4/DDR5 @ 51.2 GB/s bandwidth)
  - Zero-copy unified memory eliminates PCIe bus transfer penalties when mapped correctly.

---

## 2. Dynamic Partitioning & Scheduling Rules

1. **CPU P-Core Affinity**: Control-heavy branches, irregular trees (BVH, KD-Tree), recursive algorithms, low-latency speculative drafting, and register-tiled small-to-medium GEMM ($M, N \le 512$).
2. **CPU E-Core Affinity**: Background verification, asynchronous memory prefetching, telemetry logging, and compilation of candidate strategies.
3. **Intel UHD iGPU**: Wide parallel kernels, image/video post-processing, dense FP16 convolutions, and bulk streaming transforms where arithmetic intensity exceeds 10 FLOPs/byte.
4. **Dynamic Split Search**: For workloads exceeding $N=1024$, the fabric evaluates partitions:
   $$\{100\% \text{ CPU}, 80/20, 60/40, 50/50, 40/60, 20/80, 100\% \text{ iGPU}\}$$
   and commits the partition minimizing total execution latency.

---

## 3. Data Movement Elimination

- Direct zero-copy buffer sharing between CPU host pointers and OpenVINO USM (Unified Shared Memory) or DirectX shared handles.
- Avoid unnecessary device-to-host synchronizations via double-buffering and asynchronous pipeline stages.
