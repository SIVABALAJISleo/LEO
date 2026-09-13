# HYPER / LEO Necessary-Work Specification & Elimination Ledger

## 1. The Principle of Minimal Information & Computation
In brute-force computing architectures (e.g. monolithic GPU clusters), dense matrix multiplication $Y = A \times B$ is executed by evaluating all $2 \cdot M \cdot K \cdot N$ floating-point operations regardless of structure, context, or observable requirements.

HYPER operates under the fundamental principle:
> **"Never optimize computation merely because it exists. Determine what information is necessary, what computation is required, and compute only the irreducible remainder."**

---

## 2. Work Categorization Taxonomies
Every workload is decomposed into explicit operational categories:

| Category | Definition | Accounting Rule |
| :--- | :--- | :--- |
| **`ORIGINAL_WORK`** | Total nominal FLOPs of the canonical reference implementation ($2 M K N$). | Baseline denominator. |
| **`NECESSARY_WORK`** | Minimal FLOPs mathematically required to produce the requested observable under Contract $\mathcal{C}$. | Proven or measured remainder. |
| **`ELIMINABLE_WORK`** | Operations redundant due to zero-entries, low-rank subspace, or unobserved outputs. | $\text{Original} - \text{Necessary}$. |
| **`REUSED_WORK`** | Operations avoided by direct exact cryptographic cache hits or temporal memoization. | Logged in `exact_reuse`. |
| **`APPROXIMATED_WORK`** | Operations avoided by bounded numerical approximation (e.g. INT4 or truncated SVD). | Validated against $\epsilon$. |
| **`PREDICTED_WORK`** | Operations avoided by temporal extrapolation or speculative draft proposals. | Validated against verifier. |
| **`RECONSTRUCTED_WORK`** | Operations avoided by perceptual interpolation or spatial super-resolution. | Validated against SSIM/PSNR. |
| **`VERIFICATION_WORK`** | Overhead incurred by randomized checks (e.g. Freivalds $O(N^2)$ probe) and contract verifiers. | Added to candidate cost. |
| **`FALLBACK_WORK`** | Reference computation executed when shortcut verification fails. | Added to penalty cost. |

---

## 3. The Work Elimination Ratio Formula
$$\text{Work Elimination Ratio} = 1.0 - \frac{\text{Measured Necessary FLOPs} + \text{Verification Overhead FLOPs}}{\text{Reference Nominal FLOPs}}$$

**Strict Invariant**:
No work reduction percentage may be asserted as a hard-coded constant (e.g. "90%", "99%", "100%"). Every percentage must be computed dynamically from the operation count of the candidate kernel and verified against the reference workload.
