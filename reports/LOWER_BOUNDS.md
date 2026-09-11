# LEO / HYPER: Lower-Bound & Indispensable Work Report

**Document**: `reports/LOWER_BOUNDS.md`  
**Version**: 1.0.0  
**Principle**: The system distinguishes between computation that has not yet been optimized vs computation that is provably necessary.

---

## 1. Lower Bound Classifications

- **`PROVABLY_NECESSARY_UNDER_MODEL`**:
  - `DENSE_GAUSSIAN_EXACT`: Contract specifies `EXACT_EQUIVALENT` ($\varepsilon = 0$). SVD and low-rank decompositions cannot reduce operations without introducing non-zero truncation error.
- **`CURRENTLY_NECESSARY`**:
  - `SpMV_CSR_10k`: Tested SVD, Nystrom, and randomized subspace projections all exceeded tolerance threshold $\varepsilon = 1.0 \times 10^{-3}$. Current scientific evidence demonstrates that uniform random sparsity requires full non-zero traversal.
- **`NOT_YET_OPTIMIZED`**:
  - Open multi-dimensional workloads where search space remains unexplored by evolutionary synthesis.
