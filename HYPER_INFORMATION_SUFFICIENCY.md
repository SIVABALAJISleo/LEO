# HYPER Information Sufficiency Engine

## 1. Overview
The Information Sufficiency Engine answers the foundational question of Minimum Verified Computation:
> **"What information is actually required by the user's contract, and what can be safely ignored or derived?"**

Conventional computing computes all elements of an intermediate tensor or state array blindly. The Information Sufficiency Engine traces output dependencies backwards from the user-facing contract to identify:
1. **Required Outputs**: The subset of outputs inspected by downstream consumers.
2. **Output Sensitivity**: The Jacobian $\frac{\partial \text{Output}}{\partial \text{Input}}$ identifying elements whose variations fall below the contract's error tolerance $\epsilon$.
3. **Discardable Dimensions**: Unused channels, zero-padded margins, and high-frequency noise.
4. **Decision Boundaries**: For classification, ranking, or thresholding tasks, only the sign or ordinal rank is needed—exact scalar magnitudes are irrelevant.
5. **Visible Geometry / Rays**: In rendering, geometry hidden behind opaque occluders requires zero shading computation.

---

## 2. Classification of Computation

Every operation in the computation DAG is categorized by information utility:

- **`ESSENTIAL`**: Required to satisfy the contract; cannot be derived or predicted within error $\epsilon$.
- **`CONDITIONALLY_ESSENTIAL`**: Required only if a branch or threshold condition is triggered.
- **`REDUNDANT`**: Identical to an already computed or cached value.
- **`DERIVABLE`**: Can be computed with fewer FLOPs via an invariant or closed-form statistic.
- **`PREDICTABLE`**: Can be estimated cheaply with confidence exceeding the verification threshold.
- **`DISCARDABLE`**: Output does not influence user-visible contract metrics.
- **`UNKNOWN`**: Insufficient static information; requires dynamic instrumentation.

---

## 3. Mathematical Formulation of Value Density

We define **Computational Value Density** ($V_D$) as:

$$V_D = \frac{\Delta \text{Information Content} \times \text{Sensitivity Weight}}{\text{FLOPs} + \alpha \cdot \text{Memory Bytes}}$$

Operations with high $V_D$ are prioritized and scheduled on high-throughput P-cores or iGPU vector units. Operations with low $V_D$ are pruned, downsampled, or deferred.
