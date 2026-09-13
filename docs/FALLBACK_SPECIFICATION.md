# HYPER / LEO Fallback Architecture & Degradation Ladder

## 1. The Fallback Principle
In HYPER, a fallback is not a runtime failure:
> **"Fallback is not failure. Fallback is a first-class citizen of the architecture."**

Whenever a candidate shortcut, approximation, low-rank factorization, or speculative draft fails verification, the engine must gracefully degrade through a deterministic fallback ladder until mathematical correctness is guaranteed.

---

## 2. The Multi-Tier Degradation Ladder

```
[Candidate Shortcut Attempted]
               │
               ▼
   [Tier 1: Verifier Check] ────(PASS)────> [Output Validated]
               │ (FAIL)
               ▼
[Tier 2: Conservative Approximation]
   (e.g., Higher Rank r=32 instead of r=8, INT8 instead of INT4)
               │
               ▼
   [Tier 2: Verifier Check] ────(PASS)────> [Output Validated]
               │ (FAIL)
               ▼
[Tier 3: Exact Algorithmic Reformulation]
   (e.g., Strassen / Winograd / FFT convolution)
               │
               ▼
   [Tier 3: Verifier Check] ────(PASS)────> [Output Validated]
               │ (FAIL)
               ▼
[Tier 4: Exact Reference Baseline]
   (Canonical dense FP32 BLAS kernel on CPU P-core AVX2)
               │
               ▼
    [Guaranteed Correct Output]
```

---

## 3. Fallback Accounting & Transparency
1. Every fallback event is explicitly logged in `evidence_ledger.json` with the root failure cause (e.g. `NumericalToleranceExceeded`, `AdversarialResidualSpike`, `ConditionNumberUnstable`).
2. The runtime status of a fallback execution is reported as `FALLBACK_ENGAGED` (never disguised as an accelerated pass).
3. The fallback path guarantees that the application never produces corrupted or silent NaN/Inf results.
