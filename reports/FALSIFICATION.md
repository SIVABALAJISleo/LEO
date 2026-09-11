# LEO / HYPER: Scientific Falsification Report

**Document**: `reports/FALSIFICATION.md`  
**Version**: 1.0.0  
**Scientific Method**: Every optimization candidate is subjected to active attempts to disprove it.

---

## 1. 13 Hostile Adversarial Stress Suites

| Suite ID | Adversarial Payload Description | Observed Behavior | Status |
| :--- | :--- | :--- | :--- |
| **STRESS_01** | Subnormal floating point inputs ($10^{-38}$) | Exact fallback handled underflow | **PASS** |
| **STRESS_02** | Injected IEEE-754 NaNs and Infs | Sanitizer caught NaNs; triggered fallback | **PASS** |
| **STRESS_03** | Rank-1 degenerate matrices | SVD factored down to $r=1$ | **PASS** |
| **STRESS_04** | Ill-conditioned matrices ($\kappa > 10^{12}$) | Condition number detector triggered exact path | **PASS** |
| **STRESS_05** | Heavy-tailed Cauchy distribution shift | Sensitivity bound exceeded; exact fallback | **PASS** |
| **STRESS_06** | Instantaneous scene cut (all pixels changed) | Delta detector caught 100% diff; re-rendered | **PASS** |
| **STRESS_07** | Cryptographic cache key collision attack | Hash seal mismatch rejected overwrite | **PASS** |
| **STRESS_08** | Memory budget starvation | Streaming in-place buffers activated | **PASS** |
| **STRESS_09** | Strict deadline pressure ($t_{\text{rem}} \to 0$) | Dropped optional tiers; computed core observable | **PASS** |
| **STRESS_10** | Checkerboard and block-diagonal sparsity | CSR format preserved exact values | **PASS** |
| **STRESS_11** | Gradient explosion ($10^6\times$ magnitude jump) | Dynamic range clipping prevented overflow | **PASS** |
| **STRESS_12** | Precision truncation to FP8 | Error exceeded contract bound; rejected shortcut | **PASS** |
| **STRESS_13** | Zero-tolerance exact contract ($\varepsilon = 0$) | All lossy shortcuts blocked; exact execution | **PASS** |
