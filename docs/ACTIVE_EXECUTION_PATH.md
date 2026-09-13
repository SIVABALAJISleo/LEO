# HYPER / LEO Active Execution Path Specification

## 1. Authoritative Production Call Graph

A module is strictly classified as **`ACTIVE_PRODUCTION`** if and only if it is reachable from the authoritative execution path:

```
[User Request / Workload Input]
  │
  ├─> hyper_x/pipeline.py (AuthoritativePipeline.execute)
        │
        ├── [1] Contract Ingestion
        │     └── hyper_x/contract_ir/parser.py (ContractParser.parse)
        │           └── hyper_x/contract_ir/contract.py (ContractIR)
        │
        ├── [2] Workload Classification
        │     └── hyper_x/contract_ir/workload_classifier.py (classify_workload)
        │
        ├── [3] Information Boundary Analysis
        │     └── hyper_x/information_boundary/engine.py (InformationBoundaryEngine.analyze)
        │           └── hyper_x/information_boundary/influence_graph.py
        │
        ├── [4] Necessary-Work Compilation
        │     └── hyper_x/necessity/compiler.py (NecessaryWorkCompiler.compile)
        │           └── hyper_x/necessity/work_ledger.py (WorkLedger.record_work)
        │
        ├── [5] Pathway Search & Shortcut Evaluation
        │     └── hyper_x/pathway_search/search_engine.py (PathwaySearchEngine.find_cheapest_valid)
        │           ├── hyper_x/pathway_search/exact_reuse.py (ExactReuseEngine.lookup)
        │           ├── hyper_x/pathway_search/semantic_cache.py (SemanticCacheEngine.query)
        │           └── hyper_x/pathway_search/candidate.py (CandidatePathway)
        │
        ├── [6] Fail-Closed Verification
        │     └── hyper_x/verification/verifier.py (AuthoritativeVerifier.verify_candidate)
        │           ├── hyper_x/verification/numerical.py (NumericalVerifier.verify_tolerances)
        │           ├── hyper_x/verification/adversarial.py (AdversarialVerifier.generate_stress)
        │           └── hyper_x/verification/holdout.py (BlindHoldoutVerifier.evaluate)
        │
        ├── [7] Execution & Fallback Dispatch
        │     ├── (If Verified): Selected Candidate Execution (CPU P-core / iGPU)
        │     └── (If Rejected): hyper_x/fallback/engine.py (FallbackEngine.execute_exact_reference)
        │
        ├── [8] Deterministic Cross-Hardware Check
        │     └── hyper_x/decp/engine.py (DECPLayer.validate_reproducibility)
        │           ├── hyper_x/decp/manifest.py
        │           └── hyper_x/decp/comparator.py
        │
        ├── [9] Certificate Generation & Ledger Update
        │     ├── hyper_x/certificates/certificate.py (CertificateBuilder.issue)
        │     └── hyper_x/evidence/ledger.py (EvidenceLedger.record_evidence)
        │
        └── [10] Live Telemetry & Metric Publishing
              ├── hyper_x/telemetry/monitor.py (TelemetryMonitor.sample)
              └── hyper_x/dashboard.py (ParityDashboard.render)
```

---

## 2. Invariant Rules for Active Execution
1. **Zero Unverified Output**: No shortcut result is permitted to bypass the fail-closed verifier.
2. **Deterministic Provenance**: Every generated output captures full SHA-256 hashes of input tensors, contract definitions, candidate code revisions, and hardware fingerprints.
3. **Transparent Fallback**: When an approximation fails numerical or adversarial testing, fallback to the exact reference is executed transparently and recorded in `evidence_ledger.json`.
