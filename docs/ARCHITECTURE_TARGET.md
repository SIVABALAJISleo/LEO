# LEO / HYPER: Target Architecture Specification

**Document Version**: 1.0.0 (Unified Discovery Engine Target)  
**Date**: September 2026  
**Target Platform**: Intel Core i5-12450H (4P + 4E cores, 12 threads, AVX2, FMA) + Intel UHD Graphics (48 EUs), 16 GB RAM, Windows 11.

---

## 1. Primary Architectural Objective

The goal of LEO / HYPER is to build a scientifically rigorous, software-only, CPU + Intel integrated GPU, contract-driven computational optimization and discovery engine.

The system does **NOT** attempt to physically imitate an NVIDIA GPU.

Instead, the system answers:
> **"What computation does the application actually need to produce the required observable?"**

Once identified, it systematically searches for the cheapest verified computational pathway that satisfies the declared application contract.

---

## 2. Canonical Discovery Pipeline

```
APPLICATION
      ↓
WORKLOAD CAPTURE
      ↓
CONTRACT DEFINITION (Contract IR: 10 Correctness Classes)
      ↓
OBSERVABLE COMPILER (Target Observables & Visibility Slicing)
      ↓
INFORMATION BOUNDARY (Causal Influence Analysis: REQUIRED vs UNNECESSARY)
      ↓
NECESSARY-WORK ANALYZER (Proof-Carrying Work Elimination)
      ↓
COUNTERFACTUAL ELIMINATION (Lipschitz Sensitivity & Ablation Testing)
      ↓
REPRESENTATION SEARCH (Sufficient Statistics, Low-Rank, Sparse, Delta)
      ↓
ALGORITHM SEARCH (E-Graph Rewrite & Evolutionary Synthesis)
      ↓
PROGRAM REWRITE (Canonical Hyper IR / Expression S-Expressions)
      ↓
COST MODEL (Analytical + Calibrated Hardware Execution Model)
      ↓
HARDWARE-AWARE SCHEDULER (Thermal-Aware P/E-Core + Intel UHD Dispatch)
      ↓
CPU / iGPU / HYBRID EXECUTION
      ↓
INDEPENDENT VERIFIER (Strict Reference vs Candidate Comparison)
      ↓
ADVERSARIAL TESTING (13 Hostile Failure Modes & Fuzzing)
      ↓
BLIND HOLDOUT (Unseen Workload Validation)
      ↓
EXECUTION CERTIFICATE (Cryptographically Sealed Proof of Parity)
      ↓
KNOWLEDGE BASE (Continuous Pattern & Failure Learning)
      ↓
FUTURE SEARCH
```

---

## 3. Subsystem Detailed Specifications

### Stage 1: Contract Definition (`ContractIR`)
- **Location**: `hyper_cco/contract.py`
- **Specification**: Formal dataclass encapsulating input domain, output domain, observable specification, tolerance bounds (absolute, relative, Frobenius, SSIM, perceptual), latency SLO, memory ceiling, and determinism requirements.
- **Rule**: Strict monotonicity. Workload contracts can never be silently downgraded from `EXACT_EQUIVALENT` to an approximate class.

### Stage 2: Observable Compiler (`ObservableCompiler`)
- **Location**: `hyper_cco/observable_compiler.py` & `hyper_x/wormhole_compiler/observable_compiler.py`
- **Specification**: Analyzes what downstream components consume. For example:
  - Full matrix multiplication $C = A \times B$ where only `top_k(C)` is needed.
  - 4K rendering where the display target is 1080p.
  - 4096-token LLM generation where only the first 50 tokens are processed by the caller.

### Stage 3: Information Boundary Analyzer (`InformationBoundaryAnalyzer`)
- **Location**: `hyper_cco/information_boundary.py` & `hyper_x/info_boundary/compiler.py`
- **Specification**: Backward causal slicing on the computational DAG. Classifies nodes into:
  `REQUIRED`, `CONDITIONALLY_REQUIRED`, `REDUNDANT`, `REUSABLE`, `PREDICTABLE`, `APPROXIMABLE`, `UNKNOWN`.
- **Invariant**: `UNKNOWN` is NEVER classified as unnecessary.

### Stage 4: Necessary-Work Compiler & Proof Elimination (`NecessaryWorkCompiler`)
- **Location**: `hyper_cco/proof_elimination.py`
- **Specification**: Produces a necessary sub-graph $G_N \subseteq G$. Every removed operation generates a `RegionEliminationCertificate` containing the boundary condition, residual bound, and SHA-256 integrity seal.

### Stage 5: Counterfactual Elimination Engine (`CounterfactualEliminationEngine`)
- **Location**: `hyper_cco/counterfactual.py`
- **Specification**: Tests hypothetical removal ($G \setminus \{v\}$). Evaluates output perturbation against the Lipschitz sensitivity bound $\Delta y \le L \cdot \|\Delta x\| \le \varepsilon / \text{margin}$. Employs a mandatory safety margin $\ge 1.5$ and 10% randomized physical verification sampling.

### Stage 6: Sufficient Representation Discovery (`RepresentationInventor`)
- **Location**: `hyper_cco/semantic_compression.py` & `hyper_x/representations/`
- **Specification**: Discovers low-cost sufficient representations:
  - Sparse (CSR/COO, structural zeros)
  - Low-Rank (SVD / randomized SVD, low-rank factorizations)
  - Compressed / Quantized (INT8, FP8, ternary)
  - Temporal / Spatial Deltas (event frames, bounding boxes)
  - Latent / Sufficient Statistics

### Stage 7: Algebraic Reformulation Engine (`EGraphRewriteEngine`)
- **Location**: `hyper_x/rewrite/egraph.py` & `hyper_cco/contract_compiler.py`
- **Specification**: Equality saturation on e-graphs using algebraic equivalences (associativity, distributivity, common subexpression elimination, operator fusion, loop tiling).

### Stage 8: Evolutionary Algorithm Discovery (`AlgorithmGenome`)
- **Location**: `hyper_cco/algorithm_genome.py` & `algorithm_discovery/`
- **Specification**: Mutates computation topologies, memory schedules, and tiling factors. Selects candidates based on multi-objective Pareto fitness: $\text{Correctness} \times \text{Contract} / (\text{Latency} + \text{MemoryMovement})$.

### Stage 9: Hardware-Aware Execution Fabric & Empirical Scheduler
- **Location**: `hyper_cco/thermal_scheduler.py` & `hyper_x/hardware/`
- **Specification**: Calibrated execution on the Intel Core i5-12450H:
  - P-Cores: Latency-critical, branchy, irregular workloads.
  - E-Cores: Background verification, telemetry, cache maintenance.
  - Intel UHD (48 EUs): Coalesced vector operations, dense filters, batched linear algebra.
  - Multi-objective loss: $J = \alpha \cdot \text{latency} + \beta \cdot \text{energy} + \gamma \cdot \text{thermal} + \delta \cdot \text{fallback} + \varepsilon \cdot \text{mem}$.

### Stage 10: Independent Verifier & Adversarial Fuzzing
- **Location**: `hyper_cco/adversarial_fuzzer.py` & `hyper_x/wormhole_compiler/functional_verifier.py`
- **Specification**: Strict architectural isolation. The optimizer NEVER evaluates itself. Verifier runs on independent numeric paths with 13 hostile test suites (NaNs, subnormals, rank-deficient matrices, lighting shocks, token distribution shifts).

### Stage 11: Blind Holdout & Anti-Cheat Provenance
- **Location**: `hyper_cco/provenance_ledger.py` & `hyper_x/holdout/`
- **Specification**: Candidates are frozen before testing on blind holdouts. Execution certificates are stamped with 25+ audit fields, SHA-256 hash chains, and verified execution timestamps.

---

## 4. Scientific Outcome Tri-State Taxonomy

Every investigated workload must conclude with one of three unambiguous outcomes:

1. **`WORMHOLE_FOUND`**:
   - A cheaper computational pathway was discovered, formally proven, independently verified, and passed all adversarial and holdout suites under the contract.
2. **`NECESSARY_COMPUTATION_IDENTIFIED`**:
   - All candidate reformulations and eliminations violated contract error bounds. The computational barrier is formally classified (Information-Theoretic, Algorithmic, Numerical, Memory-Bound, or Synchronization-Bound).
3. **`SEARCH_INCONCLUSIVE`**:
   - The search budget was exhausted without proving necessity or discovering a verified wormhole.

---

## 5. Hardware Advantage Inversion Metrics

We evaluate system efficiency using scientifically honest metrics:

- **Work Elimination Ratio ($WE$)**:
  $$WE = 1 - \frac{W_{\text{candidate}}}{W_{\text{reference}}}$$
- **Data Movement Reduction ($DMR$)**:
  $$DMR = 1 - \frac{M_{\text{candidate}}}{M_{\text{reference}}}$$
- **GPU Advantage Dependency Ratio ($GADR$)**:
  $$GADR = \frac{\text{GPU-Advantaged Necessary Work}}{\text{Original GPU-Advantaged Work}}$$
- **Hardware Advantage Erasure ($HAE$)**:
  $$HAE = 1 - GADR$$
- **Contract Parity Rate ($CPR$)**:
  $$CPR = \frac{\text{Verified Contract-Satisfied Workloads}}{\text{Total Evaluated Workloads}}$$

*Note: $HAE = 100\%$ does NOT mean the CPU physically matches RTX hardware throughput; it means the application's required observable has zero remaining dependency on GPU-specific architectural advantages.*
