# LEO / HYPER Platform — Baseline Test Results & Environment Audit

**Audit Date**: October 2026  
**Host Machine**: Lenovo IdeaPad Slim 3 15IAH8  
**CPU**: Intel Core i5-13420H (4 Performance cores, 4 Efficient cores, 12 logical processors)  
**Memory**: 15.7 GB Available System DDR RAM  
**Graphics**: Intel(R) UHD Graphics (48 Execution Units, OpenVINO `GPU` target verified)  
**Operating System**: Microsoft Windows 11 Home (Build 26100, AMD64)  
**Python Runtime**: 3.13.5 (`C:\Program Files\Python313\python.exe`)  
**Node.js / Frontend**: Node.js v22.12.0, Vite 5.4.19, React 18  

---

## 1. Test Suite Baseline Outcomes

Prior to applying Phase 1 repairs, baseline test executions were performed across the core suites:

### Suite 1: Unseen Pathway Engine (`tests/test_unseen_pathway_engine.py`)
- **Execution Command**: `python -m pytest tests/test_unseen_pathway_engine.py -k "test_upe_engine or test_api_upe"`
- **Collected Tests**: 5
- **Passed**: 5
- **Failed**: 0
- **Duration**: 32.76 seconds
- **Exit Code**: 0
- **Verification Details**:
  - `test_upe_engine_end_to_end_horner`: PASS (Polynomial evaluation via Horner pathway validated against Freivalds / relative tolerance).
  - `test_upe_engine_verified_cache_reuse`: PASS (Cryptographic content hash cache reuse verified).
  - `test_api_upe_status`: PASS (HTTP 200, status payload confirmed).
  - `test_api_upe_contracts_and_analyze`: PASS (Contract discovery & candidate search confirmed).
  - `test_api_upe_search_and_execute`: PASS (Full pathway discovery to verified result confirmed).

### Suite 2: Tony Stark Escape Engine Suite (`tests/test_tony_stark_escape_engine.py`)
- **Execution Command**: `python -m pytest tests/test_tony_stark_escape_engine.py`
- **Collected Tests**: 31
- **Passed**: 31
- **Failed**: 0
- **Duration**: 3.16 seconds
- **Exit Code**: 0

### Suite 3: Frontend Build & Unit Suite
- **Vite Production Build**: `npm run build`
  - Output: `dist/` bundle compiled in 2.62 seconds with zero errors.
- **Vitest Unit Suite**:
  - Tests: 20 passed / 20 total.
  - Duration: 1.84 seconds.

---

## 2. Environment & Dependency Audit

| Dependency | Required Version / Role | Installed Version | Status | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `python` | Baseline 3.12+ | 3.13.5 | PASS | Fully functional; C extensions built cleanly. |
| `numpy` | Array operations & BLAS | 2.2.3 | PASS | OpenBLAS multi-threaded AVX2 operational. |
| `openvino` | Intel CPU & iGPU execution | 2026.2.1 | PASS | Devices detected: `['CPU', 'GPU']`. Device name: `Intel(R) UHD Graphics (iGPU)`. |
| `torch` | PyTorch baseline | 2.10.0+cpu | PASS | CPU-only PyTorch verified. No CUDA required or pretended. |
| `llama-cpp-python` | Local quantized GGUF inference | 0.3.2 | PASS | C/C++ backend loaded; local model inferencing verified. |
| `fastapi` | Backend API server | 0.115.8 | PASS | Running on port 8005. |
| `uvicorn` | ASGI server | 0.34.0 | PASS | Standard async I/O worker. |
| `pydantic` | Data validation | 2.10.6 | PASS | Type safety and schema enforcement. |
| `pytest` | Test execution | 9.0.2 | PASS | Note: Config warning for unknown option `env` handled cleanly. |

---

## 3. Discovered Defects & Integrity Violations (Pre-Patch State)

1. **Simulated Reference Latency in GEMM Benchmark**:
   - `benchmarks/hyper_omega_001_gemm.py` line 114 passed `reference_latency_ms=0.15` as a simulated RTX 5090 timing. The candidate algorithm is `np.dot` with `np.ascontiguousarray` compared against `np.matmul`. This was not an empirical hardware run on an RTX 5090.
2. **Latent FLOP Deduction via Latency Ratio**:
   - `hyper_x/omega_runner.py` line 215 computed:
     `cand_ops = nominal_operations * (cand_lat / max(1e-4, measured_ref_lat))`
     `work_elim = max(0.0, 1.0 - (cand_ops / max(1e-4, nominal_operations)))`
     This violates fundamental physical and benchmark principles by deriving operation counts directly from execution time ratios.
3. **Simulated Memory & iGPU Telemetry**:
   - `candidate_memory_bytes` was set to `nominal_memory_bytes * 0.7` in `hyper_x/omega_runner.py` line 266 without measuring RAM.
   - `igpu_time_ms` was set to constant `0.0`.
4. **False Zero-Copy in OpenCL Memory Management**:
   - `hyper/extreme/opencl_uva.py` performed three `ctypes.memmove` operations into/out of pinned host pointers, but reported `copy_overhead_bytes: 0` and `is_zero_copy: True`.
5. **False Hybrid Execution in Orchestrator**:
   - `hyper_x/heterogeneous_orchestrator.py` fell back to CPU if GPU was unavailable, but still returned `execution_mode: "HETEROGENEOUS_CPU_IGPU_HYBRID"`.

All of these issues are systematically targeted and eliminated in Phase 1 (P0).
