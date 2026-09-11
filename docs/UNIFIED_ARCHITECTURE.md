# LEO / HYPER: Unified Architecture Specification

**Document Version**: 3.0.0 (Master Unified Escape Engine)  
**Target Hardware**: Intel Core i5-12450H (AVX2, FMA, 4P + 4E cores, 12 threads) + Intel UHD Graphics (48 EUs), 16 GB RAM, Windows 11.  
**Philosophy**: Never start with "How can the CPU imitate a powerful GPU?" Start with "Why does the application need the computation that the GPU is accelerating?"

---

## 1. End-to-End Computational Discovery Pipeline

The canonical architecture transforms an expensive computation into the cheapest verified computational path to the required observable:

```
                      ┌────────────────────────┐
                      │   APPLICATION INPUT    │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   WORKLOAD CAPTURE     │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   CONTRACT IR (10 Cls) │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │  OBSERVABLE COMPILER   │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │  INFORMATION BOUNDARY  │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │ NECESSARY-WORK ANALYZER│
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │COUNTERFACTUAL ELIMINATE│
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │ REPRESENTATION DISCOV. │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   ALGORITHM DISCOVERY  │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   PROGRAM REWRITE      │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │       HYPER IR         │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   COST MODEL & SCHED.  │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │ CPU / iGPU / HYBRID    │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │ INDEPENDENT VERIFIER   │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   ADVERSARIAL FUZZING  │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │     BLIND HOLDOUT      │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │ EXECUTION CERTIFICATE  │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │     KNOWLEDGE BASE     │
                      └───────────┬────────────┘
                                  │
                                  ▼
                      ┌────────────────────────┐
                      │   FUTURE DISCOVERY     │
                      └────────────────────────┘
```

---

## 2. The 21-Step Universal Computational Escape Search Sequence

Every incoming workload is evaluated through a strict, hierarchical 21-step search order prioritizing work elimination over micro-optimization:

1. **Exact Cache**: Bit-exact SHA-256 state matching. If hit, 100% compute is eliminated ($O(1)$ latency).
2. **Reuse**: Partial subgraph memoization and static weight caching.
3. **Delta**: Dynamic frame-to-frame or query-to-query state differencing.
4. **Observable Reduction**: Slicing the output space (e.g. $4\text{K} \to 1080\text{p}$, full matrix $\to$ top-$k$).
5. **Necessity Analysis**: Causal DAG backward reachability; pruning provably dispensable nodes (`UNKNOWN` preserved).
6. **Elimination**: Proof-carrying region elimination with formal Lipschitz sensitivity guarantees.
7. **Reformulation**: Algebraic restructuring (associativity, distributivity, common subexpressions).
8. **Representation Change**: Synthesizing alternative mathematical substrates.
9. **Sparsity**: Zero-skipping, threshold filtering ($\le \varepsilon$), and CSR/COO compression.
10. **Low-Rank**: SVD/Nystrom truncation when intrinsic singular value decay is steep.
11. **Compression**: Quantization across 6 semantic priority tiers (FP32 $\to$ INT8/FP8/Ternary).
12. **Projection**: Dimensionality reduction preserving pairwise distances (Johnson-Lindenstrauss).
13. **Selective Computation**: Branch-aware and region-of-interest dynamic dispatch.
14. **Temporal Reuse**: Motion-vector reprojection and temporal accumulation.
15. **Prediction**: Low-cost neural/spline surrogate estimation.
16. **Residual Correction**: 7-Mode residual recalculation ($Y = \hat{Y} + R$).
17. **Surrogate Computation**: Physics/ODE reduced-order model substitution.
18. **Algorithm Discovery**: Evolutionary genome mutation and crossover across operator grammars.
19. **E-Graph Rewrite**: Equality saturation extracting minimum-cost AST expressions.
20. **Hardware-Aware Scheduling**: P-core, E-core, and Intel UHD partition based on $J(\text{lat}, \text{eng}, \text{therm}, \text{mem})$.
21. **Micro-Optimization**: AVX2/FMA vectorization, cache tiling, zero-copy USM memory.

---

## 3. Strict Separation of Metrics (Section 4 & Section 104)

The architecture forbids merging disparate evaluation concepts into a single vanity score. The system strictly separates:

- **Raw Hardware Parity**: Silicon vs silicon throughput comparison (Intel UHD 48 EUs cannot match discrete RTX silicon).
- **Contract Parity**: Does the optimized output satisfy application constraints within declared tolerance $\varepsilon$?
- **Work Elimination Ratio ($WE$)**: Percentage of original FLOPs proven unnecessary and removed ($1 - W_{\text{cand}} / W_{\text{ref}}$).
- **Hardware Advantage Erasure ($HAE$)**: Proportion of GPU-specific advantages rendered irrelevant ($1 - GADR$).
- **Application Parity**: Real-world application SLO compliance (interactive FPS, SSIM, model perplexity, convergence rate).
