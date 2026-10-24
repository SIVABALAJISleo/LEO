# LEO / HYPER Platform — Current System Architecture

**Audit & Verification Date**: October 2026  
**Status**: Authoritative Architectural Baseline  
**Host Target**: Intel Core i5-13420H (4P + 4E cores, 12 threads), 16 GB DDR RAM, Intel(R) UHD Graphics (OpenVINO `GPU` device verified), Windows 11 Home.

---

## 1. High-Level Architectural Model

The platform integrates a multi-tier runtime architecture designed for provable correctness, verified pathway discovery, local AI inference, and transparent benchmark reporting:

```
┌────────────────────────────────────────────────────────────────────────┐
│               Unified Workload Request (API / CLI / Tests)              │
│       (Shapes, Dtypes, Operations, Precision, Equivalence Contract)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Canonical Pipeline Router                        │
│   Request ──> Input Validation ──> Workload Contract Enforcement       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          ▼                                                   ▼
┌───────────────────────────────────┐               ┌────────────────────┐
│      Safe Optimization Engine     │               │  Local AI Engine   │
│  - Symbolic Rewriting (Horner)    │               │  - llama.cpp GGUF  │
│  - Freivalds Probabilistic Check  │               │  - Qwen2.5-0.5B    │
│  - Cache Hierarchy Blocking (SIMD)│               │  - 4-8 Threads CPU │
│  - Memoization with Input Hashes  │               │  - Local Streamer  │
└─────────────────┬─────────────────┘               └─────────┬──────────┘
                  │                                           │
                  ▼                                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Backend Registry & Dispatch                    │
│   - CPU Baseline (OpenBLAS / NumPy AVX2)                               │
│   - Intel UHD iGPU (OpenVINO GPU Runtime: Compiled MatMul Graph)       │
│   - Heterogeneous Scheduler (Measured Concurrency & Fallback)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   Independent Verification Engine                      │
│   - Exact Bitwise / IEEE 754 Check                                     │
│   - Relative Error Tolerance Threshold (1e-4 / 1e-5)                   │
│   - Adversarial Falsification Gauntlet                                 │
│   - Unseen Holdout Validation                                          │
│   - Cryptographic Certificate Seal (SHA-256)                           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Unified Result & Provenance                       │
│   - Verdict: PASS / FAIL / UNKNOWN                                     │
│   - Provenance: MEASURED / DERIVED / CONFIGURED / SIMULATED            │
│   - Hardware: Intel Core i5-13420H / Intel UHD Graphics (No Fake 5090) │
│   - Memory: Measured RAM Overhead (tracemalloc / psutil)               │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Subsystems

### 2.1 Canonical Execution Runtime (`hyper/upe/runtime.py`)

- Central coordination pipeline that accepts typed `WorkloadRequest` instances.
- Mines or matches verified `WorkloadContract`.
- Dispatches through `UnseenPathwayPlanner` to locate verified algorithmic shortcuts (e.g. Horner's scheme, rank reduction, cache-tiled kernels).
- Invokes independent `FreivaldsVerifier` or `ExternalEquivalenceVerifier` before returning results.

### 2.2 Truthful Backend Registry (`hyper_x/heterogeneous_orchestrator.py`, `hyper/upe/execution.py`)

- Discovers physical devices at runtime via `openvino.Core()` and `numpy.__config__`.
- Identifies:
  - `CPU`: Intel Core i5-13420H with AVX2/FMA3 support.
  - `GPU`: Intel(R) UHD Graphics (48 EUs) via OpenVINO driver.
- Strictly guards against false backend reporting:
  - If GPU is unavailable, execution logs `CPU_ONLY_FALLBACK` and marks `is_real_gpu_executed = False`.
  - True copy overhead is measured and reported; host-mapped transfers are never labeled zero-copy.

### 2.3 Local AI Inference Subsystem (`backend/routers/inference_router.py`)

- Integrates `llama_cpp` engine loading `models/qwen2.5-0.5b-instruct-q4_k_m.gguf` (491 MB).
- Runs 100% locally with zero cloud dependencies, zero external network requests, and zero paid API keys.
- Measures and reports:
  - `load_time_ms`
  - `time_to_first_token_ms` (TTFT)
  - `generation_throughput_tokens_per_sec`
  - `total_latency_ms`
  - `memory_bytes`
  - `tokens_generated`

### 2.4 Verification & Fail-Closed Certification (`hyper_x/omega_runner.py`, `hyper_x/equivalence_verifier.py`)

- Generates `ExternalEquivalenceWorkCertificate` carrying SHA-256 digests of input, reference output, candidate output, and contract.
- Status gate rules:
  - Any failed primary check $\to$ `FAIL`.
  - Any failed adversarial or holdout check $\to$ `FAIL`.
  - Missing telemetry $\to$ `UNKNOWN`.
  - All mandatory checks pass $\to$ `VERIFIED`.

### 2.5 REST API & Frontend Observability (`backend/main.py`, `src/`)

- Exposes typed REST endpoints:
  - `/api/v1/upe/status`: Engine health and detected hardware.
  - `/api/v1/upe/contracts`: Registered workload contracts.
  - `/api/v1/upe/execute`: Canonical pipeline execution.
  - `/api/v1/inference/generate`: Local GGUF LLM inference with live token generation metrics.
  - `/api/v1/benchmarks/gemm`: Truthful GEMM benchmark execution.
