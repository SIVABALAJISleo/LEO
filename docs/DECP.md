# HYPER / LEO — Deterministic Exact-Compute & Parity (DECP)
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Track A vs Track B Architecture

HYPER-DECP enforces strict separation between two independent verification tracks:

### TRACK A — SAME COMPUTATION
- **Core Question:** *"Did the CPU/iGPU execute the exact declared computational specification and produce bit-identical results to the reference?"*
- **Required Metric:** Cryptographic output SHA-256 digest match ($H(\text{cand}) == H(\text{ref})$).
- **Target Workloads:** Discrete sorting, exact graph search, cryptographic operations, exact numerical solvers.

### TRACK B — DIFFERENT COMPUTATION
- **Core Question:** *"Did HYPER discover a mathematically or contract-valid alternative pathway that requires significantly less work?"*
- **Required Metric:** Invariant preservation within declared error bounds ($\epsilon_{\text{rel}}$, $\epsilon_{\text{abs}}$, $\text{SSIM}$).
- **Target Workloads:** Low-rank GEMM, block-sparse attention, speculative decoding, temporal scene reconstruction.

---

## 2. Definitive Status Classifications

1. `EXACT_MATCH`: Bit-identical output hash on target hardware.
2. `NUMERICAL_MATCH`: Output falls strictly within machine epsilon / declared ULP bounds.
3. `CONTRACT_MATCH`: Output satisfies contract bounds under alternative representation.
4. `COMPUTATIONALLY_DIFFERENT_BUT_VALID`: Verified shortcut with demonstrable FLOP elimination.
5. `MISMATCH`: Output violates declared contract invariants.
6. `UNKNOWN`: Insufficient evidence or unexecuted verification (NEVER reported as PASS).
