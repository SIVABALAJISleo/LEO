# HYPER: CPU + Intel iGPU Heterogeneous Computational Fabric

## 1. Unified Hardware Target
HYPER targets the user's host hardware environment:
- **Host CPU**: 13th Gen Intel(R) Core(TM) i5-13420H
  - 8 physical cores: 4 Performance cores (P-cores) + 4 Efficient cores (E-cores)
  - 12 logical execution threads
  - 16 GB DDR5 System RAM (Measured Bandwidth: 39.77 GB/s)
  - AVX2, FMA3, and SSE4.2 SIMD vector extensions
- **Integrated GPU (iGPU)**: Intel(R) UHD Graphics
  - 48 Execution Units (EUs)
  - OpenVINO GPU plugin runtime
  - Shared physical memory architecture (zero PCIe transfer bus bottlenecks)

---

## 2. Dynamic Workload Partitioning
The heterogeneous scheduler continuously profiles kernel characteristics to determine optimal device placement:

```mermaid
graph TD
    Kernel[Incoming Kernel] --> Intensity{Arithmetic Intensity}
    Intensity -->|< 2.0 FLOPs/Byte| CPU[CPU AVX2 SIMD Core]
    Intensity -->|>= 2.0 FLOPs/Byte| Size{Workload Size}
    Size -->|< 256KB| CPU
    Size -->|>= 256KB| Hybrid[Concurrent CPU + iGPU Partition]
    Hybrid -->|Upper Rows| CPU_Worker[CPU Thread Pool]
    Hybrid -->|Lower Rows| iGPU_Worker[Intel UHD OpenVINO Queue]
```

---

## 3. Zero-Copy Memory via Unified Shared Memory (USM)
On discrete GPU systems, host-to-device transfers across PCIe saturate bandwidth and inject latency.
On Intel integrated systems, the CPU and iGPU share physical DRAM. HYPER leverages page-aligned zero-copy pointers, eliminating redundant duplicate buffers and achieving zero transfer overhead.
