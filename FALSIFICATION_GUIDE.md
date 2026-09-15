# FALSIFICATION GUIDE FOR LEO/HYPER

**Standard:** Popperian Scientific Falsification Protocol  
**Purpose:** Defines exact conditions under which claims made by this project are considered falsified.  

---

## 1. Primary Falsification Conditions

A claim made by LEO/HYPER is considered **FALSIFIED** if any of the following occur:

### 1.1 Unproven Exactness
- **Claim:** A computation candidate executed via `CACHED`, `REDUCED_WORK`, or `NUMERICALLY_APPROXIMATE` is claimed to be mathematically exact.
- **Falsification Test:** Calculate maximum absolute error $|y_{\text{candidate}} - y_{\text{ground\_truth}}|$. If max error $> 0.0$, the claim of exactness is falsified.

### 1.2 Unaccounted Factorization Overhead
- **Claim:** Low-rank factorization ($A \approx U_k \Sigma_k V_k^T$) provides speedup for a one-shot matrix multiplication.
- **Falsification Test:** Measure total elapsed time including randomized SVD decomposition:
  $$T_{\text{total}} = T_{\text{factorize}} + T_{\text{low\_rank}}$$
  If $T_{\text{total}} \ge T_{\text{dense}}$, the claim of one-shot speedup is falsified.

### 1.3 Unverified Sparsity Advantage
- **Claim:** Thresholding matrix values below $\tau$ produces faster execution.
- **Falsification Test:** Measure:
  $$T_{\text{pipeline}} = T_{\text{threshold}} + T_{\text{sparse}} + T_{\text{verify}}$$
  If $T_{\text{pipeline}} \ge T_{\text{dense}}$, the claim of sparse speedup is falsified.

### 1.4 Unjustified Hardware Equivalences
- **Claim:** Software running on the Intel Core i5 + Intel UHD iGPU possesses RTX 5090 CUDA throughput or memory bandwidth.
- **Falsification Test:** Run unreduced dense FP32 GEMM without pruning or caching. The raw hardware ratio will remain approximately 1.85% of RTX 5090 throughput.

### 1.5 Contract Violations
- **Claim:** Candidate satisfies contract $C$.
- **Falsification Test:** If measured metric (e.g. $max\_abs\_error$, latency, or SSIM) violates the contract threshold, `contract_satisfied` must report `False` and trigger exact fallback. If the candidate was accepted anyway, the contract enforcement claim is falsified.
