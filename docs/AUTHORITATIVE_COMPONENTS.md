# LEO / HYPER: Authoritative Components & Single Source of Truth

**Document Version**: 1.0.0  
**Date**: September 2026  
**Rule**: For every capability, there is exactly one authoritative production module. All auxiliary, experimental, and legacy modules must delegate to or inherit from these authoritative implementations.

---

## 1. Single Source of Truth Matrix

```
┌──────────────────────────────┬──────────────────────────────────────────┬─────────────────────────────┐
│ Capability Responsibility    │ Authoritative Implementation Module      │ Execution Interface         │
├──────────────────────────────┼──────────────────────────────────────────┼─────────────────────────────┤
│ 1. Universal Escape Engine   │ hyper_cco.universal_escape_engine        │ UniversalEscapeEngine       │
│ 2. Workload Contract IR      │ hyper_cco.contract                       │ WorkloadContract            │
│ 3. Observable Compilation    │ hyper_x.wormhole_compiler.observable     │ UniversalObservableCompiler │
│ 4. Information Boundary      │ hyper_x.wormhole_compiler.info_boundary  │ InformationBoundaryAnalyzer │
│ 5. Proof-Carrying Work Elim. │ hyper_cco.proof_elimination              │ ProofCarryingElimination    │
│ 6. Counterfactual Execution  │ hyper_cco.counterfactual                 │ CounterfactualExecution     │
│ 7. 7-Mode Residual Recalc.   │ hyper_cco.residual_engine                │ ResidualEngine7Mode         │
│ 8. Lower-Bound Analysis      │ hyper_cco.lower_bound_analyzer           │ LowerBoundAnalyzer          │
│ 9. Hardware Advantage Invers.│ hyper_cco.hardware_advantage_analyzer    │ HardwareAdvantageAnalyzer   │
│ 10. Universality Analysis    │ hyper_cco.universality_analyzer          │ UniversalityAnalyzer        │
│ 11. Workload Universe        │ hyper_cco.workload_universe              │ WorkloadUniverse            │
│ 12. Coverage Engine          │ hyper_cco.coverage_engine                │ CoverageEngine              │
│ 13. Application Parity       │ hyper_cco.application_parity_engine      │ ApplicationParityEngine     │
│ 14. Claim Validation         │ hyper_cco.claim_validator                │ ClaimValidator              │
│ 15. Computational Maps       │ hyper_cco.maps                           │ Necessity/Wormhole/Frontier │
│ 16. Domain Adapters          │ hyper_cco.domain_adapters                │ Graphics/AI/Matrix/Science  │
│ 17. Heterogeneous Scheduler  │ hyper_cco.thermal_scheduler              │ ThermalAwareDeadlineSched.  │
│ 18. Anti-Cheat Provenance    │ hyper_cco.provenance_ledger              │ AntiCheatProvenanceLedger   │
│ 19. Adversarial Fuzzing      │ hyper_cco.adversarial_fuzzer             │ AdversarialContractFuzzer   │
│ 20. Master CLI & Driver      │ hyper.py / hyper_x.cli                   │ main()                      │
└──────────────────────────────┴──────────────────────────────────────────┴─────────────────────────────┘
```

---

## 2. Invariant Policies

1. **Non-Downgrade Invariant**: An `EXACT_EQUIVALENT` contract can never be satisfied by a predictive or approximate candidate.
2. **Provenance Invariant**: No execution report or benchmark entry can be emitted without candidate SHA-256 hash, git commit hash, timestamp, and hardware fingerprint.
3. **Audited Falsification Invariant**: An optimization claim is rejected if it fails on any adversarial or blind holdout test, regardless of training set accuracy.
4. **Offline First Invariant**: Core synthesis, compilation, execution, and verification run 100% locally on the host machine without external API dependencies.
