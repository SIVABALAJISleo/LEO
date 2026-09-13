# HYPER / LEO — Claim Integrity & Scientific Audit Standard
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## Absolute Scientific Claim Rules

To guarantee uncompromising scientific integrity, the following rules are permanently enforced across all code, tests, and documentation:

1. **Zero Hardware Imitation**:
   - The host system is an Intel Core i5-12450H with Intel UHD Graphics (48 EUs) and 16 GB Unified RAM.
   - We do NOT claim to emulate CUDA cores, Tensor cores, RT cores, or GDDR7 memory.
   - We make the RTX 5090's hardware advantage unnecessary where the workload contract allows it via computation pathway transformation.

2. **Zero Fail-Open Verification**:
   - Verification status defaults strictly to `UNKNOWN` or `FAIL`.
   - In the absence of physical evidence or on exception, the status remains `UNKNOWN`. It is forbidden to default to `True` or `PASS`.

3. **Candidate-Coupled Verification**:
   - The exact candidate pathway that is benchmarked MUST be the exact candidate that is executed and verified.
   - Verification of baseline B cannot be cited as proof of candidate A.

4. **Honest Metric Separation**:
   - **Raw Hardware Parity**: ~1.85% (physical ratio between a 45W laptop SoC and a 450W/600W flagship desktop GPU).
   - **Exact Computational Parity**: 100% on discrete DECP mathematical identity workloads.
   - **Contract Parity**: 100% when verified shortcuts satisfy declared invariant bounds.
   - **Application Performance Parity**: Measured wall-clock latency vs application SLO.

5. **Cold vs Warm Separation**:
   - Cold runs (zero cache/kernel reuse) must be measured and reported separately from Warm runs.
   - Cache lookup time is measured separately and never disguised as arithmetic compute throughput.

6. **Evidence Classification Schema**:
   Every claim, benchmark number, and comparison is explicitly tagged with one of six evidence classes:
   - `MEASURED`: Physically timed on the host silicon.
   - `REFERENCE`: Published official specifications or vendor measurements.
   - `ESTIMATED`: Analytically derived with formal formulas.
   - `SIMULATED`: Theoretical model output (never used for parity claims).
   - `CACHED`: Cryptographically verified exact reuse hit.
   - `UNAVAILABLE`: Unproven or unmeasured (reported as UNKNOWN).
