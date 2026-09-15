# The Real Execution Path of LEO / HYPER (Part 2)

See full documentation at [reports/REAL_EXECUTION_PATH.md](file:///c:/Users/sivab/OneDrive/Documents/HYPER/reports/REAL_EXECUTION_PATH.md).

```
[1. User API Call]
    │  api.py / hyper.cli.py / MasterEngine.execute_workload_end_to_end()
    ▼
[2. Contract Construction & Fail-Closed Validation]
    │  hyper/contracts/contract.py :: Contract(...)
    ▼
[3. Multi-State Cryptographic Identity Cache]
    │  hyper/cache/exact_cache.py :: ExactCache.get(...)
    ▼
[4. Information Boundary Analysis]
    │  hyper_x/information_boundary/
    ▼
[5. Necessary-Work Decomposition]
    │  hyper_x/necessary_work/compiler.py :: UniversalNecessaryWorkCompiler
    ▼
[6. Candidate Optimization Selection]
    │  hyper/low_rank/, hyper/sparsity/, hyper/incremental.py
    ▼
[7. Heterogeneous Backend Scheduling]
    │  hyper/scheduler/heterogeneous_scheduler.py (CPU_AVX2 / OpenVINO UHD / Hybrid)
    ▼
[8. Independent Mathematical Verification]
    │  hyper/verification/verifier.py (Freivalds / Numerical)
    ▼
[9. Provenance Logging & Output Emission]
       evidence_ledger.json & ExecutionCertificate
```
