# LEO/HYPER BENCHMARKING PROTOCOL

**Module Reference:** `hyper.benchmark.master_benchmark`  
**Output Target:** `HYPER_100_RESULTS.json`  
**Standard:** Phase 13 & 14 Ground-Truth Measurement Standard  

---

## 1. Non-Negotiable Benchmarking Rules

1. **Physical Timing Only**: All benchmark timings must use high-resolution system timers (`time.perf_counter_ns()`). The use of `time.time()` for micro-benchmarks is strictly prohibited.
2. **Warmup & Measurement Minimums**:
   - Minimum **10 warmup iterations** to prime instruction caches, CPU branch predictors, and runtime JITs.
   - Minimum **30 measured iterations** for fast kernels.
   - Minimum **10 measured iterations** for heavy end-to-end workloads.
3. **Statistical Reporting**: A single timing measurement is unacceptable. Benchmarks must report the full distribution:
   - `min`: Fastest observed latency
   - `median`: 50th percentile (primary comparison metric)
   - `mean`: Arithmetic average
   - `p95`: 95th percentile (tail latency)
   - `max`: Slowest observed latency
   - `std_dev`: Standard deviation
4. **Zero Fabrication**: Speedups, baseline times, error values, and parity scores must never be hardcoded or inferred from synthetic formulas.
5. **Separation of Concerns**:
   - Speedup is defined strictly as:
     $$\text{speedup} = \frac{\text{median}(T_{\text{baseline}})}{\text{median}(T_{\text{candidate}})}$$
   - Algorithmic operation reduction is defined separately as:
     $$\text{work\_eliminated\_pct} = (1 - \frac{W_{\text{candidate}}}{W_{\text{baseline}}}) \times 100$$
   - FLOP reductions or memory bandwidth reductions must NEVER be reported as "latency speedup".
6. **Device Synchronization**: GPU kernels (OpenVINO iGPU) must explicitly wait for completion via `infer_request.wait()` before stopping the timer.

---

## 2. Benchmark Execution Command

To execute the ground-truth benchmark suite locally:

```bash
python -m hyper.benchmark.master_benchmark
```

This runs all authenticated workloads, validates contracts, and writes the complete machine-readable record to `HYPER_100_RESULTS.json`.
