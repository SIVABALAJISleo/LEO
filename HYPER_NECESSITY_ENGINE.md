# HYPER Necessity Engine

## 1. Core Principle
The Necessity Engine proves whether each operation in the Computation IR must physically execute. No optimization assumes an operation is mandatory simply because the conventional algorithm included it.

---

## 2. The 11 Invariant Queries

For every candidate operation $O_i$, the Necessity Engine evaluates:
1. **Direct Necessity**: Does the contract output change if $O_i$ is omitted?
2. **Reuse**: Is $O_i(x)$ already present in strategy memory, L1/L2 cache, or the semantic hash index?
3. **Derivability**: Can $O_i$ be derived from an invariant $\sum x_i$ or sufficient statistic (e.g., Welford online variance)?
4. **Elimination**: Is $O_i$ dead code under current contract conditions?
5. **Postponement**: Can $O_i$ be lazily deferred until a consumer explicitly requests its value?
6. **Partial Evaluation**: Can a partial sum or top-$k$ truncation satisfy the contract?
7. **Sufficient Statistic**: Can moments (mean, variance) substitute for the full distribution?
8. **Cheaper Exact Algorithm**: Does an exact reformulation (Winograd, Strassen, Karatsuba) execute with fewer operations?
9. **Bounded Approximation**: Does a low-rank, sparse, or quantized representation satisfy error bound $\epsilon$?
10. **Predict + Verify**: Can a lightweight neural or statistical predictor propose $\hat{y}$ verified in $O(N)$ instead of $O(N^2)$?
11. **Break-Even Analysis**: Does the overhead of optimizing $O_i$ exceed the runtime savings?

---

## 3. Necessity Audit Trail
Every elimination or substitution emits a cryptographic audit token recorded in the `WorkLedger`, verifying that the mathematical contract was respected.
