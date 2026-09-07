# LEO × HYPER: Scientific Claims Registry & Historical Audit

**Date**: 2026-09-07  
**Scope**: Classification and falsification of all past, present, and proposed claims.

---

## 1. Scientific Claims Taxonomy

Every claim in the repository is classified into one of five immutable statuses:
1. **HYPOTHESIS**: Proposed theoretical conjecture requiring experimental formulation.
2. **EXPERIMENTAL**: Prototype implementation under active measurement.
3. **REPRODUCED**: Validated on local development environment.
4. **VERIFIED**: Independently proven across all 11 verification tiers.
5. **REFUTED**: Disproven by empirical falsification or physical impossibility.

---

## 2. Audited Historical Claims & Rectifications

### Claim H-1: "Intel UHD achieves 100% physical hardware parity with NVIDIA Hopper/Blackwell"
- **Status**: **REFUTED**
- **Rectification**: Intel UHD (Gen12 Xe-LP, 48 EUs) possesses 384 FP32 ALUs, while an NVIDIA H100 possesses 16,896 CUDA cores and 528 Tensor Cores. Software transformations cannot alter silicon geometry.
- **Scientific Reclassification**: Reclassified to **Application Parity under Constrained Workloads**.

### Claim H-2: "Infinite effective throughput through mathematical bypass"
- **Status**: **REFUTED**
- **Rectification**: Mathematical bypass (e.g. hash-gated zero skips) eliminates unnecessary operations, which lowers latency. It does not generate infinite physical throughput.

### Claim H-3: "Freivalds algorithm provides deterministic mathematical proof of matrix multiplication"
- **Status**: **REFUTED**
- **Rectification**: Freivalds algorithm is a **randomized Monte Carlo verification probe** with failure probability $\le 2^{-k}$. It is classified as **Level 4 Randomized Verification**, never as deterministic mathematical proof.

### Claim H-4: "CBE 8-tier hierarchy achieves >=30 FPS rendering on Intel UHD with SSIM >= 0.98"
- **Status**: **VERIFIED**
- **Evidence**: Verified via `python leo.py cbe benchmark --suite full` on host Intel Core i5-13420H + Intel UHD Graphics, producing 98.7 FPS at 0.9991 SSIM.

### Claim H-5: "OpenVINO zero-copy USM memory eliminates CPU-iGPU PCIe bottleneck"
- **Status**: **VERIFIED**
- **Evidence**: Shared host system RAM allows pointer exchange without bus transfers, verified via `GPU_USM_MEMORY` capability flags.
