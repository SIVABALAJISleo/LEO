# HYPER / LEO — Ultra-Sonic System Architecture
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Core Architectural Principle

HYPER transforms the traditional systems question:
> *"How do we execute this brute-force workload faster on available hardware?"*

into the fundamental mathematical question:
> *"What is the minimum valid computation required to satisfy the requested observable under the declared contract?"*

### Hardware Constraint
- **Target CPU:** Intel Core i5-12450H (8 Cores, 12 Threads: 4 Performance-cores + 4 Efficient-cores, AVX2).
- **Target iGPU:** Intel UHD Graphics (48 Execution Units).
- **Target RAM:** 16 GB Unified System RAM (45W Package Envelope).
- **Constraint:** Zero dedicated GPU, zero cloud acceleration, zero hardware simulation. Software algorithms only.

---

## 2. Linear Execution Pipeline

HYPER enforces a single authoritative pipeline:
1. **Contract Parser & Observable Identifier** (`hyper_x/contract_ir/`): Declares typed constraints across 7 correctness modes.
2. **Information Boundary Engine** (`hyper_x/information_boundary/`): SVD spectral decay & 6-way information partitioning.
3. **Necessary-Work Compiler** (`hyper_x/necessity/`): Formal DAG operations & FLOP ledger ($1 - \frac{\text{Necessary}}{\text{Original}}$).
4. **Adaptive Representation Search** (`hyper_x/representations/`): Evaluates 14 data formats.
5. **Algorithm Discovery Engine** (`hyper_x/discovery/`): Falsification-driven candidate search lifecycle.
6. **Prediction & Reconstruction Engines** (`hyper_x/prediction/`, `hyper_x/reconstruction/`): Speculative target validation & temporal scene reconstruction.
7. **Real-Time CPU + UHD Orchestrator & Memory Manager** (`hyper_x/orchestrator/`, `hyper_x/memory/`): Live telemetry routing within 16 GB RAM boundary.
8. **Fail-Closed Authoritative Verifier** (`hyper_x/verification/`): Zero-default verifier with numerical, adversarial, and holdout checks.
9. **HYPER-DECP Deterministic Layer** (`hyper_x/decp/`): Track A (Bit-identical) vs Track B (Contract-valid).
10. **Tamper-Evident Certificate & Ledger** (`hyper_x/certificates/`, `hyper_x/evidence/`): Cryptographic SHA-256 signatures.
11. **Live Parity Scorecard Dashboard** (`hyper_x/dashboard.py`): Real-time evidence-derived metric reporting.
