# HYPER / LEO — Forensic Architecture Inventory
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)  
**Host Target Silicon:** Intel Core i5-12450H (8 Cores, 12 Threads: 4P + 4E) | Intel UHD Graphics (48 EUs) | 16 GB Unified RAM | Windows 11

---

## 1. Module Taxonomy & Classification (8 Categories)

Every directory and module in this repository has been audited and classified according to strict evidentiary standards:

### 1. ACTIVE_PRODUCTION
Core runtime pathways that actively participate in production execution without bypasses or hardcoded shortcuts.
- `hyper_x/pipeline.py`: Master authoritative linear execution pipeline.
- `hyper_x/contract_ir/`: Machine-readable formal computation contracts.
- `hyper_x/information_boundary/`: SVD spectral analysis & 6-way dependency partitioning.
- `hyper_x/necessity/`: Necessary-work DAG compiler and FLOP accounting ledger.
- `hyper_x/pathway_search/`: Exact reuse engine (SHA-256) and semantic cache.
- `hyper_x/discovery/`: Mathematical & algorithm discovery with candidate lifecycle.
- `hyper_x/representations/`: 14-format adaptive representation search.
- `hyper_x/prediction/`: Speculative decoding with verified target acceptance.
- `hyper_x/reconstruction/`: Temporal & spatial frame/scene reconstruction.
- `hyper_x/verification/`: Fail-closed verifier (numerical, adversarial, holdout).
- `hyper_x/decp/`: HYPER-DECP deterministic exact-compute layer (Track A vs Track B).
- `hyper_x/orchestrator/`: Real-time CPU + UHD dynamic scheduler.
- `hyper_x/memory/`: 16 GB RAM boundary and zero-copy buffer manager.
- `hyper_x/certificates/`: SHA-256 tamper-evident execution certificates.
- `hyper_x/evidence/`: Persistent append-only evidence ledger.
- `hyper_x/dashboard.py`: Live evidence-derived parity scorecard.

### 2. ACTIVE_RESEARCH
Live research modules investigating novel algorithmic shortcuts, verified on host silicon before promotion.
- `hyper_runtime/sparse_attention.py`: Block-sparse attention engine (sliding window + global landmarks).
- `hyper_runtime/token_merging/tome_engine.py`: Bipartite soft matching token reduction.
- `hyper_runtime/semantic_token_pruning.py`: Consecutive & N-gram cosine similarity pruner.
- `hyper_runtime/adaptive_precision.py`: SVD condition spectrum precision selector.
- `universal_compute_router/adaptive_dispatch.py`: Sub-100µs heterogeneous dispatch router.

### 3. EXPERIMENTAL
Isolated research prototypes undergoing validation; strictly quarantined from production claims.
- `algorithm_discovery/`: Initial genetic search prototypes.
- `leo_quantum_kan_lut_engine.py`: Kolmogorov-Arnold representation search experiment.
- `leo_fourier_light_transport.py`: Synthetic Fourier basis light field transport.
- `leo_prt_continuous_cache_experiment.py`: Precomputed radiance transfer cache explorer.

### 4. LEGACY
Historical implementations superseded by the unified `hyper_x` pipeline; preserved for regression reference.
- `leo_engine.py`, `leo_runtime.py`: Early orchestration wrappers.
- `hyper_v2/`, `hyper_v3/`: Previous generation iteration artifacts.
- `cbe/`: Compute-Budget Elimination early prototype.

### 5. ARCHIVED
Static reference implementations and snapshots maintained for scientific reproducibility.
- `archive_engines/`: Frozen snapshots of earlier solver iterations.
- `HYPER_v6_BREAKTHROUGH/`: Checkpoint of v6 engine.

### 6. BENCHMARK_ONLY
Harnesses and test drivers used exclusively for measuring performance on real hardware.
- `hyper_x/benchmark/harness.py`: Frozen benchmark harness with cold/warm separation.
- `benchmarks/benchmark_int4_vs_fp32.py`: INT4 vs FP32 memory & throughput profiling.
- `real_hardware_benchmark.py`: Host silicon measurement runner.

### 7. SIMULATION_ONLY
Simulation frameworks used strictly for theoretical modeling; completely barred from parity claims.
- `models/`: Reference neural architecture definitions without hardware-specific bindings.

### 8. UNSAFE_FOR_PARITY_CLAIMS
Any module containing historical mock fallbacks, heuristic passes, or uncalibrated constants.
- Any test or script utilizing `mock` or `MagicMock` without candidate-coupled execution.
- Quarantined legacy benchmarks that did not separate cold from warm runs.

---

## 2. Production Entry Points
The repository defines exactly one authoritative execution entry point:
- **CLI Entry Point:** `python -m hyper_x.pipeline`
- **Dashboard Entry Point:** `python -m hyper_x.dashboard`
- **Comparison Engine:** `python -m hyper_x.rtx5090.comparison_engine`
