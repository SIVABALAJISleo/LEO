# HYPER 2.0: Existing System Architecture & Baseline Map

## 1. System Overview
The LEO (Local Edge Orchestrator) / HYPER repository implements a local-first semantic intelligence and computational efficiency platform running on commodity client hardware (Intel Core i5-13420H / i5-12450H CPU with Intel UHD Graphics iGPU).

## 2. Existing Baseline Inventory

### A. Core Engine Components
- **`backend/core/`**: Central memory system, database, HDC engine, knowledge graph, and security sandbox.
- **`backend/layer1_memory` to `layer18_neural_blender`**: Multi-layered compute routing, semantic caching, crystallization, and OpenVINO/iGPU execution.
- **`backend/routers/`**: FastAPI endpoints including `breakthrough_dashboard.py`, `cgfp.py`, `cgace.py`, `contract_subsumption.py`, and `governor.py`.
- **`src/` & `src/components/breakthrough/`**: React 19 + TanStack Start UI featuring the Breakthrough Studio, Contract Simulator, and GPU Comparison Matrix.

### B. Baseline Performance (HYPER 1.0 / v5.0 Tri-Metric Audit)
- **Score 1 (Exact Hardware Replacement)**: 2/15 (13.3%) — Workloads with zero mathematical compressibility (such as raw dense full-rank FP32 GEMM) remain bound by physical silicon FLOPs.
- **Score 2 (Contract-Aware Subsumption)**: 15/15 (100.0%) — All 15 application-level contracts are fully satisfied within specified tolerances ($\epsilon \le 10^{-3}$, SSIM $\ge 0.95$, target FPS $\ge 30$).
- **Score 3 (Verified Computational Work Avoided)**: 95.6% average work legitimately eliminated before silicon dispatch.

### C. Baseline Preservation Location
All historical baseline data is preserved in:
- `reports/hyper_1_0_baseline/TRI_METRIC_AUDIT_REPORT.md`
- `reports/hyper_1_0_baseline/TRI_METRIC_RESULTS.json`
- `reports/hyper_1_0_baseline/SUBSUMPTION_RESULTS.json`

## 3. Transition to HYPER 2.0
HYPER 2.0 upgrades the system from manual, domain-specific bypasses to a generalized, autonomous compiler pipeline:
1. **Contract Compiler**: Formal, immutable contract specification.
2. **Intermediate Representation (IR)**: DAG-based computation graph.
3. **Necessity & Structure Analyzers**: Autonomous mathematical necessity detection.
4. **Autonomous Strategy Search**: Candidate generator with predictive cost models.
5. **Heterogeneous CPU+iGPU Runtime**: Dynamic hardware dispatch and persistent memory residency.
6. **Independent Verifier & Fallback Ladder**: Segregated verification with automatic 8-level fallback.
