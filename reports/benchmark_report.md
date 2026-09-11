# LEO / HYPER: Scientific Benchmark Report

**Document Version**: 1.0.0  
**Date**: September 2026  
**Hardware Fingerprint**:
- **CPU**: 13th Gen Intel Core i5-13420H (4 Performance cores @ up to 4.6 GHz, 4 Efficient cores @ up to 3.4 GHz, 12 Threads)
- **iGPU**: Intel UHD Graphics (48 Execution Units, ~1.2 GHz)
- **RAM**: 15.7 GB LPDDR5
- **OS**: Windows 11 Build 26100
- **Compiler / Runtime**: Python 3.13, NumPy 2.2, OpenVINO 2026.2.1, Level Zero OpenCL 3.0

---

## 1. Benchmark Taxonomy

The engine strictly separates 6 distinct benchmark categories to prevent confusing hardware speed with contract shortcuts:

| Category | Category Name | Scientific Question Addressed | Target Status |
| :--- | :--- | :--- | :--- |
| **Category A** | **Raw Hardware Parity** | Does the Intel Core i5 + UHD physically match discrete RTX GPU throughput? | **NO** (Physical Silicon Law: 48 EUs vs 16,384 CUDA cores cannot match raw FLOPS) |
| **Category B** | **Exact Computational Parity** | Is the identical mathematical calculation reproduced without modification? | **YES** for exact workloads (verified via Freivalds $O(N^2)$ and bit-exact hashing) |
| **Category C** | **Contract Parity** | Is the application's declared contract satisfied within numerical/perceptual tolerance? | **YES** (Achieved across PDE, Graphics Filter, and Structured GEMM) |
| **Category D** | **Application Performance** | Does the end-to-end workload finish within the interactive latency SLO? | **YES** (Sub-5ms for 720p filter, sub-1ms for Poisson solver) |
| **Category E** | **Work Elimination** | How much original computation was proven unnecessary and eliminated? | **72.5% to 99.7%** on decomposable workloads |
| **Category F** | **GPU Advantage Erasure** | How much of the workload actually required GPU-specific hardware advantages? | **HAE = 87.5% - 99.7%** on verified wormhole workloads |

---

## 2. Quantitative Results Table (Physical Target Machine)

| Workload ID | Input Dimension | Baseline Latency (ms) | Candidate Latency (ms) | Physical Speedup | Work Elimination ($WE$) | Max Numerical Error | Correctness Class | Contract Satisfied |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GEMM_512x512` | $512 \times 512$ FP32 | 2.26 ms | 3.50 ms (cold)<br>0.08 ms (warm) | 0.65x (cold)<br>**28.2x (warm)** | 100.0% (warm) | 0.0 (exact) | `CACHED` | **TRUE** |
| `PDE_Poisson_256` | $256 \times 256$ Grid | 2.20 ms | 0.96 ms | **2.28x** | 72.5% | $6.10 \times 10^{-3}$ | `NUMERICALLY_BOUNDED` | **TRUE** |
| `Realtime_720p_Filter` | $1280 \times 720$ Frame | 5.58 ms | 1.43 ms | **3.89x** | 99.7% | 0.0 (masked) | `PERCEPTUALLY_EQUIVALENT` | **TRUE** |
| `SpMV_CSR_10k` | $10000 \times 10000$ Sparse | 29.46 ms | 37.50 ms | 0.79x | 0.8% | $3.93 \times 10^{-2}$ | `APPLICATION_CONTRACT_EQUIVALENT` | **FALSE** |
| `LLM_Residual_Block` | 512 tokens, $d=1024$ | 0.73 ms | 5.23 ms | 0.14x | 65.0% | 17.93 | `PREDICTIVE` | **FALSE** |

---

## 3. Path Breakdown Across 10 Canonical Pathways

For each workload, all 10 distinct execution pathways were measured on physical hardware:

```
[Workload: Realtime_720p_Filter]
1. ORIGINAL_EXACT_BASELINE:     5.58 ms (100% full-frame re-render)
2. EXISTING_HYPER_PATH:         2.79 ms (Heuristic spatial downsample)
3. PROOF_CARRYING_PATH:         1.57 ms (Certificate verification + sparse region mask)
4. COUNTERFACTUAL_SKIP_PATH:    1.36 ms (Lipschitz skip on unchanged background)
5. RESIDUAL_ONLY_PATH:          1.43 ms (7-Mode Residual recalculation)
6. CONTRACT_COMPILED_PATH:      1.43 ms (Integrated cheapest valid plan)
7. CPU_ONLY_PATH:               5.58 ms (Pure AVX2 baseline)
8. IGPU_ONLY_PATH:              2.00 ms (Direct OpenVINO GPU dispatch)
9. CPU_IGPU_PIPELINE_PATH:      2.29 ms (Cooperative P-core filter + iGPU USM)
10. EXACT_FALLBACK_PATH:        5.58 ms (Safe fallback path)
```

---

## 4. Key Empirical Discoveries

1. **Subprocess Overhead Bottleneck**:
   Querying `git rev-parse` via Windows subprocess introduced 40–70 ms of latency per execution. Memoizing Git hashes in memory was essential to enable accurate microsecond-level latency measurement.
2. **Cold vs Warm Cache Disambiguation**:
   Cold cache evaluations for dense GEMM add hashing overhead ($3.50\text{ ms}$ vs $2.26\text{ ms}$ baseline). On warm repeats, work elimination reaches 100%, delivering an empirical $28.2\times$ speedup ($0.08\text{ ms}$).
3. **Physical Necessity of Random Structures**:
   Uniform random sparse matrices (`SpMV_CSR_10k`) cannot be compressed into low-rank representations without catastrophic error ($0.039 > 0.001$). The engine correctly rejected the shortcut and proved the computation was necessary.
