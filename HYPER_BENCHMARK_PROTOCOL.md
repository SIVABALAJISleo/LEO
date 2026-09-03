# HYPER: Benchmark Protocol & Evaluation Integrity

## 1. Dual-Scoreboard Architecture
To eliminate all ambiguity between exact hardware comparisons and application-level computational sufficiency, HYPER enforces two strictly isolated scoreboards:

### Scoreboard A: Exact Workload Parity
- Bit-exact mathematical reference computation.
- No algorithmic shortcuts, low-rank approximations, or precision drops permitted.
- Measures raw compute and memory throughput on the host CPU + iGPU.

### Scoreboard B: Contract-Aware Computational Sufficiency
- Permits contract-legal transformations (low-rank SVD, 2:4 sparsity, adaptive sampling, BitNet quantization).
- Every output independently verified against frozen contract bounds.
- Measures Verified Work Avoidance (VWA%), wall-clock speedup, and error tolerance compliance.

---

## 2. Measurement Methodology
1. **Deterministic Random Seeds**: Workload inputs are generated deterministically per workload ID.
2. **Warmup Cycles**: Two unmeasured warmup iterations are executed before timing begins to ensure JIT/CPU frequency stabilization.
3. **High-Precision Monotonic Timers**: All execution timings use `time.perf_counter()` with sub-microsecond resolution.
4. **Out-of-Distribution Blind Holdout**: Frozen holdout workloads (prime dimension GEMM, white noise FFT, ill-conditioned matrices) are evaluated without optimization tuning to prevent benchmark overfitting.
