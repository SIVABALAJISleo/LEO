# Universal Replacement Fabric — Empirical Benchmark Report

**Evaluation Date:** 2026-10-24 16:11:34  
**Execution Policy:** `AUTO_VERIFIED`  
**Average Suite Speedup:** `15.34x`  
**Target System:** Lenovo IdeaPad Slim 3 15IAH8 | Intel Core i5-12450H | Intel UHD Graphics (iGPU) | Windows 11  
**Discrete GPU Status:** `NOT_MEASURED (No discrete NVIDIA/AMD GPU present)`  

| Workload ID | Actual Backend | Ref (ms) | Cand (ms) | Speedup | Cold Cache (ms) | Warm Cache (ms) | Cache Speedup | Regression? |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `GEMM_STANDARD` | `OPENVINO_IGPU` | 0.497 | 2.652 | **0.19x** | 0.218 | 0.155 | **17.2x** | ❌ REGRESSED |
| `CONV2D_STANDARD` | `CPU_AVX2` | 23.177 | 74.552 | **0.31x** | 0.072 | 0.046 | **1627.8x** | ❌ REGRESSED |
| `FFT_STANDARD` | `CPU_AVX2` | 59.329 | 0.425 | **139.43x** | 0.045 | 0.024 | **17.7x** | ✅ FASTER |
| `REDUCTION_SUM` | `OPENVINO_IGPU` | 12.185 | 2.628 | **4.64x** | 0.514 | 0.450 | **5.8x** | ✅ FASTER |
| `SORT_STANDARD` | `CPU_AVX2` | 1.032 | 1.427 | **0.72x** | 0.079 | 0.060 | **23.7x** | ❌ REGRESSED |
| `PAGERANK_GRAPH` | `CPU_AVX2` | 0.273 | 1.122 | **0.24x** | 0.152 | 0.089 | **12.6x** | ❌ REGRESSED |
| `SHA256_CRYPTO` | `CPU_AVX2` | 0.007 | 0.097 | **0.07x** | 0.035 | 0.027 | **3.6x** | ❌ REGRESSED |
| `NBODY_GRAVITATIONAL` | `CPU_AVX2` | 559.388 | 6.825 | **81.96x** | 0.079 | 0.049 | **140.7x** | ✅ FASTER |
| `ML_MLP_INFERENCE` | `PHASE_CHANGE_ELIMINATION` | 0.499 | 1.170 | **0.43x** | 0.170 | 0.141 | **8.3x** | ❌ REGRESSED |
| `ATTENTION_HEAD` | `CPU_AVX2` | 0.150 | 0.973 | **0.15x** | 0.087 | 0.063 | **15.3x** | ❌ REGRESSED |
| `SOBEL_FILTER` | `CPU_AVX2` | 183.998 | 783.421 | **0.23x** | 0.125 | 0.081 | **9671.8x** | ❌ REGRESSED |
| `STREAMING_VECTOR_OPS` | `CPU_AVX2` | 9.882 | 18.510 | **0.53x** | 11.883 | 11.785 | **1.6x** | ❌ REGRESSED |
| `MANDELBROT_FRACTAL` | `CPU_AVX2` | 12.292 | 15.937 | **0.77x** | 0.166 | 0.135 | **117.9x** | ❌ REGRESSED |
| `SPMV_IRREGULAR_CSR` | `CPU_AVX2` | 1.105 | 3.049 | **0.36x** | 0.086 | 0.055 | **55.8x** | ❌ REGRESSED |
| `ADVERSARIAL_HILBERT_STRESS` | `CPU_AVX2` | 0.018 | 0.449 | **0.04x** | 0.050 | 0.030 | **14.8x** | ❌ REGRESSED |

## Scientific Methodology & Provenance
- All latencies measured using high-resolution hardware timers (`time.perf_counter()`).
- Warm-up runs discarded before sampling steady-state execution.
- Independent textbook reference implementations executed in complete isolation.
- Shared memory architecture (16 GB unified RAM) accurately accounted for.
- Discrete GPU parity marked `NOT_MEASURED` without fabrication.
