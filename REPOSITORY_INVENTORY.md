# REPOSITORY INVENTORY — LEO / HYPER (GODMODE Ω∞)

**Date**: 2026-10-11  
**Project**: LEO / HYPER Universal Alternative-Computation & Parity Engine  
**Target Hardware**: Intel Core i5-12450H (8 Cores: 4P+4E, 12 Threads), Intel UHD Graphics (iGPU), 16 GB RAM (15.7 GB detected), 512 GB SSD (474.7 GB formatted, 230.9 GB free), Windows 11 Home.  
**Fixed Restrictions**: Software-only, no dedicated GPU, no hardware upgrades, no cloud/external compute, no paid services.

---

## 1. Executive Summary & Repository Topology

The repository contains a hybrid full-stack system consisting of:

1. **Python Systems & Mathematical Core (`hyper_universal/`, `hyper_omega/`, `hyper/`, `backend/`)**:
   - Compilers, transformation passes, out-of-core memory controllers, hardware schedulers, verification suites, and FastAPI server endpoints.
2. **TypeScript / React Frontend (`src/`)**:
   - Modern TanStack Start / Vite dashboard interface featuring real-time diagnostics, benchmark charts, hardware profile cards, and capability explorers.
3. **Test Infrastructure (`tests/`)**:
   - Over 230 test files validating algebraic invariants, hardware limits, memory escape, adversarial fuzzing, and cryptographic audit trails.

---

## 2. Directory & Module Inventory

| Module Path                                | Primary Responsibility                                                 | Architectural Role | Current Status                                            |
| :----------------------------------------- | :--------------------------------------------------------------------- | :----------------- | :-------------------------------------------------------- |
| `hyper_universal/`                         | Universal alternative computation engine, contracts, IR, and scheduler | Core Engine        | **Active & Production-Ready**                             |
| `hyper_universal/capability_mirror/`       | Software mirror for 21+ GPU capabilities & substitution search         | Feature 1          | **Implemented in this session**                           |
| `hyper_universal/contracts/`               | Workload contracts, numerical tolerance specs, resource budgets        | Feature 2          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/memory_escape/`           | TinyStories-inspired streaming, chunking, layerwise, out-of-core       | Feature 3          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/computation_elimination/` | Algebraic simplification, DCE, CSE, loop fusion, work ledger           | Feature 4          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/data_movement/`           | Cache blocking, loop interchange, in-place processing, layout opt      | Feature 5          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/pathway_discovery/`       | Multi-candidate discovery, bounds checking, Pareto comparison          | Feature 6          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/backends/`                | Host hardware detection (AVX2, Intel UHD iGPU via OpenVINO/OpenCL)     | Feature 7          | **Active & Enhanced** (OpenVINO GPU validated)            |
| `hyper_universal/scheduler/`               | Adaptive CPU + iGPU scheduling with measured transfer costs            | Feature 7          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/certification/`           | Exactness validation, speedup measurement, tamper-proof hashes         | Feature 8          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/precision/`               | FP32, FP16, INT8 quantization, sparse formats, error tracking          | Feature 9          | **Active & Tested** (100% test passing)                   |
| `hyper_universal/incremental/`             | Dirty regions, temporal coherence, memoization, subproblem reuse       | Feature 10         | **Active & Tested** (100% test passing)                   |
| `hyper_universal/counterexamples/`         | Differential, property-based, boundary-value, adversarial fuzzing      | Feature 11         | **Active & Tested** (100% test passing)                   |
| `hyper_universal/evidence_store/`          | SQLite-backed persistent audit ledger and hardware fingerprinting      | Feature 14         | **Active & Tested** (100% test passing)                   |
| `hyper_universal/benchmarking/`            | Multi-trial statistics, warmup exclusion, variance measurement         | Feature 16         | **Active & Tested** (100% test passing)                   |
| `backend/`                                 | FastAPI REST API backend (port 8000)                                   | Integration API    | **Active** (Mounted in `backend/main.py`)                 |
| `backend/routers/hyper_escape_router.py`   | REST endpoints for workload intake, discovery, memory, benchmarks      | Integration API    | **Active & Mounted**                                      |
| `src/`                                     | TanStack Start + React 19 + Tailwind CSS frontend                      | User Interface     | **Active & Lint-Clean** (ESLint 0 errors, Vitest passing) |
| `src/components/HyperGodmodeDashboard.tsx` | Dashboard displaying real-time metrics, contracts, and certifications  | User Interface     | **Active**                                                |
| `tests/hyper_escape/`                      | Test suite for Universal Escape Engine & Contracts (34 tests)          | Test Harness       | **Passing 34/34**                                         |
| `tests/hyper_mirror/`                      | Test suite for Universal Capability Mirror & Substitutions             | Test Harness       | **Implemented in this session**                           |
| `hyper_omega/`                             | Heterogeneous Intel hardware scheduler & legacy acceleration passes    | Foundation         | **Active**                                                |
| `hyper100/`                                | Canonical parity engines & parity boundary certificates                | Foundation         | **Active**                                                |

---

## 3. Disconnected or Legacy Subsystems

1. **`cbe/` (Computational Bypass Engine)**: Prototype predecessor to `computation_elimination/`. Mostly subsumed by `hyper_universal`.
2. **`chimera/` & `chimera_engine.py`**: Heuristic hybrid execution prototype. Replaced by `hyper_universal/scheduler/scheduler.py`.
3. **`leo_*.py` root scripts**: Historical research experiments and micro-benchmarks. Retained for historical verification and reproducible benchmarks.
4. **`archive_engines/`**: Deprecated engines preserved for historical provenance.
5. **`archive_engines/legacy_layers/`**: Quarantined legacy orchestrators (`v10_alpha`, `v10_beta`, `v10_mvp`, `v16`, `v19`, `v42`, `v43`, `v_infinity`, `ucsip`, and `v10_l1`..`v10_l16`).
   - The **single canonical active execution path** is `backend/canonical/functional_replacement_engine.py`, `backend/canonical/native_runtime_bridge.py`, and `backend/caoe/caoe_engine.py`.

---

## 4. Hardware Verification & Runtime Environment

- **Detected Host CPU**: Intel64 Family 6 Model 186 Stepping 2 (`13th Gen Intel(R) Core(TM) i5-13420H` / `i5-12450H` family), 8 physical cores (4 Performance + 4 Efficient), 12 logical threads.
- **Detected Graphics**: `Intel(R) UHD Graphics (iGPU)`, Driver 32.0.101.7076, 2048 MB shared memory.
- **Detected RAM**: 15.7 GB physical memory with dynamic copy bandwidth measured at ~18.57 GB/s.
- **Detected Storage**: 474.7 GB SSD partition (230.9 GB available).
- **Available Native Acceleration**:
  - `openvino` 2026.2.1: Native CPU (`CPU`) and Native Intel UHD iGPU (`GPU`) execution verified with live matrix multiplication compilation!
  - `numpy` 2.3.2 with `OpenBLAS` 0.3.30 (AVX2, FMA3, Haswell optimized kernel).
  - `torch` 2.10.0+cpu.
