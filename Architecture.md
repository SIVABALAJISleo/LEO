# LEO/HYPER ARCHITECTURE SPECIFICATION

**Version:** 10.0.0 — Verified Computation-Elimination Runtime  
**Core Target:** Heterogeneous Intel Core i5 CPU + Intel UHD integrated GPU (OpenVINO)  

---

## 1. System Pipeline Architecture

```text
INPUT (Data, Model, Context)
  │
  ▼
[1. FORMAL CONTRACT SPECIFICATION] ──► Fails closed if inconsistent
  │
  ▼
[2. WORKLOAD & DEPENDENCY ANALYSIS] ──► DependencyGraph & Linearity Check
  │
  ▼
[3. EXACT CRYPTOGRAPHIC CACHE] ──────► Multi-State Key Hit? ──► [RETURN CACHED]
  │ (Cache Miss)
  ▼
[4. INCREMENTAL & DELTA CHECK] ──────► Linear Delta Δx? ──────► [REUSE INTERMEDIATES]
  │ (Non-linear / Full Input)
  ▼
[5. SPARSITY & LOW-RANK AUDIT] ──────► T_overhead + T_opt < T_dense?
  │                                       ├─ Yes ──► [EXECUTE REDUCED PATH]
  │                                       └─ No  ──► [FALLBACK TO DENSE]
  ▼
[6. MULTI-PRECISION & PREDICTION] ───► y = y_hat + r with Residual Correction
  │
  ▼
[7. HETEROGENEOUS SCHEDULER] ────────► Profiles CPU vs. Intel UHD iGPU (OpenVINO)
  │                                       └─ Dispatches to cheapest measured backend
  ▼
[8. MULTI-DOMAIN VERIFICATION] ──────► Exact / Freivalds / SSIM / Retrieval / LLM
  │
  ├─ PASS ────────────────────────────► Return verified result + Full Provenance Block
  └─ FAIL ────────────────────────────► Exact Fallback Execution (FAIL-CLOSED)
```

---

## 2. Core Optimization Subsystems

### 2.1 Formal Contract Engine (`hyper.contracts.contract`)
- Declares application tolerances: `exact_required`, `max_abs_error`, `max_relative_error`, `max_rmse`, `min_psnr`, `min_ssim`, `min_accuracy`, `min_recall`, `max_latency_ms`.
- Strict validation rejects contradictory configurations (e.g. `exact_required=True` with `allow_approximation=True`).

### 2.2 Multi-State Exact Cache (`hyper.cache.exact_cache`)
- Cryptographic hash over 9 execution dimensions: input data, model weights, hyper-parameters, precision mode, random seed, software version, hardware backend, contract version, and algorithm version.
- Independent hit/miss tracking and separate latency accounting. Never compares cache hit against uncached execution as a speedup.

### 2.3 Incremental & Delta Computation (`hyper.incremental`)
- Tracks DAG dependencies and node linearity.
- Reuses intermediates on linear delta paths: $A'B = AB + \Delta A B$.
- Fails closed to full recomputation on unproven or non-linear dependencies.

### 2.4 Overhead-Aware Sparsity Engine (`hyper.sparsity.sparsity_engine`)
- Measures thresholding time $T_{\text{thresh}}$, sparse execution $T_{\text{sparse}}$, and verification $T_{\text{verify}}$.
- Only selects sparse representation when $T_{\text{thresh}} + T_{\text{sparse}} + T_{\text{verify}} < T_{\text{dense}}$.

### 2.5 Low-Rank Break-Even Engine (`hyper.low_rank.low_rank_engine`)
- Randomized SVD ($A \approx U_k \Sigma_k V_k^T$).
- Calculates break-even reuse count: $N_{\text{break\_even}} = \lceil T_{\text{factor}} / (T_{\text{dense}} - T_{\text{lr}}) \rceil$.
- Rejects low-rank factorization for one-shot workloads unless total cost is lower.

### 2.6 Multi-Precision Engine (`hyper.precision.precision_engine`)
- Explicit support for: `float64`, `float32`, `float16`, `bfloat16`, `int8`, `int4`, and `ternary` (BitNet b1.58).
- Measures true numerical deviations relative to float64 ground truth.

### 2.7 Predictive & Residual Engine (`hyper.residual.residual_engine`)
- Implements: $y = \hat{y} + r$.
- Executes: Predict $\hat{y}$ $\to$ Estimate Error $\to$ If within contract, accept $\to$ Else compute residual $r$ $\to$ If verified, return $\hat{y} + r$ $\to$ Else exact fallback.

### 2.8 Heterogeneous Scheduler (`hyper.scheduler.heterogeneous_scheduler`)
- Dispatches across backends: `CPU_SCALAR`, `CPU_AVX2`, `CPU_MULTITHREADED`, `OPENVINO_CPU`, `OPENVINO_GPU`, `HYBRID_PIPELINED`.
- Measures physical time across all phases: $T_{\text{total}} = T_{\text{prepare}} + T_{\text{transfer}} + T_{\text{kernel}} + T_{\text{sync}} + T_{\text{verify}}$.
- Only routes to Intel UHD iGPU when measured $T_{\text{iGPU}} < T_{\text{CPU}}$.

### 2.9 Multi-Domain Verification Suite (`hyper.verification.verifier`)
- Exact numerical metrics: max absolute error, relative error, RMSE, output SHA-256.
- Matrix relation verification: Freivalds randomized probe ($A(Br) \stackrel{?}{=} Cr$) with bounded failure probability $2^{-k}$.
- Perceptual metrics: PSNR and SSIM.
- Retrieval metrics: Top-$k$ recall, precision, and MRR.
- LLM metrics: Exact token agreement and prefix matching.
