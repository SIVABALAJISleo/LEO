# HYPER Benchmark Integrity & Anti-Cheat Protocol

**Document:** `docs/HYPER_BENCHMARK_INTEGRITY.md`  
**Date:** October 10, 2026  
**Status:** Mandatory Engineering Standard

---

## 1. The Iron Law of Verification

> **"If an optimization cannot be independently verified with real mathematical evidence, wall-clock measurements, and adversarial testing, it does not exist."**

To maintain absolute scientific rigor, the HYPER platform enforces strict rules prohibiting artificial benchmark fabrication, hardcoding, and misleading performance metrics.

---

## 2. Core Prohibitions

1. **Zero Manufactured Numbers:**
   - Benchmarks must be derived exclusively from live hardware execution using high-resolution monotonic clocks (`time.perf_counter_ns()`).
   - Hardcoded timing numbers, simulated multipliers, or fictitious speedup estimates presented as real measurements are strictly prohibited.
2. **Zero Hardcoded Output Tables:**
   - Optimization candidates must never return precomputed or lookup-table responses for specific test inputs.
   - Every candidate is subjected to dynamic input mutation sensitivity testing: altering the input must measurably change the candidate's output.
3. **No Omission of Critical Computation:**
   - Candidates that achieve sub-microsecond runtimes by silently skipping required work, failing to write to output memory, or discarding operations are instantly flagged as `CHEAT_DETECTED` and rejected.
4. **Fair Measurement Boundaries:**
   - Excluded initialization or compilation phases must be explicitly stated.
   - Warm-up and steady-state timings must be reported with their sample counts and variance.
   - Baseline and candidate algorithms must process the exact same workload dimensions and data types.

---

## 3. Anti-Cheat Verification Fortress

The verification engine (`hyper/hyper100_parity/verification_engine.py`) and test suite execute four layers of defensive auditing on every candidate:

### Layer 1: Sub-Microsecond Zero-Latency Check

Any non-trivial kernel (e.g., $1024 \times 1024$ GEMM or $256 \times 256$ spatial convolution) executing in $< 0.1 \mu\text{s}$ is audited for omitted execution or unexecuted loops.

### Layer 2: Input Mutation Sensitivity Audit

```python
mutated_input = sample_input.copy()
mutated_input.flat[0] += 10.0
out_orig = candidate_fn(sample_input)
out_mutated = candidate_fn(mutated_input)
if np.array_equal(out_orig, out_mutated):
    # Check secondary zeroed-array probe to distinguish classification thresholds from hardcoded constants
    out_zero = candidate_fn(np.zeros_like(sample_input))
    if np.array_equal(out_orig, out_zero):
        raise AntiCheatViolation("Hardcoding detected: input mutation produced identical output.")
```

### Layer 3: Freivalds Randomized Matrix Verification

For matrix operations $A \in \mathbb{R}^{m \times k}, B \in \mathbb{R}^{k \times n}, C \in \mathbb{R}^{m \times n}$:
Instead of expensive $O(n^3)$ double execution, Freivalds algorithm generates Rademacher random vectors $r \in \{-1, +1\}^n$ and tests:
$$A \cdot (B \cdot r) - C \cdot r \stackrel{?}{=} 0$$
Running $k=10$ independent iterations bounds the error probability to $P(\text{False Positive}) \le 2^{-10} < 0.00098$.

### Layer 4: Blind Holdout Validation

Candidates that pass known benchmark inputs must immediately be tested against randomly generated unseen inputs and adversarial distributions (zeros, checkerboard sparsity, ill-conditioned matrices, and Cauchy heavy-tailed noise).

---

## 4. Raw Evidence & Provenance Storage

Every benchmark trial outputs an immutable provenance record containing:

- Workload ID and canonical contract version.
- Exact hardware topology fingerprint (CPU model, P/E-core count, RAM, OS build).
- Input dataset SHA-256 hash.
- Candidate source/IR transformation trace.
- Latency samples ($N \ge 10$): Mean, Median, Min, Max, $p95$, Standard Deviation.
- Peak working-set RAM during execution (MB).
- Error profile ($\text{MaxAbsError}$, $\text{RelativeL2}$, $\text{RMSE}$, $\text{PSNR}$, $\text{SSIM}$).
- Cryptographic proof certificate ID.
