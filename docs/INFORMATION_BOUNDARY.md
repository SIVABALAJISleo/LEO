# HYPER / LEO — Information Boundary Specification
**Document Version:** 2.0.0 (Ultra-Sonic Master Engineering)

---

## 1. Information Partitioning Architecture

The Information Boundary Engine determines the minimal sufficient statistic required to determine an observable.
It explicitly categorizes input data into six distinct partitions:

1. **`WHAT_MUST_BE_COMPUTED`**: Core irreducible subspace components that directly dictate the observable result.
2. **`WHAT_DOES_NOT_NEED_TO_BE_COMPUTED`**: Null space residuals, occluded geometry, and zero-influence components.
3. **`WHAT_CAN_BE_REUSED`**: Identical historical states verified via cryptographic SHA-256 provenance.
4. **`WHAT_CAN_BE_APPROXIMATED`**: Bounded perturbations where error falls strictly within contract tolerance $\epsilon$.
5. **`WHAT_CAN_BE_PREDICTED`**: Speculative drafts, autoregressive continuations, and temporal trajectory trends.
6. **`WHAT_MUST_BE_VERIFIED`**: All candidate outputs, approximations, and observable-influencing nodes.

---

## 2. Spectral Energy & Rank Boundary

For matrix operations $Y = A \cdot B$:
- Singular Value Spectrum $S = \text{diag}(\sigma_1, \sigma_2, \dots, \sigma_k)$ is evaluated.
- Cumulative energy threshold:
  $$\sum_{i=1}^{r} \sigma_i^2 \ge 0.99 \cdot \sum_{i=1}^{k} \sigma_i^2$$
- When $r \ll \min(M, K)$, rank $r$ defines the information boundary, eliminating $(M \cdot K - M \cdot r)$ redundant dimensions.
