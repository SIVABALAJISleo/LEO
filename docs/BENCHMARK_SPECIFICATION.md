# HYPER / LEO Benchmark Specification & Reproduction Protocol

## 1. Frozen Benchmark Manifest Protocol
To ensure 100% scientific reproducibility and prevent benchmark gaming:
1. **Separation of Cold, Warm, and Cached**:
   - **Cold Start**: Measured on the very first invocation with unloaded caches and uncompiled kernels.
   - **Warm Steady-State**: Measured over repetitions 5 through 50 with steady-state thermal behavior.
   - **Exact Cache Hit**: Measured exclusively when inputs match exact cryptographic provenance.
   - **Invariant**: Cold, warm, and cached metrics must never be mixed or averaged together.

2. **Identical Workload Matching**:
   - Benchmarking against a reference requires using identical input tensors, token lengths, batch sizes, and model parameters.
   - A smaller model (e.g. 0.5B) must never be compared against a larger model (e.g. 70B) under the label of "same workload."

3. **Physical Hardware Telemetry**:
   - Every benchmark run captures host CPU frequency, memory RSS, package temperature, and CPU/iGPU utilization.

---

## 2. Benchmark Artifact Outputs
Every automated benchmark execution produces:
- `benchmark_manifest.json`: Machine-readable specification of all workloads, seeds, and hardware configurations.
- `int4_vs_fp32_benchmark.json`: Real measurements of quantized vs floating-point operations.
- `speculative_decoding_benchmark.json`: Measured parallel verification overhead ratios.
- `week1_baseline.json`: Measured time-to-first-token and throughput baseline.
