# LEO / HYPER Ω∞ — Authoritative Repository Inventory

**Audit Date**: October 2026  
**Repository**: `https://github.com/SIVABALAJISleo/LEO`  
**Host Target Profile**: Intel Core i5-12450H (8 Cores: 4P+4E / 12 Threads), Intel UHD Graphics (48 EUs), 16 GB DDR RAM, 512 GB SSD, Windows 11  
**Detected Host Hardware**: 13th Gen Intel Core i5-13420H (8 Cores: 4P+4E / 12 Threads), Intel UHD Graphics, 16 GB RAM  

---

## 1. Executive Structure Overview

The repository consists of a dual-stack architecture:
1. **High-Performance Python Core (`hyper_v3`, `hyper_omega`, `hyper_x`, `backend/`, `core_ai/`, `hyper/`)**:
   - Algorithmic work avoidance, mathematical compression, heterogeneous CPU/iGPU scheduling, and independent formal verification engines.
   - FastAPI REST API serving parity reports, CIR graph compilation, and pathway discovery endpoints.
2. **TypeScript / React Web Application (`src/`, `ui_core/`, `app/`)**:
   - Modern TanStack Start / Nitro dashboard displaying multi-dimensional scorecards, real-time telemetry, and chat interface.

---

## 2. Directory Taxonomy & Component Roles

| Directory | Core Role | Execution Status | Audit Finding |
| :--- | :--- | :--- | :--- |
| `hyper_v3/` | Canonical 15-Workload Dual-Track Engine (Track A Exact vs Track B Contract) | **Active Production** | Root-cause of loose tolerance bug repaired. Canonical certifier added. |
| `hyper_omega/` | Heterogeneous Scheduler & Memory Bypass Amplification Engine | **Active Production** | Repaired to eliminate synthetic 25 GB/s transfer assumption and block-tile cache execution. |
| `hyper_x/` | 13-Dimension Master Certification Engine with Conjunctive Gates | **Active Production** | Enforces fail-closed evaluation across all contract gates. |
| `hyper/` | Discovery, Structural CIR Graph Transformations, Counterexample Hunter | **Active Production** | Verified mathematical pathways and algebraic rewriting. |
| `backend/` | FastAPI REST API routers (`pathway_router.py`, `discovery_router.py`, `main.py`) | **Active Production** | Healthy, dashboard routing verified. |
| `src/` & `app/` | React 19 / TypeScript 5.7 UI with TanStack Start & Vite 8 | **Active Production** | Builds cleanly, ESLint passes with 0 errors. |
| `reports/` | Historical and generated benchmark results (`HYPER_3_0_RESULTS.json`) | **Canonical Mirror** | Synchronized with root canonical results. |
| `tests/` | 100+ pytest test files with >1,600 automated tests | **Validation Suite** | 1,594+ passing tests across all components. |

---

## 3. Disconnected & Stale Modules Triage

- `reports/hyper_1_0_baseline/`, `reports/hyper_2_baseline/`: Historical baseline snapshots preserved for provenance auditing. Marked as historical snapshots, not fresh measurements.
- `agentic-awesome-skills-main/`: Bundled agent skill repository used for development automation and security review tools. Not part of runtime user application bundle.
