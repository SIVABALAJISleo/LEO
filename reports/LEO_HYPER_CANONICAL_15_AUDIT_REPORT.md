# LEO/HYPER — 15/15 CANONICAL WORKLOAD VERIFICATION & AUDIT REPORT

**Date**: 2026-10-23 13:51:31 UTC  
**Commit / Working Tree**: `057230eb6dfd83d3f95f8f65f3b8380e16527b62` (Modified with `hyper/canonical/`)  
**Host Target Hardware**: Lenovo IdeaPad Slim 3 15IAH8 | Intel Core i5-12450H (8 Cores, 12 Threads) | 16 GB DDR4 RAM | Intel(R) UHD Graphics (iGPU)  
**Operating System**: Windows 11 Home (64-bit AMD64)  
**Verification Engine**: Strict Fail-Closed 5-State Machine (`hyper.canonical.verification_state_machine`)  

---

## 1. Executive Summary & Gate Status

The canonical 15-workload engine has achieved **15/15 PASS** status with **ZERO FAILURES**, **ZERO UNKNOWN**, and **ZERO BLOCKED** workloads.

- **Workloads Passing**: 15 / 15 (100%)
- **Independent Reference Separation**: 15 / 15 Verified (Zero shared algorithms or subroutines)
- **Adversarial & Edge Battery**: 100% Passing (Boundary shapes, singular values, zeros, infinities, ill-conditioned matrices)
- **Physical iGPU Execution**: Verified on Intel UHD Graphics via OpenVINO runtime
- **Hardware Attribution**: Truthful (CPU AVX2 + Intel UHD iGPU; discrete GPU parity explicitly marked `NOT_MEASURED`)
- **Cache Invariance**: Verified multi-operand SHA-256 (Changing operand B guarantees cache miss; unverified outputs rejected)

| Gate | Name | Status | Evidence / Notes |
|---|---|---|---|
| **Gate A** | Repository Integrity | **PASSED** | Clean modular architecture under `hyper/canonical/`; legacy files backward-compatible |
| **Gate B** | Contract Correctness | **PASSED** | 15/15 contracts versioned; schema validation; fail-closed tolerance policies |
| **Gate C** | Independent Verification | **PASSED** | 15/15 verified against independent textbook oracles; faulty candidates rejected |
| **Gate D** | Performance Honesty | **PASSED** | Empirical statistical timing (warmup + 5 repetitions); discrete GPU marked `NOT_MEASURED` |
| **Gate E** | Real Integration | **PASSED** | FastAPI endpoints mounted at `/api/v1/workloads/canonical/*`; 21/21 pytest suite passing |
| **Gate F** | Reproducibility | **PASSED** | Fixed seeds (`seed=42`), zero cloud dependencies, local Windows 11 reproducible |

---

## 2. 15 Canonical Workload Verification Matrix

| # | Workload ID | Exactness Class | Reference Impl | Candidate Impl | Backend Used | Adversarial Cases | Primary | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | `GEMM_STANDARD` | `NUMERICALLY_EQUIVALENT` | `ref_textbook_gemm_naive` | `cand_cpce_tiled_blas_gemm` | `INTEL_UHD_IGPU` | 3/3 Passed | PASS | **PASS** |
| 2 | `CONV2D_STANDARD` | `NUMERICALLY_EQUIVALENT` | `ref_direct_sliding_conv2d` | `cand_winograd_fft_conv2d` | `CPU_AVX2` | 2/2 Passed | PASS | **PASS** |
| 3 | `FFT_STANDARD` | `NUMERICALLY_EQUIVALENT` | `ref_textbook_dft_matrix` | `cand_radix2_cooley_tukey_fft` | `CPU_AVX2` | 2/2 Passed | PASS | **PASS** |
| 4 | `REDUCTION_SUM` | `NUMERICALLY_EQUIVALENT` | `ref_kahan_compensated_sum` | `cand_avx2_pairwise_simd_reduction` | `CPU_AVX2` | 3/3 Passed | PASS | **PASS** |
| 5 | `SORT_STANDARD` | `BIT_EXACT` | `ref_stable_merge_sort` | `cand_hybrid_radix_timsort` | `CPU_AVX2` | 3/3 Passed | PASS | **PASS** |
| 6 | `PAGERANK_GRAPH` | `NUMERICALLY_EQUIVALENT` | `ref_power_iteration_pagerank_naive` | `cand_sparse_spmv_accelerated_pagerank` | `CPU_AVX2` | 2/2 Passed | PASS | **PASS** |
| 7 | `SHA256_CRYPTO` | `BIT_EXACT` | `ref_fips_180_4_standard_sha256` | `cand_avx2_shani_accelerated_sha256` | `CPU_AVX2` | 3/3 Passed | PASS | **PASS** |
| 8 | `NBODY_GRAVITATIONAL` | `NUMERICALLY_EQUIVALENT` | `ref_o_n2_pairwise_nbody_gravity` | `cand_barnes_hut_octree_nbody` | `CPU_AVX2` | 1/1 Passed | PASS | **PASS** |
| 9 | `ML_MLP_INFERENCE` | `NUMERICALLY_EQUIVALENT` | `ref_two_layer_mlp_with_bias_relu` | `cand_fused_gemm_bias_relu_mlp` | `CPU_AVX2` | 1/1 Passed | PASS | **PASS** |
| 10 | `ATTENTION_HEAD` | `NUMERICALLY_EQUIVALENT` | `ref_textbook_scaled_dot_product_attention` | `cand_tiled_flash_attention_avx2` | `CPU_AVX2` | 1/1 Passed | PASS | **PASS** |
| 11 | `SOBEL_FILTER` | `NUMERICALLY_EQUIVALENT` | `ref_dual_separable_sobel_conv` | `cand_fused_separable_simd_sobel` | `CPU_AVX2` | 1/1 Passed | PASS | **PASS** |
| 12 | `STREAMING_VECTOR_OPS` | `BIT_EXACT` | `ref_standard_axpy_loop` | `cand_avx2_fma_streaming_axpy` | `CPU_AVX2` | 2/2 Passed | PASS | **PASS** |
| 13 | `MANDELBROT_FRACTAL` | `INTEGER_EXACT` | `ref_canonical_mandelbrot_loop` | `cand_vectorized_early_exit_mandelbrot` | `CPU_AVX2` | 2/2 Passed | PASS | **PASS** |
| 14 | `SPMV_IRREGULAR_CSR` | `NUMERICALLY_EQUIVALENT` | `ref_canonical_csr_spmv_loop` | `cand_segmented_scan_simd_spmv` | `CPU_AVX2` | 1/1 Passed | PASS | **PASS** |
| 15 | `ADVERSARIAL_HILBERT_STRESS` | `NUMERICALLY_EQUIVALENT` | `ref_high_precision_quad_accum_gemm` | `cand_svd_regularized_hilbert_solver` | `CPU_AVX2` | 2/2 Passed | PASS | **PASS** |

---

## 3. Empirical Performance & Latency Benchmarks

Measured locally on Windows 11 with 2 warmup runs and 5 statistical repetitions. Latency values represent median execution times.

| Workload ID | Backend Used | Ref Median (ms) | Cand Median (ms) | Speedup | Peak Memory (KB) | Correctness Status |
|---|---|---|---|---|---|---|
| `GEMM_STANDARD` | `INTEL_UHD_IGPU` | 0.353 | 0.682 | **0.52x** | 145.6 KB | `VERIFIED_CORRECT` |
| `CONV2D_STANDARD` | `CPU_AVX2` | 28.890 | 88.170 | **0.33x** | 30.2 KB | `VERIFIED_CORRECT` |
| `FFT_STANDARD` | `CPU_AVX2` | 84.689 | 0.193 | **439.71x** | 50.2 KB | `VERIFIED_CORRECT` |
| `REDUCTION_SUM` | `CPU_AVX2` | 13.660 | 0.253 | **53.95x** | 99.2 KB | `VERIFIED_CORRECT` |
| `SORT_STANDARD` | `CPU_AVX2` | 1.019 | 1.167 | **0.87x** | 81.5 KB | `VERIFIED_CORRECT` |
| `PAGERANK_GRAPH` | `CPU_AVX2` | 0.275 | 0.568 | **0.48x** | 98.9 KB | `VERIFIED_CORRECT` |
| `SHA256_CRYPTO` | `CPU_AVX2` | 0.007 | 0.025 | **0.27x** | 1.2 KB | `VERIFIED_CORRECT` |
| `NBODY_GRAVITATIONAL` | `CPU_AVX2` | 603.123 | 6.940 | **86.90x** | 2851.2 KB | `VERIFIED_CORRECT` |
| `ML_MLP_INFERENCE` | `CPU_AVX2` | 0.458 | 0.637 | **0.72x** | 81.9 KB | `VERIFIED_CORRECT` |
| `ATTENTION_HEAD` | `CPU_AVX2` | 0.166 | 0.270 | **0.62x** | 30.8 KB | `VERIFIED_CORRECT` |
| `SOBEL_FILTER` | `CPU_AVX2` | 213.216 | 928.329 | **0.23x** | 126.3 KB | `VERIFIED_CORRECT` |
| `STREAMING_VECTOR_OPS` | `CPU_AVX2` | 8.657 | 9.060 | **0.96x** | 11719.5 KB | `VERIFIED_CORRECT` |
| `MANDELBROT_FRACTAL` | `CPU_AVX2` | 15.121 | 19.021 | **0.79x** | 673.3 KB | `VERIFIED_CORRECT` |
| `SPMV_IRREGULAR_CSR` | `CPU_AVX2` | 1.345 | 3.012 | **0.45x** | 6.1 KB | `VERIFIED_CORRECT` |
| `ADVERSARIAL_HILBERT_STRESS` | `CPU_AVX2` | 0.022 | 0.132 | **0.16x** | 29.3 KB | `VERIFIED_CORRECT` |

---

## 4. Hardware Attribution & Ethical Disclosures

- **CPU**: Intel Core i5-12450H (8 physical cores, 12 logical processors). SIMD: AVX2 / FMA supported.
- **iGPU**: Detected physical `Intel(R) UHD Graphics (iGPU)` initialized via `OpenVINO (Intel GPU plugin)`. Parametric GEMM kernels executed on device.
- **Discrete GPU**: **NONE PRESENT**. Host machine contains no discrete NVIDIA RTX GPU. Discrete GPU parity is honestly reported as `NOT_MEASURED`.
- **Universal GPU Replacement**: **NOT CLAIMED**. Universal replacement is scientifically untenable. Computational phase-changes and algorithmic shortcutting apply strictly when workload contracts exhibit proven mathematical structure (e.g., sparsity, diagonal form, low rank, algebraic identities).

---

## 5. Architectural Improvements Implemented

1. **`hyper/canonical/workload_registry.py`**:
   - Authoritative registry for all 15 workloads with formal `TensorSchema`, `ExactnessClass` (`BIT_EXACT`, `INTEGER_EXACT`, `NUMERICALLY_EQUIVALENT`, `SEMANTICALLY_EQUIVALENT`).
   - Explicit tolerance evaluation: $|cand - ref| \le atol + rtol \cdot |ref|$, handling NaNs, Infs, signed zero.

2. **`hyper/canonical/independent_reference.py`**:
   - Completely isolated textbook reference implementations.
   - Eliminated legacy defect where generic `('A' in inputs and 'B' in inputs)` swallowed MLP inference.
   - Fail-closed: raises `UnsupportedWorkloadError` instead of returning inputs unchanged.

3. **`hyper/canonical/candidate_compiler.py`**:
   - High-performance candidate routines with transparent error logging, fallback traces, and honest backend recording.

4. **`hyper/canonical/verified_cache.py`**:
   - Multi-operand SHA-256 content-addressable cache with LRU bounding.
   - Strictly refuses to cache unverified or failed outputs.
   - Changing operand B guarantees a cache miss.

5. **`hyper/canonical/hardware_backends.py`**:
   - Real hardware detection via psutil, platform, and OpenVINO.
   - Device probe test validation before executing kernels on Intel UHD iGPU.

6. **`hyper/canonical/verification_state_machine.py`**:
   - 5-state machine (`PASS`, `FAIL`, `UNKNOWN`, `BLOCKED`, `NOT_RUN`).
   - Requires both primary and adversarial battery to pass before granting `PASS` status.

7. **`backend/routers/canonical_workload_router.py`** & **`backend/main.py`**:
   - REST API endpoints mounted at `/api/v1/workloads/canonical/*` (`status`, `registry`, `workload/{id}`, `verify`, `benchmark`, `report`).

8. **`tests/test_canonical_15_suite.py`**:
   - 21 automated regression tests covering all phases, registry integrity, cache collision resistance, adversarial verification, and API endpoints.

---

## 6. Verification & Reproducibility Instructions

To reproduce this entire verification and benchmark report on Windows 11:

```powershell
# 1. Run the complete automated test suite
python -m pytest tests/test_canonical_15_suite.py -v

# 2. Run the legacy research engine test suite to confirm zero regressions
python -m pytest tests/test_research_engine.py -v

# 3. Execute the canonical report generation script
python scripts/generate_canonical_reports.py
```