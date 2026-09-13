# LEO / HYPER

## Ultra-Sonic Adaptive Computation Elimination Engine
### RTX 5090 Equivalent Software Pathway

> **"Achieve RTX 5090-class useful computational capability through software pathway transformation on fixed commodity silicon (Intel Core i5-12450H + Intel UHD Graphics)."**
> 
> *Official Report:* [RTX 5090 Software Equivalence Report](file:///c:/Users/sivab/OneDrive/Documents/HYPER/reports/RTX5090_EQUIVALENCE_REPORT.md)

**LEO / HYPER** is an open-source, truth-first research and engineering framework for contract-driven computation elimination:

> **Do not try to make weak hardware perform the same amount of work faster. Determine what work the application actually requires, eliminate everything else, and execute only the cheapest computation that can be verified to satisfy the required contract.**


HYPER is built for an Intel Core i5 (i5-12450H / i5-13420H) + Intel integrated UHD GPU with 16 GB unified system RAM and no dedicated accelerator.

The project does **not** claim raw hardware equivalence to discrete datacenter GPUs ("laptop = GPU"). Rather, it implements verified algorithmic elimination — using randomized rank sketches, low-rank decompositions, addition-only ternary kernels, sparse representations, and Freivalds stochastic proofs to eliminate 50% to 97% of linear algebra operations while provably satisfying the contract. Any irreducible noise falls back honestly to exact computation.

---

## Current Project Status

**Stage:** Active research / engineering / experimental implementation

**Primary objective:** Software-only application/contract parity on selected workload classes

**Hardware target:**

* Intel Core i5-12450H
* 8 cores / 12 threads
* Intel integrated UHD graphics
* 16 GB RAM
* 512 GB SSD
* Windows 11

**Hardware constraint:**

* No dedicated GPU
* No external accelerator
* No FPGA
* No ASIC
* No paid cloud GPU
* No hardware modification

---

# Core Principle

Traditional optimization asks:

```text
How can the same workload run faster?
```

HYPER asks a more aggressive question:

```text
Does the application actually require the entire workload?
```

The intended execution path is:

```text
INPUT
  ↓
APPLICATION CONTRACT
  ↓
WORKLOAD ANALYSIS
  ↓
DEPENDENCY ANALYSIS
  ↓
REDUNDANCY DETECTION
  ↓
EXACT REUSE
  ↓
INCREMENTAL / DELTA COMPUTATION
  ↓
EXACT ALGEBRAIC REFORMULATION
  ↓
SPARSITY
  ↓
LOW-RANK / FACTORIZATION
  ↓
COMPRESSION
  ↓
PRECISION OPTIMIZATION
  ↓
PREDICTION / SPECULATION
  ↓
RESIDUAL COMPUTATION
  ↓
TEMPORAL / STRUCTURAL REUSE
  ↓
CPU + INTEL UHD SCHEDULING
  ↓
VERIFICATION
  ↓
ACCEPT
  OR
FALLBACK
  ↓
PROOF-CARRYING RESULT
  ↓
MEASURED TELEMETRY
```

The objective is:

> **Minimum computation satisfying the required application contract.**

---

# What HYPER Is

HYPER is a collection and orchestration layer for computational elimination techniques.

Major research areas include:

* exact memoization and cache reuse
* dependency-aware reuse
* incremental computation
* residual computation
* common-subexpression elimination
* algebraic reformulation
* low-rank approximation
* sparse computation
* compressed representations
* mixed/adaptive precision
* prediction
* speculative execution
* temporal reuse
* reconstruction
* heterogeneous CPU+iGPU execution
* communication avoidance
* kernel fusion
* memory movement reduction
* application-aware verification
* adversarial benchmark validation

The repository contains multiple generations and experimental implementations of these concepts, including the `hyper100` and `HYPER_v6_BREAKTHROUGH` workstreams.

---

# What HYPER Is Not

HYPER does **not** create:

* CUDA cores
* Tensor Cores
* RT Cores
* dedicated VRAM
* NVIDIA memory bandwidth
* NVIDIA hardware instructions
* datacenter-class hardware throughput

HYPER does not claim to physically transform an i5-12450H into an RTX 5090, H100, or equivalent hardware.

The research target is fundamentally different:

```text
NVIDIA advantage
       ↓
Why does the application need that computation?
       ↓
Can the required result be obtained with substantially less computation?
       ↓
Can the reduced computation satisfy the contract?
```

---

# Four Different Meanings of "Parity"

One of the most important rules in the project is that parity must not be treated as a single number.

## 1. Raw Hardware Parity

Physical compute capability.

Examples:

* FLOPS
* memory bandwidth
* dedicated accelerator resources
* specialized GPU hardware

HYPER does **not** claim software can reproduce this hardware.

## 2. Exact Computational Parity

The same mathematical workload is executed and produces the equivalent result.

This is the strongest computational comparison.

## 3. Contract Parity

The application receives an output satisfying the explicitly defined correctness and quality requirements.

This may permit a lower-cost formulation where the application contract allows it.

## 4. Application Performance Parity

The required output is delivered with the required:

* correctness
* quality
* latency
* throughput

This is the most important practical target for HYPER.

---

# Correctness Classes

Every optimization must be classified.

```text
EXACT
EXACT_REFORMULATION
NUMERICALLY_EQUIVALENT
BOUNDED_APPROXIMATION
PERCEPTUAL_APPROXIMATION
PREDICTIVE
SPECULATIVE
CACHED
REUSED
REDUCED_WORK
SIMULATED
UNVERIFIED
```

These categories are not interchangeable.

For example:

```text
Exact cache
≠
approximation

Prediction
≠
exact computation

Reduced workload
≠
same workload

Perceptual similarity
≠
mathematical equivalence
```

HYPER's benchmark and reporting infrastructure is being redesigned around this distinction.

---

# Current Architecture

The long-term architecture is organized around a contract-constrained execution optimizer.

```text
                 ┌──────────────────────────┐
                 │ Application Input/Request │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Contract / Requirements │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Workload Classification │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Dependency Graph         │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Work-Elimination Search  │
                 └─────────────┬────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
      Exact Reuse        Reformulation       Approximation
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Candidate Execution      │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ CPU / UHD / Hybrid       │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Verification             │
                 └───────┬───────────┬──────┘
                         │           │
                      PASS          FAIL
                         │           │
                         ▼           ▼
                    Return      Stronger Strategy
                         │           │
                         │           ▼
                         │       Exact Fallback
                         │
                         ▼
                 Execution Certificate
```

---

# Contract-Constrained Compute Optimizer

The central optimization problem is conceptually:

$$
\min_{a\in A} C(a)
$$

subject to:

$$
Error(a) \le \epsilon
$$

$$
Quality(a) \ge Q_{min}
$$

$$
Latency(a) \le L_{max}
$$

$$
Throughput(a) \ge T_{min}
$$

where `a` is a candidate execution strategy.

The cost function may incorporate:

* latency
* energy
* memory
* verification cost
* fallback risk
* CPU utilization
* iGPU utilization

The implementation must use measurements where available rather than treating theoretical peak specifications as measured performance.

---

# Major Existing Capabilities

## Exact Reuse / Caching

HYPER contains cache/reuse infrastructure intended to avoid recomputing identical work.

The current engineering direction strengthens this by requiring exact cache identities to incorporate the complete relevant input and execution state rather than relying on sampled tensor contents.

An exact-cache certificate should include:

```text
input hash
shape
dtype
layout
model/version
algorithm version
contract
result identity
```

Exact cache hits are reported as:

```text
executed computation = 0
lookup latency = measured value
```

rather than artificially converting cache hits into compute throughput.

---

# Incremental / Delta Computation

Repeated workloads frequently contain only small changes.

HYPER investigates:

$$
Y_t = F(X_t)
$$

with:

$$
\Delta X_t = X_t-X_{t-1}
$$

and searches for cheaper update formulations:

$$
Y_t = Y_{t-1}+\Delta Y_t
$$

where mathematically valid.

Potential targets include:

* matrices
* images
* video
* simulations
* repeated ML operations
* dynamic application state

---

# Residual Computation

One of the principal next-generation HYPER strategies is:

```text
previous result
      +
prediction
      ↓
residual
      ↓
compute only residual information
      ↓
reconstruct
      ↓
verify
```

Conceptually:

$$
Output = Prediction + ResidualCorrection
$$

The goal is to avoid recomputing information that can already be inferred from previous state.

This is particularly relevant to workloads with temporal or spatial coherence.

---

# Algebraic Reformulation

HYPER investigates exact or conditional mathematical transformations that reduce complexity.

Examples include:

* Woodbury identity
* Sherman-Morrison
* block matrix methods
* factorization
* separable transforms
* FFT-based formulations
* Winograd-style transforms
* structured matrix methods
* incremental linear algebra
* divide-and-conquer formulations

Each transformation must document:

```text
original computation
alternative computation
mathematical assumptions
complexity
numerical stability
correctness classification
verification strategy
```

---

# Sparsity

HYPER analyzes whether workloads contain:

* exact zeros
* near-zero values
* block sparsity
* temporal sparsity
* spatial sparsity
* structured sparsity
* activation sparsity

Approximate zeros are not treated as exact zeros unless the contract and error analysis justify the transformation.

---

# Low-Rank Computation

HYPER investigates:

* SVD
* truncated SVD
* randomized SVD
* QR
* CUR
* Nyström
* tensor decompositions
* tensor-train representations
* structured matrix factorization

The key question is not:

```text
Can this matrix be compressed?
```

but:

```text
Can it be compressed enough to reduce computation while still satisfying the application contract?
```

---

# Precision Optimization

Potential execution modes include:

* FP32
* FP16
* BF16 where supported
* INT8
* INT4
* ternary/binary techniques where appropriate

Precision reduction must always be classified correctly.

Changing precision is not automatically an exact optimization.

HYPER therefore tracks:

```text
input precision
internal precision
output precision
absolute error
relative error
quality
latency
memory traffic
```

---

# Prediction and Speculative Execution

HYPER explores:

```text
cheap prediction
      ↓
confidence estimation
      ↓
selective verification
      ↓
accept
or
      ↓
exact fallback
```

This can potentially reduce expensive work for workloads where the next state can be accurately inferred.

Prediction is never automatically classified as exact.

---

# Temporal Reconstruction

For appropriate visual and temporal workloads:

```text
previous frame
+
motion/change information
+
current low-cost information
      ↓
prediction
      ↓
residual detection
      ↓
selective exact computation
      ↓
reconstruction
      ↓
quality verification
```

This is a key research direction for reducing expensive per-frame computation.

The concept is consistent with the broader family of temporal reconstruction techniques used in modern graphics systems, but HYPER's objective is to develop a hardware-independent computation-elimination framework around the same underlying principle.

---

# CPU + Intel UHD Heterogeneous Execution

HYPER is designed to use both available compute resources where beneficial.

## CPU

Best suited to:

* dependency analysis
* graph traversal
* control-heavy operations
* sparse bookkeeping
* compression
* decompression
* verification
* irregular workloads
* exact fallback
* SIMD workloads

## Intel UHD

Potentially suited to:

* regular dense kernels
* tiled arithmetic
* image-space operations
* parallel reconstruction
* regular reductions
* suitable compute workloads

The runtime must not assume the iGPU is always faster.

The system should empirically measure:

```text
CPU execution
UHD execution
transfer overhead
synchronization overhead
hybrid execution
```

and make decisions accordingly.

---

# Empirical Scheduling

Older experimental scheduling logic used theoretical hardware assumptions.

The newer direction is to make the scheduler empirical.

For each workload/kernel the system should learn:

```text
input size
arithmetic intensity
memory footprint
CPU time
UHD time
transfer time
synchronization time
verification time
```

and use those observations to improve future scheduling decisions.

---

# Memory and Data-Movement Optimization

HYPER treats memory traffic as an important source of overhead.

Research areas include:

* buffer reuse
* memory pooling
* lazy materialization
* tiled layouts
* cache locality
* zero-copy where supported
* reduced serialization
* reduced CPU↔GPU movement
* communication avoidance
* kernel fusion
* intermediate elimination

The objective is:

> Move less data, not merely calculate faster.

---

# Execution Certificates

The planned execution model requires every optimization result to produce a machine-readable execution certificate.

Conceptual structure:

```json
{
  "workload_id": "...",
  "input_hash": "...",
  "model_hash": "...",
  "code_hash": "...",
  "contract_hash": "...",

  "strategy": "...",
  "exactness_class": "...",

  "original_work": 0,
  "executed_work": 0,
  "eliminated_work": 0,

  "latency_ms": 0,
  "throughput": 0,

  "error_abs": 0,
  "error_rel": 0,

  "device": "CPU/UHD/Hybrid",

  "cache_hit": false,
  "fallback": false,

  "verification": {
    "status": "PASS",
    "method": "..."
  },

  "measurement": {
    "measured": true,
    "estimated": false
  }
}
```

The certificate itself should be integrity-protected with a cryptographic digest.

---

# Verification Policy

Verification levels should be explicitly differentiated:

```text
LEVEL 0 — no verification
LEVEL 1 — sample verification
LEVEL 2 — block verification
LEVEL 3 — full numerical verification
LEVEL 4 — mathematical equivalence
LEVEL 5 — application-level independent validation
```

A sample check must never be described as a mathematical proof.

An estimate must never be described as a measurement.

---

# Benchmark Integrity

HYPER follows a strict benchmark philosophy.

## Every serious benchmark should distinguish:

### Cold

No reusable state.

### Warm

Normal repeated execution.

### Persistent

Long-running execution.

### Adversarial

Inputs designed to defeat the optimization.

### Random

Unstructured randomized inputs.

### Structured

Inputs with exploitable redundancy.

### Application

Real application workloads.

---

# Benchmark Contamination Defense

Benchmarks should test:

```text
clean cache
warm cache
randomized input
perturbed input
adversarial input
```

The system must detect:

* hidden precomputation
* lookup-table cheating
* fixed benchmark answers
* benchmark-specific shortcuts
* workload substitution
* cache contamination

---

# Self-Falsification

A HYPER optimization is considered scientifically credible only if it survives attempts to break it.

Adversarial workload families include:

```text
cache adversaries
dense random matrices
full-rank matrices
low-coherence data
distribution-shifted prediction data
high-motion visual inputs
ill-conditioned numerical problems
large memory working sets
branch-heavy workloads
rapid scene changes
```

A strategy that works only on structured data must be described as such.

---

# Current Evidence

The repository contains application-level benchmark material comparing HYPER against RTX 3060-class references.

These numbers are **repository-reported**, not independent measurements from the target Lenovo system.

Reported examples include:

| Workload                |       HYPER | RTX 3060 reference | Relative HYPER throughput |
| ----------------------- | ----------: | -----------------: | ------------------------: |
| Blender viewport        |     ~38 FPS |           ~110 FPS |                    ~34.5% |
| Blender 1080p rendering | ~62 s/frame |       ~4.2 s/frame |                     ~6.8% |
| Unreal Engine 5         |     ~22 FPS |            ~80 FPS |               ~27.5–27.8% |
| Unity 1M particles      |     ~35 FPS |           ~140 FPS |                       25% |

These results demonstrate that the current system has **not** established universal application replacement.

They are valuable because they identify where the remaining research problem actually exists.

---

# Important Interpretation of Current Results

The current evidence does **not** mean the project has failed.

It means the broad claim:

```text
HYPER universally replaces much stronger GPUs
```

is not yet demonstrated.

The meaningful research question is narrower and stronger:

```text
For which workload classes can HYPER eliminate enough computation
that the original hardware advantage becomes unnecessary?
```

That is the direction of the current architecture.

---

# NVIDIA Comparison Philosophy

HYPER comparisons should distinguish actual hardware capabilities from application-level requirements.

Modern NVIDIA systems provide specialized resources including:

* massive parallel compute
* high memory bandwidth
* Tensor acceleration
* ray-tracing hardware
* dedicated memory subsystems
* specialized execution pipelines

HYPER does not attempt to reproduce those resources.

Instead it attacks the workload before those resources become necessary.

The strategy is:

```text
GPU does more work very fast
            VS
HYPER proves that much of that work is unnecessary
```

---

# Computational Complexity Goal

The highest-value optimization is not:

```text
same O(N³) workload
→ 20% faster
```

The highest-value optimization is:

```text
O(N³)
→ O(N²)
```

or:

```text
O(N²)
→ O(N log N)
```

or:

```text
full computation
→ small residual computation
```

where correctness and contract requirements remain satisfied.

Complexity reduction is therefore a primary research objective.

---

# Application-Specific Research

Current application-oriented research includes:

## Blender

Investigate:

* temporal reuse
* adaptive sampling
* image-space reconstruction
* visibility reuse
* selective recomputation
* CPU preprocessing
* UHD reconstruction

## Unreal Engine

Investigate:

* visibility reuse
* adaptive resolution
* temporal information
* selective rendering
* post-processing reduction
* residual computation

## Unity

Investigate:

* sparse state updates
* particle locality
* temporal coherence
* selective particle update
* CPU/UHD partitioning

These are research targets, not claims that the complete engines are already replaced.

---

# Work-Elimination Accounting

For a workload:

$$
WorkReduction =
1-
\frac{ExecutedWork}{OriginalWork}
$$

The system should track:

```text
original work
reused work
cached work
mathematically eliminated work
sparsified work
predicted work
verified work
fallback work
executed work
```

The accounting must prevent double counting.

---

# Performance Metrics

Depending on workload, HYPER records:

* latency
* throughput
* FPS
* FLOPs where meaningful
* executed operations
* eliminated operations
* memory usage
* CPU utilization
* iGPU utilization
* transfer time
* synchronization time
* thermal behavior
* power/energy where measurable
* correctness
* numerical error
* perceptual quality
* fallback rate
* cache hit rate

Unmeasured values must remain explicitly marked as unmeasured.

---

# Scientific Honesty Policy

HYPER does not accept:

```text
estimated FPS → measured FPS
theoretical FLOPS → measured FLOPS
estimated energy → measured energy
cache hit → compute throughput
prediction → exact computation
smaller workload → same workload
perceptual similarity → mathematical equivalence
```

Every result must state whether it is:

```text
MEASURED
DERIVED
PROVEN
ESTIMATED
HYPOTHESIS
UNVERIFIED
```

---

# Current Major Limitations

The current project still has important limitations.

## 1. Universal GPU replacement is not demonstrated

Some real application workloads still show substantial performance gaps.

## 2. Some historical benchmark logic was heuristic

Older experimental components contain modeled or estimated quantities that must not be confused with physical measurements.

## 3. Prediction verification needs stronger guarantees

Sampling can be useful for screening but is insufficient as a universal mathematical proof.

## 4. Optimization effects cannot simply be multiplied

Combined optimizations must be benchmarked as compositions.

## 5. Hardware telemetry is platform-dependent

Not every CPU/iGPU/thermal/power metric is available through every Windows runtime.

## 6. Some optimizations are workload-dependent

Caching, sparsity, low-rank structure and temporal reuse can fail on adversarial or unstructured inputs.

These limitations are part of the research program rather than being hidden.

---

# Breakthrough Architecture: HYPER-CCO

The next-generation architecture is referred to internally as:

# HYPER-CCO

**Contract-Constrained Computation Optimizer**

Its central objective is:

$$
\boxed{
\text{Find the cheapest verifiable computation satisfying the application contract}
}
$$

The intended strategy hierarchy is:

```text
EXACT CACHE
      ↓
EXACT REUSE
      ↓
COMMON-SUBEXPRESSION REUSE
      ↓
INCREMENTAL COMPUTATION
      ↓
EXACT REFORMULATION
      ↓
SPARSITY
      ↓
LOW-RANK
      ↓
COMPRESSION
      ↓
PRECISION OPTIMIZATION
      ↓
PREDICTION
      ↓
RESIDUAL COMPUTATION
      ↓
TEMPORAL RECONSTRUCTION
      ↓
CPU + UHD
      ↓
EXACT FALLBACK
```

The actual order may be changed by measured cost.

---

# Research Direction

The central research question is:

> **How much of a computation can be removed while preserving the exact or application-level contract that actually matters?**

This leads to several major research directions:

```text
representation reduction
dependency elimination
information reuse
algorithmic reformulation
complexity reduction
residual computation
temporal reconstruction
adaptive precision
learned prediction
CPU+iGPU cooperation
communication avoidance
verification-driven execution
```

---

# Research Method

HYPER follows:

```text
HYPOTHESIS
   ↓
IMPLEMENTATION
   ↓
BASELINE
   ↓
OPTIMIZED EXECUTION
   ↓
VERIFICATION
   ↓
ADVERSARIAL TEST
   ↓
MEASUREMENT
   ↓
REPRODUCTION
   ↓
CONCLUSION
```

A failed optimization is not deleted merely because it failed.

Its failure is recorded as research evidence.

---

# Project Roadmap

## Phase 1 — Correctness Foundation

* exact cache semantics
* contract schema
* verification interface
* execution certificates
* benchmark provenance

## Phase 2 — Work Elimination

* dependency graph
* reuse
* common-subexpression elimination
* incremental computation
* residual computation

## Phase 3 — Mathematical Reduction

* reformulation
* low-rank
* sparse execution
* structured computation
* complexity reduction

## Phase 4 — Approximate Execution

* adaptive precision
* prediction
* speculative execution
* reconstruction
* application-level quality contracts

## Phase 5 — Heterogeneous Runtime

* CPU calibration
* Intel UHD calibration
* hybrid scheduling
* transfer minimization
* kernel fusion

## Phase 6 — Application Integration

* numerical workloads
* image/video workloads
* rendering workloads
* simulation workloads
* ML workloads

## Phase 7 — Scientific Validation

* blind holdouts
* adversarial workloads
* contamination tests
* long-duration benchmarks
* regression testing
* reproducibility

---

# Success Criteria

A HYPER result is considered successful when:

```text
required output is produced
AND
contract is satisfied
AND
quality requirement is satisfied
AND
latency requirement is satisfied
AND
throughput requirement is satisfied
AND
verification passes
AND
measurement is reproducible
```

Only then may an application-level parity result approach:

```text
100%
```

---

# 100% Objective

The project's ultimate target remains:

# 100% APPLICATION / CONTRACT PARITY

where legitimately achievable.

This does **not** mean:

```text
100% raw hardware parity
```

and it does **not** mean:

```text
100% exact hardware replacement for every possible workload
```

It means:

> The application receives the required result, at the required quality, latency and throughput, without violating the declared contract, using only the available CPU + Intel UHD software stack.

When that is impossible for a workload, HYPER must identify the exact barrier instead of fabricating a score.

---

# Philosophy

```text
Do not make weak hardware imitate powerful hardware.

Ask what computation the powerful hardware is performing
that the application does not actually need.

Eliminate that computation.

Verify the result.

Execute only the irreducible remainder.
```

---

# Repository Structure

The repository contains multiple generations of research and engineering work.

Important areas include:

```text
hyper100/
HYPER_v6_BREAKTHROUGH/
benchmarks/
tests/
application integrations/
research experiments/
documentation/
```

Because the project is actively evolving, individual experimental modules may represent different maturity levels.

Always check the module's documentation and benchmark status before treating it as production-ready.

---

# Contributing

Useful contributions should prioritize:

* measurable improvements
* correctness
* reproducibility
* algorithmic complexity reduction
* memory reduction
* data-movement reduction
* CPU+iGPU utilization
* verification
* adversarial testing
* benchmark quality

Avoid contributions that merely inflate benchmark numbers without preserving the workload contract.

---

# Research Standard

Every significant optimization should answer five questions:

```text
1. What work was performed before?

2. What work is performed now?

3. Why is the reduced computation valid?

4. What evidence verifies the result?

5. What workload causes the optimization to fail?
```

If these cannot be answered, the optimization is not yet fully validated.

---

# Final Project Statement

LEO / HYPER is an attempt to explore a different frontier of performance engineering:

> **Performance does not always come from doing the same computation faster. Sometimes the biggest optimization is discovering that most of the computation was never necessary.**

The project therefore focuses on:

```text
COMPUTATION ELIMINATION
+
ALGORITHMIC REFORMULATION
+
REPRESENTATION REDUCTION
+
REUSE
+
PREDICTION
+
VERIFICATION
+
CPU/UHD HETEROGENEOUS COMPUTING
```

The final objective is not to claim that inexpensive hardware becomes physically equivalent to expensive hardware.

The objective is to discover workload classes where **the expensive computation itself becomes unnecessary while the application contract remains satisfied**.

That is the central research problem of HYPER.
