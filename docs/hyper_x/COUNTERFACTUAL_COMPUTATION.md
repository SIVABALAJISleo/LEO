# Counterfactual Computation & Information Boundaries in HYPER-X

## 1. What is Counterfactual Computation?

In standard compiler analysis, program statements are taken as essential: if the programmer writes $C = A \times B$, the compiler must compute all $M \times K \times N$ scalar multiply-accumulate operations.

**Counterfactual Computation** asks the inverse question:
> *"What happens to the final observable output if this operation is omitted, approximated, predicted, or replaced?"*

For every intermediate node $v$ in the Information Dependency Graph, the compiler constructs a counterfactual mutation $\tilde{v}$ and measures its impact on the contract satisfaction function $\Phi(Y)$:

$$\Delta \Phi = \|\Phi(Y(v)) - \Phi(Y(\tilde{v}))\|$$

If $\Delta \Phi \le \epsilon_{\text{contract}}$, the counterfactual modification is **contract-preserving**, and the corresponding computation can be permanently eliminated or substituted with an asymptotic shortcut.

---

## 2. Taxonomy of Counterfactual Mutations

1. **Omission Mutation (`OMISSION`)**:
   - Intermediate node $v$ is deleted entirely ($v \to 0$ or $v \to I$).
   - Applicable when $v$ contributes to null-space directions of subsequent projection operators.
2. **Coarse + Residual Mutation (`COARSE_PLUS_RESIDUAL`)**:
   - Decomposes computation into a low-cost coarse basis plus a sparse residual update:
     $$A \approx U_r V_r + R$$
   - Inner product computation evaluates $U_r (V_r B) + R B$. When rank $r \ll N$ and $R$ is sparse, total FLOPs drop from $O(N^3)$ to $O(r N^2 + \text{nnz}(R) N)$.
3. **Temporal Delta Mutation (`TEMPORAL_DELTA`)**:
   - In iterative algorithms or graphics frame rendering, reuses prior state $Y_{t-1}$ and evaluates only the event-driven change:
     $$Y_t = Y_{t-1} + \Delta Y$$
   - Eliminates redundant background computations where temporal correlation $\rho > 0.95$.
4. **Output-Sensitive Projection Mutation (`OUTPUT_PROJECTION`)**:
   - When the contract only observes $y = (A B) x$, associativity allows evaluation as $A (B x)$, dropping complexity from $O(N^3)$ to $O(N^2)$.
5. **Speculative Prediction with Safe Fallback (`SPECULATIVE_PREDICT`)**:
   - Computes an ultra-fast learned surrogate $\hat{y} = f_\theta(x)$ and verifies it using an $O(N)$ or $O(N^2)$ residual check. If the residual exceeds $\epsilon$, the system seamlessly falls back to exact computation.
