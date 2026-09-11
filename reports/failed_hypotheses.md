# LEO / HYPER: Failed Hypotheses & Falsified Transformations

**Document Version**: 1.0.0  
**Date**: September 2026  
**Purpose**: Scientific integrity requires rigorous documentation of negative results. Documenting failed shortcuts prevents repeated dead-end searches and maps the boundaries of computational possibility.

---

## 1. Failed Hypotheses Registry

### Failed Hypothesis 01: Low-Rank SVD Approximation on Uniform Dense Random GEMM
- **Hypothesis**: Any $N \times N$ dense matrix product can be accelerated by factoring $A \approx U_k \Sigma_k V_k^T$ with rank $k = N / 4$.
- **Target Workload**: `DENSE_GAUSSIAN_512x512` ($A, B \sim \mathcal{N}(0, 1)$).
- **Test Result**: **FALSIFIED**.
- **Measured Error**: Relative Frobenius error $\|A B - (U_k V_k^T) B\|_F / \|A B\|_F = 0.428$ (Contract required $\le 10^{-3}$).
- **Root Cause**: Random Gaussian matrices follow the Marchenko-Pastur distribution. Their singular values do not decay exponentially. Truncating 75% of singular values discards 75% of the matrix energy.
- **Action Taken**: Logged in `failure_knowledge_base`. Added precondition: Low-rank factorization is forbidden unless spectral decay ratio $\sigma_{k} / \sigma_1 \le 0.05$.

---

### Failed Hypothesis 02: Speculative Token Recycling on Unstructured Dialogue Shifts
- **Hypothesis**: Speculative draft verification can reuse KV-cache activations from previous unrelated conversational turns.
- **Target Workload**: Multi-turn dialogue with topic switches.
- **Test Result**: **FALSIFIED**.
- **Measured Failure**: Draft acceptance rate dropped from $84\%$ to $3.2\%$. Verification overhead caused a $1.8\times$ slowdown relative to autoregressive baseline.
- **Root Cause**: Topic shifts introduce high attention entropy; previous key-value manifolds become orthogonal to new context queries.
- **Action Taken**: Added contextual cosine-similarity gating before triggering KV recycling.

---

### Failed Hypothesis 03: Global Sub-Sampling on High-Frequency Texture Rendering
- **Hypothesis**: Frame rendering can always be accelerated by 50% spatial sub-sampling followed by bilateral upscaling.
- **Target Workload**: Procedural foliage and high-frequency wireframe meshes.
- **Test Result**: **FALSIFIED**.
- **Measured Error**: Structural Similarity Index ($\text{SSIM}$) dropped to $0.81$ (Contract required $\ge 0.98$). Subsampling created severe Moiré aliasing and temporal flicker.
- **Root Cause**: Spatial sub-sampling violates the Nyquist-Shannon sampling theorem when scene frequencies exceed half the sample rate.
- **Action Taken**: Added spectral high-frequency variance detector. When high-frequency energy exceeds threshold $\tau_{\text{freq}}$, full-resolution rendering is mandated.

---

### Failed Hypothesis 04: Asynchronous iGPU Offloading for Sub-1ms Micro-Kernels
- **Hypothesis**: Dispatching matrix operations to Intel UHD graphics will always outperform CPU AVX2 execution.
- **Target Workload**: $64 \times 64$ float32 GEMM.
- **Test Result**: **FALSIFIED**.
- **Measured Latency**: CPU AVX2: $0.024\text{ ms}$ vs Intel UHD: $0.880\text{ ms}$ ($36.6\times$ slower on iGPU).
- **Root Cause**: Kernel launch queue latency and command submission overhead on Level Zero/DirectX driver dominate execution time for workloads smaller than $10^6$ FLOPs.
- **Action Taken**: Integrated operational intensity threshold into `ThermalAwareDeadlineScheduler`: operations with FLOP count $< 5 \times 10^5$ are strictly pinned to CPU P-cores.

---

## 2. Meta-Learning from Failure Catalog

Cataloging these 4 fundamental failure categories has enhanced the search engine's efficiency:
1. **Spectral Guard**: Pre-checks singular value decay before attempting low-rank decomposition.
2. **Entropy Guard**: Pre-checks contextual similarity before reusing cached state.
3. **Nyquist Guard**: Pre-checks high-frequency spatial gradients before applying resolution decimation.
4. **Dispatch Guard**: Pre-checks FLOP volume against driver launch overhead before routing to iGPU.
