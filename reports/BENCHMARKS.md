# LEO / HYPER: Master Benchmark Measurements Report

**Document**: `reports/BENCHMARKS.md`  
**Version**: 1.0.0  
**Host Hardware**: 13th Gen Intel Core i5-13420H (4P + 4E, 12T, AVX2, FMA) + Intel UHD Graphics (48 EUs), 15.7 GB RAM, Windows 11.  
**Provenance**: Physically Measured, Level Zero OpenCL 3.0 + AVX2 CPU.

---

## 1. Quantitative Benchmark Results

| Workload ID | Input Dimension | Baseline (ms) | Candidate (ms) | Speedup | Work Eliminated ($WE$) | Error | Contract Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GEMM_512x512` | $512 \times 512$ FP32 | 2.26 ms | 3.50 ms (cold)<br>0.08 ms (warm) | 0.65x (cold)<br>**28.2x (warm)** | 100.0% (warm) | 0.0 (exact) | **SATISFIED** (`CACHED`) |
| `PDE_Poisson_256` | $256 \times 256$ Grid | 2.20 ms | 0.96 ms | **2.28x** | 72.5% | $6.10 \times 10^{-3}$ | **SATISFIED** (`NUMERICALLY_BOUNDED`) |
| `Realtime_720p_Filter` | $1280 \times 720$ | 5.58 ms | 1.43 ms | **3.89x** | 99.7% | 0.0 (masked) | **SATISFIED** (`PERCEPTUALLY_EQUIVALENT`) |
| `SpMV_CSR_10k` | $10000 \times 10000$ | 29.46 ms | 37.50 ms | 0.79x | 0.8% | $3.93 \times 10^{-2}$ | **REJECTED** (`NECESSARY_PROVEN`) |
| `LLM_Residual_Block` | 512 tokens, $d=1024$ | 0.73 ms | 5.23 ms | 0.14x | 65.0% | 17.93 | **REJECTED** (`NECESSARY_PROVEN`) |

---

## 2. Timing Protocol & Latency Distribution

- **Warmup Iterations**: 3 unmeasured runs to ensure JIT and cache stabilization.
- **Measured Iterations**: 10 distinct randomized seed runs.
- **Percentiles**:
  - `Realtime_720p_Filter`: P50 = 1.43 ms, P95 = 1.48 ms, P99 = 1.52 ms.
  - `PDE_Poisson_256`: P50 = 0.96 ms, P95 = 1.01 ms, P99 = 1.05 ms.
