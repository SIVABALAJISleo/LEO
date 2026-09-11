# LEO / HYPER: Legacy Integration Map & Disposition Registry

**Document Version**: 1.0.0 (Granular Module Classification)  
**Date**: September 2026  
**Standard**: Every historical subsystem is cataloged and assigned an explicit architectural disposition: `KEEP`, `INTEGRATE`, `REFACTOR`, `DEPRECATE`, or `ARCHIVE`. No working code is deleted blindly.

---

## 1. Classification Definitions

- **`KEEP`**: Authoritative production component in active use. Maintained with zero modifications required.
- **`INTEGRATE`**: High-value algorithm or kernel connected into the `UniversalEscapeEngine` / `hyper_cco` pipeline.
- **`REFACTOR`**: Useful subsystem requiring interface modernization, verification hardening, or removal of hardcoded assumptions.
- **`DEPRECATE`**: Superseded by a more rigorous implementation; retained for backward compatibility with existing tests.
- **`ARCHIVE`**: Historical prototype or experimental branch moved to reference status without runtime invocation.

---

## 2. Granular Module Disposition Registry

| Module Path | Historical Purpose | Disposition | Action & Canonical Successor |
| :--- | :--- | :--- | :--- |
| `hyper_cco/contract.py` | 10 Correctness Classes | **KEEP** | Authoritative Contract IR |
| `hyper_cco/proof_elimination.py` | Region Elimination Certificates | **KEEP** | Authoritative Proof-Carrying Elimination |
| `hyper_cco/counterfactual.py` | Lipschitz Sensitivity Analysis | **KEEP** | Authoritative Counterfactual Engine |
| `hyper_cco/residual_engine.py` | 7-Mode Residual Recalculation | **KEEP** | Authoritative Residual Engine |
| `hyper_cco/contract_compiler.py` | Path Planning & Compilation | **KEEP** | Authoritative Contract Planner |
| `hyper_cco/semantic_compression.py` | Tiered Intermediate Buffer Comp. | **KEEP** | Authoritative Compression Engine |
| `hyper_cco/thermal_scheduler.py` | Thermal & Deadline Loss $J$ | **KEEP** | Authoritative Heterogeneous Scheduler |
| `hyper_cco/provenance_ledger.py` | 25+ Field Audit Ledger | **KEEP** | Authoritative Anti-Cheat Provenance |
| `hyper_cco/adversarial_fuzzer.py` | 13 Hostile Failure Modes | **KEEP** | Authoritative Adversarial Fuzzer |
| `hyper_cco/cheapest_valid_path.py` | 10-Stage Pipeline Coordinator | **KEEP** | Authoritative Pipeline Coordinator |
| `hyper_x/wormhole_compiler/observable_compiler.py` | 12 Observable Domains | **INTEGRATE** | Connected into `UniversalEscapeEngine` |
| `hyper_x/wormhole_compiler/information_boundary.py` | Causal Reachability DAG | **INTEGRATE** | Connected into `UniversalEscapeEngine` |
| `hyper_x/wormhole_compiler/algorithm_genome.py` | Genetic Algorithm Composition | **INTEGRATE** | Connected into evolutionary synthesis |
| `hyper_x/wormhole_compiler/domain_adapters.py` | Domain Problem Adapters | **INTEGRATE** | Extended with video, RAG, and memory |
| `hyper_x/hardware/fingerprint.py` | Hardware Detection & Anti-Cheat | **INTEGRATE** | Provides hardware telemetry for scheduler |
| `hyper_x/rewrite/egraph.py` | AST Equality Saturation | **INTEGRATE** | Integrated as Step 19 in escape search |
| `hyper_x/strict/verifier.py` | Freivalds Probe & Metrics | **INTEGRATE** | Level 4 randomized verification provider |
| `core_ai/layers/linear_bitnet.py` | 1.58-bit Ternary Weight Engine | **REFACTOR** | Wrap with fallback when C++ AVX2 uncompiled |
| `core_ai/avx2_fast_matmul.py` | AVX2 SIMD Matrix Multiplication | **INTEGRATE** | Micro-optimization fallback kernel |
| `cbe/` (Tiers 0 through 7) | Compute-Budget Rendering | **INTEGRATE** | Underlying engine for `GraphicsWormholeAdapter` |
| `render/software_rt_pipeline.py` | CPU/iGPU Ray Tracer | **INTEGRATE** | Reference implementation for graphics tests |
| `memory/omnipresent_cache.py` | Resident State Cache | **REFACTOR** | Add cryptographic hash validation to prevent poisoning |
| `algorithm_discovery/` | Complexity Transformer | **INTEGRATE** | Genetic strategy candidate generator |
| `hyper_ares/` | Autonomous Escape Prototype | **DEPRECATE** | Superseded by `UniversalEscapeEngine` |
| `hyper_cel/` | Continuous Execution Prototype | **DEPRECATE** | Superseded by `hyper_cco.cheapest_valid_path` |
| `hyper_v2/` & `hyper_v3/` | Early AST Rewriters | **DEPRECATE** | Superseded by `hyper_cco.contract_compiler` |
| `universal_compute_router/` | Rule-Based Router | **DEPRECATE** | Superseded by `hyper_cco.thermal_scheduler` |
| `CENTURION_ENGINE.py` (root) | Duplicate Centurion Prototype | **ARCHIVE** | Canonical copy in `core_ai/centurion_engine.py` |
| `phoenix/` | Speculative Sketches | **ARCHIVE** | Historical reference archive |
| `cosmic_singularity/` | Speculative Optimization Sketches | **ARCHIVE** | Historical reference archive |
| `experiments/htm_vision.py` | HTM Vision Prototype | **ARCHIVE** | Research experiment |
