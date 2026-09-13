# HYPER / LEO Evidence Specification & Provenance Standards

## 1. Provenance Classification
In accordance with Section 28 of the Master Evolution Protocol, every measurement, record, and benchmark entry in the repository must carry an explicit evidence provenance tag:

| Provenance Tag | Strict Definition | Permitted Usage |
| :--- | :--- | :--- |
| **`MEASURED`** | Wall-clock measurement recorded directly on physical host silicon (Intel Core i5-12450H / Intel UHD Graphics) using high-resolution timers (`time.perf_counter_ns()`). | Authoritative scorecards, regression checks, and claims. |
| **`REFERENCE`** | Established independent external standard (e.g. OpenBLAS, PyTorch CPU gold reference, published specification). | Independent verification baselines only. Never reported as candidate throughput. |
| **`ESTIMATED`** | Model-based cost projection derived from device calibration parameters. | Internal pathway search ranking. Never published as measured parity. |
| **`SIMULATED`** | Pure mathematical or synthetic emulation (e.g. mock latency). | Algorithmic exploration only. Explicitly forbidden in parity claims. |
| **`CACHED`** | Direct retrieval from exact reuse storage with verified cryptographic hash. | Must be labeled `CACHED_EXACT`. Never reported as raw compute FLOPs. |
| **`UNAVAILABLE`** | Metric not physically measurable on host. | Evaluates strictly to `UNKNOWN` in verifiers. |

---

## 2. Cryptographic Integrity Rules
1. **No Certificate, No Verified Status**: No pathway can claim `VERIFIED` status without an associated entry in `evidence_ledger.json` and a signed `execution_certificate.json`.
2. **Immutable Input/Output Hashes**: Every certificate records:
   - `input_hash`: SHA-256 hash of raw input tensor bytes.
   - `output_hash`: SHA-256 hash of candidate output tensor bytes.
   - `reference_hash`: SHA-256 hash of trusted reference output tensor bytes.
   - `contract_hash`: SHA-256 hash of the canonical JSON-serialized `ContractIR`.
   - `candidate_hash`: SHA-256 hash of candidate kernel source implementation.
3. **Anti-Circularity Invariant**: The reference implementation and the verifier are completely decoupled from candidate code. The candidate implementation physically produces the output data evaluated by the verifier.
