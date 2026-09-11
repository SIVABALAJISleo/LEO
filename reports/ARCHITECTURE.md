# LEO / HYPER: Master Architecture Report

**Document**: `reports/ARCHITECTURE.md`  
**Version**: 3.0.0  
**Target Hardware**: Intel Core i5-12450H (AVX2/FMA) + Intel UHD Graphics (48 EUs), 16 GB RAM, Windows 11.

---

## 1. Architectural Mandate

The system enforces one unified computational discovery pipeline:

```
INPUT -> WORKLOAD CAPTURE -> CONTRACT IR -> OBSERVABLE COMPILER -> 
INFORMATION BOUNDARY -> NECESSARY-WORK ANALYSIS -> COUNTERFACTUAL ELIMINATION -> 
REPRESENTATION DISCOVERY -> ALGORITHM DISCOVERY -> PROGRAM REWRITE -> 
HYPER IR -> COST MODEL -> HARDWARE SCHEDULER -> CPU / iGPU / HYBRID -> 
INDEPENDENT VERIFIER -> ADVERSARIAL TESTING -> BLIND HOLDOUT -> 
EXECUTION CERTIFICATE -> KNOWLEDGE BASE -> FUTURE SEARCH
```

---

## 2. Structural Layer Separation

1. **Contract Layer (`hyper_cco.contract`)**:
   Enforces 10 non-negotiable correctness classes.
2. **Analysis Layer (`hyper_cco.lower_bound_analyzer`, `hyper_x.wormhole_compiler.info_boundary`)**:
   Identifies essential operations and classifies boundaries into Required, Conditional, Redundant, Reusable, Predictable, Approximable, and Unknown.
3. **Synthesis Layer (`hyper_cco.proof_elimination`, `hyper_cco.residual_engine`, `hyper_cco.domain_adapters`)**:
   Employs proof-carrying elimination, 7-mode residual recalculation, and e-graph rewrites.
4. **Execution Layer (`hyper_cco.thermal_scheduler`, `hyper_x.hardware.fingerprint`)**:
   Multi-objective scheduling across Intel P-cores, E-cores, and Intel UHD graphics.
5. **Verification & Provenance Layer (`hyper_cco.provenance_ledger`, `hyper_cco.adversarial_fuzzer`)**:
   Architecturally isolated independent verification emitting cryptographically signed execution certificates.
