# HYPER: Information Sufficiency Specification

## 1. Executive Concept
The **Information Sufficiency Engine** (`information_sufficiency/`) answers the foundational question:
> **Which information from the complete computation can actually affect the requested output under the frozen contract?**

Traditional compilers blindly optimize whatever operations the developer wrote. HYPER instead inspects downstream consumers to discard computation whose outputs are never read or whose contributions lie below contract perception thresholds.

---

## 2. Seven-Class Node Classification Taxonomy

Every operation and tensor in the universal computation graph is categorized into one of seven distinct classes:

| Classification | Definition | Elimination Strategy |
|---|---|---|
| `ESSENTIAL` | Directly influences downstream output within contract bounds. | Optimize implementation (SIMD, fusion, loop tiling). |
| `CONDITIONALLY_ESSENTIAL` | Influences output only under specific input regimes or threshold conditions. | Adaptive depth / early exit evaluation. |
| `REDUNDANT` | Identical or algebraically equivalent to an existing active result. | Subgraph reuse, common subexpression elimination, or cache lookup. |
| `DERIVABLE` | Output can be produced via a cheaper exact or bounded mathematical shortcut. | Algebraic reformulation, low-rank SVD, or sublinear transform. |
| `PREDICTABLE` | High confidence speculative prediction verifiable via cheap spot checks. | Predict-Verify-Accept cascade with fallback. |
| `DISCARDABLE` | Produces output components with zero downstream consumption. | Dead-code elimination (DCE) and channel culling. |
| `UNKNOWN` | Insufficient profile data to prove safety. | Conservatively preserved as essential until profiled. |

---

## 3. Downstream Sensitivity & Value Density
- **Top-K Selection**: When an application requires only top-$k$ elements, full sorting $O(N \log N)$ is replaced by QuickSelect / Argpartition $O(N)$.
- **Frustum & Region-of-Interest Culling**: Geometry and pixels outside the active viewport are culled prior to rasterization or shading.
- **Computation Value Density**:
$$\text{Value Density} = \frac{\Delta \text{Information Gain (bits)} \times 10^6}{\text{Total Work Units}}$$
Computations with $\text{Value Density} < 0.1$ are prioritized for elimination or bounded approximation.
