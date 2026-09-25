# Current Architecture Map: LEO / HYPER Codebase

**Date of Audit**: September 25, 2026  
**Auditor**: Principal Research & Systems Architecture Engineer  
**Workspace**: `c:\Users\sivab\OneDrive\Documents\HYPER`  
**Host Target**: Intel(R) Core(TM) i5-13420H (8 physical cores / 12 logical threads), 16 GB RAM, Intel(R) UHD Graphics (Driver 32.0.101.7076, OpenVINO 2026.2.1 `['CPU', 'GPU']`), Windows 11.

---

## 1. Executive Summary & Codebase Structure

The LEO/HYPER codebase is a multi-generational numerical optimization, execution routing, and algorithm discovery research platform. It integrates Python backends, high-performance CPU execution routines, iGPU hardware acceleration (OpenVINO, DirectML, GNA, Level-Zero/OneDNN), REST/FastAPI backends, CLI tools, and a React + Vite + TanStack frontend dashboard.

### Core Directory Breakdown
| Directory | File Count | Purpose & Existing Capabilities |
| :--- | :--- | :--- |
| `hyper/` | 376 | Core algorithms, hardware profiling, ablation engines, adversarial suites, Kimi K3 brain, algorithm reformulation. |
| `hyper_x/` | 348 | Algorithmic escape search, contract miner, e-graph rewrite engine, heterogeneous orchestrator, independent verifiers, falsification loops. |
| `hyper_omega/` | 39 | Multi-agent reasoning (Breakthrough agent, Falsification agent, Duel protocol), counterexample database, escape engine. |
| `hyper_cco/` | 44 | Computational Contract Optimization: algebraic engine, application parity engine, cheapest valid path, CSE engine, incremental engine, coverage engine. |
| `hyper_universal/` | 23 | Adaptive orchestrator, claim gate, necessary work analyzer, reference provenance, verification fortress. |
| `hyper_runtime/` | 133 | Adaptive precision, Albert weight sharing, GaLore/BitNet, GNA neural accelerator, iGPU orchestrator, LUT oneDNN inference, sparse attention. |
| `backend/` | 563 | FastAPI application (`backend/main.py`, `backend/server.py`), analytics (avoidance tracker, cache analytics, cost monitor, telemetry), answers cache, auth, routing. |
| `contracts/` | 4 | Formal contract IR (`contract_ir.py`), error budgeting (`error_budget.py`), perceptual saturation curves (`perceptual_saturation.py`). |
| `universal_compute_router/` | 9 | Universal Compute Router (UCR): adaptive dispatch, hardware detection, Intel optimal execution, meta compiler, router logic. |
| `algorithm_discovery/` | 4 | Complexity transformer, evolutionary loops, candidate generator. |
| `execution/` | 7 | Execution governor, GPU hijack/interceptors, reasoning loops, swarm grid. |
| `optimization/` | 1 | LEO Alchemy numerical acceleration engine (`leo_alchemy.py`). |
| `predictors/` | 3 | Predictive reality, state engine, Markov/temporal state estimation. |
| `cache/` | 2 | Universal multi-level cache hub (`cache_hub.py`). |
| `benchmarks/` | 39 | Benchmark suites (matrix, attention, speculative LLM, graphics, int4 vs fp32, holdout audits). |
| `tests/` | 229 | Unit, integration, chaos, and adversarial test suites (`test_api.py`, `test_adaptive_execution.py`, `test_anti_cheat_provenance.py`, etc.). |
| `src/` | 141 | React/Vite/TanStack frontend: diagnostic dashboards, benchmark runners, comparison views, system monitors. |
| `cli/` | 1 | Command-line interface (`hyper_cli.py`). |
| `spectral/` | 5 | Sparse FFT (`sfft.py`), compressed sensing FFT, linear attention, signal routing. |
| `physics/` | 4 | Barnes-Hut n-body solver (`barnes_hut.py`), Fast Multipole Method (`fmm_solver.py`), causal simulation. |
| `render/` | 6 | Software raytracing, FSR upscaling, OIDN denoising, multi-fidelity renderer. |
| `rag/` | 7 | Local RAG vector indexing, embedding, query routing, retrieval. |
| `.github/workflows/` | 5 | CI/CD automation: `ci-cd.yml`, `ci.yml`, `codeql.yml`, `security.yml`, Dependabot. |

---

## 2. Inventory of Subsystems by Master Prompt Category

### A. Optimization Engines
1. **`hyper_cco/` (Computational Contract Optimization)**:
   - `algebraic_engine.py`: Symbolic and numeric algebraic restructuring.
   - `cse_engine.py`: Common Subexpression Elimination across computational DAGs.
   - `incremental_engine.py`: Memoization, delta computation, and temporal state differential calculation.
   - `cheapest_valid_path.py`: Dynamic programming search for lowest-cost execution graph satisfying contract constraints.
2. **`hyper_x/egraph_engine.py`**: E-graph based equality saturation for rewrite rules.
3. **`optimization/leo_alchemy.py`**: Hybrid kernel fusion, SIMD-aligned vectorization, and cache-line blocking.
4. **`hyper_runtime/sparse_attention.py` & `adaptive_precision.py`**: Dynamic precision switching (FP32 -> FP16 -> INT8/Ternary) and block-sparse attention masks.

### B. Algorithm Discovery Systems
1. **`algorithm_discovery/`**:
   - `complexity_transformer.py`: Asymptotic complexity reduction transformations (e.g., $O(N^3) \to O(N^{\log_2 7})$ or FFT-based convolutions).
   - `evolutionary_loop.py`: Genetic mutation and crossover of computational pathways.
   - `generator.py`: Generates candidate algorithmic variants.
2. **`hyper_omega/algorithm_discovery/`**:
   - `engine.py`: AlphaDev-style discovery of micro-architectural instruction schedules.
   - `strategies.py`: Mathematical identity substitutions (Strassen, Winograd, Karatsuba, PRT spherical harmonics).
3. **`hyper_x/algorithmic_escape_search.py`**: Search for alternative formulations that bypass compute bottlenecks.

### C. Universal Compute Routers (UCR)
1. **`universal_compute_router/`**:
   - `orchestrator.py`: Central dispatch coordinating CPU, iGPU, and fallback execution.
   - `adaptive_dispatch.py`: Real-time dispatch choosing backend based on input size, memory locality, and device queues.
   - `hw_detector.py`: Detects Intel CPU features (AVX2, AVX-512, AMX, VNNI) and iGPU capabilities.
   - `router_logic.py`: Heuristic and cost-based routing rules.

### D. Benchmark Workers & Harnesses
1. **`benchmarks/`**:
   - `cel_experiment_1_matrix.py`: Matrix multiplication benchmark harness.
   - `cel_experiment_2_speculative_llm.py`: Speculative decoding benchmark.
   - `cel_experiment_3_temporal_graphics.py`: Real-time graphics and frame generation benchmark.
   - `benchmark_week1_attention.py`: Transformer attention efficiency benchmarks.
   - `blind_holdout_audit.py`: Automated evaluation on unseen holdout test cases.
2. **Root benchmark scripts**:
   - `hyper_bench_harness.py`: Multi-run statistical measurement harness with warm-up isolation.
   - `gemm_truth_experiment.py`: Ground-truth reference comparison.

### E. Verification Systems
1. **`hyper_x/`**:
   - `equivalence_verifier.py`: Verifies numeric and algebraic equivalence between candidate and reference.
   - `independent_verifier.py`: Independent validation harness to prevent same-bug false positives.
   - `falsification_loop.py`: Active counterexample generation searching for boundary failures.
2. **`hyper_universal/verification_fortress.py`**: Cryptographic provenance hashes and multi-stage verification gates.
3. **`contracts/contract_ir.py`**: The formal contract validator ensuring error tolerances, latency, and memory bounds are respected.

### F. Schedulers & Governors
1. **`execution/execution.py`**: Worker pool and task scheduling.
2. **`hyper_runtime/hyper_fabric_orchestrator.py`**: Heterogeneous pipeline scheduler coordinating concurrent execution across CPU cores and iGPU EUs.
3. **`leo/cgfp_frame_governor.py`**: Frame-time budget governor for real-time applications.

### G. Predictors & State Estimators
1. **`predictors/predictive_reality.py`**: Temporal prediction of next state from history.
2. **`hyper_runtime/predictive_dreamer_v3.py`**: Speculative state precomputation.

### H. Caching & Reuse Systems
1. **`cache/cache_hub.py`**: Unified memory, disk, and tensor cache with LRU/LFU eviction.
2. **`hyper_cco/exact_cache.py`**: Bit-exact content-addressed cache keyed by input tensor hash and contract ID.
3. **`backend/answers/canonical_store.py`**: Deduplication and delta-store for repeated query payloads.

### I. CPU Execution Paths
1. **NumPy / SciPy BLAS/LAPACK**: MKL / OpenBLAS optimized routines.
2. **PyTorch CPU Backend**: Vectorized C++ kernels with AVX2/AVX-512 support.
3. **OpenVINO CPU Plugin**: High-throughput multi-threaded inference targeting Intel hybrid architecture (P-cores + E-cores).
4. **Pure Python Fallback**: Reference implementations ensuring maximum portability and testability.

### J. iGPU Execution Paths
1. **OpenVINO GPU Plugin**: Compiled kernels targeting Intel UHD Graphics (Gen12 / Xe LP architecture).
2. **DirectML (ONNX Runtime / PyTorch DirectML)**: Direct3D 12 compute shaders for Windows iGPU acceleration.
3. **OneDNN / Level-Zero**: Low-level Intel compute runtime integration.

### K. Mathematical Workers
1. **`spectral/`**: Fast Fourier Transform, Sparse FFT, Wavelet transforms.
2. **`physics/`**: Barnes-Hut gravitational/electrostatic tree codes, FMM.
3. **`hyper_x/info_boundary.py`**: Information-theoretic limits and Shannon entropy calculators.

### L. ML Workers & Inference Engines
1. **`hyper_runtime/inference_loop.py`**: Quantized transformer inference loop.
2. **`hyper_runtime/galore_bitnet_trainer.py`**: 1.58-bit ternary neural network execution.
3. **`hyper_runtime/albert_weight_sharing.py`**: Cross-layer parameter sharing for low-memory execution.

### M. RAG Components
1. **`rag/`**:
   - `composer.py`, `embed.py`, `index.py`, `query.py`, `retriever.py`: Local embedding and vector retrieval pipeline (FAISS / ChromaDB).

### N. Telemetry & Analytics
1. **`backend/analytics/telemetry_collector.py`**: System metrics, CPU/iGPU utilization, thermals, memory usage.
2. **`core/analytics/`**: Historical query patterns and performance regressions.

### O. Dashboard & Visualization
1. **Frontend (`src/`)**: Modern React + TanStack Router + Tailwind CSS web interface:
   - System resource monitor, benchmark comparison, backend status switchers, error budget graphs.
2. **`competitiveness_dashboard.html` / `falsification_suite.html`**: Standalone HTML/JS reporting dashboards.

### P. APIs & CLI
1. **`backend/main.py` & `backend/server.py`**: FastAPI server exposing endpoints for workloads, benchmarks, status, auth, and analytics.
2. **`cli/hyper_cli.py`**: Command-line tool for benchmark execution, profiling, and verification.

### Q. Tests, Docker, CI/CD
1. **`tests/`**: 229 test files covering API, algorithms, adversarial regression, anti-cheating, contract verification, and mathematical transforms.
2. **Docker**: `Dockerfile`, `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`.
3. **CI/CD**: GitHub Actions workflows in `.github/workflows/` validating security, formatting, and unit tests.

---

## 3. Critical Assessment & Architectural Opportunities

1. **Fragmentation of Concepts**:
   Previous work developed pieces of contract verification (`contracts/contract_ir.py`), rewrite generation (`hyper_cco/`, `hyper_x/egraph_engine.py`), and falsification (`hyper_x/falsification_loop.py`), but they were fragmented across separate submodules without a single, canonical **Computational Intermediate Representation (CIR)** graph that unifies all mathematical workloads.
2. **Scientific Parity Separation**:
   Previous versions occasionally conflated "contract compliance" or "speedup" with "GPU equivalence". The new architecture must enforce strict ontological separation between:
   - Hardware Parity (never claim dedicated GPU hardware on CPU+iGPU).
   - Computational Parity (exact vs numeric vs contract).
   - Bit-Exact Output Equivalence.
   - Performance & Energy Parity.
3. **Independent Reference Backend**:
   Verification must strictly execute candidate against an independent, trusted baseline (double execution verifier) and compute exact bit-level hashes, absolute/relative errors, and ULP differences.
4. **Anti-Cheating & Unknown Workload Mode**:
   A strict anti-cheat gate must proactively scan and reject hardcoded benchmark values, lookup tables, and test-specific branches.

This existing architecture provides an extraordinarily rich collection of building blocks. By integrating them into a unified **Verified Computational Pathway Discovery Engine**, we preserve 100% backward compatibility while elevating HYPER into a world-class, scientifically irreproachable system.
