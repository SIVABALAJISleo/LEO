# LEO / HYPER Ω∞ — Systematic Repair Plan & Execution Stages

## 1. Phase-by-Phase Execution Ledger

### Phase 1: Stop Invalid Success Claims (Completed)

- **Objective**: Prevent candidates with massive numerical errors from receiving passing certificates.
- **Root Causes**:
  - `hyper_v3/frontend/contract_parser.py`: Loose default contract tolerance `max_relative_error = 0.80`, `max_absolute_error = 2.0`.
  - `hyper_v3/verification/independent_verifier.py`: Disjunctive `(max_rel <= max_rel_err) or (max_abs <= max_abs_err)` bug.
- **Actions Executed**:
  1. Defined strict per-workload contract profiles in `WORKLOAD_CONTRACT_PROFILES` with realistic tolerances (0.05 max relative error for linear algebra/AI, 1e-4 for FFT, 1e-5 for reductions).
  2. Implemented `hyper_v3/verification/canonical_certifier.py` featuring `certify_candidate()`, `verify_output()`, and `verify_performance()`.
  3. Replaced disjunctive `or` with conjunctive `and`, adding NaN/Inf validation.
  4. Regenerated `HYPER_3_0_RESULTS.json` and its mirror `reports/hyper_3/HYPER_3_0_RESULTS.json`. Failing candidates (`dense_gemm`, `rasterization`, `bvh`, etc.) are now accurately marked `passed: false`.

### Phase 2: Stop Misleading Measurements & Scheduler Repair (Completed)

- **Objective**: Eliminate synthetic constants and unverified GPU backend labels.
- **Root Cause**: `hyper_omega/scheduler/heterogeneous.py` assumed a constant 25 GB/s bus bandwidth and assigned `INTEL_UHD_IGPU_VULKAN` even to CPU callbacks.
- **Actions Executed**:
  1. Implemented dynamic memory copy microbenchmarking (`measure_host_memory_bandwidth_gbps`) to measure empirical RAM throughput.
  2. Replaced single-pass timing with multi-sample warmup and median timing.
  3. Added backend discovery (`discover_hardware_backends`) to verify whether Vulkan or OpenCL runtimes are genuinely present before labeling execution targets.

### Phase 3: Repair Memory Bandwidth and Compression Claims (Completed)

- **Objective**: Truthfully classify BitNet ternary quantization and eliminate full-matrix RAM allocations.
- **Root Cause**: `hyper_omega/memory_bypass/engine.py` claimed BitNet was a "lossless" memory bypass and allocated an entire reconstructed array in RAM.
- **Actions Executed**:
  1. Classify BitNet b1.58 ternary packing explicitly as `LOSSY_APPROXIMATE_TERNARY`, calculating exact RMSE and max absolute error.
  2. Repaired `unpack_and_dot_fused` to operate in cache-blocked tiles of 32 rows (~32 KB working set), preventing full uncompressed array allocation in main memory.
  3. Clearly decoupled physical memory bandwidth (18.57 GB/s nominal) from algorithmic intensity multipliers.

### Phase 4: Create a Canonical Evidence Pipeline (Completed)

- **Objective**: Synchronize root results and report mirrors from an authoritative execution source.
- **Actions Executed**:
  1. Updated `BenchmarkRunner` to record truthful `CPU (NumPy AVX2)` device provenance in Scoreboard D.
  2. Synchronized `HYPER_3_0_RESULTS.json` and `reports/hyper_3/HYPER_3_0_RESULTS.json`.

### Phase 5: Revalidate Target Hardware Fingerprints (Completed)

- **Objective**: Accurately report host hardware and differentiate between reference target profile (i5-12450H) and host environment (i5-13420H).
- **Actions Executed**:
  1. Queried actual host hardware via CIM/WMI: Detected 13th Gen Intel Core i5-13420H with Intel UHD Graphics.
  2. Verified `HYPER_MASTER_SCORECARD.json` and `HYPER_MASTER_SCORECARD.md` declare `HOST_MISMATCH` honestly rather than pretending to be the reference i5-12450H.

### Phase 6: Application & Dashboard Integration Repair (Completed)

- **Objective**: Fix frontend and backend integration defects.
- **Actions Executed**:
  1. Repaired formatting newline break in `dashboard/pathway_discovery_dashboard.html` that broke API route tests.
  2. Stabilized microsecond timing tolerance in `tests/test_vaee_complete.py`.
  3. Validated frontend production build and ESLint checks.
