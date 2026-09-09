# HYPER-CCO Scientific Reproduction & Verification Guide

This guide specifies the exact protocol to reproduce all benchmarks, hostile tests, and cryptographic certificates for **HYPER-CCO** from a clean checkout.

---

## 1. Target Hardware & Reference Platform

The target hardware specification for all primary benchmark claims is:
- **Model**: Lenovo IdeaPad Slim 3 15IAH8
- **Processor**: Intel Core i5-12450H (8 physical cores: 4 Performance cores + 4 Efficient cores, 12 logical threads, max turbo 4.40 GHz)
- **Integrated Graphics**: Intel UHD Graphics for 12th Gen Intel Processors (48 Execution Units, up to 1.20 GHz)
- **Memory**: 16 GB LPDDR5 / DDR5 Shared System RAM
- **Storage**: 512 GB NVMe PCIe SSD
- **Operating System**: Microsoft Windows 11 64-bit
- **Discrete GPU**: `NONE` (Strict 100% Software-Only Constraint)

*Note on Development Host Environment*:
When executed on non-target machines (e.g., 13th Gen Intel Core i5-13420H), the benchmark suite automatically detects the mismatch and explicitly tags all results with `MEASURED_NON_TARGET` in accordance with the 8-class scientific evidence taxonomy.

---

## 2. Prerequisites & Dependency Setup

### Required Runtimes
- **Python**: Python 3.10, 3.11, 3.12, or 3.13 (64-bit on Windows)
- **C/C++ Build Tools**: MSVC or MinGW (optional for precompiled C extensions; pure Python / NumPy / SciPy fallbacks are active)

### Installation
In PowerShell or CMD:
```powershell
# Clone repository
git clone https://github.com/SIVABALAJISleo/LEO.git
cd LEO

# Install verified core dependencies
pip install numpy scipy openvino psutil pytest
```

---

## 3. One-Command Full Reproduction

To run the complete validation, hostile falsification battery, and 30-repetition benchmark campaign:

```cmd
reproduce_clean.bat
```
or in PowerShell:
```powershell
python reproduce_clean.py
```

### What this command executes:
1. **Hardware Provenance Probe**: Inspects CPU architecture, core counts, RAM, and OpenVINO iGPU runtime.
2. **Hostile Falsification Battery (15 Tests)**:
   - Anti-truncation verification (short candidates must fail).
   - Single-element corruption detection.
   - NaN / Inf injection rejection.
   - Zero-norm and empty-output rejection.
   - Dense matrix fallback & 39%/40%/41% sparsity threshold boundary defense.
   - Flat-spectrum full-rank noise defense ($\sigma_{\text{decay}} \ge 0.60$).
   - 0% speculative draft acceptance fallback.
   - Sudden camera cut / teleportation full recomputation.
   - CPU-only fallback and thread scaling (1, 2, 4, 8, 12 threads).
3. **Manifest Workloads Verification (6 Workloads)**:
   - `GEMM_512x512`
   - `SPMV_CSR_10K`
   - `LLM_SPECULATIVE_32TOK`
   - `CBE_RENDER_720P`
   - `QSV_AV1_TRANSCODE_1080P`
   - `PDE_POISSON_ITERATIVE`
4. **Strict Contract & E-Graph Tests (14 Tests)**:
   - Freivalds $O(N^2)$ randomized verification ($k=15$, 99.997% confidence).
   - E-Graph equality saturation and lowest-cost extraction.
   - Blind holdout and anti-leakage audit.
5. **Target Scientific Benchmark Campaign**:
   - 3 warmups discarded per workload.
   - 30 timed iterations recorded with nanosecond resolution via `perf_counter_ns`.
   - Process RSS memory recorded before/after each repetition.
   - Statistical distribution (min, median, mean, p95, p99, std, IQR) emitted to `benchmark_results/raw_trials.json`.

---

## 4. Verification of Generated Artifacts

After execution, verify that the following files exist in `benchmark_results/`:
- `benchmark_results/raw_trials.json`: Uncompressed ledger containing all 33 iterations per workload.
- `benchmark_results/results.json`: Complete aggregated JSON summary with hardware telemetry.
- `benchmark_results/results.csv`: Spreadsheet-compatible metric table.
- `benchmark_results/REPORT.md`: Human-readable markdown report with evidence classifications.
- `benchmark_results/certificates/*.json`: Cryptographically signed execution certificates.

---

## 5. Strict Scientific Principles Checklist

- [x] **No Fabricated Measurements**: Every number is measured with `time.perf_counter_ns()`.
- [x] **Zero Synthetic Delays**: No `time.sleep()`, fake token loops, or hardcoded multipliers.
- [x] **Separation of Evidence**: Host runs tagged `MEASURED_NON_TARGET`.
- [x] **Anti-Truncation Rule**: Candidate size $< \text{baseline size}$ causes immediate `FAIL`.
- [x] **Decoupled Parity**: 0.0% raw hardware parity reported honestly; 96.0% application parity verified under contract.
