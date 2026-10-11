# LEO / HYPER Ω∞ — Execution Path & Pipeline Forensics

## 1. Authoritative Execution Pipeline

The canonical execution pathway across LEO/HYPER flows strictly through the following verified stages:

```
[ USER REQUEST / WORKLOAD INVOCATION ]
                    │
                    ▼
[ API / BENCHMARK HARNESS ] (backend/routers/pathway_router.py or hyper_v3/benchmark/runner.py)
                    │
                    ▼
[ WORKLOAD CONTRACT DEFINITION ] (hyper_v3/frontend/contract_parser.py)
    - Immutable execution contract frozen with SHA-256 hash
    - Explicit tolerance specification (rel_err, abs_err, min_ssim, exactness_class)
                    │
                    ▼
[ OPTIMIZATION ENGINE & SCHEDULER ] (hyper_omega/scheduler/heterogeneous.py)
    - Empirical memory bandwidth measurement (GB/s copy microbenchmark)
    - Multi-sample CPU warmup & median latency timing
    - Hardware capability discovery (OpenCL/Vulkan vs CPU fallback)
                    │
                    ▼
[ ACTUAL BACKEND COMPUTATION ]
    - Track A (Reference): Standard IEEE floating point / bitwise algorithm
    - Track B (Candidate): Work-avoidance transformation (e.g. sparse FFT, BitNet ternary)
                    │
                    ▼
[ INDEPENDENT VERIFICATION & CERTIFICATION ] (hyper_v3/verification/canonical_certifier.py)
    - NaN / Inf numerical stability check
    - Structural shape match validation
    - Conjunctive error tolerance enforcement: (max_rel <= threshold) AND (max_abs <= threshold)
    - Perceptual image SSIM check
    - Fail-closed: Never trusts candidate-supplied passed flag
                    │
                    ▼
[ SCORECARD / ARTIFACT / DASHBOARD ] (HYPER_3_0_RESULTS.json & HYPER_MASTER_SCORECARD.json)
    - Truthful reporting: Exactly records passed vs failed workloads
    - Hardware execution truth: Labeled as CPU (NumPy AVX2) when running on CPU
```

---

## 2. Identified Bypasses & Forensic Corrections

1. **The Disjunctive Tolerance Bypass (Repaired)**:
   - *Previous Path*: `IndependentVerifier.verify_contract_bounds` evaluated `(max_rel <= max_rel_err) or (max_abs <= max_abs_err)`. Because `max_abs_err` was default `2.0`, candidates with 100% relative error passed because their absolute values were <= 2.0.
   - *Repaired Path*: Enforces conjunctive evaluation `(max_rel <= max_rel_err) and (max_abs <= max_abs_err)`. Candidates with errors exceeding contract are rejected (`passed: False`).

2. **Synthetic Telemetry Bypass in Scoreboard D (Repaired)**:
   - *Previous Path*: `ScoreboardDEntry` assigned `cpu_percent=40.0, igpu_percent=60.0` whenever `"gemm"` was in the workload name, despite executing purely in Python NumPy on the CPU.
   - *Repaired Path*: Accurately records `target_device="CPU (NumPy AVX2)"`, `cpu_percent=100.0`, `igpu_percent=0.0`.

3. **Memory Bypass Formula vs Reality (Repaired)**:
   - *Previous Path*: Calculated `effective_bw = physical_bw * 16 * 4` and claimed memory bus was bypassed, while allocating a full unpacked matrix in RAM during execution.
   - *Repaired Path*: Separates measured DDR physical copy bandwidth (18.57 GB/s) from algorithmic intensity multiplier. Implements cache-blocked tiling (32 rows per block, ~32 KB) so uncompressed full matrices are never materialized in main RAM.
