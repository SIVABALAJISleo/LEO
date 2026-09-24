# LEO / HYPER Ω — Universal Scientific Integrity & Anti-Cheating Policy
**Document ID:** `docs/UNIVERSAL_NO_CHEATING_POLICY.md`  
**Standard:** Constitutional System Constraint  
**Applicability:** Universal across all modules, benchmarks, discoveries, and claims

---

## 1. Core Principles of Scientific Honesty

The LEO / HYPER project seeks to discover whether software-only computational pathways can satisfy dedicated external GPU contracts under fixed CPU+iGPU constraints. Fabricating or misrepresenting results destroys scientific value.

The following practices are **STRICTLY PROHIBITED** and will cause immediate candidate rejection and test failure:

1. **Reference Function Delegation:** Evaluating an algorithmic candidate by invoking the reference implementation internally.
2. **Hidden Precomputation:** Computing answers ahead of time and returning cached results during a benchmark without declaring `PRECOMPUTED`.
3. **Hidden Oracles / Secret Cache:** Looking up stored answers keyed by input hashes or problem instances.
4. **Benchmark-Specific Hardcoding:** Special-casing known benchmark inputs in generated or discovered code.
5. **Workload Substitution:** Replacing an expensive requested computation with an easier, smaller, or truncated problem.
6. **Silent Contract Weakening:** Lowering required numerical precision, tolerance, or fidelity without explicit declaration.
7. **Simulated Hardware Misrepresentation:** Calling a simulated or theoretical GPU number a "measured" hardware baseline.
8. **Circular Operation Metrics:** Calculating operation counts by dividing by latency speedup instead of direct measurement.
9. **Unreported External Compute:** Calling external network APIs, accelerators, or cloud GPUs.
10. **Asymmetric Cache Comparisons:** Comparing a cold GPU baseline against a warm/precomputed CPU cache.

---

## 2. Mandatory Cache Declarations

Every benchmark, candidate evaluation, and baseline run MUST explicitly declare its execution cache regime:

| Cache Regime | Definition | Allowable Comparison Baseline |
| :--- | :--- | :--- |
| **`COLD`** | All caches flushed, memory cold, JIT un-warmed, zero precomputation. | **Must ONLY be compared against COLD reference.** |
| **`WARM`** | System caches warm, JIT compiled, memory resident, but input dynamic. | **Must ONLY be compared against WARM reference.** |
| **`CACHED`** | Repeated exact input retrieved from memory lookup. | **Must declare lookup overhead and memory footprint.** |
| **`MEMOIZED`** | Partial intermediate sub-problem reuse. | **Must account for table lookup and hash latency.** |
| **`PRECOMPUTED`** | Output or lookup table computed prior to timing start. | **Must account for offline preparation time and RAM storage.** |
| **`INCREMENTAL`** | Output updated from prior frame/state using delta propagation. | **Must declare dependency on previous frame state.** |

---

## 3. Strict Provenance Tagging

Every numerical metric, latency, throughput, energy value, and operation count reported by LEO/HYPER Ω must carry an immutable provenance tag:

- **`MEASURED`**: Directly obtained from hardware performance counters (`rdtsc`, `perf_event_open`, OS high-resolution timers, NVML, or Intel RAPL).
- **`DERIVED`**: Mathematically computed from measured quantities via proven equations (e.g. $Throughput = Operations / MeasuredLatency$).
- **`ESTIMATED`**: Approximated using an analytical cost model.
- **`SIMULATED`**: Simulated execution via cycle-accurate simulator or analytical hardware profile.
- **`REFERENCE_ONLY`**: Historical, datasheet, or vendor-published reference value.
- **`UNAVAILABLE`**: Hardware performance counter or physical device does not exist. **Never fabricate a number when unavailable.**

---

## 4. Enforcement Mechanisms

1. **Instrumentation Guard:** All reference implementations in tests are wrapped with call counters. If a candidate execution increments the reference counter, the test framework raises `CheatingDetectedError`.
2. **Cache Isolation:** Cold-cache benchmarks execute dirty-cache thrashing buffers before timing.
3. **Universality Gate:** The `UniversalClaimGate` automatically denies `GUARANTEED` status if any metric lacks provenance or contains an undeclared cache state.
