# HYPER / LEO Module Classification & Provenance Map

In accordance with Section 3 of the Master Evolution Protocol, every existing module is classified into one of eight formal operational categories.

---

## 1. Module Taxonomy

### A. ACTIVE_PRODUCTION
Directly reachable from the authoritative pipeline. Enforces strict contract verification, fail-closed checking, and measurable performance on Intel Core i5-12450H + UHD Graphics.
- `hyper_x/pipeline.py`: Master Authoritative Pipeline
- `hyper_x/contract_ir/`: Formal Contract IR & Parser
- `hyper_x/information_boundary/`: Information Boundary Engine
- `hyper_x/necessity/`: Necessary-Work Compiler
- `hyper_x/pathway_search/`: Pathway Search Engine & Exact Reuse
- `hyper_x/verification/`: Authoritative Fail-Closed Verifier
- `hyper_x/decp/`: Deterministic Exact-Compute & Parity Layer (HYPER-DECP)
- `hyper_x/certificates/`: Execution Certificate System
- `hyper_x/evidence/`: Evidence Ledger
- `hyper_x/cost_model/`: Calibrated Hardware Cost Model
- `hyper_x/fallback/`: Fallback Engine
- `hyper_x/dashboard.py`: Live Parity Scorecard Dashboard
- `universal_compute_router/adaptive_dispatch.py`: Sub-100µs Heterogeneous Dispatch Router

---

### B. ACTIVE_RESEARCH
Actively maintained scientific exploration engines that feed candidate proposals to `pathway_search`:
- `ace_engine.py`: Adaptive Compute Eliminator with Freivalds stochastic certificates
- `hyper_runtime/token_merging/`: Bipartite Token Merging with weighted drift invariance
- `hyper_runtime/sparse_attention.py`: Block-Sparse Attention ($O(N \log N)$)
- `hyper_runtime/adaptive_precision.py`: SVD Singular Value Spectrum Quantization Selector
- `hyper_runtime/semantic_token_pruning.py`: Semantic Consecutive Similarity Pruner
- `hyper_x/rewrite/egraph.py`: Equality Saturation & E-Graph Rewrite Rules

---

### C. EXPERIMENTAL
Advanced prototypes undergoing empirical validation:
- `hyper_ares/`: Algorithmic Reformulation & Structure Detection
- `hyper_cel/`: Controlled Compute Unit Prototypes
- `hyper_mvc_dar/`: Model-View-Controller Decomposition & Ladder Architecture
- `hyper_runtime/speculative_decoding/`: Speculative Execution Draft Verifiers

---

### D. BENCHMARK_ONLY
Harnesses, manifests, and automated profiling scripts designed strictly for benchmarking on physical host silicon:
- `benchmarks/benchmark_int4_vs_fp32.py`
- `hyper_x/benchmark/harness.py`
- `tests/test_performance_regression.py`
- `tests/test_integration_prompts.py`
- `tests/test_pathological_inputs.py`
- `leo_implementation_artifacts.py`

---

### E. LEGACY
Pre-vNext implementations retained for regression checking and backwards compatibility:
- `hyper100/`: Early 100-workload benchmark suites
- `leo_engine.py`, `leo_runtime.py`: Early monolithic execution loops
- `chimera/`: Early heuristic search prototypes

---

### F. UNSAFE_FOR_PARITY_CLAIMS
Modules that must NEVER be used to assert hardware or exact computational parity:
- Mock engines or simulations using synthetic sleeps (`time.sleep`)
- Hardcoded constant speedup assertions

---

### G. ARCHIVED
Superseded historical checkpoints preserved for Git history integrity:
- `archive_engines/`
- `.bak` files and one-off conversion scripts

---

### H. SIMULATION_ONLY
Emulators used solely when physical acceleration devices or target models are unavailable:
- DirectML mock fallbacks when running without Windows D3D12 drivers
