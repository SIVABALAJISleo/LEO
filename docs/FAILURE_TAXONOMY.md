# HYPER-Ω Failure Taxonomy & Counterexample Learning Architecture

## 1. The Role of Failure in Algorithmic Discovery
In HYPER-Ω:
> **Failure is not hidden. Failure is learning signal.**

When a candidate optimization fails—whether through numerical divergence, memory throttling, or contract violation—the event is captured, categorized, and stored in the `CounterexampleRegistry`.
The search engines consult this database to guarantee that the system **never repeatedly attempts a transformation already disproven under the same structural conditions**.

---

## 2. The 12 Formal Failure Classes

Every failure is mapped into one of 12 distinct failure classes:

| Failure Class | Root Cause Description | Example Scenario | Guided Recovery Action |
| :--- | :--- | :--- | :--- |
| **`INSUFFICIENT_STRUCTURE`** | Data lacks the low-rank or sparse structure assumed by the transformation. | Low-rank SVD attempted on a full-rank random dense matrix. | Abandon low-rank approximation; fall back to cache-blocked SIMD. |
| **`NUMERICAL_INSTABILITY`** | Algorithm accumulates floating-point roundoff error exceeding contract bounds. | Strassen or Winograd bilinear forms on ill-conditioned matrices. | Increase precision tier or revert to numerically stable decomposition. |
| **`CANDIDATE_SLOWER`** | Candidate operation count is lower, but memory movement or synchronization overhead causes net regression. | Small-matrix kernel split across too many CPU threads. | Increase tile granularity or execute serially on single P-core. |
| **`MEMORY_BOUND`** | System memory bandwidth saturated; computation stalled waiting for DRAM. | Unfused memory passes reading and writing full 1080p frame buffers. | Apply operator fusion; keep data in L1/L2 cache lines. |
| **`IO_BOUND`** | Data throughput bottlenecked by disk or host-to-device bus transfers. | Loading uncompressed model weights from storage during inference. | Memory-map quantized weights; use asynchronous prefetching. |
| **`TRANSFER_BOUND`** | PCIe/ring bus bandwidth between CPU and Intel UHD iGPU exceeds computation time. | Offloading small matrix multiplication to iGPU. | Retain small workloads on CPU P-cores; offload only large batches. |
| **`THERMAL_BOUND`** | Processor power dissipation exceeds TDP, causing thermal throttling down-clocking. | Sustained AVX2 execution raising core temperatures above 95°C. | Throttle execution rate or dispatch non-critical passes to E-cores. |
| **`EQUIVALENCE_FAILURE`** | Candidate output differs from reference beyond declared error tolerance. | Stencil boundary slicing omitting toroidal wrapping coordinates. | Log counterexample; correct boundary coordinates or use fallback. |
| **`CONTRACT_FAILURE`** | Output satisfies basic numerical bounds but violates application-level contract. | Frame latency exceeds 16.6 ms budget in 60 FPS VR contract. | Drop optional detail tiers; engage temporal reprojection. |
| **`GENERALIZATION_FAILURE`** | Candidate succeeds on training data but fails on holdout or adversarial tests. | Overfitted heuristic threshold tailored to specific test scene. | Retrain heuristic on broad distribution; penalize over-specialization. |
| **`UNSUPPORTED_BACKEND`** | Requested hardware driver or instruction set is not present on physical host. | Attempting to launch CUDA kernel on Intel UHD integrated graphics. | Mark status `UNAVAILABLE`; engage CPU AVX2 or OpenVINO backend. |
| **`ALGORITHM_SEARCH_FAILURE`** | Evolution or E-graph search budget exhausted without finding valid candidate. | Search grammar lacks the rewrite rule needed for the expression. | Expand grammar rules; consult research discovery knowledge base. |

---

## 3. Persistent Schema
Each counterexample record stores:
- `record_id`: Unique SHA-256 identifier
- `workload_class`: e.g., `random_dense_gemm`, `temporal_graphics`
- `failure_mode`: One of the 12 failure classes
- `candidate_id`: Identifier of the failed candidate algorithm
- `input_hash`: Cryptographic digest of the input triggering failure
- `expected_output_hash` vs. `actual_output_hash`
- `numerical_error`: Maximum absolute and relative discrepancy
- `structural_conditions`: Matrix rank, condition number, sparsity ratio, scene dynamics
- `reproducibility_command`: Exact CLI command to reproduce the failure.
