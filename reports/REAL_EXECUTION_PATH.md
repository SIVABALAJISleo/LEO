# The Real Execution Path of LEO / HYPER (Part 2)

**System**: LEO / HYPER — Omega Research Mode  
**Substrate**: Lenovo IdeaPad Slim 3 15IAH8 (Intel Core i5-12450H / i5-13420H + Intel UHD Graphics + 16 GB RAM)  
**Standard**: Omega Research Mode Part 2 (Concrete, traceable code execution)  

---

## 1. Concrete Execution Trace

Every optimization claiming production benefit is traceable through an unbroken call chain:

```
[1. User API Call]
    │  api.py / hyper.cli.py / MasterEngine.execute_workload_end_to_end()
    ▼
[2. Contract Construction & Fail-Closed Validation]
    │  hyper/contracts/contract.py :: Contract(...)
    │  hyper/contracts/contract.py :: validate_contract()
    ▼
[3. Multi-State Cryptographic Identity Cache]
    │  hyper/cache/exact_cache.py :: compute_cache_key(...)
    │  hyper/cache/exact_cache.py :: ExactCache.get(...)
    │  ├── HIT:  Return immediately; compute_latency = 0.0 ms; report lookup_latency.
    │  └── MISS: Proceed to Information Boundary & Necessary-Work analysis.
    ▼
[4. Information Boundary Analysis]
    │  hyper_x/information_boundary/compiler.py :: InformationBoundaryCompiler.analyze(...)
    │  Prunes unobservable dimensions (zero tokens, occluded tiles, empty spectral bins).
    ▼
[5. Necessary-Work Decomposition]
    │  hyper_x/necessary_work/compiler.py :: UniversalNecessaryWorkCompiler.analyze_gemm(...)
    │  Computes: W_original, W_necessary, W_eliminated, W_transformed, and CCR.
    ▼
[6. Candidate Optimization Selection]
    │  hyper/candidate.py :: CandidateResult
    │  ├── Exact Linear Delta:     hyper/incremental.py :: IncrementalExecutor
    │  ├── Overhead-Gated Sparse:  hyper/sparsity/sparsity_engine.py :: SparsityEngine
    │  ├── Randomized Low-Rank SVD: hyper/low_rank/low_rank_engine.py :: LowRankEngine
    │  ├── Precision Tiering:      hyper/precision/precision_engine.py :: PrecisionEngine
    │  └── Residual Correction:    hyper/residual/residual_engine.py :: ResidualEngine
    ▼
[7. Heterogeneous Backend Scheduling]
    │  hyper/scheduler/heterogeneous_scheduler.py :: HeterogeneousScheduler.select_backend()
    │  ├── Small tensors (<256):    CPU_AVX2 (Scalar / Vector C++ intrinsics, zero compile lag)
    │  ├── Intermediate (256-1024): CPU_MULTITHREADED (OpenMP / ThreadPool on 8 cores)
    │  ├── Large tensors (>1024):   OPENVINO_GPU (Intel UHD Graphics 48 EUs via OpenVINO opset13)
    │  └── Pipelined Co-Execution:  HYBRID_PIPELINED (Split tile processing across CPU + UHD)
    ▼
[8. Independent Mathematical Verification]
    │  hyper/verification/verifier.py :: VerificationEngine
    │  ├── Numerical Distance: verify_numerical() (max_abs, relative_error, RMSE, SHA-256)
    │  ├── Freivalds Probe:    verify_freivalds() (probabilistic O(N^2) check, bound 2^-k)
    │  └── Perceptual Metric:  verify_perceptual() (PSNR, SSIM)
    │  ├── PASS: Commit to output ledger & emit ExecutionCertificate.
    │  └── FAIL: Trigger immediate fallback to exact dense BLAS kernel (zero corrupted output).
    ▼
[9. Provenance Logging & Output Emission]
       evidence_ledger.json :: Append verified execution record with MEASURED provenance.
```

---

## 2. File-by-File Traceability Matrix

| Stage | Responsible Module | Concrete Functions Executed |
|---|---|---|
| **Contract** | `hyper/contracts/contract.py` | `validate_contract()`, `contract_to_json()` |
| **Cache** | `hyper/cache/exact_cache.py` | `compute_cache_key()`, `ExactCache.get()`, `ExactCache.put()` |
| **Boundary** | `hyper_x/information_boundary/compiler.py` | `analyze_matrix_workload()`, `compile_summary()` |
| **Work Decomposition** | `hyper_x/necessary_work/compiler.py` | `analyze_gemm()`, `WorkLedgerEntry()` |
| **Low-Rank** | `hyper/low_rank/low_rank_engine.py` | `factorize()`, `benchmark_and_execute()` |
| **Sparsity** | `hyper/sparsity/sparsity_engine.py` | `evaluate_sparsity()`, `execute_with_overhead_check()` |
| **Incremental** | `hyper/incremental.py` | `DeltaAnalyzer.analyze()`, `IncrementalExecutor.step()` |
| **Routing** | `hyper/scheduler/heterogeneous_scheduler.py` | `profile_backends()`, `select_backend()`, `dispatch()` |
| **Verification** | `hyper/verification/verifier.py` | `verify_numerical()`, `verify_freivalds()` |
| **Certification** | `hyper_x/certificates/certificate.py` | `ExecutionCertificate(...)`, `save_certificate()` |

---

## 3. Verified Execution Invariants

1. **No Phantom Code**: No optimization is credited in benchmarks unless it actively executed in the timed measurement loop.
2. **Fail-Closed Fallback**: If an algorithmic shortcut fails any verification threshold, the scheduler immediately executes the unoptimized reference implementation (`EXACT_FALLBACK`).
3. **Lookup Latency Separation**: Exact cache lookups report cache lookup latency ($<0.005\text{ ms}$) strictly isolated from execution compute latency.
