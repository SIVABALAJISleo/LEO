# Task Plan: LEO / HYPER — Verified Computational Pathway Discovery Engine

## User Goal
Extend the existing LEO/HYPER project into a rigorous system capable of:
"Taking a computational problem and its required output contract, automatically searching for alternative mathematically valid execution pathways, eliminating unnecessary computation where possible, executing the best verified pathway on the available CPU+iGPU resources, and independently verifying the resulting output against a trusted reference."

The system must discover whether stronger-GPU-equivalent computation is achievable under explicitly defined workload conditions without fabricating benchmark results, hard-coding shortcuts, or confusing separate parity metrics.

---

## Architectural & Scientific Principles
1. **Never Confuse Parity Classes**:
   - Hardware Parity
   - Computational Parity
   - Exact Output Equivalence (Bit-Exact)
   - Numerical Equivalence (Numeric Exact / Numeric Tolerance)
   - Contract Equivalence
   - Performance Parity
   - Energy Parity
   - Universality Not Established
2. **Failure-First & Anti-Cheating**:
   - Prohibit benchmark-specific shortcuts, lookup tables, predetermined branches.
   - Unknown Workload Mode & Blind Holdout Set.
   - Adversarial Workload Generator testing corner cases, awkward dimensions, cancellation, sparsity, memory-bound.
3. **Independent Verification**:
   - Reference(x) vs Candidate(x) evaluated independently.
   - Double execution verifier + independent reference backends.
4. **Counterfactual Engine**:
   - "What if this computation did not happen?"
   - Calculate Residual(Op) and test whether it can be reconstructed more cheaply than executing Op.
5. **Canonical CIR (Computational Intermediate Representation)**:
   - Inputs, outputs, operators, constants, tensors, scalars, shapes, dtypes, dependencies, control flow, precision, determinism, cost.
   - Supports graph rewrites, algebraic reassociation, CSE, factorization, fusion, tiling, etc.
6. **Local CPU + iGPU Execution**:
   - Existing CPU-first architecture preserved; resource-aware scheduler across CPU, iGPU, RAM, thermals.
7. **Proof-Carrying Results & Research Traces**:
   - Machine-readable proof record + human-readable explainer + auditable search trace.

---

## Phases & Progress

### Phase 1: Repository Audit & Architecture Mapping
- [x] Scan existing modules: optimization engines, algorithm discovery, universal compute router, execution paths, schedulers, verification, CLI, APIs, tests.
- [x] Document current state in `docs/architecture/current_architecture.md`.
- [x] Design verified discovery architecture in `docs/architecture/pathway_discovery_architecture.md`.
- [x] Verify backward compatibility and identify reusable building blocks.

### Phase 2: Canonical CIR (Computational Intermediate Representation)
- [x] Define CIR Node, Edge, Operator, DataType, Shape, Tensor, Constant, PrecisionRequirement, ContractSpec.
- [x] Implement CIR Graph builder, serializer, deserializer, and graph-rewriter foundation.
- [x] Implement CIR export/import (JSON/dict format) and verified with automated test suite.

### Phase 3: Computational Contract Engine
- [x] Define formal WorkloadContract (required outputs, exactness modes, numerical tolerance, deterministic/non-deterministic, latency/memory/power constraints).
- [x] Support verification modes: BIT_EXACT, NUMERIC_EXACT, NUMERIC_TOLERANCE, SYMBOLIC_EQUIVALENCE, CONTRACT_EQUIVALENCE, PERCEPTUAL_EQUIVALENCE.
- [x] Enforce strict scientific rule: Never label Mode 3-6 as bit-exact parity; verified with automated unit tests.

### Phase 4: Search-Space Compiler
- [x] Implement transformation rules: algebraic reassociation, CSE, factorization, decomposition, operator fusion/splitting, dead-operation elimination, constant propagation, tiling/blocking, vectorization, batching, sparsity, low-rank, recurrence, strength reduction.
- [x] Track candidate metadata: candidate_id, parent_id, transformation_history, mathematical_assumptions, validity_conditions, estimated_cost.

### Phase 5: Counterfactual Engine
- [x] Implement "What if this computation did not happen?" analyzer.
- [x] Residual calculation and correction search (zero-residual omission, scalar bias correction).

### Phase 6: Computational Pathway Search
- [x] Implement search strategies: Beam Search, Best-First, A*, Branch-and-Bound, Heuristic Search.
- [x] Implement search budget controls: MAX_SEARCH_DEPTH, MAX_CANDIDATES, MAX_RUNTIME, MAX_MEMORY, VERIFICATION_BUDGET.

### Phase 7: Exact & Independent Verification Engine
- [x] Bit-exact verifier, numeric verifier (absolute error, relative error, ULP difference), symbolic verifier.
- [x] Independent reference backend execution to avoid same-bug false positives.
- [x] Verification record generator with cryptographic hashes.

### Phase 8: Anti-Cheating & Anti-Hardcoding System
- [ ] Detection & prohibition of lookup tables, cached outputs, fingerprint matching, test-name inspection.
- [ ] UNKNOWN_WORKLOAD_MODE enforcement.

### Phase 9: Holdout Workloads & Adversarial Workload Generator
- [ ] Discovery Set, Validation Set, Blind Holdout Set.
- [ ] Adversarial generator: prime dimensions, awkward tensors, dense/sparse, memory-bound, compute-bound, extreme values, cancellation.

### Phase 10: CPU + iGPU Execution Engine & Scheduler
- [ ] Preserve CPU-first architecture; integrate hardware detection and resource-aware scheduling.
- [ ] CPU-only, iGPU-only, CPU+iGPU partitioned execution.

### Phase 11: Cost Model (Predicted vs Measured)
- [ ] FLOPs, operations, memory traffic, latency estimation.
- [ ] Measured execution metrics profiling (separate PREDICTED_COST from MEASURED_COST).

### Phase 12: Proof-Carrying Result & Pathway Explainer
- [ ] Generate machine-readable proof JSON and human-readable explanation (why valid, why cheaper, what eliminated, assumptions, failure modes).
- [ ] Visualizer: Original Pathway vs Discovered Pathway.
- [ ] Full auditable Search Trace.

### Phase 13: Benchmark Engine & Reproducibility
- [ ] Multi-repetition benchmarking (warm-up, median, mean, stddev, min, max, confidence interval).
- [ ] Experiment manifest (`experiment_manifest.json`) capturing git commit, OS, Python, CPU, iGPU, RAM, seeds.

### Phase 14: API, CLI & Research Dashboard
- [ ] REST API endpoints (`/api/v1/pathway/*`).
- [ ] CLI commands (`hyper analyze`, `hyper discover`, `hyper verify`, `hyper benchmark`, `hyper adversarial`, `hyper prove`, `hyper compare`, `hyper audit`).
- [ ] Research dashboard showing original vs discovered, operations eliminated, exactness, verifications, hardware warning.

### Phase 15: Required Experiments (A through J) & Final Reports
- [ ] Run Experiments A (Matrix), B (Convolution), C (FFT), D (Graph), E (Crypto/Hash), F (Scientific/ODE), G (ML inference), H (Irregular), I (Memory-bound), J (Compute-bound).
- [ ] Audit mode verification & falsification.
- [ ] Generate comprehensive final reports in `reports/`.
