# HYPER Current Architecture Map (Audit & Forensics)

## 1. System Topology Overview

This document provides an unvarnished, forensic map of the active execution paths, historical layers, and modular relationships within the LEO / HYPER codebase as of September 2026.

```
                           EXTERNAL CLIENTS
                 (Web Browser / REST Client / Test Suites)
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │        FASTAPI BACKEND        │ (Port 8000)
                   │       backend/main.py         │
                   └───────────────┬───────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   │       DISCOVERY ROUTER        │
                   │ backend/routers/discovery_... │
                   └───────────────┬───────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐         ┌─────────────────────────────────┐
│ UNIVERSAL COMPUTATIONAL ENGINE  │         │  COMPUTATIONAL BYPASS ENGINE    │
│ hyper/discovery/engine.py       │         │ hyper/discovery/computational...│
└────────────────┬────────────────┘         └────────────────┬────────────────┘
                 │                                           │
         ┌───────┴───────┬───────────────┬───────────────────┤
         ▼               ▼               ▼                   ▼
┌────────────────┐┌─────────────┐┌───────────────┐┌───────────────────────────┐
│CAPABILITY      ││WORKLOAD     ││PATHWAY IR &   ││FIVE BYPASS FOUNDATIONS    │
│DECOMPOSER      ││DECOMPOSER   ││GENERATOR/     ││• Zero-Copy Unified Memory │
│(7 GPU Families)││(Dependency  ││COMPOSER       ││• BitNet b1.58 Additive    │
│                ││ DAG Engine) ││(Multi-Family) ││• PowerInfer Sparsity      │
└────────────────┘└─────────────┘└───────────────┘│• Temporal Delta Graphics   │
                                                  │• Analytic SDF Ray March   │
                                                  └─────────────┬─────────────┘
                                                                │
         ┌──────────────────────────────────────────────────────┴───────────────┐
         ▼                                                                      ▼
┌───────────────────────────────────────────────┐       ┌──────────────────────────────┐
│        VERIFICATION & SAFETY FORTRESS         │       │    RESEARCH INFRASTRUCTURE   │
│ • AST Security Inspector (sandbox.py)         │       │ • Research Question Tracker  │
│ • 8-Level Verification Stack                  │       │   (H001 - H008 Lifecycle)    │
│ • Adversarial Counterexample Engine           │       │ • 100% Destination Tracker  │
│ • Proof Engine (Symbolic Certificates)        │       │ • Controlled Benchmark Suite │
└───────────────────────────────────────────────┘       └──────────────────────────────┘
```

---

## 2. Active Package Inventory & Execution Paths

### 2.1 The Active Core (`hyper/discovery/`)
The authoritative active discovery engine resides entirely under `hyper/discovery/`:
* `engine.py` (`UniversalComputationalDiscoveryEngine`): Master coordinator tying together decomposition, pathway generation, debate, benchmarking, and tracking.
* `loop.py` (`UniversalDiscoveryLoop`): The iterative 13-step hypothesis $\to$ candidate $\to$ verification $\to$ critique loop.
* `capability_decomposer.py` (`GPUCapabilityDecomposer`): Decomposes dedicated GPU capabilities into 7 families (Graphics, Ray Tracing, AI/ML, Scientific, Media, Memory, General Compute).
* `workload_decomposer.py` (`WorkloadDecomposer`): Extracts function/kernel dependencies into DAG nodes classified into `REQUIRED`, `REDUNDANT`, `REPEATED`, or `OPTIONAL`.
* `computational_bypass_engine.py` (`ComputationalBypassEngine`): The 5 hardware-bypassing breakthrough engines (Zero-copy unified memory, BitNet ternary additions, PowerInfer sparsity, Temporal graphics delta carryforward, Analytic SDF sphere tracing).
* `alphadev_engine.py` (`AlphaDevEngine`): Discovers minimal branch-free sorting networks (Sort3, Sort4, Sort5 verified via 0-1 Sorting Lemma) and branch-free hashing.
* `alphatensor_engine.py` (`AlphaTensorEngine`): Discovers bilinear tensor contractions (e.g. Strassen rank 7).
* `alphaevolve_engine.py` (`AlphaEvolveEngine`): Evolutionary program synthesis with mutation and crossover.
* `transformation_dsl.py` (`TransformationDSLEngine`): Declarative DSL rules defining Preconditions, Operations, Postconditions, and Cost Models.
* `sandbox.py` (`SecurePathwaySandbox`, `ASTSecurityInspector`): AST inspection blocking malicious imports and process spawning; thread-isolated execution with CPU timeouts.
* `verification_stack.py` (`FormalVerificationStack`): Sequentially executes Levels 1 to 8 (Unit, Differential, Bit-Exact, Numerical, Property, Metamorphic, Sandbox, Formal Proof).
* `research_tracker.py` (`ResearchQuestionTracker`): Epistemic state management for formal hypotheses H001–H008.
* `controlled_workloads.py` (`ControlledWorkloadBenchmark`): 12 canonical reference workloads evaluated under strict cold-cache discipline.
* `destination_tracker.py` (`DestinationTracker`): Maintains multi-dimensional parity metrics without fake percentages.

### 2.2 Host Server & API Layer (`backend/`)
* `backend/main.py`: Entry point for FastAPI application. Includes routers for discovery, health, and status.
* `backend/routers/discovery_router.py`: Exposes REST endpoints (`/capability-matrix`, `/destination-tracker`, `/alphadev/catalog`, `/dsl/rules`, `/research-tracker`, `/bypass-engine`, `/workloads/controlled-suite`, etc.).

### 2.3 User Interface Layer
* `dashboard/universal_discovery_lab.html`: Standalone interactive operations dashboard for live discovery runs, debate logs, destination tracking, and AlphaDev benchmarks.
* `src/`: Modern React/TanStack single-page web app running on Vite (`http://localhost:8080/`).

---

## 3. Forensic Identification of Legacy / Archival Layers

1. **Root-Level Monolithic Engines**:
   Files like `CENTURION_ENGINE.py`, `chimera_engine.py`, `leo.py`, `leo_*.py` represent early generations (v1 to v3). They are preserved for provenance but have been superseded by `hyper/discovery/`.
2. **Duplicated Concepts**:
   - `hyper/contracts/` vs `hyper/universal/contracts/`: Historically duplicate definitions of contracts. The system now uses `UniversalContract` with `ExactnessTier`.
   - `hyper/escape_engine/` vs `hyper/escape/` vs `hyper/discovery/computational_bypass_engine.py`: Early partial escape modules now consolidated into the 5 foundations in CBE.
3. **Standalone Benchmark Dumps**:
   Numerous root JSON/CSV files (`symbolic_results_v2.json`, `TRI_METRIC_RESULTS.json`, etc.) represent historical point-in-time snapshots from earlier audit phases.

---

## 4. Hardware Calibration & Operating Targets

* **Host Machine**: Intel Core i5-12450H (4 Performance cores, 4 Efficient cores, 12 threads, AVX2 + FMA, no AVX-512).
* **Integrated Graphics**: Intel UHD Graphics (Alder Lake-H GT1, 48 Execution Units, ~1.20 GHz, shared DDR system RAM).
* **Memory Subsystem**: 16 GB Unified System RAM (~18.57 GB/s measured dual-channel bandwidth).
* **Dedicated GPU Stance**: Zero dedicated GPU required or utilized. Physical parity is strictly `NOT_CLAIMED (PHYSICALLY_DISJOINT)`.
