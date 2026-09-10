# HYPER Scientific Claim Policy & Verification Protocol
**Standard of Rigor**: Uncompromising Scientific Truthfulness. Zero Tolerance for Fabrication or Hardware Faking.

---

## 1. Foundational Axioms

1. **Hardware Invariance Axiom**: Software cannot alter physical silicon hardware. No compiler or software engine creates physical NVIDIA CUDA cores, Tensor Cores, RT Cores, or dedicated GDDR/HBM memory bandwidth on an Intel Core i5 with integrated UHD graphics.
   $$\text{Physical Raw Silicon Parity } P_{\text{raw}} \equiv 0.0\%$$
2. **Workload Invariance Axiom**: A performance comparison is strictly invalid if the candidate silently reduces problem size, alters resolution, lowers sample counts, or truncates precision without explicit contract authorization.
3. **No Unearned Success Axiom**: An optimization search that fails to discover a verified shortcut is classified as `SEARCH_INCONCLUSIVE`. It must NEVER be reported as a success, pass, or wormhole discovery.
4. **Separation of Evidence Axiom**: Simulated execution timings, analytical models, and synthetic replays must never be labeled or reported as real hardware evidence. Only measurements collected via high-precision physical timers (`time.perf_counter_ns()`) on the target machine qualify as `REAL_HARDWARE`.

---

## 2. Prohibited Claims & Automatic Audit Rejections

The Automated Scientific Auditor (`scientific_auditor.py`) scans all code, commit messages, telemetry, certificates, and documentation. Any occurrence of the following patterns results in an automatic audit failure:

| Prohibited Statement | Scientific Violation | Mandatory Remediation |
|---|---|---|
| *"GPU replaced"* | Violates hardware reality. Software does not replace hardware. | Replace with: *"Eliminated X% of GPU-advantaged work under declared contract."* |
| *"100% NVIDIA parity"* | Conflates application outcome with silicon equivalence. | State exact metric: *"100% Application Contract Parity over feasible set."* |
| *"HYPER beats RTX 5090"* | False hardware equivalence. | Report measured latency and GADR/HAE work elimination on target workload. |
| *"Measured Power"* (without RAPL/sensors) | Analytical estimation passed off as sensor data. | Label strictly as `ESTIMATED_POWER` or `UNKNOWN`. |
| Hardcoded `functional_pass = True` | Circular verification without execution evidence. | Replace with 9-layer `UniversalFunctionalVerifier`. |

---

## 3. Five-Tier Verification Hierarchy

Every claim, certificate, and performance result must be classified into its verified level:

- **LEVEL 0: UNVERIFIED**
  - Candidate executed without crash, but has not undergone formal verification or adversarial stress testing. Cannot be published or certified.
- **LEVEL 1: SIMULATED**
  - Evaluated on analytical hardware models or architectural simulators. Permitted for exploratory research only; prohibited from physical hardware leaderboards.
- **LEVEL 2: EMPIRICALLY_VALIDATED**
  - Verified on nominal sample inputs against trusted reference implementations with relative error $\le \text{tolerance}$.
- **LEVEL 3: ADVERSARIALLY_VALIDATED**
  - Attacked by the 8-suite adversarial stress generator (zeros, extreme scale, ill-conditioned matrices, subnormals, boundary NaNs/Infs) and survived without invariant violation.
- **LEVEL 4: BLIND-HOLDOUT VALIDATED**
  - Evaluated on cryptographically seeded, out-of-distribution holdout inputs completely hidden from candidate generation and e-graph saturation.
- **LEVEL 5: FORMALLY VERIFIED**
  - Mathematically proven via algebraic equivalence, Freivalds probabilistic checks ($15$ rounds, $p > 99.997\%$), or symbolic SMT equivalence checking.

---

## 4. Truthful Statement Generation Guidelines

When authoring research results, adhere strictly to evidence-based terminology:

- **UNACCEPTABLE**: *"HYPER achieves 10x speedup over GPU."*
- **ACCEPTABLE**: *"For workload GEMM (128x128) under BOUNDED_APPROXIMATION contract (tolerance=1e-3), HYPER discovered a rank-8 factorization reducing necessary FLOPs by 87.5% with an effective speedup of 1.4x on Intel Core i5-12450H."*

- **UNACCEPTABLE**: *"All workloads closed at 100%."*
- **ACCEPTABLE**: *"Universal Workload Closure reached 100% across the evaluated registry: 8 workloads achieved verified wormholes, 2 workloads were proven to reach information-theoretic lower bounds, with 0 inconclusive searches."*
