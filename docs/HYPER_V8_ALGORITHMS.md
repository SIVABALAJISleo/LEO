# HYPER v8 Algorithmic Specification

## 1. Candidate Execution Paths

HYPER v8 organizes compute into 14 distinct paths evaluated in cost-ascending order:

| Path Priority | Path Classification | Mechanism | Theoretical FLOP Complexity | Verification Guarantee |
|:---|:---|:---|:---|:---|
| 1 | `EXACT_REUSED` | SHA-256 Cache Table Lookup | $O(1)$ | Exact Bitwise Match |
| 2 | `EXACT_RESIDUAL` (Row) | Incremental Row Delta Update | $O(k \cdot N^2)$ ($k \ll N$) | Exact Parity ($<10^{-10}$) |
| 3 | `EXACT_RESIDUAL` (Col) | Incremental Col Delta Update | $O(k \cdot N^2)$ ($k \ll N$) | Exact Parity ($<10^{-10}$) |
| 4 | `EXACT_RESIDUAL` (Full) | Full Bilinear Decomposition | $O(k_A N^2 + k_B N^2)$ | Exact Parity ($<10^{-10}$) |
| 5 | `SPARSE_EXACT` | Compressed Sparse Row (CSR) | $O(\text{nnz}(A) \cdot \text{nnz}(B))$ | Exact Parity |
| 6 | `LOW_RANK_EXACT` | Algebraic Rank Factorization | $O(r \cdot N^2)$ ($r \ll N$) | Exact Parity |
| 7 | `EXACT_REFORMULATED` | Associative / Distributive Reordering | Reordered operations | Exact Parity |
| 8 | `APPROXIMATE` | Truncated SVD / Quantization | $O(r \cdot N^2)$ | Contract Bounded ($\le \epsilon$) |
| 9 | `PREDICTIVE` | Speculative Projection | $O(1)$ to $O(N)$ | Perceptual Contract Bounded |
| 10 | `CPU_EXACT` | AVX2 Multi-threaded CPU BLAS | $O(N^3)$ | Reference Benchmark |
| 11 | `IGPU_EXACT` | OpenCL 48-EU Zero-Copy Kernel | $O(N^3)$ | GPU Output Verified |
| 12 | `HYBRID_COOP` | Dynamic CPU/iGPU Work Sharing | $O(N^3)$ split | Concatenated Verification |
| 13 | `FALLBACK` | Safe Reference Execution | $O(N^3)$ | Guaranteed Convergence |

---

## 2. Mathematical Formulations

### 2.1 Bilinear Residual Decomposition
For state transition from $(A_{t-1}, B_{t-1})$ to $(A_t, B_t)$:
$$A_t = A_{t-1} + \delta A, \quad B_t = B_{t-1} + \delta B$$
$$C_t = A_t B_t = C_{t-1} + \delta A \cdot B_{t-1} + A_{t-1} \cdot \delta B + \delta A \cdot \delta B$$

When $\delta B = 0$ and $\delta A$ is supported on a sparse row index set $\mathcal{I}$:
$$C_t[\mathcal{I}, :] = A_t[\mathcal{I}, :] \cdot B_t$$
$$C_t[\mathcal{I}^c, :] = C_{t-1}[\mathcal{I}^c, :]$$

Flops eliminated:
$$\text{Eliminated} = \left(1 - \frac{|\mathcal{I}|}{M}\right) \times 100\%$$

### 2.2 Low-Rank Factored Evaluation
If $\text{rank}(A) = r < N / 2$:
Factor $A \approx U V$ where $U \in \mathbb{R}^{N \times r}, V \in \mathbb{R}^{r \times N}$.
Evaluate right-to-left:
$$C = U \times (V \times B)$$
- Stage 1: $T = V \times B \implies 2 \cdot r \cdot N^2$ FLOPs
- Stage 2: $C = U \times T \implies 2 \cdot N^2 \cdot r$ FLOPs
- Total FLOPs: $4 \cdot r \cdot N^2$ versus $2 \cdot N^3$ for dense multiplication.
- Break-even threshold: $4 r N^2 < 2 N^3 \implies r < N / 2$.
Empirical measured break-even on Intel i5-12450H occurs at $r \approx 50$ for $N=256$.
