# HYPER / LEO Architecture Map & Codebase Inventory

## Executive Overview

HYPER / LEO is a reproducible, contract-directed, software-only computation-elimination and heterogeneous execution system designed for standard consumer hardware, specifically targeted to the **Lenovo IdeaPad Slim 3 15IAH8** (Intel Core i5-12450H, 8 cores / 12 threads, Intel UHD Graphics 48 EUs, 16 GB RAM, Windows 11).

This document serves as the authoritative inventory and architectural taxonomy of the codebase, explicitly delineating active production engines, verification infrastructure, heterogeneous routing layers, and historical experimental artifacts.

---

## 1. System Taxonomy & Module Classification

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       HYPER / LEO UNIFIED ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. CONTRACT-DIRECTED COMPUTATION ELIMINATION (hyper_cco/)                  │
│     ├── Exact Contract & Multi-Class Correctness Taxonomy                   │
│     ├── 8-Class Strict Evidence Provenance Taxonomy                         │
│     ├── 100% Full-Content SHA-256 Exact Cache Engine                        │
│     ├── Incremental State Diffing & Residual Low-Rank Updates               │
│     ├── Common Subexpression Elimination & Algebraic Canonicalization       │
│     ├── Structural & Value-Based Dynamic Sparsity Engine                   │
│     ├── Precision & Speculative Prediction Verification Engines             │
│     ├── Temporal Graphics Reprojection & Error-Bounded Tile Cache           │
│     ├── Heterogeneous Execution Cost Model & Cooperative Scheduler          │
│     ├── Cryptographic Audit Certificates, Freivalds & Verifiers             │
│     └── Total Scientific Parity Scorecard & Manifest Workloads              │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. COMPUTATIONAL WORMHOLE & ALGORITHM DISCOVERY (hyper_x/)                 │
│     ├── Information Boundary Compiler & 7-Class Necessity Analysis          │
│     ├── Computational Wormhole Search (CWS) Engine                          │
│     ├── E-Graph Equality Saturation & Rewriting Engine                      │
│     ├── Counterfactual Mutation Engine & Representation Synthesizer         │
│     ├── Multi-Dimensional Hardware Cost Vector Model                        │
│     ├── Hardware Fingerprint & Target Machine Qualification                 │
│     └── Blind Holdout & Scientific Falsification Battery                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. HETEROGENEOUS COMPUTATION & RUNTIME (universal_compute_router/, hyper100/) │
│     ├── OpenVINO Intel UHD Graphics Acceleration Runtime                    │
│     ├── Multi-Threaded CPU Kernels (AVX2 / FMA / VNNI)                      │
│     └── Hardware Capability & Topology Detection                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. BENCHMARK & REPRODUCIBILITY HARNESS                                      │
│     ├── bench_target_hyper.py (3-warmup, 30-repetition benchmark runner)     │
│     ├── Raw-Trial Ledger (perf_counter_ns, min, median, p95, p99, std)      │
│     └── Automated Verification & Falsification Test Batteries               │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. USER INTERFACE & MONITORING (ui_core/)                                  │
│     ├── React / Vite Real-Time Dashboard & Telemetry Visualizer             │
│     └── Multi-Engine Metric Aggregation Panels                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Module Catalog

### 2.1 Core Active Engines (`hyper_cco/`)

| File | Status | Description & Key Responsibilities |
| :--- | :--- | :--- |
| `hyper_cco/contract.py` | **Production** | Formal `ComputeContract` specification, 12-class `ExactnessClass` taxonomy, 8-class `EvidenceClass` taxonomy, strict normwise error bounds, shape/dtype validation, and anti-truncation checks. |
| `hyper_cco/exact_cache.py` | **Production** | 100% full-content SHA-256 cryptographic tensor hashing, model ID & contract binding, eviction policies, exact cache lookup/storage without subsampling. |
| `hyper_cco/incremental_engine.py` | **Production** | Incremental computation via state diffing, sparse mask tracking, and selective re-computation. |
| `hyper_cco/residual_engine.py` | **Production** | Residual low-rank updates ($A = A_0 + U V^T$) enabling rank-$k$ work reduction. |
| `hyper_cco/cse_engine.py` | **Production** | Directed acyclic graph (DAG) common subexpression elimination, operation memoization, and algebraic reuse. |
| `hyper_cco/algebraic_engine.py` | **Production** | Algebraic rewrites (associativity, distributivity, matrix chain reordering, transpose factorization). |
| `hyper_cco/low_rank_engine.py` | **Production** | Dynamic low-rank decomposition with flat-spectrum detection ($\sigma_{\text{decay}} \ge 0.6$ rejection to prevent accuracy loss). |
| `hyper_cco/sparsity_engine.py` | **Production** | Dynamic structural and value-based sparsity exploitation with 40% density threshold guard. |
| `hyper_cco/precision_engine.py` | **Production** | Mixed-precision downcasting (FP32 to FP16/INT8) with contract error tolerance verification. |
| `hyper_cco/prediction_speculation.py`| **Production** | Speculative draft generation and target model verification with strict prefix matching and zero synthetic delays. |
| `hyper_cco/temporal_graphics.py` | **Production** | Motion-vector temporal reprojection, tile residual rendering, and perceptual SSIM/PSNR verification. |
| `hyper_cco/scheduler.py` | **Production** | Cost-directed cooperative scheduler assigning subtasks between AVX2 CPU threads and Intel UHD Graphics. |
| `hyper_cco/optimizer.py` | **Production** | Unified CCO optimization pipeline combining all computation elimination techniques under contract bounds. |
| `hyper_cco/certificate.py` | **Production** | Cryptographically signed execution certificates (`OptimizationCertificate`) binding hardware provenance and verification status. |
| `hyper_cco/verifier.py` | **Production** | Multi-tier verification engine implementing deterministic, Freivalds randomized ($O(N^2)$), and full reference checks. |
| `hyper_cco/scorecard.py` | **Production** | Total Scientific Parity Scorecard assessing contract satisfaction, evidence class assignment, and target parity. |
| `hyper_cco/raw_ledger.py` | **Production** | High-precision raw trial ledger recording individual timestamped iterations, memory usage, and distribution statistics. |
| `hyper_cco/workloads/*.py` | **Production** | 6 manifest workload implementations (`GEMM_512x512`, `SPMV_CSR_10K`, `LLM_SPECULATIVE_32TOK`, `CBE_RENDER_720P`, `QSV_AV1_TRANSCODE_1080P`, `PDE_POISSON_ITERATIVE`). |

### 2.2 Algorithmic Search & Information Theory (`hyper_x/`)

| File | Status | Description & Key Responsibilities |
| :--- | :--- | :--- |
| `hyper_x/hardware/fingerprint.py` | **Production** | Immutable hardware detection, CPU/GPU profiling, and `HOST_MISMATCH` qualification against the target machine. |
| `hyper_x/info_boundary/compiler.py`| **Production** | Computational dependency graph generation and 7-class necessity classification (essential, redundant, invariant, etc.). |
| `hyper_x/cws/search.py` | **Production** | Computational Wormhole Search exploring algorithmic pathways to bypass redundant FLOPs. |
| `hyper_x/rewrite/egraph.py` | **Production** | Equality saturation via e-graphs for discovering globally optimal algebraic rewrites. |
| `hyper_x/counterfactual/engine.py` | **Production** | Counterfactual mutation generation (pruning, reordering, substitution) with differential verification. |
| `hyper_x/representations/synthesizer.py` | **Production** | Representation synthesizer transforming dense tensors into sparse CSR, low-rank SVD, or spectral domains. |
| `hyper_x/discovery/grammar.py` | **Production** | Algorithmic grammar defining valid program transformations and novelty categorization (`KNOWN`, `VARIANT`, `NOVEL`). |
| `hyper_x/cost_model/cost_vector.py`| **Production** | 8-dimensional hardware execution cost vector (ALU, memory bandwidth, cache pressure, dispatch overhead). |
| `hyper_x/falsification/engine.py` | **Production** | Hostile falsification battery generating extreme adversarial inputs, edge cases, and degenerate matrices. |
| `hyper_x/holdout/blind_eval.py` | **Production** | Sealed blind holdout evaluation preventing test-set contamination and shortcut heuristics. |
| `hyper_x/master_engine.py` | **Production** | Orchestration engine coordinating search, compilation, execution, and verification. |

### 2.3 Heterogeneous Runtime & System Routing

| Directory / Module | Status | Description |
| :--- | :--- | :--- |
| `universal_compute_router/` | **Production** | Heterogeneous dispatch router managing workload placement across Intel Core CPU and Intel UHD Graphics (OpenVINO / SYCL / DirectML). |
| `hyper100/` | **Active / Refactored** | Legacy core engines upgraded to eliminate subsampling shortcuts (full-content cryptographic caching). |
| `video/quicksync_pipeline.py` | **Active** | Intel QuickSync Video (QSV) hardware video pipeline probe and transcoding executor. |

### 2.4 User Interface & Telemetry (`ui_core/`)

| Directory | Status | Description |
| :--- | :--- | :--- |
| `ui_core/src/` | **Active** | React, TypeScript, and Vite-based interface providing real-time telemetry, audit visualizers, and benchmark charts. |
| `ui_core/src/v43/`, `v45/` | **Dashboard** | Specialized telemetry views (Singularity and Omega panels) displaying runtime throughput and energy efficiency. |

### 2.5 Historical & Experimental Artifacts

| Component | Status | Purpose & Notes |
| :--- | :--- | :--- |
| `hyper_core/` (early prototypes) | **Historical** | Initial exploratory compute graph implementations; superseded by `hyper_cco/` and `hyper_x/`. Kept for regression verification. |
| `*.bak` files | **Archive** | Backup copies preserved during architectural refactoring; excluded from active execution paths. |
| `ui_core/src/v31-v34/` | **Historical** | Incremental feature prototypes explored during earlier design sprints; preserved for reference. |

---

## 3. Strict Verification & Integrity Rules

1. **Evidence Separation**: All benchmark results executed on non-target hardware (e.g. Core i5-13420H) are unambiguously tagged `MEASURED_NON_TARGET`. Claims regarding target machine behavior require execution on the target hardware (`MEASURED_TARGET`) or explicit simulation boundaries.
2. **Zero Synthetic Delays**: No `time.sleep()`, simulated loops, or synthetic scaling factors exist in production benchmark paths.
3. **No Shortcut Caching**: Caches must hash 100% of tensor bytes using cryptographic algorithms (SHA-256); subsampling heuristics are strictly banned.
4. **Anti-Truncation Invariant**: Candidate outputs shorter than the baseline ground truth trigger an immediate `FAIL` during contract verification.
5. **Clean Fallback**: Any optimization failure, numerical violation, or runtime error falls back to standard BLAS/CPU reference execution without data corruption.
