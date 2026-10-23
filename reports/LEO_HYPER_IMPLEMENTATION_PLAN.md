# LEO / HYPER — Master Implementation Plan (Phases 1 to 13)

**Objective**: Integrate the 15/15 Verified Workload Engine, Independent Correctness Verification, Computational Phase-Change Engine (CPCE), and Evidence-Driven CPU+iGPU Optimization into the real LEO/HYPER codebase.

---

## Architecture & Phase Roadmap

### Phase 1: Authoritative Canonical Workload Contract Registry
- **File**: `hyper/canonical/workload_registry.py`
- **Specification**:
  - Exactly 15 versioned canonical workload definitions (`v2.0-canonical`).
  - Standardized workload IDs:
    1. `GEMM_STANDARD` (Dense FP32 matrix multiplication)
    2. `CONV2D_STANDARD` (2D spatial convolution)
    3. `FFT_STANDARD` (1D Complex Discrete Fourier Transform)
    4. `REDUCTION_SUM` (High-throughput floating-point sum reduction)
    5. `SORT_STANDARD` (Array element sorting - BIT_EXACT)
    6. `PAGERANK_GRAPH` (Iterative power-method graph centrality)
    7. `SHA256_CRYPTO` (FIPS 180-4 SHA-256 cryptographic hash - BIT_EXACT)
    8. `NBODY_GRAVITATIONAL` (Direct $O(N^2)$ pairwise gravitational simulation step)
    9. `ML_MLP_INFERENCE` (Multi-layer perceptron forward inference $\text{ReLU}(X W_1 + b_1) W_2 + b_2$)
    10. `ATTENTION_HEAD` (Scaled dot-product attention $\text{Softmax}(Q K^T / \sqrt{d_k}) V$)
    11. `SOBEL_FILTER` (2D spatial gradient edge detection)
    12. `STREAMING_VECTOR_OPS` (Memory-bandwidth limited sequential AXPY $y_{out} = \alpha x + y$ - BIT_EXACT)
    13. `MANDELBROT_FRACTAL` (Compute-bound iterative divergence count - INTEGER_EXACT)
    14. `SPMV_IRREGULAR_CSR` (Compressed Sparse Row matrix-vector product)
    15. `ADVERSARIAL_HILBERT_STRESS` (Ill-conditioned Hilbert matrix product)
  - Explicit exactness policies: `BIT_EXACT`, `INTEGER_EXACT`, `NUMERICALLY_EQUIVALENT`, `SEMANTICALLY_EQUIVALENT`.
  - Mathematical comparison: $|cand - ref| \le atol + rtol \cdot |ref|$.
  - Strict input/output schema validation.

### Phase 2: Independent Reference Engine
- **File**: `hyper/canonical/independent_reference.py`
- **Specification**:
  - 100% standalone, isolated textbook reference algorithms.
  - No shared subroutines, nodes, or cache with candidates.
  - Explicit typed dictionary dispatch mapping each `workload_id` directly to its handler.
  - Real mathematical implementations:
    - `ML_MLP_INFERENCE`: $\text{ReLU}(X W_1 + b_1) W_2 + b_2$
    - `STREAMING_VECTOR_OPS`: $y_{out} = \alpha x + y$
    - `REDUCTION_SUM`: high-precision compensated accumulation
  - Fail-closed: raises `UnsupportedWorkloadError` on unknown workloads.

### Phase 3: Candidate Compiler and Dispatch Engine
- **File**: `hyper/canonical/candidate_compiler.py`
- **Specification**:
  - Independent candidate implementations optimized for Intel CPU AVX2 and iGPU.
  - Pre-execution input validation.
  - Structured execution evidence record returning selected algorithm, backend, and timing.
  - Transparent fallback to CPU if an accelerator or rewrite is unsupported.

### Phase 4: Computational Phase-Change Engine (CPCE) Integration
- **Integration**: Connect `hyper_x/cpce` rewrite rules and canonical IR to the 15 workloads.
- Verified shortcuts when preconditions hold (identity matrix, zero matrix, sparse CSR, Horner polynomial form).

### Phase 5: Correctness-Preserving Cache
- **File**: `hyper/canonical/verified_cache.py`
- **Specification**:
  - Content-addressable cache using SHA-256 digests over ALL input operands ($A$, $B$, biases, alphas, etc.).
  - Cache key incorporates workload ID, contract version, precision, and backend settings.
  - Bounded memory with LRU eviction and collision handling.

### Phase 6: Truthful CPU & Intel UHD iGPU Execution Backends
- **File**: `hyper/canonical/hardware_backends.py`
- **Specification**:
  - Detect Intel Core i5-12450H and Intel UHD Graphics GT1.
  - Execute genuine OpenCL / vectorized CPU kernels.
  - Distinguish measured execution from fallback; record memory copy costs.

### Phase 7 & 8: Adversarial Verification & Strict State Machine
- **File**: `hyper/canonical/verification_state_machine.py`
- **Specification**:
  - Adversarial gauntlet: zero matrices, identities, prime dimensions, ill-conditioned matrices, NaNs/Infs, non-contiguous arrays.
  - 5-state machine: `PASS`, `FAIL`, `UNKNOWN`, `BLOCKED`, `NOT_RUN`.
  - Aggregation rule: 15/15 is permitted ONLY if all 15 workloads achieve verified `PASS`.

### Phase 9: Honest Performance Benchmarking Harness
- **File**: `hyper/canonical/benchmark_harness.py`
- **Specification**:
  - Multi-run statistical protocol (warmup runs, measured iterations, median, stddev, memory measurement).
  - Separate correctness tracking from latency.

### Phase 10 & 11: Real Application Integration & API Endpoints
- **Files**:
  - `backend/routers/canonical_workload_router.py`
  - Integration into `backend/main.py`
- **Specification**:
  - Expose `/api/v1/workloads/canonical/registry`
  - Expose `/api/v1/workloads/canonical/verify`
  - Expose `/api/v1/workloads/canonical/benchmark`
  - Expose `/api/v1/workloads/canonical/report`

### Phase 12 & 13: Test Suite & Comprehensive Reports
- **Files**:
  - `tests/test_canonical_15_suite.py`
  - `reports/LEO_HYPER_CANONICAL_15_VERIFICATION_REPORT.json`
  - `reports/LEO_HYPER_CANONICAL_15_AUDIT_REPORT.md`
