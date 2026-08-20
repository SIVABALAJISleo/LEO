# 📜 Full-Stack Benchmark & Falsification Protocol (Phase 3)

**Protocol Version:** `2.0.0-FALSIFICATION-GAUNTLET`  
**Status:** **FROZEN & IMMUTABLE**  

---

## 1. Adversarial Falsification Methodology

This protocol is designed to test the claim:
> *"HYPER replaces dedicated GPUs for all workloads end-to-end across the entire hardware/software stack."*

The protocol treats this claim as a hypothesis to be falsified. If HYPER fails to achieve functional equivalence or performance parity against a physical discrete GPU in **any** material category, the universal replacement claim is ruled **FALSIFIED**, and the specific validated boundary is recorded.

---

## 2. Hardcoded Pass/Fail Thresholds

1. **Numerical Correctness:**
   - Double-precision reference standard ($C_{\text{ref}}$).
   - Maximum absolute error $\Delta \le 10^{-4}$ for floating-point calculations.
   - Exact bitwise matching for integer hashing and cryptographic tasks.
2. **Performance Target:**
   - Universal replacement requires $\ge 100\%$ throughput of the dedicated GPU reference baseline.
   - Interactive tasks require P95 latency $\le 16.0\,\text{ms}$ (graphics) or $\le \text{P95}_{\text{dGPU}}$ (AI).
3. **Cache Integrity (Two Separate Tracks):**
   - **Track 1 (Uncached):** 100% active model generation. Semantic cache strictly disabled.
   - **Track 2 (Cached):** Measures exact hit rate, semantic similarity hit rate, and zero-compute lookup latency.
   - *Rule: Cached and uncached numbers must NEVER be merged into a single headline metric.*
4. **Endurance & Stability:**
   - Continuous multi-workload execution for up to 60 minutes.
   - Maximum permitted performance degradation (thermal throttling drop): $\le 15.0\%$.
   - Memory leak tolerance: $\le 256\,\text{MB}$.

---

## 3. The 8 Evaluation Domains

- **Domain A — Dense Compute:** FP32/FP16/INT8 GEMM, FFT, Convolutions, Vector Reductions.
- **Domain B — AI / Machine Learning:** Transformer Attention, Embeddings, CNN, Batch 1 vs Batch 8/16/32, TTFT, Tokens/sec.
- **Domain C — AI Component Ablation:** Baseline $\to$ +Quant $\to$ +Speculative $\to$ +Heterogeneous $\to$ +Cache $\to$ +MoE.
- **Domain D — Graphics:** Complete rendering pipeline (Vertex $\to$ Raster $\to$ Fragment $\to$ Compute).
- **Domain E — Ray Tracing:** BVH construction, Ray traversal, Shadows, Global Illumination.
- **Domain F — Media:** 4K decode $\to$ convolution filter $\to$ encode.
- **Domain G — Scientific / HPC:** N-Body ($10^6$ bodies), Monte Carlo, Linear Algebra.
- **Domain H — Real Application & System Integration:** Blender viewport/geometry scaling, Unity/Unreal graphics pipeline, driver interaction, DMA data movement.
