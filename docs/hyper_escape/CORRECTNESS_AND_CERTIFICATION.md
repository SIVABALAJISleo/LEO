# Exactness, Correctness & Formal Certification Engine

## 1. Non-Negotiable Verification Principles

1. **Independent Reference Implementation:** Every candidate must be validated against a trusted canonical reference (e.g. NumPy BLAS, SciPy FFT, Python integer math). The candidate is never allowed to be its own reference.
2. **Fail-Closed Gate:** Any exception, mismatch, non-finite value (`NaN`, `Inf`), or missing metric results in `FAILED_CORRECTNESS`.
3. **No Upgrades:** An approximate transformation (e.g. INT8 quantization or lossy compression) can **never** receive `EXACT_VERIFIED` status, regardless of speedup.

---

## 2. Nine Formal Certification States

```
                           +----------------------+
                           |   CANDIDATE OUTPUT   |
                           +----------+-----------+
                                      |
                                      v
                           [Contract Verification]
                                 /          \
                           (Pass)            (Fail)
                            /                  \
              +------------+---------+          v
              | Check Exactness Mode |    FAILED_CORRECTNESS
              +------------+---------+
              /      |          |    \
             /       |          |     \
  [BITWISE] [NUMERIC] [APPROX] [PROB]
     |          |         |       |
     v          v         v       v
   EXACT     CONTRACT  APPROX   PROB
  VERIFIED   VERIFIED  VERIFIED VERIFIED
```

- `EXACT_VERIFIED`: Bitwise 100% equivalence demonstrated.
- `CONTRACT_VERIFIED`: Floating-point output satisfies conjunctive bounds.
- `APPROXIMATE_VERIFIED`: Output within explicit user approximation budget.
- `PROBABILISTICALLY_VERIFIED`: Meets statistical confidence interval bounds.
- `PERFORMANCE_VERIFIED`: Correct and exceeds performance baseline.
- `FAILED_CORRECTNESS`: Violated contract tolerances or shape requirements.
- `FAILED_PERFORMANCE`: Correctness passed but introduced severe latency regression.
- `UNSUPPORTED`: Workload IR construct cannot be parsed by current adapters.
- `UNCERTIFIED`: Untested candidate or pending evaluation.

---

## 3. Cryptographic Provenance

Every `FormalCertificate` includes:

- `contract_hash`: SHA-256 hash of the immutable workload specification.
- `provenance_hash`: SHA-256 signature binding certificate ID, workload ID, certified state, and speedup.
