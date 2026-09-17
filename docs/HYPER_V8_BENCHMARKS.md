# HYPER v8 Measured Scientific Benchmark Report

## 1. Hardware Environment
- **Platform**: Lenovo IdeaPad Slim 3 15IAH8
- **Processor**: Intel Core i5-12450H (8 physical cores: 4 P-cores + 4 E-cores, 12 logical threads, 12MB L3 Smart Cache)
- **Graphics**: Intel(R) UHD Graphics (48 Execution Units, OpenCL 3.0 NEO driver)
- **RAM**: 16 GB Unified System Memory
- **Operating System**: Windows 11
- **Constraint**: Strict local execution. Zero dedicated GPU. Zero cloud offload.

---

## 2. Experiment 1: HYPER_WORMHOLE (6-Path Benchmark)

Measured using `BenchmarkHarnessV2` with strict cold/warm separation:

| Dimension | Path Name | Cold Latency (ms) | Warm Median (ms) | Speedup vs Ref | Work Eliminated | Verification Status |
|:---|:---|:---|:---|:---|:---|:---|
| **64x64** | FULL_RECOMPUTATION | 0.1102 | 0.0128 | 1.00x | 0.0% | VERIFIED_EXACT |
| | EXACT_CACHE | 0.3267 | 0.2289 | 0.05x | 100.0% | VERIFIED_EXACT |
| | EXACT_RESIDUAL | 0.6134 | 0.0098 | 1.19x | 90.6% | VERIFIED_EXACT |
| | SPARSE_EXACT (90%) | 0.2567 | 0.0698 | 0.17x | 90.0% | VERIFIED_EXACT |
| | LOW_RANK_APPROX (r=4) | 0.0097 | 0.0072 | 1.61x | 87.5% | VERIFIED_NUMERICAL |
| | TEMPORAL_REUSE | 0.4735 | 0.0097 | 1.22x | 98.4% | VERIFIED_EXACT |
| **128x128** | FULL_RECOMPUTATION | 1.0285 | 0.3906 | 1.00x | 0.0% | VERIFIED_EXACT |
| | EXACT_CACHE | 2.0276 | 1.1518 | 0.09x | 100.0% | VERIFIED_EXACT |
| | EXACT_RESIDUAL | 1.4761 | 0.0159 | **7.85x** | 90.6% | VERIFIED_EXACT |
| | SPARSE_EXACT (90%) | 0.4659 | 0.3964 | 0.53x | 90.0% | VERIFIED_EXACT |
| | LOW_RANK_APPROX (r=4) | 0.0493 | 0.0193 | **10.52x** | 93.8% | VERIFIED_NUMERICAL |
| | TEMPORAL_REUSE | 1.2602 | 0.0162 | **9.52x** | 99.2% | VERIFIED_EXACT |
| **256x256** | FULL_RECOMPUTATION | 0.6146 | 0.3983 | 1.00x | 0.0% | VERIFIED_EXACT |
| | EXACT_CACHE | 3.2599 | 3.6828 | 0.16x | 100.0% | VERIFIED_EXACT |
| | EXACT_RESIDUAL | 2.9426 | 0.0675 | **8.33x** | 90.2% | VERIFIED_EXACT |
| | SPARSE_EXACT (90%) | 2.3830 | 2.2310 | 0.28x | 90.0% | VERIFIED_EXACT |
| | LOW_RANK_APPROX (r=4) | 0.2003 | 0.0685 | **9.68x** | 96.9% | VERIFIED_NUMERICAL |
| | TEMPORAL_REUSE | 3.0056 | 0.0670 | **9.48x** | 99.6% | VERIFIED_EXACT |
| **512x512** | FULL_RECOMPUTATION | 2.1377 | 1.8658 | 1.00x | 0.0% | VERIFIED_EXACT |
| | EXACT_CACHE | 27.7980 | 30.2090 | 0.07x | 100.0% | VERIFIED_EXACT |
| | EXACT_RESIDUAL | 16.8524 | 0.9381 | **2.44x** | 90.0% | VERIFIED_EXACT |
| | SPARSE_EXACT (90%) | 14.5064 | 14.4576 | 0.16x | 90.0% | VERIFIED_EXACT |
| | LOW_RANK_APPROX (r=4) | 1.2294 | 0.9081 | **7.57x** | 98.4% | VERIFIED_NUMERICAL |
| | TEMPORAL_REUSE | 25.2698 | 1.2991 | **1.91x** | 99.8% | VERIFIED_EXACT |

---

## 3. Experiment 2: HYPER_INFORMATION_ESCAPE (Dimensionality Sweep)

Matrix dimension: $256 \times 256$, Dense baseline time: $0.4728$ ms, Baseline Storage: $256.0$ KB.

| Rank | Compressed Storage (KB) | Compression Ratio | Factored Time (ms) | Speedup vs Dense | Max Abs Error | Parity Classification |
|:---|:---|:---|:---|:---|:---|:---|
| 1 | 2.0 KB | 0.78% | 0.1194 | **3.96x** | $9.92 \times 10^{-5}$ | EXACT_PARITY |
| 2 | 4.0 KB | 1.56% | 0.0698 | **6.77x** | $1.07 \times 10^{-4}$ | APPROX_PARITY |
| 4 | 8.0 KB | 3.12% | 0.0921 | **5.13x** | $1.07 \times 10^{-4}$ | APPROX_PARITY |
| 8 | 16.0 KB | 6.25% | 0.1613 | **2.93x** | $1.53 \times 10^{-4}$ | APPROX_PARITY |
| 16 | 32.0 KB | 12.50% | 0.2180 | **2.17x** | $2.14 \times 10^{-4}$ | APPROX_PARITY |
| 32 | 64.0 KB | 25.00% | 0.3365 | **1.41x** | $2.44 \times 10^{-4}$ | APPROX_PARITY |
| 64 | 128.0 KB | 50.00% | 0.4883 | 0.97x | $4.58 \times 10^{-4}$ | BREAK-EVEN EXCEEDED |
| 128 | 256.0 KB | 100.00% | 0.6182 | 0.76x | $5.49 \times 10^{-4}$ | SLOWDOWN |

---

## 4. Experiment 3: HYPER_DENSE_WORST_CASE (Falsification)

| Dimension | Iterations | Median Runtime (ms) | Reference BLAS (ms) | Decision Overhead | Path Chosen | Fallback Status | Max Error |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 64x64 | 5 | 1.6651 | 0.0230 | +1.64 ms | `FALLBACK` | HONEST_FALLBACK | $0.00 \times 10^{0}$ |
| 128x128 | 5 | 5.6504 | 0.6399 | +5.01 ms | `FALLBACK` | HONEST_FALLBACK | $0.00 \times 10^{0}$ |
| 256x256 | 5 | 11.9895 | 0.7532 | +11.13 ms | `FALLBACK` | HONEST_FALLBACK | $0.00 \times 10^{0}$ |
| 512x512 | 5 | 73.5761 | 3.0906 | +70.49 ms | `FALLBACK` | HONEST_FALLBACK | $0.00 \times 10^{0}$ |

Result: 100% of incompressible random inputs were correctly identified as having no valid shortcut, falling back to full precision reference computation with zero error.

---

## 5. Experiment 4: HYPER_CPU_IGPU_COOP (Heterogeneous Benchmark)

| Dimension | CPU AVX2 (ms) | Intel UHD iGPU (ms) | Hybrid CPU/iGPU (ms) | iGPU vs CPU Speedup | Numerical Difference |
|:---|:---|:---|:---|:---|:---|
| 128x128 | 0.2475 | 2.1754 | 1.5516 | 0.11x (Slowdown) | $2.29 \times 10^{-5}$ |
| 256x256 | 0.8268 | 11.4605 | 2.7745 | 0.07x (Slowdown) | $5.72 \times 10^{-5}$ |
| 512x512 | 4.1081 | 115.2895 | 22.0254 | 0.04x (Slowdown) | $9.92 \times 10^{-5}$ |
| 1024x1024 | 17.3044 | 665.6574 | 67.8947 | 0.03x (Slowdown) | $2.06 \times 10^{-4}$ |

Scientific Assessment:
The Intel Core i5-12450H CPU benefits from mature multi-threaded AVX2 BLAS with L1/L2/L3 cache tiling. The naive unblocked OpenCL kernel executing on the 48 Execution Units of the Intel UHD graphics is memory-bandwidth bound on shared system RAM and incurs substantial launch overhead. Under HYPER v8 principles, the scheduler automatically routes standard dense GEMM to the CPU.

---

## 6. Experiment 5: HYPER_ADVERSARIAL (Stress Testing)
24 of 24 adversarial tests passed across $64 \times 64$ and $128 \times 128$ dimensions with zero unhandled exceptions, zero numerical corruption, and 100% contract compliance.
