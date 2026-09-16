# HYPER-Ω Benchmark Integrity & Anti-Fraud Specification

## 1. Zero-Cheating Policy
HYPER-Ω enforces an automated anti-cheating system via `BenchmarkIntegrityGuard`.
Any benchmark harness, candidate function, or measurement run that exhibits fraudulent patterns is automatically flagged as **`INVALID`**.

**Rule**: An `INVALID` result can NEVER be converted into a `PASS`.

---

## 2. Prohibited Patterns & Automatic Rejection Criteria

The following patterns trigger immediate disqualification:

1. **Hard-Coded Performance Numbers**:
   - Assigning constant speedups: `speedup = 2.15`
   - Assigning constant work elimination percentages: `work_elimination = 70.0`
   - Hardcoded execution timings: `latency = 9.8`

2. **Artificial Timing Injection**:
   - Using `time.sleep(...)` to fabricate latency differences between reference and candidate runs.

3. **Precomputed Benchmark Oracles**:
   - Returning pre-stored arrays or lookup tables indexed by benchmark names (e.g. `if "test_case" in name: return lookup_table`).

4. **Self-Comparison (Identity Verification)**:
   - Comparing a candidate function against itself or trivially wrapping the reference function without algorithmic modification.

5. **Silent Contract Downgrades**:
   - Downscaling image resolution from 1080p to 720p without declaring it in the contract.
   - Reducing precision (e.g. FP32 to INT4) when the contract specifies exact numerical equivalence.
   - Using smaller model checkpoints without demonstrating equivalence to the target model.

6. **Hardware Emulation Claims**:
   - Reporting that software executed on NVIDIA CUDA Tensor Cores or GDDR7 memory when running on Intel hardware.

---

## 3. Automated Inspection Mechanism
The `BenchmarkIntegrityGuard` performs two distinct audit passes:
- **Static Inspection**: Uses Python AST and regex inspects source code of candidate callables for suspicious patterns.
- **Dynamic Telemetry Inspection**: Validates that latency is non-zero, raw clock measurements exist, and claimed work elimination percentages fall strictly in $[0.0, 100.0]$.
