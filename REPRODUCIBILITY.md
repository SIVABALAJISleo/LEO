# REPRODUCIBILITY GUIDE FOR LEO/HYPER

**Target Environment:** Local Python 3.10+ / 3.13 on Intel Core i5 + Windows 11  

---

## 1. Prerequisites and Setup

Ensure Python dependencies are installed:

```bash
pip install numpy scipy torch openvino onnx onnxruntime psutil pytest
```

---

## 2. Dynamic Hardware Verification

Verify host hardware without hardcoding:

```bash
python -m hyper.cli hardware-profile
```

Expected JSON output confirms:
- Detected CPU model and core count
- Total and available RAM
- Intel UHD Graphics GPU model
- OpenVINO available devices: `['CPU', 'GPU']`

---

## 3. Running the Verification Test Suite

Run all 18 formal verification test suites (43 test cases):

```bash
python -m pytest tests/test_contract_validation.py tests/test_cache_key_completeness.py tests/test_cache_invalidation.py tests/test_exact_equivalence.py tests/test_approximation_error_bounds.py tests/test_low_rank_break_even.py tests/test_sparse_thresholding.py tests/test_prediction_fallback.py tests/test_residual_correction.py tests/test_freivalds_verification.py tests/test_cpu_backend.py tests/test_openvino_cpu_backend.py tests/test_openvino_gpu_backend.py tests/test_hybrid_scheduler.py tests/test_provenance.py tests/test_benchmark_integrity.py tests/test_synthetic_result_rejection.py tests/test_hardware_identity.py -v
```

All 43 tests should report `PASSED`.

---

## 4. Running the Ground-Truth Benchmark Suite

Execute the physical benchmarks across CPU and Intel UHD iGPU:

```bash
python -m hyper.benchmark.master_benchmark
```

Inspect the generated ground-truth report:

```bash
type HYPER_100_RESULTS.json
```
