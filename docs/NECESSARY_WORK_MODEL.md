# HYPER-Ω Necessary-Work Model & Mathematical Abstraction

## 1. Formal Definition
In classical brute-force computing, a system executes all operations dictated by an unoptimized reference implementation $R(x)$.
In HYPER-Ω, we model computation not as an imperative sequence of instructions to execute, but as an **information-theoretic mapping from inputs $x$ to a declared observable output $O(x)$ under contract $C$**.

Let $G = (V, E)$ be the full computation graph of reference $R$, where $V$ represents individual operations, tensor allocations, memory transfers, and synchronizations, and $E$ represents dataflow dependencies.

We define the **Necessary-Work Subgraph** $G^* = (V^*, E^*)$ as:
$$V^* = \{ v \in V \mid \text{Influence}(v, O) = \text{TRUE} \land \text{Reusable}(v) = \text{FALSE} \}$$

---

## 2. Node Classification Taxonomy
Every computational node in the `NecessaryWorkGraph` is classified into one of 8 mutually exclusive states:

1. **`REQUIRED`**: Operations whose mathematical results directly and irreducibly determine the value of the declared observable $O(x)$.
2. **`REUSABLE`**: Operations whose exact outputs have been computed previously and remain invariant across temporal steps or subregions.
3. **`INCREMENTAL`**: Operations whose values can be derived from prior state plus a delta update: $v_t = v_{t-1} + \Delta v$.
4. **`ELIMINABLE`**: Operations with zero reachability to the declared observable (e.g. culled geometry, unread tensor channels, off-diagonal elements in a trace calculation).
5. **`CONTRACT_OPTIONAL`**: Operations that provide fidelity beyond the declared contract threshold (e.g. 8th-bounce diffuse light paths when perceptual contract requires $\ge 40$ dB PSNR).
6. **`PREDICTIVE`**: Operations that can be synthesized via bounded statistical extrapolation and subsequently verified.
7. **`APPROXIMATE`**: Operations that tolerate reduced precision (INT8, FP16) without violating contract bounds.
8. **`UNKNOWN`**: Indeterminate dependency. **Law of Fail-Closed Pruning**: `UNKNOWN` nodes must NEVER be eliminated.

---

## 3. Verified Work Elimination Metric
The primary scientific metric of HYPER-Ω is **Verified Work Elimination (VWE)**, defined independently from wall-clock speedup:

$$\text{VWE} = 1.0 - \frac{\sum_{v \in V^*} \text{FLOPs}(v)}{\sum_{v \in V} \text{FLOPs}(v)}$$

### Distinction Between Work Elimination and Speedup
- **Work Elimination** measures the algorithmic and informational reduction in mathematical operations.
- **Speedup** ($\frac{\text{Latency}_{\text{ref}}}{\text{Latency}_{\text{cand}}}$) measures execution time. A candidate may achieve 75% work elimination with only 2x speedup due to memory bus bottlenecks, or achieve 3x speedup with 0% work elimination due to better cache tiling and SIMD vectorization.
- HYPER-Ω tracks and reports both metrics independently without conflation.
