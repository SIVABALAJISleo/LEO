# LEO CBE — Benchmark Protocol & Scientific Methodology

## 1. Experimental Setup & Host Platform

All benchmarks for the LEO Compute-Budget Elimination Engine (CBE) are conducted on consumer laptop hardware under standardized conditions:

- **Host Processor**: Intel Core i5-13420H (4 Performance Cores @ 4.6 GHz Max Turbo, 4 Efficient Cores @ 3.4 GHz, 12 Total Logical Processors).
- **Host GPU**: Intel UHD Graphics (48 Execution Units, Intel Xe-LP architecture, OpenVINO device identifier `GPU.0`).
- **Memory**: 16 GB DDR5 System Memory (Unified Shared Virtual Memory pool).
- **Operating System**: Microsoft Windows 11 Home (x86_64, Build 26100).
- **Runtime Libraries**:
  - Python 3.13.5
  - OpenVINO 2026.2.1
  - PyTorch 2.10.0+cpu
  - Microsoft DirectX 12, Intel Level Zero Loader (`ze_loader.dll`), OpenCL 3.0 (`OpenCL.dll`).

---

## 2. Benchmark Suites & Measurement Invariants

### 2.1 Suites
1. **`leo cbe inspect`**: Probes CPU, memory, iGPU EUs, USM support, and runtime status.
2. **`leo cbe validate`**: Executes structural correctness invariants, visual quality contracts, and adversarial stress tests (camera teleportation, strobe lighting, subpixel geometry).
3. **`leo cbe benchmark --suite full`**: Runs all 8 compute tiers across repeated warm iterations, reporting average latency, FPS, CER, SSIM, and PSNR.
4. **`leo cbe profile --frames N`**: Samples microsecond stage latency breakdown (state diff, prediction, temporal reprojection, residual classify, render, reconstruction, quality check).
5. **`leo cbe ablation`**: Quantifies the isolated contribution of each algorithmic subsystem (adaptive resolution, temporal reuse, CAS sharpening).

### 2.2 Measurement Rules
- **Wall-Clock High-Resolution Timers**: Timings must use Python's `time.perf_counter()` or OS high-resolution counters.
- **Warmup Iteration Required**: The first iteration compiles JIT shaders and OpenVINO OpenCL kernels. A mandatory warmup pass occurs before benchmark timing begins.
- **No Double Counting**: Net CER accounts for all computational steps:
  $$C_{\text{actual}} = C_{\text{render}} + C_{\text{prediction}} + C_{\text{reconstruction}} + C_{\text{control}}$$

---

## 3. Reproduction Instructions

To reproduce the exact published benchmark numbers on any Intel laptop:

```bash
# 1. Inspect hardware environment
python leo.py cbe inspect

# 2. Run automated validation and stress tests
python leo.py cbe validate

# 3. Execute the full 8-tier benchmark
python leo.py cbe benchmark --suite full --runs 3 --output cbe_benchmark_results.json

# 4. Profile stage-by-stage compute distribution
python leo.py cbe profile --frames 10

# 5. Run component ablation study
python leo.py cbe ablation
```
