# Architecture Specification: Verified Computational Pathway Discovery Engine

**Document**: `docs/architecture/pathway_discovery_architecture.md`  
**Status**: APPROVED & ACTIVE  
**Engine**: LEO / HYPER — Verified Computational Pathway Discovery Engine  
**Hardware Target**: Dynamic Local Topology (Intel Core i5-13420H P+E hybrid CPU, Intel UHD iGPU, 16 GB DDR5/LPDDR5 RAM)  

---

## 1. System Mission & Foundational Philosophy

The primary mission of the upgraded HYPER engine is to:
> *"Take a computational problem and its required output contract, automatically search for alternative mathematically valid execution pathways, eliminate unnecessary computation where possible, execute the best verified pathway on the available CPU+iGPU resources, and independently verify the resulting output against a trusted reference."*

### The Scientific Truth Imperative
1. **Never Confuse Parity Classes**: The system strictly separates:
   - **Hardware Parity**: Strictly false on commodity hardware. CPU+iGPU never creates dedicated GPU hardware.
   - **Computational Parity**: Whether equivalent mathematical operations are computed.
   - **Bit-Exact Equivalence**: Output bytes or bit representations match 100%.
   - **Numerical Equivalence**: Output matches within explicit machine precision ($\epsilon$, ULP difference).
   - **Application / Contract Parity**: Output satisfies all specified contract invariants.
   - **Performance Parity**: Discovered pathway executes within or below the reference wall-clock latency.
   - **Energy Parity**: Energy consumption per completed problem meets or beats reference.
   - **Universality**: Generalization across defined workload families versus single instance success.
2. **Failure-First Design**: The system actively attempts to falsify optimizations. When no verified pathway beats the reference or satisfies the contract, the engine executes the trusted baseline and transparently reports `NO_VERIFIED_SHORTCUT_FOUND`.
3. **No Synthetic Shortcuts**: Zero lookup tables, zero precomputed answers, zero benchmark name detection, and zero hidden network compute.

---

## 2. End-to-End Discovery Pipeline

```
           [ INPUT WORKLOAD ]
                   │
                   ▼
     [ 1. PROBLEM / CONTRACT EXTRACTION ] ────► Workload Contract Specification
                   │
                   ▼
     [ 2. WORKLOAD & TOPOLOGY ANALYSIS ] ────► Dimensions, Sparsity, Memory Bound
                   │
                   ▼
     [ 3. CIR GRAPH GENERATION ] ─────────────► Canonical Computational IR
                   │
                   ▼
     [ 4. SEARCH-SPACE COMPILER ] ────────────► Transformation Families (Algebraic, CSE, etc.)
                   │
                   ├──► [ COUNTERFACTUAL ENGINE ] ("What if op X was omitted?")
                   │          │
                   │          ▼
                   │    Residual(X) Correction Search
                   │
                   ▼
     [ 5. BOUNDED PATHWAY SEARCH ] ───────────► Beam / A* / Branch-and-Bound / Heuristic
                   │
                   ▼
     [ 6. COST ESTIMATION ] ──────────────────► Predicted FLOPs, Memory Traffic, Latency
                   │
                   ▼
     [ 7. HETEROGENEOUS COMPILATION ] ────────► CPU (SIMD/BLAS) + iGPU (OpenVINO/Level-Zero)
                   │
                   ▼
     [ 8. INDEPENDENT VERIFICATION ] ─────────► Independent Reference Backend (Double Execution)
                   │                            Error Metrics: Abs, Rel, ULP, Bit-Hash
                   ├── Fail ──► Record Falsification & Prune Branch
                   │
                   ▼ Pass
     [ 9. ADVERSARIAL VALIDATION ] ───────────► Blind Holdout / Boundary / Cancellation Tests
                   │
                   ▼
     [ 10. PATHWAY SELECTION & PROOF ] ───────► Machine-Readable Proof Record + Explainer
                   │
                   ▼
     [ 11. BENCHMARK & AUDIT RECORD ] ────────► Statistical Metrics (Median, CI) + Manifest
```

---

## 3. Subsystem Architecture Specifications

### Subsystem 1: Canonical CIR (Computational Intermediate Representation)
- **Data Model**:
  - `CIRGraph`: Directed acyclic graph containing nodes, edges, inputs, outputs, attributes, and contracts.
  - `CIRNode`: Represents operations (`OpType`: `MATMUL`, `CONV2D`, `FFT`, `RELU`, `ADD`, `REDUCE_SUM`, `TRANSPOSE`, `SLICING`, `CUSTOM`), tensors, or constants.
  - `CIREdge`: Dataflow or control/memory dependency edge carrying data type (`DataType`: `FP64`, `FP32`, `FP16`, `INT64`, `INT32`, `INT8`, `BOOL`), shape (`Tuple[int | str, ...]`), sparsity annotations, and memory layout.
- **Rewriting Engine**:
  - Graph rewrite rules acting on subgraphs.
  - Pattern matching with condition guards (e.g., associativity, distributivity, symmetry).
  - Preserves metadata: `candidate_id`, `parent_id`, `transformation_history`, `mathematical_assumptions`.

### Subsystem 2: Formal Workload Contract Engine
- **Verification Modes**:
  1. `BIT_EXACT`: Byte-for-byte or exact binary identity (`hash(cand) == hash(ref)`).
  2. `NUMERIC_EXACT`: Floating point zero delta within machine precision ($\Delta = 0.0$ or $|cand - ref| \le 1 \text{ ULP}$).
  3. `NUMERIC_TOLERANCE`: Bounded error $|cand - ref| \le \text{atol} + \text{rtol} \times |ref|$.
  4. `SYMBOLIC_EQUIVALENCE`: Symbolic simplification confirms algebraic identity ($A - B \equiv 0$).
  5. `CONTRACT_EQUIVALENCE`: High-level contract criteria met (e.g., Top-k classification indices match, sorting order verified).
  6. `PERCEPTUAL_EQUIVALENCE`: Explicit perceptual distance bounded (SSIM $\ge$ threshold, PSNR $\ge$ threshold).
- **Constraints**:
  - `LatencyConstraint`: Maximum execution wall-clock time in milliseconds.
  - `MemoryConstraint`: Maximum peak memory allocation in megabytes.
  - `PowerConstraint`: Maximum thermal / power envelope in watts.
  - `DeterminismConstraint`: Whether identical inputs must produce bit-reproducible outputs.

### Subsystem 3: Search-Space Compiler
- **Transformation Families**:
  - **Algebraic**: Reassociation $((A B) C \to A (B C))$, distributivity, inverse propagation.
  - **Redundancy Elimination**: Common subexpression elimination (CSE), dead-operation elimination, constant folding.
  - **Structural**: Factorization, low-rank decomposition ($W \approx U V^T$), operator fusion (Conv+ReLU, GEMM+Add), operator splitting.
  - **Memory & Access**: Tiling, cache blocking, SIMD vectorization, memory layout transpose elimination.
  - **Mathematical Reformulation**: Winograd convolution, Strassen matrix multiplication, FFT-based polynomial convolution, recurrence closed-form solution.
  - **Sparsity & Symmetry**: Exploitation of diagonal/banded/symmetric structures.

### Subsystem 4: Counterfactual Engine
- **Core Operation**:
  1. For candidate operation $O_k$ in the computational graph:
  2. Compute graph without $O_k$: $G' = G \setminus \{O_k\}$.
  3. Compute downstream residual impact: $\text{Residual}(O_k) = \text{RefOutput} - \text{Eval}(G')$.
  4. Search space for low-cost correction: $C \approx \text{Residual}(O_k)$ where $\text{Cost}(C) \ll \text{Cost}(O_k)$.
  5. If valid correction found satisfying contract: generate alternative pathway $G' \cup \{C\}$.

### Subsystem 5: Computational Pathway Search
- **Search Algorithms**:
  - **A\* / Best-First Search**: Priority queue ranked by estimated cost $f(c) = g(c) + h(c)$.
  - **Beam Search**: Retains top-$K$ promising candidate frontiers at each search depth.
  - **Branch-and-Bound**: Prunes candidate subtrees whose lower bound cost exceeds the current best verified pathway.
- **Strict Budget Controls**:
  - `max_search_depth`: Maximum number of sequential rewrites.
  - `max_candidates`: Maximum total pathways generated.
  - `max_runtime_sec`: Timeout wall-clock limit.
  - `verification_budget`: Maximum number of full executions allowed.

### Subsystem 6: Exact Verification & Independent Reference
- **Independent Verification Backend**:
  - Reference execution executes in an isolated context using pure standard libraries (e.g., direct NumPy/SciPy/SymPy gold implementation).
  - Candidate execution runs via optimized compiled kernels.
  - **Double Execution Verifier**: Evaluates output hashes, maximum absolute difference, relative Frobenius error, and bitwise ULP differences.

### Subsystem 7: Anti-Cheating & Anti-Hardcoding Layer
- **Prohibited Patterns**:
  - Static lookup tables indexed by input features.
  - Branching on test suite names (`__file__`, `pytest`, benchmark strings).
  - Hardcoded precomputed tensor constants matching known test answers.
  - Hidden network requests or offloaded cloud compute.
- **Enforcement**:
  - AST inspection and runtime memory validation.
  - `UNKNOWN_WORKLOAD_MODE`: Strips all names and descriptions, passing only raw mathematical problem, input tensors, and contract.

### Subsystem 8: Adversarial Holdout & Workload Generator
- **Three-Tier Workload Split**:
  - **Discovery Set**: Used to discover transformation rules and train heuristics.
  - **Validation Set**: Standard evaluation set.
  - **Blind Holdout Set**: Strictly isolated workloads never exposed to rule miners.
- **Adversarial Generator**:
  - Pathological and prime dimensions (e.g., $1009 \times 1013$ GEMM preventing standard powers-of-two tiling).
  - Catastrophic cancellation cases ($x - y$ where $x \approx y$).
  - Ill-conditioned matrices, extreme dynamic range ($10^{-30}$ to $10^{30}$).
  - Dense vs ultra-sparse (99.9% zeros), memory-bound streaming vs compute-bound arithmetic.

### Subsystem 9: Resource-Aware CPU + iGPU Execution Engine
- **Hardware Integration**:
  - CPU: Multi-core threading with thread-pool affinity, SIMD vectorization.
  - iGPU: Intel UHD Graphics via OpenVINO GPU plugin and Level-Zero / DirectML.
  - Dynamic Partitioning: Computes work partition ratio $\alpha \in [0, 1]$ based on measured throughput and transfer latency across shared RAM.

### Subsystem 10: Cost Model (Predicted vs Measured)
- **Predicted Cost**:
  - Theoretical FLOPs.
  - Memory traffic bytes (arithmetic intensity $\text{FLOPs} / \text{Byte}$).
  - Estimated memory allocation footprint.
- **Measured Cost**:
  - High-precision CPU/GPU wall-clock duration ($\mu s$).
  - Measured peak RSS memory.
  - Realized arithmetic throughput (GFLOP/s).

### Subsystem 11: Proof-Carrying Result & Explainer
- **Proof Artifact**: Machine-readable JSON including SHA-256 hashes of inputs, reference outputs, candidate outputs, transformation history, and verification metrics.
- **Human-Readable Explainer**:
  - What computation was eliminated?
  - Why was the alternative pathway mathematically valid?
  - What assumptions were required?
  - Under what input conditions would the optimization fail?
- **Pathway Visualizer**: ASCII and structural graph comparison (Original vs Discovered).

### Subsystem 12: Benchmark Engine & Manifest Reproducibility
- **Statistical Rigor**:
  - Dedicated warmup iterations isolated from timed runs.
  - Minimum $N \ge 10$ repetitions.
  - Reports median, mean, standard deviation, min, max, and 95% confidence interval.
- **Reproducibility Manifest**: Captures git commit, CPU model, iGPU driver, RAM, Python version, dependencies, random seeds, and full input hashes.

---

## 4. Integration into HYPER Directory Structure

To maintain 100% backward compatibility and seamless reuse of existing assets:
- All core engine components will reside in `hyper/discovery/`:
  - `cir.py`: Canonical CIR graph, nodes, edges, serialization.
  - `contract.py`: Formal WorkloadContract engine and verification modes.
  - `search_space.py`: Search-space compiler and transformation families.
  - `counterfactual.py`: Counterfactual engine and residual correction.
  - `search.py`: Bounded search algorithms (Beam, A*, Branch-and-bound).
  - `verifier.py`: Independent reference backend and exact verification.
  - `anticheat.py`: Anti-cheating gate and Unknown Workload mode.
  - `adversarial.py`: Adversarial workload generator and holdout sets.
  - `scheduler.py`: Resource-aware CPU+iGPU execution engine.
  - `cost_model.py`: Predicted vs measured cost profiling.
  - `proof.py`: Proof-carrying result generator and explainer.
  - `benchmarking.py`: Multi-repetition benchmark runner and reproducibility manifest.
  - `engine.py`: Unified `VerifiedPathwayEngine` coordinating all subsystems.
- Top-level integration:
  - `backend/main.py`: Extend with `/api/v1/pathway/*` endpoints.
  - `cli/hyper_cli.py`: Extend with `hyper analyze`, `discover`, `verify`, `benchmark`, `adversarial`, `prove`, `compare`, `audit`.
  - Research dashboard: Unified dashboard interface.
