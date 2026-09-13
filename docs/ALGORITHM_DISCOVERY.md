# HYPER / LEO — Falsification-Driven Algorithm Discovery
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Discovery Candidate Lifecycle

HYPER upgrades algorithm optimization into a rigorous falsification-driven search pipeline. Candidates must progress through a mandatory 9-stage lifecycle:

```
[GENERATED]
    │
    ▼
[STATIC_CHECK] ──► Validates signature, dependencies, memory footprint
    │
    ▼
[EXECUTION] ──► Physical execution on host silicon
    │
    ▼
[CORRECTNESS] ──► Numerical tolerance verification (abs_err <= tol AND rel_err <= tol)
    │
    ▼
[ADVERSARIAL] ──► Stress-testing against pathological noise, NaNs, Infs, rank-deficiency
    │
    ▼
[HOLDOUT] ──► Evaluation on blind, frozen unseen test distributions
    │
    ▼
[PERFORMANCE] ──► Wall-clock latency and throughput measurement vs baseline
    │
    ▼
[PROMOTED / REJECTED] ──► Candidate registered in candidate_registry.json or logged to failure map
```

### Golden Rule
**A candidate is NEVER promoted based solely on predicted performance.** It must execute physically and survive every falsification stage.
