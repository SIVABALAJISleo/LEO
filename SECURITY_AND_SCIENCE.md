# Security & Scientific Governance: HYPER Ω

## 1. Scientific Integrity Policy
HYPER Ω operates under the strict rule:
> *"Do not make weak hardware physically become stronger hardware. Discover whether the application mathematically needed that computation in the first place."*

### Core Invariants:
1. **Never Fabricate Equivalence**: If a candidate shortcut diverges from reference output on even 1 test case, it is rejected permanently.
2. **Never Mask Approximation as Exact**: Lossy compression, low-bit quantization, and heuristic predictions are categorized as `APPROXIMATE` or `HEURISTIC`, never `PROVEN_EXACT`.
3. **Fail-Closed by Default**: Any unproven candidate immediately falls back to canonical reference execution.
4. **Cryptographic Provenance**: Every accepted escape generates a `ScientificCertificate` bearing SHA-256 hashes of the input, candidate code, proof statement, and mathematical contract.

## 2. Red-Team & Adversarial Protection
- **Cache Anti-Cheating**: Cache keys incorporate input hash, contract hash, code hash, model hash, and host hardware fingerprint to prevent cross-benchmark cache poisoning.
- **Timing Contamination Prevention**: Benchmarks are strictly decoupled from reference evaluation and proof verification passes.
- **Self-Falsification (--falsify)**: Evaluates edge cases (zeros, ones, negative values, extreme floating-point magnitudes) before promoting any new rewrite rule.
