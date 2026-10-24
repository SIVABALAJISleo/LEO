# Adaptive CPU & Intel UHD iGPU Backend Execution

## 1. Physical Target Profile

- **Processor:** Intel Core i5-12450H / i5-13420H (4 Performance cores + 4 Efficient cores, 12 Threads)
- **Integrated Graphics:** Intel UHD Graphics (48 Execution Units, ~1.2 GHz)
- **Shared Memory:** 16 GB DDR RAM (Unified system and graphics memory)
- **Operating System:** Windows 11 64-bit

---

## 2. Backend Detection & Zero-Fabrication Invariant

The **Backend Capability Registry** (`hyper_universal/backends/registry.py`) probes live OS and runtime drivers:

- `CPU_AVX2`: Always available on the Intel Core i5 host. Utilizes AVX2, FMA3, and multicore OpenMP thread parallelism.
- `INTEL_UHD_IGPU_OPENCL`: Probed via PyOpenCL / Intel OpenCL runtime. If unavailable or drivers are absent, marked `is_available = False`.
- `INTEL_UHD_IGPU_VULKAN`: Probed via Vulkan Compute loader. If unavailable, marked `is_available = False`.
- `NVIDIA_CUDA`: Discovered as absent on the host. Under no circumstances is a CUDA or dedicated GPU backend simulated or fabricated.

---

## 3. Dynamic Scheduler & Safe CPU Fallback

The **Universal Scheduler** (`hyper_universal/scheduler/scheduler.py`):

1. Analyzes workload arithmetic intensity via Roofline Knee (~13.5 FLOPs/byte).
2. Computes host-to-device memory copy overhead. If transfer time exceeds estimated GPU compute savings, schedules on `CPU_AVX2`.
3. Wraps heterogeneous execution in `execute_with_fallback`. If an OpenCL / Vulkan runtime crash occurs, catches the exception cleanly and completes execution on `CPU_AVX2`.
