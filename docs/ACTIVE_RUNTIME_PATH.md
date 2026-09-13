# HYPER / LEO — Authoritative Active Runtime Path
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## Complete Runtime Call Graph

The master execution pathway executes as a single, unbranching, authoritative linear pipeline:

```
[USER REQUEST / WORKLOAD INVOCATION]
                  │
                  ▼
         [ContractParser.parse()]
  - Extracts workload_id, observable, application
  - Assigns exactness_mode, tolerances, latency/memory SLOs
                  │
                  ▼
   [InformationBoundaryEngine.analyze()]
  - Performs SVD spectral energy decay & sparsity profiling
  - Explicitly partitions input into:
      1. WHAT_MUST_BE_COMPUTED
      2. WHAT_DOES_NOT_NEED_TO_BE_COMPUTED
      3. WHAT_CAN_BE_REUSED
      4. WHAT_CAN_BE_APPROXIMATED
      5. WHAT_CAN_BE_PREDICTED
      6. WHAT_MUST_BE_VERIFIED
                  │
                  ▼
       [NecessaryWorkCompiler.compile()]
  - Constructs operations DAG (DELETE, REUSE, MERGE, FACTOR, REORDER,
    SPARSE, LOW_RANK, COMPRESS, APPROXIMATE, PREDICT, RECONSTRUCT, etc.)
  - Computes exact FLOP accounting:
      Work Elimination = 1 - (Necessary_FLOPs / Original_FLOPs)
                  │
                  ▼
       [PathwaySearchEngine.search()]
  - Queries ExactReuseEngine (SHA-256 complete 14-parameter identity)
  - Queries SemanticCacheEngine (Strictly isolated, labeled non-exact)
  - Queries RepresentationSearch (14 data representations)
  - Queries DiscoveryEngine (Algebraic, low-rank, structured sparsity)
  - Queries PredictionEngine (Lossless speculative draft)
  - Queries ReconstructionEngine (Temporal/spatial scene reconstruction)
  - Generates ranked candidate list ordered by minimum predicted cost
                  │
                  ▼
        [AuthoritativeVerifier.verify()]
  - Iterates through candidates: Candidate benchmarked == candidate verified
  - Fail-closed verification (status defaults to UNKNOWN, never PASS)
  - Numerical checks: abs_error <= tol AND rel_error <= tol
  - Adversarial stress tests (NaN, Inf, pathological noise)
  - Blind holdout verification (records generalization gap)
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
     [PASS]              [FAIL]
        │                   │
        │                   ▼
        │        [FallbackEngine.execute()]
        │         - Safe deterministic ladder:
        │           Shortcut -> Next Candidate -> Original BLAS -> Emergency
        │         - Fallback status recorded: FALLBACK_EXECUTED
        │                   │
        └─────────┬─────────┘
                  ▼
           [DECPEngine.run()]
  - Track A (Same Computation): Bit-identical verification
  - Track B (Different Computation): Contract-valid alternative pathway
  - ULP distance and tensor SHA-256 digests
                  │
                  ▼
      [TelemetryMonitor.sample()]
  - Real-time CPU P/E core load, UHD load, RAM RSS, thermal stability
                  │
                  ▼
    [ExecutionCertificate.generate()]
  - Cryptographic SHA-256 tamper-evident digital signature
  - Complete work breakdown (Original, Necessary, Eliminated, Reused)
  - Provenance: MEASURED on target host silicon
                  │
                  ▼
       [EvidenceLedger.record()]
  - Appends certificate to persistent append-only ledger
  - Updates candidate registry
                  │
                  ▼
       [ParityDashboard.render()]
  - Dynamically computes RTX5090_EQUIVALENCE_INDEX and 16 scores
  - Emits parity_report.json (Zero hardcoded values)
                  │
                  ▼
            [FINAL RESULT]
```
