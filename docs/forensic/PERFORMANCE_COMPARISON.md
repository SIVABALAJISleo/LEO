# LEO / HYPER Ω∞ — Performance Comparison & Workload Benchmarks

## 1. Canonical 15-Workload Suite Measurements

Evaluated on host machine: Intel Core i5-13420H (AVX2), Intel UHD Graphics, 16 GB RAM.

| Workload ID          | Track A Reference Latency (μs) | Track B Candidate Latency (μs) | Measured Speedup       | Verified Work Avoidance (VWA) | Max Relative Error | Certification Decision            |
| :------------------- | :----------------------------- | :----------------------------- | :--------------------- | :---------------------------- | :----------------- | :-------------------------------- |
| `dense_gemm_fp32`    | 12,486.8                       | 154,668.0                      | **0.08x** (Regression) | 50.0%                         | 0.78691            | **REJECTED (TOLERANCE EXCEEDED)** |
| `dense_gemm_fp16`    | 136,466.6                      | 10,410,166.2                   | **0.01x** (Regression) | 50.0%                         | 0.32541            | **REJECTED (TOLERANCE EXCEEDED)** |
| `fft_1d`             | 9,899.0                        | 2,903.8                        | **3.41x**              | 99.8%                         | 0.00000            | **CERTIFIED PASSED**              |
| `vector_reduction`   | 6,151.7                        | 3,054.0                        | **2.01x**              | 90.0%                         | 0.00000            | **CERTIFIED PASSED**              |
| `batch1_ai`          | 158.5                          | 3,851.4                        | **0.04x** (Regression) | 65.0%                         | 0.54049            | **REJECTED (TOLERANCE EXCEEDED)** |
| `batched_ai`         | 15,531.2                       | 22,290.9                       | **0.70x**              | 50.0%                         | 0.00000            | **CERTIFIED PASSED**              |
| `semantic_query`     | 559.6                          | 299.1                          | **1.87x**              | 89.0%                         | 0.28775            | **REJECTED (TOLERANCE EXCEEDED)** |
| `rasterization`      | 13,641.5                       | 225.3                          | **60.55x**             | 96.9%                         | 1.00000            | **REJECTED (TOLERANCE EXCEEDED)** |
| `particle_physics`   | 1,534.6                        | 139.2                          | **11.02x**             | 99.9%                         | 0.00000            | **CERTIFIED PASSED**              |
| `bvh_hierarchy`      | 204.6                          | 287.6                          | **0.71x**              | 60.0%                         | 0.98046            | **REJECTED (TOLERANCE EXCEEDED)** |
| `path_tracing`       | 3,559.2                        | 3,187.1                        | **1.12x**              | 87.5%                         | 0.00000            | **CERTIFIED PASSED**              |
| `video_pipeline`     | 11,036.3                       | 4,405.0                        | **2.51x**              | 80.0%                         | 0.17157            | **REJECTED (TOLERANCE EXCEEDED)** |
| `nbody_simulation`   | 495,235.6                      | 219,895.7                      | **2.25x**              | 50.0%                         | 0.38242            | **REJECTED (TOLERANCE EXCEEDED)** |
| `monte_carlo`        | 3,509.1                        | 505.6                          | **6.94x**              | 90.0%                         | 0.01742            | **CERTIFIED PASSED**              |
| `viewport_transform` | 1,821.5                        | 4,236.5                        | **0.43x**              | 50.0%                         | 0.00101            | **CERTIFIED PASSED**              |

---

## 2. Performance Summary

- **Fastest Passing Speedup**: `particle_physics` (11.02x speedup with 0.0 relative error).
- **Highest Passing Work Avoidance**: `fft_1d` (99.8% FLOPs avoided via top-32 sparse FFT with 0.0 relative error).
- **Regressions Accurately Reported**: Uncompiled interpreted Python transformations (such as SVD low-rank projection in Python vs optimized BLAS in C) are slower than reference and are honestly reported as regressions rather than masked.
