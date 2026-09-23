# HYPER 8-Level Verification & Counterexample Protocol

## 1. Principles of Verification

In the HYPER discovery engine, no performance improvement or algorithmic transformation is accepted without passing through the formal **Verification Stack**. Speedup without verification is treated as corruption.

---

## 2. The 8-Level Verification Stack

```
 LEVEL 8: FORMAL EQUIVALENCE & THEOREM PROVING
    ▲
    │
 LEVEL 7: INDEPENDENT ISOLATED SANDBOX VERIFICATION
    ▲
    │
 LEVEL 6: METAMORPHIC RELATION TESTING
    ▲
    │
 LEVEL 5: PROPERTY-BASED INVARIANT TESTING
    ▲
    │
 LEVEL 4: NUMERICAL TOLERANCE BUDGET EVALUATION
    ▲
    │
 LEVEL 3: BIT-EXACT OUTPUT COMPARISON
    ▲
    │
 LEVEL 2: DIFFERENTIAL TEST SUITES (REFERENCE VS CANDIDATE)
    ▲
    │
 LEVEL 1: ISOLATED UNIT TESTING & REGRESSION GATES
```

### Level 1: Isolated Unit Testing
- Verifies that candidate functions execute without throwing unhandled exceptions, memory faults, or infinite loops.
- Enforces strict input validation on data types, array dimensionality, and memory layouts.

### Level 2: Differential Testing
- Executes both the canonical unoptimized reference function $f_{ref}(x)$ and the discovered pathway candidate $f_{cand}(x)$ on identical inputs across hundreds of randomized trials.
- Captures output deviations across varied seed initializations.

### Level 3: Bit-Exact Output Comparison
- Mandatory for contracts specifying `ExactnessTier.BIT_EXACT`.
- Computes SHA-256 digests over output memory buffers.
- Requires $hash(f_{ref}(x)) == hash(f_{cand}(x))$.

### Level 4: Numerical Tolerance Budget Evaluation
- Mandatory for numerical floating-point workloads (`FP64`, `FP32`, `FP16`).
- Evaluates:
  $$\max_i |y_{cand}[i] - y_{ref}[i]| \le \epsilon_{abs} + \epsilon_{rel} \cdot |y_{ref}[i]|$$
- Flags any candidate whose numerical drift exceeds the contract budget as `TOLERANCE_EXCEEDED`.

### Level 5: Property-Based Invariant Testing
- Tests structural mathematical invariants:
  - *Idempotency*: $f(f(x)) == f(x)$ for projections and sorting.
  - *Monotonicity*: $x_1 \le x_2 \implies f(x_1) \le f(x_2)$ for monotonic transforms.
  - *Permutation Invariance*: Output elements of a sorting network must be an exact multiset permutation of the input elements.

### Level 6: Metamorphic Testing
- Tests input/output relations under domain-specific transformations without requiring known ground-truth labels:
  - Linear scaling: $f(\alpha \cdot x) == \alpha \cdot f(x)$ for linear operators.
  - Spatial translation: $f(T(x)) == T(f(x))$ for translation-equivariant convolutions.

### Level 7: Independent Isolated Sandbox Verification
- Re-executes the candidate in an out-of-process clean environment with fresh memory allocations.
- Proves that the candidate does not rely on hidden global state, memoized cache leakage, or side-channel inputs.

### Level 8: Formal Equivalence & Proof Discovery
- Applies symbolic computer algebra and rewrite rules (e.g. Horner expansion, matrix multiplication commutativity/associativity).
- Emits formal `ProofCertificate` with machine-checkable deduction steps.
- Distinguishes between `EMPIRICALLY_VERIFIED` (passed Levels 1-7) and `FORMALLY_PROVED` (passed Level 8).

---

## 3. Hostile Adversarial Counterexample Protocol

Every candidate that passes verification is immediately attacked by the **Adversarial Counterexample Engine**:

1. **Random Distribution Attacks**:
   Uniform, normal, exponential, and Cauchy random inputs generated over millions of samples.
2. **Boundary & Pathological Edge Cases**:
   Zeroes, extreme infinities, NaNs, denormalized floats, maximum integer values ($2^{31}-1, 2^{63}-1$), empty lists, single-element collections, and all-duplicate arrays.
3. **Adversarial Gradient Optimization**:
   For continuous functions, uses numerical gradient ascent to search for the input $x^*$ that maximizes discrepancy:
   $$x^* = \arg\max_x \|f_{cand}(x) - f_{ref}(x)\|$$
4. **Anti-Structure Inputs**:
   Permuted, reverse-sorted, or maximally noisy inputs specifically designed to defeat caching or sorting assumptions.

If any attack succeeds, the counterexample is:
- Minimized to its smallest reproducible form.
- Recorded in the Knowledge Graph with a `CONTRADICTED_BY` relationship.
- Fed into the Failure Memory to prune future search spaces.
