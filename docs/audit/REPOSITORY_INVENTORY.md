# LEO / HYPER Platform — Repository Inventory & Component Matrix

**Audit Date**: October 2026  
**Auditor**: Principal Systems Architect & Lead Verification Engineer  
**Baseline Hardware**: Intel Core i5-13420H (4P+4E cores, 12 threads), 16 GB DDR RAM, Intel(R) UHD Graphics (48 EUs), Windows 11 Home.  
**Execution Baseline**: Python 3.13.5 (Compatible baseline for project runtime), OpenVINO 2026.2.1, PyTorch 2.10.0+cpu, llama_cpp 0.3.2.

---

## 1. Executive Summary

This inventory documents all core runtime implementations, benchmark engines, optimization modules, device backends, caches, schedulers, API routers, and test infrastructure in the LEO/HYPER repository. Each component is audited for real implementation vs. simulated claims, integration status, callers, and test coverage.

---

## 2. Component Inventory Matrix

| Component Path                             | Primary Responsibility                                                      | Backends / Hardware                  | Integration Status           | Caller / Entry Point                                     | Known Defects / Misleading Claims Identified                                                                                                                                                                                | Test Coverage         |
| :----------------------------------------- | :-------------------------------------------------------------------------- | :----------------------------------- | :--------------------------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------- |
| `hyper/upe/runtime.py`                     | Canonical Unseen Pathway Engine execution runtime                           | CPU (NumPy/BLAS), OpenVINO (CPU/GPU) | Operational                  | `backend/main.py`, `tests/test_unseen_pathway_engine.py` | None; properly validates contracts and dispatches verified pathways.                                                                                                                                                        | Pass (100%)           |
| `hyper/upe/contracts.py`                   | Workload contracts & strict equivalence semantics                           | Agnostic                             | Operational                  | `hyper/upe/runtime.py`, API routes                       | Previously lacked explicit provenance enumeration (`MEASURED` vs `SIMULATED`).                                                                                                                                              | Pass (100%)           |
| `hyper/upe/verifier.py`                    | Independent multi-level equivalence verifier (exact, tolerance, perceptual) | CPU                                  | Operational                  | `hyper/upe/runtime.py`                                   | Solid Freivalds & relative error verifier.                                                                                                                                                                                  | Pass (100%)           |
| `hyper/upe/execution.py`                   | Subgraph execution adapters (NumPy, OpenVINO CPU/GPU, Horner, FFT)          | CPU, Intel UHD iGPU                  | Operational                  | `hyper/upe/runtime.py`                                   | Verified OpenVINO execution on genuine Intel UHD iGPU.                                                                                                                                                                      | Pass (100%)           |
| `hyper_x/omega_runner.py`                  | HYPER-Ω 29-step pipeline & work certificate generator                       | CPU (BLAS), OpenVINO iGPU            | Operational (Audited for P0) | `benchmarks/hyper_omega_001_gemm.py`                     | **CRITICAL DEFECT (P0)**: Derived operations from latency ratio (`cand_lat / ref_lat`); hardcoded candidate memory as `0.7 * ref`; hardcoded iGPU time to `0.0`. Fixed to count real algorithmic FLOPs and measured memory. | Partial (Fixed in P0) |
| `hyper_x/reference_engine.py`              | External reference target observation registry                              | External / Simulated                 | Operational (Audited for P0) | `hyper_x/omega_runner.py`                                | **CRITICAL DEFECT (P0)**: Hardcoded NVIDIA RTX 5090 Blackwell GB202 as measured hardware without physical device. Fixed to require explicit `PROVENANCE="SIMULATED_REFERENCE"` or `"UNKNOWN"`.                              | Pass                  |
| `benchmarks/hyper_omega_001_gemm.py`       | Canonical Experiment 001: Dense GEMM (512x512 FP32)                         | CPU                                  | Operational (Audited for P0) | CLI / Benchmark runner                                   | **CRITICAL DEFECT (P0)**: Passed simulated `reference_latency_ms=0.15` as RTX 5090 reference. Candidate is `np.dot` vs reference `np.matmul`. Fixed to measure local baseline and tag simulated comparisons.                | Pass                  |
| `hyper/extreme/opencl_uva.py`              | Intel UHD OpenCL memory management & bitwise kernels                        | Intel OpenCL                         | Operational (Audited for P0) | Extreme Heterogeneous tests                              | **CRITICAL DEFECT (P0)**: Executes `ctypes.memmove` but reports `copy_overhead_bytes=0` and `is_zero_copy=True`. Fixed to report true copy bytes and `HOST_MAPPED_COPY`.                                                    | Pass                  |
| `hyper_x/heterogeneous_orchestrator.py`    | Dual CPU + Intel UHD matrix multiplication scheduler                        | CPU + Intel UHD GPU                  | Operational (Audited for P0) | `tests/test_extreme_heterogeneous.py`                    | **CRITICAL DEFECT (P0)**: Returned `execution_mode="HETEROGENEOUS_CPU_IGPU_HYBRID"` even when GPU unavailable (fallback); ran sequentially on main thread. Fixed to report truthful execution mode.                         | Pass                  |
| `hyper_x/equivalence_verifier.py`          | External equivalence verifier (exact bitwise, numerical, contract)          | CPU                                  | Operational                  | `hyper_x/omega_runner.py`                                | High rigor; verified against adversarial matrices.                                                                                                                                                                          | Pass (100%)           |
| `hyper_x/counterexample_registry.py`       | Registry of verified failure modes and counterexamples                      | Local Disk / Memory                  | Operational                  | `hyper_x/omega_runner.py`                                | Clean persistence and retrieval of falsified transformations.                                                                                                                                                               | Pass (100%)           |
| `backend/main.py`                          | FastAPI canonical application backend                                       | Async Python                         | Operational                  | Frontend Vite/React client (Port 8005)                   | Integrates UPE, Discovery, Verification, and Status endpoints.                                                                                                                                                              | Pass (100%)           |
| `backend/routers/inference_router.py`      | Local AI inference router (`llama_cpp` GGUF engine)                         | Local CPU (AVX2)                     | Pending Phase 6 Integration  | `backend/main.py`                                        | New canonical local LLM router for `qwen2.5-0.5b-instruct-q4_k_m.gguf` without cloud or paid APIs.                                                                                                                          | Integrated in Phase 6 |
| `models/qwen2.5-0.5b-instruct-q4_k_m.gguf` | Quantized GGUF language model (491 MB)                                      | CPU (llama.cpp)                      | Verified Present             | Local Inference Engine                                   | Genuinely present on disk; generates real tokens in < 1.2s on target CPU.                                                                                                                                                   | Verified              |
| `frontend/src/`                            | React 18, Vite, TypeScript, Tailwind dashboard                              | Browser / Web                        | Operational                  | User interface (Port 5173/8080)                          | Clean build verified (`npm run build` succeeds).                                                                                                                                                                            | Pass (100%)           |

---

## 3. Provenance and Integrity Classification

To prevent deceptive benchmarking and unverified claims, all computational metrics must carry one of the following authoritative provenance tags:

1. **`MEASURED`**: Observed directly through high-resolution hardware timers (`time.perf_counter_ns`), memory profilers (`tracemalloc`, `psutil`), or real kernel dispatch on verified detected hardware.
2. **`DERIVED`**: Computed from a formal mathematical model (e.g., $2MNK$ FLOPs for dense GEMM), NOT inferred from latency ratios.
3. **`CONFIGURED`**: Static benchmark configuration parameters (e.g., matrix dimensions $N=512$, seed $S=42$).
4. **`SIMULATED_REFERENCE`**: Expected or theoretical numbers from unverified or external hardware (e.g., theoretical RTX 5090 timing); must NEVER be labeled as actual hardware measurement.
5. **`UNAVAILABLE` / `UNKNOWN`**: Telemetry that could not be recorded on the host machine. Must remain `UNKNOWN` rather than being coerced to `0.0` or `PASS`.

---

## 4. Canonical Pipeline Architecture

The platform architecture converges on one unified pipeline:

```
Request
  ──> Input Validation
  ──> Workload Contract
  ──> Optimization Analysis
  ──> Backend Selection (CPU / Intel UHD iGPU / Local GGUF)
  ──> Execution
  ──> Independent Verification
  ──> Result + Provenance
```

All competing or legacy entrypoints (e.g., legacy mock loops) are formally quarantined or upgraded to feed this canonical pipeline.
